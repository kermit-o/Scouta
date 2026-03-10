import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'

export default function DashboardProScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const { profile } = useProfile()
  const [stats, setStats] = useState({ jobs: 0, bids: 0, contracts: 0, earnings: 0, rating: 0, reviews: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!session?.user?.id) return
      const [bidsRes, contractsRes, reviewsRes] = await Promise.all([
        supabase.from('bids').select('id', { count: 'exact' }).eq('pro_id', session.user.id),
        supabase.from('contracts').select('id', { count: 'exact' }).eq('pro_id', session.user.id),
        supabase.from('reviews').select('rating').eq('reviewed_id', session.user.id),
      ])
      const reviews = reviewsRes.data || []
      const avgRating = reviews.length > 0 ? reviews.reduce((s, r) => s + r.rating, 0) / reviews.length : 0
      setStats({
        jobs: 0,
        bids: bidsRes.count || 0,
        contracts: contractsRes.count || 0,
        earnings: 0,
        rating: Math.round(avgRating * 10) / 10,
        reviews: reviews.length,
      })
      setLoading(false)
    }
    load()
  }, [session])

  if (profile?.role === 'client') return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Dashboard Pro</Text>
        <View style={{ width: 40 }} />
      </View>
      <View style={styles.upgradeContainer}>
        <Text style={styles.upgradeIcon}>🚀</Text>
        <Text style={styles.upgradeTitle}>Conviértete en Pro</Text>
        <Text style={styles.upgradeDesc}>Cambia tu rol a Profesional para acceder al dashboard y empezar a recibir jobs.</Text>
        <TouchableOpacity style={styles.upgradeBtn} onPress={() => router.push('/(app)/subscription')}>
          <Text style={styles.upgradeBtnText}>Ver planes Pro</Text>
        </TouchableOpacity>
      </View>
    </View>
  )

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Dashboard Pro</Text>
        <View style={{ width: 40 }} />
      </View>
      {loading ? <ActivityIndicator color="#2563EB" style={{ marginTop: 60 }} /> : (
        <ScrollView contentContainerStyle={styles.container}>
          <View style={styles.welcomeCard}>
            <Text style={styles.welcomeText}>Hola, {profile?.full_name?.split(' ')[0]} 👋</Text>
            <Text style={styles.welcomeSub}>Aquí tienes el resumen de tu actividad</Text>
          </View>
          <View style={styles.statsGrid}>
            {[
              { label: 'Ofertas enviadas', value: stats.bids, icon: '📩', color: '#2563EB' },
              { label: 'Contratos activos', value: stats.contracts, icon: '📄', color: '#16A34A' },
              { label: 'Valoración media', value: stats.rating || '—', icon: '⭐', color: '#F59E0B' },
              { label: 'Reseñas recibidas', value: stats.reviews, icon: '💬', color: '#7C3AED' },
            ].map((s, i) => (
              <View key={i} style={styles.statCard}>
                <Text style={styles.statIcon}>{s.icon}</Text>
                <Text style={[styles.statValue, { color: s.color }]}>{s.value}</Text>
                <Text style={styles.statLabel}>{s.label}</Text>
              </View>
            ))}
          </View>
          <TouchableOpacity style={styles.actionBtn} onPress={() => router.push('/(app)/jobs')}>
            <Ionicons name="briefcase-outline" size={20} color="#fff" />
            <Text style={styles.actionBtnText}>Ver jobs disponibles</Text>
          </TouchableOpacity>
          <TouchableOpacity style={[styles.actionBtn, { backgroundColor: '#F6F7FB', borderWidth: 1, borderColor: '#E5E7EB' }]} onPress={() => router.push('/(app)/profile')}>
            <Ionicons name="person-outline" size={20} color="#1a1a2e" />
            <Text style={[styles.actionBtnText, { color: '#1a1a2e' }]}>Completar mi perfil</Text>
          </TouchableOpacity>
        </ScrollView>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 16 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  title: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  container: { padding: 20, gap: 16 },
  welcomeCard: { backgroundColor: '#1a1a2e', borderRadius: 20, padding: 24 },
  welcomeText: { fontSize: 22, fontWeight: '800', color: '#fff' },
  welcomeSub: { fontSize: 13, color: 'rgba(255,255,255,0.6)', marginTop: 4 },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  statCard: { flex: 1, minWidth: '45%', backgroundColor: '#fff', borderRadius: 18, padding: 18, alignItems: 'center', gap: 6, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  statIcon: { fontSize: 24 },
  statValue: { fontSize: 28, fontWeight: '800' },
  statLabel: { fontSize: 12, color: '#9CA3AF', textAlign: 'center' },
  actionBtn: { backgroundColor: '#2563EB', borderRadius: 16, height: 52, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10 },
  actionBtnText: { fontSize: 15, fontWeight: '700', color: '#fff' },
  upgradeContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40, gap: 16 },
  upgradeIcon: { fontSize: 56 },
  upgradeTitle: { fontSize: 24, fontWeight: '800', color: '#1a1a2e' },
  upgradeDesc: { fontSize: 15, color: '#9CA3AF', textAlign: 'center', lineHeight: 22 },
  upgradeBtn: { backgroundColor: '#2563EB', borderRadius: 16, paddingHorizontal: 32, paddingVertical: 14, marginTop: 8 },
  upgradeBtnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
})
