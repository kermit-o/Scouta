import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, RefreshControl, TextInput
} from 'react-native'
import { router } from 'expo-router'
import { supabase, Job } from '../../lib/supabase'
import { useProfile } from '../../hooks/useProfile'
import { useLocation, searchJobsNearby } from '../../hooks/useLocation'

const CATEGORY_LABELS: Record<string, string> = {
  cleaning: '🧹 Limpieza', plumbing: '🔧 Fontaneria', electrical: '⚡ Electricidad',
  painting: '🎨 Pintura', moving: '📦 Mudanza', gardening: '🌿 Jardineria',
  carpentry: '🪚 Carpinteria', tech: '💻 Tecnologia', design: '✏️ Diseno', other: '🔹 Otro'
}

const RADIUS_OPTIONS = [5, 10, 25, 50, 100]

export default function JobsScreen() {
  const { profile } = useProfile()
  const { coords, requestLocation, loading: locLoading } = useLocation()
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchMode, setSearchMode] = useState<'all' | 'nearby'>('all')
  const [radius, setRadius] = useState(25)
  const [searchText, setSearchText] = useState('')

  async function fetchJobs() {
    setLoading(true)
    if (searchMode === 'nearby' && coords) {
      const { data } = await searchJobsNearby(coords.latitude, coords.longitude, radius)
      setJobs(data ?? [])
    } else {
      const query = supabase
        .from('jobs')
        .select('*')
        .eq('status', 'open')
        .eq('country', profile?.country ?? 'ES')
        .order('created_at', { ascending: false })

      if (searchText.trim()) {
        query.ilike('title', `%${searchText.trim()}%`)
      }

      const { data } = await query
      setJobs(data ?? [])
    }
    setLoading(false)
    setRefreshing(false)
  }

  useEffect(() => { fetchJobs() }, [searchMode, coords, radius])

  async function handleNearbyToggle() {
    if (searchMode === 'nearby') {
      setSearchMode('all')
    } else {
      if (!coords) {
        await requestLocation()
      }
      setSearchMode('nearby')
    }
  }

  function onRefresh() { setRefreshing(true); fetchJobs() }

  return (
    <View style={s.container}>
      {/* Header */}
      <View style={s.header}>
        <Text style={s.title}>💼 Jobs</Text>
        <View style={s.headerBtns}>
          <TouchableOpacity style={s.aiButton} onPress={() => router.push('/(app)/search')}>
            <Text style={s.aiButtonText}>🤖 IA</Text>
          </TouchableOpacity>
          {profile?.role !== 'pro' && (
            <TouchableOpacity style={s.newButton} onPress={() => router.push('/(app)/jobs/new')}>
              <Text style={s.newButtonText}>+ Publicar</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Buscador */}
      <View style={s.searchRow}>
        <TextInput
          style={s.searchInput}
          value={searchText}
          onChangeText={setSearchText}
          onSubmitEditing={fetchJobs}
          placeholder="Buscar trabajos..."
          returnKeyType="search"
        />
        <TouchableOpacity
          style={[s.nearbyBtn, searchMode === 'nearby' && s.nearbyBtnActive]}
          onPress={handleNearbyToggle}
          disabled={locLoading}
        >
          <Text style={[s.nearbyBtnText, searchMode === 'nearby' && s.nearbyBtnTextActive]}>
            {locLoading ? '...' : '📍'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Radio selector (solo en modo nearby) */}
      {searchMode === 'nearby' && (
        <View style={s.radiusRow}>
          <Text style={s.radiusLabel}>Radio:</Text>
          {RADIUS_OPTIONS.map(r => (
            <TouchableOpacity
              key={r}
              style={[s.radiusChip, radius === r && s.radiusChipActive]}
              onPress={() => setRadius(r)}
            >
              <Text style={[s.radiusChipText, radius === r && s.radiusChipTextActive]}>
                {r}km
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Lista */}
      {loading
        ? <View style={s.center}><ActivityIndicator size="large" color="#1a1a2e" /></View>
        : (
          <FlatList
            data={jobs}
            keyExtractor={item => item.id}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            contentContainerStyle={jobs.length === 0 ? s.emptyContainer : s.list}
            ListEmptyComponent={
              <View style={s.empty}>
                <Text style={s.emptyText}>
                  {searchMode === 'nearby' ? 'No hay jobs en este radio' : 'No hay jobs disponibles'}
                </Text>
                <Text style={s.emptySub}>
                  {searchMode === 'nearby' ? 'Prueba aumentar el radio de busqueda' : 'Se el primero en publicar'}
                </Text>
              </View>
            }
            renderItem={({ item }) => (
              <TouchableOpacity
                style={s.card}
                onPress={() => router.push(`/(app)/jobs/${item.id}`)}
              >
                <View style={s.cardHeader}>
                  <Text style={s.category}>{CATEGORY_LABELS[item.category]}</Text>
                  <View style={s.cardHeaderRight}>
                    {item.distance_km != null && (
                      <Text style={s.distance}>📍 {item.distance_km}km</Text>
                    )}
                    {item.is_remote && <Text style={s.remote}>🌐</Text>}
                  </View>
                </View>
                <Text style={s.jobTitle}>{item.title}</Text>
                <Text style={s.description} numberOfLines={2}>{item.description}</Text>
                <View style={s.cardFooter}>
                  {item.budget_min || item.budget_max
                    ? <Text style={s.budget}>💰 {item.budget_min ?? '?'} — {item.budget_max ?? '?'} {item.currency}</Text>
                    : <Text style={s.budget}>💰 A negociar</Text>
                  }
                  {item.city && <Text style={s.city}>📍 {item.city}</Text>}
                </View>
              </TouchableOpacity>
            )}
          />
        )
      }
    </View>
  )
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 24, paddingTop: 60, paddingBottom: 12 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a1a2e' },
  headerBtns: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  aiButton: { backgroundColor: '#f5f5ff', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, borderWidth: 1, borderColor: '#1a1a2e' },
  aiButtonText: { color: '#1a1a2e', fontWeight: '700', fontSize: 14 },
  newButton: { backgroundColor: '#1a1a2e', borderRadius: 20, paddingHorizontal: 16, paddingVertical: 8 },
  newButtonText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  searchRow: { flexDirection: 'row', paddingHorizontal: 16, gap: 8, marginBottom: 8 },
  searchInput: { flex: 1, borderWidth: 1, borderColor: '#ddd', borderRadius: 20, paddingHorizontal: 16, paddingVertical: 10, fontSize: 15, backgroundColor: '#f9f9f9' },
  nearbyBtn: { width: 44, height: 44, borderRadius: 22, backgroundColor: '#f9f9f9', borderWidth: 1, borderColor: '#ddd', justifyContent: 'center', alignItems: 'center' },
  nearbyBtnActive: { backgroundColor: '#1a1a2e', borderColor: '#1a1a2e' },
  nearbyBtnText: { fontSize: 20 },
  nearbyBtnTextActive: { fontSize: 20 },
  radiusRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, gap: 6, marginBottom: 8 },
  radiusLabel: { fontSize: 13, color: '#666', fontWeight: '600' },
  radiusChip: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, borderWidth: 1, borderColor: '#ddd' },
  radiusChipActive: { backgroundColor: '#1a1a2e', borderColor: '#1a1a2e' },
  radiusChipText: { fontSize: 12, color: '#666' },
  radiusChipTextActive: { color: '#fff', fontWeight: '700' },
  list: { padding: 16, gap: 12 },
  emptyContainer: { flex: 1 },
  empty: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingTop: 80 },
  emptyText: { fontSize: 18, fontWeight: '700', color: '#333' },
  emptySub: { fontSize: 14, color: '#999', marginTop: 8, textAlign: 'center' },
  card: { backgroundColor: '#f5f5ff', borderRadius: 16, padding: 16, gap: 6 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between' },
  cardHeaderRight: { flexDirection: 'row', gap: 6, alignItems: 'center' },
  category: { fontSize: 13, color: '#666', fontWeight: '600' },
  distance: { fontSize: 12, color: '#3498db', fontWeight: '700' },
  remote: { fontSize: 13 },
  jobTitle: { fontSize: 17, fontWeight: '800', color: '#1a1a2e' },
  description: { fontSize: 14, color: '#666', lineHeight: 20 },
  cardFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 },
  budget: { fontSize: 13, color: '#2ecc71', fontWeight: '700' },
  city: { fontSize: 13, color: '#999' },
})
