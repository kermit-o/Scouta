import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, RefreshControl, TextInput
} from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../../lib/supabase'
import { useProfile } from '../../../hooks/useProfile'
import { useAuth } from '../../../lib/AuthContext'
import { useLocation, searchJobsNearby } from '../../../hooks/useLocation'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORY_LABELS: Record<string, string> = {
  cleaning: '🧹 Limpieza', plumbing: '🔧 Fontanería', electrical: '⚡ Electricidad',
  painting: '🎨 Pintura', moving: '📦 Mudanza', gardening: '🌿 Jardinería',
  carpentry: '🪚 Carpintería', tech: '💻 Tecnología', design: '✏️ Diseño', other: '🔹 Otro'
}

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  open:        { label: 'Abierto',      color: '#2563EB', bg: '#EEF4FF' },
  in_progress: { label: 'En progreso',  color: '#D97706', bg: '#FEF3C7' },
  completed:   { label: 'Completado',   color: '#059669', bg: '#D1FAE5' },
  cancelled:   { label: 'Cancelado',    color: '#DC2626', bg: '#FEE2E2' },
}

const RADIUS_OPTIONS = [5, 10, 25, 50]

export default function JobsScreen() {
  const { profile } = useProfile()
  const { session } = useAuth()
  const insets = useSafeAreaInsets()
  const { coords, requestLocation, loading: locLoading } = useLocation()

  const [activeTab, setActiveTab] = useState<'available' | 'mine'>('available')
  const [jobs, setJobs] = useState<any[]>([])
  const [myJobs, setMyJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchText, setSearchText] = useState('')
  const [nearbyMode, setNearbyMode] = useState(false)
  const [radius, setRadius] = useState(25)

  async function fetchAvailable() {
    if (nearbyMode && coords) {
      const { data } = await searchJobsNearby(coords.latitude, coords.longitude, radius)
      setJobs(data ?? [])
    } else {
      let query = supabase
        .from('jobs').select('*').eq('status', 'open')
        .eq('country', profile?.country ?? 'ES')
        .order('created_at', { ascending: false })
      if (searchText.trim()) query = query.ilike('title', `%${searchText.trim()}%`)
      const { data } = await query
      setJobs(data ?? [])
    }
  }

  async function fetchMine() {
    const col = profile?.role === 'pro' ? 'pro_id' : 'client_id'
    const { data } = await supabase
      .from('jobs').select('*, bids(count)')
      .eq(col, session!.user.id)
      .order('created_at', { ascending: false })
    setMyJobs(data ?? [])
  }

  async function fetchAll() {
    setLoading(true)
    await Promise.all([fetchAvailable(), fetchMine()])
    setLoading(false)
    setRefreshing(false)
  }

  useEffect(() => { fetchAll() }, [nearbyMode, coords, radius, profile])

  async function toggleNearby() {
    if (nearbyMode) { setNearbyMode(false); return }
    if (!coords) await requestLocation()
    setNearbyMode(true)
  }

  function onRefresh() { setRefreshing(true); fetchAll() }

  const renderAvailableJob = ({ item }: { item: any }) => (
    <TouchableOpacity
      style={styles.card}
      onPress={() => router.push(`/(app)/jobs/${item.id}`)}
      activeOpacity={0.85}
    >
      <View style={styles.cardTop}>
        <View style={styles.cardLeft}>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>
              {(CATEGORY_LABELS[item.category] ?? item.category).toUpperCase()}
            </Text>
          </View>
          <Text style={styles.jobTitle} numberOfLines={1}>{item.title}</Text>
          <Text style={styles.jobDesc} numberOfLines={2}>{item.description}</Text>
          <View style={styles.metaRow}>
            {item.city && (
              <View style={styles.metaItem}>
                <Ionicons name="location-outline" size={12} color="#888" />
                <Text style={styles.metaText}>{item.city}</Text>
              </View>
            )}
            {item.distance_km != null && (
              <View style={styles.metaItem}>
                <Ionicons name="navigate-outline" size={12} color="#2563EB" />
                <Text style={[styles.metaText, { color: '#2563EB' }]}>{item.distance_km}km</Text>
              </View>
            )}
            {item.is_remote && (
              <View style={styles.metaItem}>
                <Ionicons name="globe-outline" size={12} color="#888" />
                <Text style={styles.metaText}>Remoto</Text>
              </View>
            )}
          </View>
        </View>
        <View style={styles.cardRight}>
          <Text style={styles.jobPrice}>
            {item.budget_max
              ? `${item.currency} ${item.budget_max}`
              : item.budget_min
              ? `${item.currency} ${item.budget_min}+`
              : 'Negociar'}
          </Text>
          <Text style={styles.jobTime}>
            {new Date(item.created_at).toLocaleDateString('es', { day: 'numeric', month: 'short' })}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  )

  const renderMyJob = ({ item }: { item: any }) => {
    const status = STATUS_CONFIG[item.status] ?? STATUS_CONFIG.open
    const bidsCount = item.bids?.[0]?.count ?? 0
    return (
      <View style={styles.card}>
        <View style={styles.cardTop}>
          <View style={styles.cardLeft}>
            <View style={[styles.statusBadge, { backgroundColor: status.bg }]}>
              <Text style={[styles.statusText, { color: status.color }]}>
                {status.label}{item.status === 'open' && bidsCount > 0 ? ` · ${bidsCount} ofertas` : ''}
              </Text>
            </View>
            <Text style={styles.jobTitle} numberOfLines={1}>{item.title}</Text>
            <View style={styles.metaRow}>
              {item.city && (
                <View style={styles.metaItem}>
                  <Ionicons name="location-outline" size={12} color="#888" />
                  <Text style={styles.metaText}>{item.city}</Text>
                </View>
              )}
            </View>
          </View>
          <View style={styles.cardRight}>
            <Text style={styles.jobPrice}>
              {item.budget_max ? `${item.currency} ${item.budget_max}` : 'Negociar'}
            </Text>
          </View>
        </View>

        {/* Action buttons */}
        <View style={styles.cardActions}>
          {item.status === 'open' && bidsCount > 0 && profile?.role !== 'pro' && (
            <TouchableOpacity
              style={styles.actionBtn}
              onPress={() => router.push(`/(app)/jobs/${item.id}`)}
            >
              <Ionicons name="eye-outline" size={15} color="#2563EB" />
              <Text style={styles.actionBtnText}>Ver ofertas ({bidsCount})</Text>
            </TouchableOpacity>
          )}
          {item.status === 'in_progress' && (
            <TouchableOpacity
              style={styles.actionBtn}
              onPress={() => router.push(`/(app)/jobs/${item.id}`)}
            >
              <Ionicons name="document-text-outline" size={15} color="#2563EB" />
              <Text style={styles.actionBtnText}>Ver contrato</Text>
            </TouchableOpacity>
          )}
          {item.status === 'completed' && (
            <TouchableOpacity
              style={[styles.actionBtn, styles.actionBtnOutline]}
              onPress={() => router.push(`/(app)/jobs/${item.id}`)}
            >
              <Ionicons name="star-outline" size={15} color="#555" />
              <Text style={[styles.actionBtnText, { color: '#555' }]}>Dejar reseña</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={[styles.actionBtn, styles.actionBtnOutline]}
            onPress={() => router.push(`/(app)/jobs/${item.id}`)}
          >
            <Ionicons name="chevron-forward" size={15} color="#555" />
            <Text style={[styles.actionBtnText, { color: '#555' }]}>Ver detalle</Text>
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  const currentData = activeTab === 'available' ? jobs : myJobs

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Trabajos</Text>
          <Text style={styles.headerSub}>
            {profile?.role === 'pro' ? 'Encuentra oportunidades' : 'Gestiona tus publicaciones'}
          </Text>
        </View>
        <View style={styles.headerBtns}>
          <TouchableOpacity
            style={styles.iconBtn}
            onPress={() => router.push('/(app)/search')}
          >
            <Ionicons name="sparkles-outline" size={20} color="#2563EB" />
          </TouchableOpacity>
          {profile?.role !== 'pro' && (
            <TouchableOpacity
              style={styles.publishBtn}
              onPress={() => router.push('/(app)/jobs/new')}
            >
              <Ionicons name="add" size={18} color="#fff" />
              <Text style={styles.publishBtnText}>Publicar</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Tabs */}
      <View style={styles.tabsRow}>
        {(['available', 'mine'] as const).map(tab => (
          <TouchableOpacity
            key={tab}
            style={[styles.tab, activeTab === tab && styles.tabActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
              {tab === 'available' ? 'Disponibles' : 'Mis trabajos'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Search + Nearby (solo en tab disponibles) */}
      {activeTab === 'available' && (
        <View style={styles.searchSection}>
          <View style={styles.searchRow}>
            <View style={styles.searchInput}>
              <Ionicons name="search-outline" size={18} color="#888" />
              <TextInput
                style={styles.searchText}
                value={searchText}
                onChangeText={setSearchText}
                onSubmitEditing={fetchAll}
                placeholder="Buscar trabajos..."
                placeholderTextColor="#aaa"
                returnKeyType="search"
              />
            </View>
            <TouchableOpacity
              style={[styles.nearbyBtn, nearbyMode && styles.nearbyBtnActive]}
              onPress={toggleNearby}
              disabled={locLoading}
            >
              <Ionicons
                name="navigate"
                size={18}
                color={nearbyMode ? '#fff' : '#888'}
              />
            </TouchableOpacity>
          </View>

          {nearbyMode && (
            <View style={styles.radiusRow}>
              {RADIUS_OPTIONS.map(r => (
                <TouchableOpacity
                  key={r}
                  style={[styles.radiusChip, radius === r && styles.radiusChipActive]}
                  onPress={() => setRadius(r)}
                >
                  <Text style={[styles.radiusText, radius === r && styles.radiusTextActive]}>
                    {r}km
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          )}
        </View>
      )}

      {/* Lista */}
      {loading
        ? <View style={styles.center}><ActivityIndicator size="large" color="#2563EB" /></View>
        : (
          <FlatList
            data={currentData}
            keyExtractor={item => item.id}
            renderItem={activeTab === 'available' ? renderAvailableJob : renderMyJob}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#2563EB" />}
            contentContainerStyle={currentData.length === 0 ? styles.emptyContainer : styles.list}
            showsVerticalScrollIndicator={false}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Ionicons name="briefcase-outline" size={48} color="#ddd" />
                <Text style={styles.emptyTitle}>
                  {activeTab === 'available' ? 'No hay trabajos disponibles' : 'Sin trabajos aún'}
                </Text>
                <Text style={styles.emptySub}>
                  {activeTab === 'available'
                    ? nearbyMode ? 'Prueba ampliar el radio' : 'Sé el primero en publicar'
                    : profile?.role !== 'pro' ? 'Publica tu primer trabajo' : 'Espera nuevas oportunidades'
                  }
                </Text>
                {activeTab === 'mine' && profile?.role !== 'pro' && (
                  <TouchableOpacity
                    style={styles.emptyBtn}
                    onPress={() => router.push('/(app)/jobs/new')}
                  >
                    <Text style={styles.emptyBtnText}>Publicar trabajo</Text>
                  </TouchableOpacity>
                )}
              </View>
            }
          />
        )
      }
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },

  // Header
  header: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    paddingHorizontal: 24, paddingTop: 16, paddingBottom: 12,
  },
  headerTitle: { fontSize: 24, fontWeight: '800', color: '#1a1a2e' },
  headerSub: { fontSize: 13, color: '#888', marginTop: 2 },
  headerBtns: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  iconBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },
  publishBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#2563EB', borderRadius: 12,
    paddingHorizontal: 14, paddingVertical: 10,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25, shadowRadius: 8, elevation: 4,
  },
  publishBtnText: { color: '#fff', fontSize: 14, fontWeight: '700' },

  // Tabs
  tabsRow: { flexDirection: 'row', gap: 10, paddingHorizontal: 24, marginBottom: 16 },
  tab: {
    flex: 1, paddingVertical: 12, borderRadius: 14,
    backgroundColor: '#fff', alignItems: 'center',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  tabActive: {
    backgroundColor: '#2563EB', borderColor: '#2563EB',
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25, shadowRadius: 8, elevation: 4,
  },
  tabText: { fontSize: 14, fontWeight: '600', color: '#888' },
  tabTextActive: { color: '#fff' },

  // Search
  searchSection: { paddingHorizontal: 24, marginBottom: 12 },
  searchRow: { flexDirection: 'row', gap: 10 },
  searchInput: {
    flex: 1, flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: '#fff', borderRadius: 14, paddingHorizontal: 14,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  searchText: { flex: 1, paddingVertical: 12, fontSize: 15, color: '#1a1a2e' },
  nearbyBtn: {
    width: 48, height: 48, borderRadius: 14,
    backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB',
    alignItems: 'center', justifyContent: 'center',
  },
  nearbyBtnActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  radiusRow: { flexDirection: 'row', gap: 8, marginTop: 10 },
  radiusChip: {
    paddingHorizontal: 14, paddingVertical: 6, borderRadius: 10,
    backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB',
  },
  radiusChipActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  radiusText: { fontSize: 13, fontWeight: '600', color: '#888' },
  radiusTextActive: { color: '#fff' },

  // List
  list: { paddingHorizontal: 24, paddingBottom: 30, gap: 12 },
  emptyContainer: { flex: 1, paddingHorizontal: 24 },

  // Card
  card: {
    backgroundColor: '#fff', borderRadius: 20, padding: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  cardTop: { flexDirection: 'row', gap: 12 },
  cardLeft: { flex: 1, minWidth: 0 },
  cardRight: { alignItems: 'flex-end', justifyContent: 'flex-start' },
  categoryBadge: {
    alignSelf: 'flex-start', backgroundColor: '#EEF4FF',
    borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3, marginBottom: 7,
  },
  categoryText: { fontSize: 10, fontWeight: '700', color: '#2563EB', letterSpacing: 0.5 },
  statusBadge: {
    alignSelf: 'flex-start', borderRadius: 6,
    paddingHorizontal: 8, paddingVertical: 3, marginBottom: 7,
  },
  statusText: { fontSize: 10, fontWeight: '700', letterSpacing: 0.3 },
  jobTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 6 },
  jobDesc: { fontSize: 13, color: '#666', lineHeight: 18, marginBottom: 8 },
  jobPrice: { fontSize: 16, fontWeight: '800', color: '#1a1a2e' },
  jobTime: { fontSize: 11, color: '#aaa', marginTop: 3 },
  metaRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  metaText: { fontSize: 12, color: '#888' },

  // Card actions
  cardActions: { flexDirection: 'row', gap: 8, marginTop: 14, flexWrap: 'wrap' },
  actionBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#EEF4FF', borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 8,
  },
  actionBtnOutline: { backgroundColor: '#F6F7FB' },
  actionBtnText: { fontSize: 13, fontWeight: '600', color: '#2563EB' },

  // Empty
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 10 },
  emptyTitle: { fontSize: 17, fontWeight: '700', color: '#333' },
  emptySub: { fontSize: 14, color: '#aaa', textAlign: 'center' },
  emptyBtn: {
    marginTop: 8, backgroundColor: '#2563EB', borderRadius: 14,
    paddingHorizontal: 24, paddingVertical: 12,
  },
  emptyBtnText: { color: '#fff', fontSize: 14, fontWeight: '700' },
})