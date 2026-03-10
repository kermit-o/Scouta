import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useEffect, useState } from 'react'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'

type Review = { id: string; rating: number; comment: string | null; created_at: string; reviewer_id: string }

export default function ReputationScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      if (!session?.user?.id) return
      const { data } = await supabase.from('reviews').select('*').eq('reviewed_id', session.user.id).order('created_at', { ascending: false })
      setReviews(data || [])
      setLoading(false)
    }
    load()
  }, [session])

  const avg = reviews.length > 0 ? reviews.reduce((s, r) => s + r.rating, 0) / reviews.length : 0
  const dist = [5,4,3,2,1].map(n => ({ n, count: reviews.filter(r => r.rating === n).length }))

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Mi reputación</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.summaryCard}>
          <Text style={styles.avgScore}>{avg > 0 ? avg.toFixed(1) : '—'}</Text>
          <View style={styles.stars}>
            {[1,2,3,4,5].map(i => (
              <Ionicons key={i} name={i <= Math.round(avg) ? 'star' : 'star-outline'} size={22} color="#F59E0B" />
            ))}
          </View>
          <Text style={styles.reviewCount}>{reviews.length} valoraciones</Text>
          <View style={styles.distContainer}>
            {dist.map(({ n, count }) => (
              <View key={n} style={styles.distRow}>
                <Text style={styles.distLabel}>{n}★</Text>
                <View style={styles.distBar}>
                  <View style={[styles.distFill, { width: reviews.length > 0 ? `${(count / reviews.length) * 100}%` as any : '0%' }]} />
                </View>
                <Text style={styles.distCount}>{count}</Text>
              </View>
            ))}
          </View>
        </View>

        {loading ? <ActivityIndicator color="#2563EB" style={{ marginTop: 32 }} /> :
         reviews.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>⭐</Text>
            <Text style={styles.emptyTitle}>Sin valoraciones aún</Text>
            <Text style={styles.emptyDesc}>Completa jobs para recibir tu primera reseña.</Text>
          </View>
        ) : (
          <View style={styles.card}>
            {reviews.map((r, i) => (
              <View key={r.id} style={[styles.reviewRow, i < reviews.length - 1 && styles.rowBorder]}>
                <View style={styles.reviewTop}>
                  <View style={styles.reviewStars}>
                    {[1,2,3,4,5].map(s => <Ionicons key={s} name={s <= r.rating ? 'star' : 'star-outline'} size={14} color="#F59E0B" />)}
                  </View>
                  <Text style={styles.reviewDate}>{new Date(r.created_at).toLocaleDateString('es-ES')}</Text>
                </View>
                {r.comment && <Text style={styles.reviewComment}>{r.comment}</Text>}
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
  summaryCard: { backgroundColor: '#fff', borderRadius: 20, padding: 24, alignItems: 'center', gap: 8, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  avgScore: { fontSize: 56, fontWeight: '800', color: '#1a1a2e', lineHeight: 64 },
  stars: { flexDirection: 'row', gap: 4 },
  reviewCount: { fontSize: 13, color: '#9CA3AF' },
  distContainer: { width: '100%', gap: 6, marginTop: 8 },
  distRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  distLabel: { width: 24, fontSize: 12, color: '#9CA3AF', textAlign: 'right' },
  distBar: { flex: 1, height: 6, backgroundColor: '#F3F4F6', borderRadius: 3, overflow: 'hidden' },
  distFill: { height: '100%', backgroundColor: '#F59E0B', borderRadius: 3 },
  distCount: { width: 20, fontSize: 12, color: '#9CA3AF' },
  empty: { alignItems: 'center', paddingTop: 40, gap: 12 },
  emptyIcon: { fontSize: 48 },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  emptyDesc: { fontSize: 14, color: '#9CA3AF', textAlign: 'center' },
  card: { backgroundColor: '#fff', borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  reviewRow: { padding: 16, gap: 8 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  reviewTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  reviewStars: { flexDirection: 'row', gap: 2 },
  reviewDate: { fontSize: 12, color: '#9CA3AF' },
  reviewComment: { fontSize: 14, color: '#374151', lineHeight: 20 },
})
