// placeholderimport React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator, Share, Platform, Alert } from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'

export default function ReferralsScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const { profile } = useProfile()
  const [referrals, setReferrals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)

  useEffect(() => { loadReferrals() }, [session])

  async function loadReferrals() {
    if (!session?.user?.id) return
    const { data } = await supabase
      .from('referrals')
      .select('*, referred:referred_id(full_name, created_at)')
      .eq('referrer_id', session.user.id)
      .order('created_at', { ascending: false })
    setReferrals(data ?? [])
    setLoading(false)
  }

  async function handleShare() {
    const code = profile?.referral_code
    if (!code) return
    const message = `Únete a Solva con mi código ${code} y obtén un descuento en tu primer servicio. Descarga la app en getsolva.co`
    try {
      if (Platform.OS === 'web') {
        await navigator.clipboard.writeText(message)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } else {
        await Share.share({ message, url: `https://getsolva.co?ref=${code}` })
      }
    } catch (err) {
      console.log(err)
    }
  }

  async function handleCopyCode() {
    const code = profile?.referral_code
    if (!code) return
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const completed = referrals.filter(r => r.status === 'completed' || r.status === 'rewarded').length
  const pending = referrals.filter(r => r.status === 'pending').length
  const totalReward = referrals.filter(r => r.status === 'rewarded').reduce((s, r) => s + (r.reward_amount || 0), 0)

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Programa de referidos</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>
        {/* Hero */}
        <View style={s.hero}>
          <Text style={s.heroEmoji}>🎁</Text>
          <Text style={s.heroTitle}>Invita y gana</Text>
          <Text style={s.heroDesc}>Por cada amigo que completa su primer pago en Solva, ambos recibís una recompensa.</Text>
        </View>

        {/* Código */}
        <View style={s.codeCard}>
          <Text style={s.codeLabel}>Tu código de referido</Text>
          <TouchableOpacity style={s.codeBox} onPress={handleCopyCode}>
            <Text style={s.codeText}>{profile?.referral_code ?? '...'}</Text>
            <Ionicons name={copied ? 'checkmark-circle' : 'copy-outline'} size={22} color={copied ? '#10B981' : '#2563EB'} />
          </TouchableOpacity>
          <Text style={s.codeTip}>{copied ? '✅ Copiado!' : 'Toca para copiar'}</Text>
        </View>

        {/* Compartir */}
        <TouchableOpacity style={s.shareBtn} onPress={handleShare}>
          <Ionicons name="share-social-outline" size={20} color="#fff" />
          <Text style={s.shareBtnText}>Compartir mi código</Text>
        </TouchableOpacity>

        {/* Stats */}
        <View style={s.statsRow}>
          <View style={s.statCard}>
            <Text style={s.statValue}>{referrals.length}</Text>
            <Text style={s.statLabel}>Invitados</Text>
          </View>
          <View style={s.statCard}>
            <Text style={[s.statValue, { color: '#10B981' }]}>{completed}</Text>
            <Text style={s.statLabel}>Completados</Text>
          </View>
          <View style={s.statCard}>
            <Text style={[s.statValue, { color: '#F59E0B' }]}>{pending}</Text>
            <Text style={s.statLabel}>Pendientes</Text>
          </View>
          <View style={s.statCard}>
            <Text style={[s.statValue, { color: '#7C3AED' }]}>{totalReward.toFixed(0)}€</Text>
            <Text style={s.statLabel}>Ganado</Text>
          </View>
        </View>

        {/* Como funciona */}
        <View style={s.howCard}>
          <Text style={s.howTitle}>¿Cómo funciona?</Text>
          {[
            { icon: '📤', text: 'Comparte tu código con amigos' },
            { icon: '📝', text: 'Se registran con tu código' },
            { icon: '💳', text: 'Completan su primer pago' },
            { icon: '🎉', text: 'Ambos recibís una recompensa' },
          ].map((step, i) => (
            <View key={i} style={s.howStep}>
              <Text style={s.howStepIcon}>{step.icon}</Text>
              <Text style={s.howStepText}>{step.text}</Text>
            </View>
          ))}
        </View>

        {/* Lista referidos */}
        {loading ? <ActivityIndicator color="#2563EB" style={{ marginTop: 20 }} /> : referrals.length > 0 ? (
          <View style={s.listCard}>
            <Text style={s.listTitle}>Tus referidos</Text>
            {referrals.map((r, i) => (
              <View key={i} style={s.listItem}>
                <View style={s.listAvatar}>
                  <Text style={s.listAvatarText}>{(r.referred?.full_name ?? '?')[0].toUpperCase()}</Text>
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={s.listName}>{r.referred?.full_name ?? 'Usuario'}</Text>
                  <Text style={s.listDate}>{new Date(r.created_at).toLocaleDateString('es-ES')}</Text>
                </View>
                <View style={[s.listBadge, { backgroundColor: r.status === 'rewarded' ? '#D1FAE5' : r.status === 'completed' ? '#DBEAFE' : '#FEF3C7' }]}>
                  <Text style={[s.listBadgeText, { color: r.status === 'rewarded' ? '#065F46' : r.status === 'completed' ? '#1D4ED8' : '#92400E' }]}>
                    {r.status === 'rewarded' ? '✅ Recompensado' : r.status === 'completed' ? '🎯 Completado' : '⏳ Pendiente'}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        ) : (
          <View style={s.emptyCard}>
            <Text style={s.emptyEmoji}>👥</Text>
            <Text style={s.emptyText}>Aún no tienes referidos</Text>
            <Text style={s.emptySub}>Comparte tu código y empieza a ganar</Text>
          </View>
        )}
      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.06)' },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  content: { padding: 20, gap: 16 },
  hero: { backgroundColor: '#1a1a2e', borderRadius: 24, padding: 28, alignItems: 'center' },
  heroEmoji: { fontSize: 48, marginBottom: 12 },
  heroTitle: { fontSize: 26, fontWeight: '900', color: '#fff', marginBottom: 8 },
  heroDesc: { fontSize: 14, color: 'rgba(255,255,255,0.65)', textAlign: 'center', lineHeight: 20 },
  codeCard: { backgroundColor: '#fff', borderRadius: 20, padding: 20, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)', alignItems: 'center', gap: 8 },
  codeLabel: { fontSize: 13, color: '#888', fontWeight: '600' },
  codeBox: { flexDirection: 'row', alignItems: 'center', gap: 12, backgroundColor: '#EFF6FF', borderRadius: 14, paddingHorizontal: 24, paddingVertical: 14, width: '100%', justifyContent: 'center' },
  codeText: { fontSize: 28, fontWeight: '900', color: '#1a1a2e', letterSpacing: 4 },
  codeTip: { fontSize: 12, color: '#888' },
  shareBtn: { backgroundColor: '#2563EB', borderRadius: 16, height: 52, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10 },
  shareBtnText: { fontSize: 15, fontWeight: '700', color: '#fff' },
  statsRow: { flexDirection: 'row', gap: 10 },
  statCard: { flex: 1, backgroundColor: '#fff', borderRadius: 16, padding: 14, alignItems: 'center', gap: 4, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  statValue: { fontSize: 22, fontWeight: '800', color: '#1a1a2e' },
  statLabel: { fontSize: 11, color: '#9CA3AF', textAlign: 'center' },
  howCard: { backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 12, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)' },
  howTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  howStep: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  howStepIcon: { fontSize: 20, width: 32 },
  howStepText: { fontSize: 14, color: '#444', flex: 1 },
  listCard: { backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 12, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)' },
  listTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  listItem: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 8, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)' },
  listAvatar: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#EFF6FF', alignItems: 'center', justifyContent: 'center' },
  listAvatarText: { fontSize: 16, fontWeight: '700', color: '#2563EB' },
  listName: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  listDate: { fontSize: 12, color: '#9CA3AF' },
  listBadge: { borderRadius: 8, paddingHorizontal: 8, paddingVertical: 4 },
  listBadgeText: { fontSize: 11, fontWeight: '700' },
  emptyCard: { backgroundColor: '#fff', borderRadius: 20, padding: 32, alignItems: 'center', gap: 8, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)' },
  emptyEmoji: { fontSize: 40 },
  emptyText: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  emptySub: { fontSize: 13, color: '#888', textAlign: 'center' },
})