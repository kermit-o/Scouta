import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, ScrollView, Alert
} from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

type Tab = 'kyc' | 'disputes' | 'payments'

export default function AdminScreen() {
  const { session } = useAuth()
  const { profile, loading: profileLoading } = useProfile()
  const insets = useSafeAreaInsets()
  const [tab, setTab] = useState<Tab>('kyc')
  const [kycs, setKycs] = useState<any[]>([])
  const [disputes, setDisputes] = useState<any[]>([])
  const [payments, setPayments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [acting, setActing] = useState<string | null>(null)

  useEffect(() => {
    if (!profileLoading && profile?.role !== 'admin') {
      router.replace('/(app)')
    }
  }, [profile, profileLoading])

  useEffect(() => {
    if (profile?.role === 'admin') loadAll()
  }, [profile])

  async function loadAll() {
    setLoading(true)
    const [kycRes, dispRes, payRes] = await Promise.all([
      supabase
        .from('kyc_verifications')
        .select('*, users(full_name, email, country)')
        .order('submitted_at', { ascending: false })
        .limit(50),
      supabase
        .from('disputes')
        .select('*, contracts(amount, currency, jobs(title)), opener:opener_id(full_name), accused:accused_id(full_name)')
        .order('created_at', { ascending: false })
        .limit(50),
      supabase
        .from('payments')
        .select('*, contracts(jobs(title)), client:client_id(full_name), pro:pro_id(full_name)')
        .order('created_at', { ascending: false })
        .limit(50),
    ])
    setKycs(kycRes.data ?? [])
    setDisputes(dispRes.data ?? [])
    setPayments(payRes.data ?? [])
    setLoading(false)
  }

  async function handleKyc(id: string, status: 'approved' | 'rejected', userId: string) {
    setActing(id)
    await supabase.from('kyc_verifications').update({
      status,
      reviewed_at: new Date().toISOString(),
      reviewer_id: session!.user.id,
    }).eq('id', id)
    if (status === 'approved') {
      await supabase.from('users').update({ is_verified: true }).eq('id', userId)
    }
    await loadAll()
    setActing(null)
  }

  async function handleDispute(id: string, resolution: 'resolved_client' | 'resolved_pro' | 'cancelled') {
    setActing(id)
    await supabase.from('disputes').update({
      status: 'resolved',
      resolution,
      resolved_at: new Date().toISOString(),
    }).eq('id', id)
    await loadAll()
    setActing(null)
  }

  const TABS: { key: Tab; label: string; icon: string; count: number }[] = [
    { key: 'kyc', label: 'KYC', icon: 'shield-checkmark-outline',
      count: kycs.filter(k => k.status === 'submitted').length },
    { key: 'disputes', label: 'Disputas', icon: 'warning-outline',
      count: disputes.filter(d => d.status === 'open').length },
    { key: 'payments', label: 'Pagos', icon: 'cash-outline',
      count: payments.filter(p => p.status === 'held').length },
  ]

  if (profileLoading || loading) {
    return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>
  }

  if (profile?.role !== 'admin') return null

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Panel Admin</Text>
        <TouchableOpacity onPress={loadAll} style={s.backBtn}>
          <Ionicons name="refresh-outline" size={22} color="#1a1a2e" />
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={s.tabBar}>
        {TABS.map(t => (
          <TouchableOpacity
            key={t.key}
            style={[s.tab, tab === t.key && s.tabActive]}
            onPress={() => setTab(t.key)}
          >
            <Ionicons name={t.icon as any} size={16} color={tab === t.key ? '#2563EB' : '#888'} />
            <Text style={[s.tabLabel, tab === t.key && s.tabLabelActive]}>{t.label}</Text>
            {t.count > 0 && (
              <View style={s.badge}>
                <Text style={s.badgeText}>{t.count}</Text>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </View>

      {/* KYC Tab */}
      {tab === 'kyc' && (
        <FlatList
          data={kycs}
          keyExtractor={i => i.id}
          contentContainerStyle={s.list}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={<Text style={s.empty}>No hay verificaciones</Text>}
          renderItem={({ item }) => (
            <View style={s.card}>
              <View style={s.cardRow}>
                <View style={[s.statusDot, { backgroundColor: item.status === 'submitted' ? '#F59E0B' : item.status === 'approved' ? '#059669' : item.status === 'rejected' ? '#DC2626' : '#9CA3AF' }]} />
                <View style={{ flex: 1 }}>
                  <Text style={s.cardName}>{item.users?.full_name ?? '—'}</Text>
                  <Text style={s.cardSub}>{item.users?.email} · {item.doc_type?.toUpperCase()}</Text>
                  <Text style={s.cardSub}>{item.status.toUpperCase()} · {item.users?.country}</Text>
                </View>
              </View>
              {/* Document previews */}
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginTop: 10, marginBottom: 8 }}>
                {item.doc_front_url && (
                  <View style={s.docPreview}>
                    <Text style={s.docLabel}>Frente</Text>
                    <Text style={s.docLink} onPress={() => {
                      if (typeof window !== 'undefined') window.open(item.doc_front_url, '_blank')
                    }}>🖼 Ver imagen</Text>
                  </View>
                )}
                {item.doc_back_url && (
                  <View style={s.docPreview}>
                    <Text style={s.docLabel}>Reverso</Text>
                    <Text style={s.docLink} onPress={() => {
                      if (typeof window !== 'undefined') window.open(item.doc_back_url, '_blank')
                    }}>🖼 Ver imagen</Text>
                  </View>
                )}
                {item.selfie_url && (
                  <View style={s.docPreview}>
                    <Text style={s.docLabel}>Selfie</Text>
                    <Text style={s.docLink} onPress={() => {
                      if (typeof window !== 'undefined') window.open(item.selfie_url, '_blank')
                    }}>🤳 Ver selfie</Text>
                  </View>
                )}
              </ScrollView>
              {item.status === 'submitted' && (
                <View style={s.actionRow}>
                  <TouchableOpacity
                    style={[s.actionBtn, s.approveBtn]}
                    disabled={acting === item.id}
                    onPress={() => handleKyc(item.id, 'approved', item.user_id)}
                  >
                    {acting === item.id
                      ? <ActivityIndicator size="small" color="#fff" />
                      : <Text style={s.actionBtnText}>✅ Aprobar</Text>
                    }
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[s.actionBtn, s.rejectBtn]}
                    disabled={acting === item.id}
                    onPress={() => handleKyc(item.id, 'rejected', item.user_id)}
                  >
                    <Text style={s.actionBtnText}>❌ Rechazar</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          )}
        />
      )}

      {/* Disputes Tab */}
      {tab === 'disputes' && (
        <FlatList
          data={disputes}
          keyExtractor={i => i.id}
          contentContainerStyle={s.list}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={<Text style={s.empty}>No hay disputas</Text>}
          renderItem={({ item }) => (
            <View style={s.card}>
              <Text style={s.cardName}>{item.contracts?.jobs?.title ?? 'Sin título'}</Text>
              <Text style={s.cardSub}>{item.contracts?.amount} {item.contracts?.currency} · {item.status?.toUpperCase()}</Text>
              <Text style={s.cardSub}>
                Abrió: {item.opener?.full_name ?? '—'} · Acusado: {item.accused?.full_name ?? '—'}
              </Text>
              {item.description && (
                <Text style={s.cardDesc} numberOfLines={3}>{item.description}</Text>
              )}
              {item.status === 'open' && (
                <View style={s.actionRow}>
                  <TouchableOpacity
                    style={[s.actionBtn, s.approveBtn]}
                    disabled={acting === item.id}
                    onPress={() => handleDispute(item.id, 'resolved_client')}
                  >
                    <Text style={s.actionBtnText}>👤 Favor cliente</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[s.actionBtn, { backgroundColor: '#7C3AED' }]}
                    disabled={acting === item.id}
                    onPress={() => handleDispute(item.id, 'resolved_pro')}
                  >
                    <Text style={s.actionBtnText}>🔧 Favor pro</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={[s.actionBtn, s.rejectBtn]}
                    disabled={acting === item.id}
                    onPress={() => handleDispute(item.id, 'cancelled')}
                  >
                    <Text style={s.actionBtnText}>Cancelar</Text>
                  </TouchableOpacity>
                </View>
              )}
            </View>
          )}
        />
      )}

      {/* Payments Tab */}
      {tab === 'payments' && (
        <FlatList
          data={payments}
          keyExtractor={i => i.id}
          contentContainerStyle={s.list}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={<Text style={s.empty}>No hay pagos</Text>}
          renderItem={({ item }) => (
            <View style={s.card}>
              <View style={s.cardRow}>
                <View style={[s.statusDot, {
                  backgroundColor: item.status === 'held' ? '#F59E0B' : item.status === 'released' ? '#059669' : '#9CA3AF'
                }]} />
                <View style={{ flex: 1 }}>
                  <Text style={s.cardName}>{item.contracts?.jobs?.title ?? '—'}</Text>
                  <Text style={s.cardSub}>
                    {item.amount} {item.currency} · {item.status?.toUpperCase()}
                  </Text>
                  <Text style={s.cardSub}>
                    Cliente: {item.client?.full_name ?? '—'} · Pro: {item.pro?.full_name ?? '—'}
                  </Text>
                  <Text style={s.cardSub}>
                    Plataforma: {item.platform_fee} {item.currency} · Pro recibe: {item.pro_amount} {item.currency}
                  </Text>
                </View>
              </View>
            </View>
          )}
        />
      )}
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14, backgroundColor: '#fff',
    borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.06)',
  },
  backBtn: { padding: 4 },
  headerTitle: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  tabBar: {
    flexDirection: 'row', backgroundColor: '#fff',
    borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.06)',
  },
  tab: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 5, paddingVertical: 12,
  },
  tabActive: { borderBottomWidth: 2, borderBottomColor: '#2563EB' },
  tabLabel: { fontSize: 13, fontWeight: '600', color: '#888' },
  tabLabelActive: { color: '#2563EB' },
  badge: {
    backgroundColor: '#DC2626', borderRadius: 8, minWidth: 16, height: 16,
    alignItems: 'center', justifyContent: 'center', paddingHorizontal: 3,
  },
  badgeText: { fontSize: 10, fontWeight: '800', color: '#fff' },
  list: { padding: 16, gap: 12 },
  empty: { textAlign: 'center', color: '#aaa', marginTop: 40, fontSize: 14 },
  card: {
    backgroundColor: '#fff', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  cardRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 12 },
  statusDot: { width: 10, height: 10, borderRadius: 5, marginTop: 5 },
  cardName: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 2 },
  cardSub: { fontSize: 12, color: '#888', marginBottom: 1 },
  cardDesc: { fontSize: 13, color: '#555', marginTop: 8, fontStyle: 'italic' },
  docPreview: {
    backgroundColor: '#F3F4F6', borderRadius: 10, padding: 10,
    marginRight: 8, alignItems: 'center', minWidth: 80,
  },
  docLabel: { fontSize: 11, color: '#888', marginBottom: 4 },
  docLink: { fontSize: 12, color: '#2563EB', fontWeight: '600' },
  actionRow: { flexDirection: 'row', gap: 8, marginTop: 12, flexWrap: 'wrap' },
  actionBtn: {
    flex: 1, borderRadius: 10, paddingVertical: 10,
    alignItems: 'center', justifyContent: 'center', minWidth: 80,
  },
  approveBtn: { backgroundColor: '#059669' },
  rejectBtn: { backgroundColor: '#DC2626' },
  actionBtnText: { fontSize: 13, fontWeight: '700', color: '#fff' },
})
