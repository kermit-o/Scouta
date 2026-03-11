import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase'
import { useSubscription } from '../../hooks/useSubscription'
import { useAuth } from '../../lib/AuthContext'

type Payment = { id: string; amount: number; currency: string; status: string; created_at: string; job_id: string }

const STATUS_COLOR: Record<string, string> = { completed: '#16A34A', pending: '#F59E0B', failed: '#DC2626', refunded: '#6B7280' }
const STATUS_LABEL: Record<string, string> = { completed: 'Completado', pending: 'Pendiente', failed: 'Fallido', refunded: 'Devuelto' }

export default function PaymentsScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const { isPro, isTrialing } = useSubscription()
  const [showUpgradeHint, setShowUpgradeHint] = useState(false)
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!session?.user?.id) return
      const { data } = await supabase.from('payments').select('*').eq('client_id', session.user.id).order('created_at', { ascending: false }).limit(30)
      setPayments(data || [])
      setLoading(false)
    }
    load()
  }, [session])

  const total = payments.filter(p => p.status === 'released').reduce((s, p) => s + p.amount, 0)

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Pagos y cobros</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryLabel}>Total pagado</Text>
          <Text style={styles.summaryAmount}>€{(total / 100).toFixed(2)}</Text>
          <Text style={styles.summaryNote}>{payments.filter(p => p.status === 'released').length} transacciones completadas</Text>
        </View>
        {loading ? <ActivityIndicator color="#2563EB" style={{ marginTop: 40 }} /> : payments.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>💳</Text>
            <Text style={styles.emptyTitle}>Sin transacciones</Text>
            <Text style={styles.emptyDesc}>Aquí aparecerán tus pagos y cobros.</Text>
          </View>
        ) : (
          <View style={styles.card}>
            {payments.map((p, i) => (
              <View key={p.id} style={[styles.row, i < payments.length - 1 && styles.rowBorder]}>
                <View style={[styles.statusDot, { backgroundColor: STATUS_COLOR[p.status] || '#9CA3AF' }]} />
                <View style={styles.rowInfo}>
                  <Text style={styles.rowLabel}>Job #{p.job_id.slice(0, 8)}</Text>
                  <Text style={styles.rowDate}>{new Date(p.created_at).toLocaleDateString('es-ES')}</Text>
                </View>
                <View style={styles.rowRight}>
                  <Text style={styles.rowAmount}>€{(p.amount / 100).toFixed(2)}</Text>
                  <Text style={[styles.rowStatus, { color: STATUS_COLOR[p.status] || '#9CA3AF' }]}>{STATUS_LABEL[p.status] || p.status}</Text>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 16 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  title: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  container: { padding: 20, gap: 16 },
  summaryCard: { backgroundColor: '#1a1a2e', borderRadius: 20, padding: 24, alignItems: 'center' },
  summaryLabel: { fontSize: 13, color: 'rgba(255,255,255,0.6)', marginBottom: 8 },
  summaryAmount: { fontSize: 36, fontWeight: '800', color: '#fff' },
  summaryNote: { fontSize: 12, color: 'rgba(255,255,255,0.4)', marginTop: 6 },
  empty: { alignItems: 'center', paddingTop: 60, gap: 12 },
  emptyIcon: { fontSize: 48 },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  emptyDesc: { fontSize: 14, color: '#9CA3AF', textAlign: 'center' },
  card: { backgroundColor: '#fff', borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  row: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  statusDot: { width: 10, height: 10, borderRadius: 5 },
  rowInfo: { flex: 1 },
  rowLabel: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  rowDate: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  rowRight: { alignItems: 'flex-end' },
  rowAmount: { fontSize: 15, fontWeight: '700', color: '#1a1a2e' },
  rowStatus: { fontSize: 11, fontWeight: '600', marginTop: 2 },
})
