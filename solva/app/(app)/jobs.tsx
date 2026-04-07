import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, RefreshControl, TextInput
} from 'react-native'
import { useTranslation } from 'react-i18next'
import { router, useLocalSearchParams } from 'expo-router'
import { supabase, Job } from '../../lib/supabase'
import { useProfile } from '../../hooks/useProfile'
import { useAuth } from '../../lib/AuthContext'
import { useLocation, searchJobsNearby } from '../../hooks/useLocation'

const CATEGORY_LABELS: Record<string, string> = {
  cleaning: '🧹 Limpieza', plumbing: '🔧 Fontaneria', electrical: '⚡ Electricidad',
  painting: '🎨 Pintura', moving: '📦 Mudanza', gardening: '🌿 Jardineria',
  carpentry: '🪚 Carpinteria', tech: '💻 Tecnologia', design: '✏️ Diseno', other: '🔹 Otro'
}

const RADIUS_OPTIONS = [5, 10, 25, 50, 100]

export default function JobsScreen() {
  const { profile } = useProfile()
  const { session } = useAuth()
  const { t } = useTranslation()
  const { filter } = useLocalSearchParams<{ filter?: string }>()
  const [activeTab, setActiveTab] = useState<'all' | 'mine' | 'history'>(filter === 'mine' ? 'mine' : 'all')
  const [myJobs, setMyJobs] = useState<any[]>([])
  const [historyJobs, setHistoryJobs] = useState<any[]>([])
  const { coords, requestLocation, loading: locLoading } = useLocation()
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [searchMode, setSearchMode] = useState<'all' | 'nearby'>('all')
  const [radius, setRadius] = useState(25)
  const [searchText, setSearchText] = useState('')

  async function fetchHistory() {
    if (!session?.user?.id) return
    const { data } = await supabase
      .from('contracts')
      .select('id, job_id, status, amount, currency, completed_at, jobs(id, title, category, status)')
      .eq('client_id', session.user.id)
      .in('status', ['completed', 'cancelled'])
      .order('completed_at', { ascending: false })
      .limit(20)
    setHistoryJobs(data ?? [])
  }

  async function fetchMyJobs() {
    if (!session?.user?.id) return
    const { data } = await supabase
      .from('jobs')
      .select('*, contracts(id, status, amount)')
      .eq('client_id', session.user.id)
      .in('status', ['open', 'in_progress', 'completed'])
      .order('created_at', { ascending: false })
    setMyJobs(data ?? [])
  }

  async function fetchJobs() {
    setLoading(true)
    if (searchMode === 'nearby' && !coords) {
      setLoading(false)
      setRefreshing(false)
      return
    }
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
  useEffect(() => { fetchMyJobs() }, [session?.user?.id, activeTab])

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
              <Text style={s.newButtonText}>{t('jobs.postJob')}</Text>
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
          placeholder={t("jobs.searchPlaceholder")}
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

      {/* Tabs */}
      <View style={s.tabs}>
        <TouchableOpacity style={[s.tab, activeTab === 'all' && s.tabActive]} onPress={() => setActiveTab('all')}>
          <Text style={[s.tabText, activeTab === 'all' && s.tabTextActive]}>{t('jobs.available')}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.tab, activeTab === 'mine' && s.tabActive]} onPress={() => setActiveTab('mine')}>
          <Text style={[s.tabText, activeTab === 'mine' && s.tabTextActive]}>{t('jobs.myJobs')}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[s.tab, activeTab === 'history' && s.tabActive]} onPress={() => setActiveTab('history')}>
          <Text style={[s.tabText, activeTab === 'history' && s.tabTextActive]}>{t('jobs.history')}</Text>
        </TouchableOpacity>
      </View>

      {/* Mis trabajos */}
      {activeTab === 'mine' && (
        <View style={s.myJobsList}>
          {myJobs.length === 0
            ? <View style={s.emptyState}>
                <Text style={s.emptyStateIcon}>📋</Text>
                <Text style={s.emptyStateTitle}>{t('jobs.noMyJobs')}</Text>
                <Text style={s.emptyStateSub}>Publica tu primer trabajo y recibe ofertas de profesionales</Text>
                <TouchableOpacity style={s.emptyStateBtn} onPress={() => router.push('/(app)/jobs/new')}>
                  <Text style={s.emptyStateBtnText}>{t('jobs.postJob')}</Text>
                </TouchableOpacity>
              </View>
            : myJobs.map((job: any) => {
                const contract = job.contracts?.[0]
                const statusColor = job.status === 'open' ? '#10B981' : job.status === 'in_progress' ? '#2563EB' : '#888'
                const statusLabel = job.status === 'open' ? 'Abierto' : job.status === 'in_progress' ? 'En progreso' : job.status
                return (
                  <TouchableOpacity
                    key={job.id}
                    style={s.myJobCard}
                    onPress={() => contract
                      ? router.push(`/(app)/jobs/${job.id}/contract`)
                      : router.push(`/(app)/jobs/${job.id}`)
                    }
                    activeOpacity={0.85}
                  >
                    <View style={s.myJobTop}>
                      <Text style={s.myJobTitle}>{job.title}</Text>
                      <View style={[s.myJobBadge, { backgroundColor: statusColor + '20' }]}>
                        <Text style={[s.myJobBadgeText, { color: statusColor }]}>{statusLabel}</Text>
                      </View>
                    </View>
                    <Text style={s.myJobSub}>
                      {contract ? `Ver contrato →` : `${job.budget_min ?? '?'}–${job.budget_max ?? '?'} ${job.currency}`}
                    </Text>
                  </TouchableOpacity>
                )
              })
          }
        </View>
      )}

      {/* Lista */}
      {activeTab === 'all' && loading && <View style={s.center}><ActivityIndicator size="large" color="#1a1a2e" /></View>}
      {activeTab === 'all' && !loading && <FlatList
            data={jobs}
            keyExtractor={item => item.id}
            refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
            contentContainerStyle={jobs.length === 0 ? s.emptyContainer : s.list}
            ListEmptyComponent={
              <View style={s.empty}>
                <Text style={s.emptyText}>
                  {searchMode === 'nearby' ? t('jobs.noJobs') : t('jobs.noJobs')}
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
          />}
      {activeTab === 'history' && (
        <View style={s.myJobsList}>
          {historyJobs.length === 0
            ? <View style={s.emptyState}>
                <Text style={s.emptyStateIcon}>🏆</Text>
                <Text style={s.emptyStateTitle}>Sin historial</Text>
                <Text style={s.emptyStateSub}>Aquí aparecerán los trabajos completados</Text>
              </View>
            : historyJobs.map((contract: any) => {
                const isCompleted = contract.status === 'completed'
                const statusColor = isCompleted ? '#059669' : '#9CA3AF'
                const statusLabel = isCompleted ? 'Completado' : 'Cancelado'
                return (
                  <TouchableOpacity
                    key={contract.id}
                    style={s.myJobCard}
                    onPress={() => router.push(`/(app)/jobs/${contract.job_id}/contract`)}
                    activeOpacity={0.85}
                  >
                    <View style={s.myJobTop}>
                      <Text style={s.myJobTitle}>{contract.jobs?.title ?? 'Trabajo'}</Text>
                      <View style={[s.myJobBadge, { backgroundColor: statusColor + '20' }]}>
                        <Text style={[s.myJobBadgeText, { color: statusColor }]}>{statusLabel}</Text>
                      </View>
                    </View>
                    <Text style={s.myJobSub}>
                      {contract.amount} {contract.currency}
                      {contract.completed_at ? ` · ${new Date(contract.completed_at).toLocaleDateString('es-ES')}` : ''}
                    </Text>
                  </TouchableOpacity>
                )
              })
          }
        </View>
      )}
      {activeTab === 'mine' && null}
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
  tabs: { flexDirection: 'row', paddingHorizontal: 16, gap: 8, marginBottom: 8 },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', borderWidth: 1, borderColor: '#E5E7EB', flexDirection: 'row', justifyContent: 'center', gap: 6 },
  tabActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  tabText: { fontSize: 14, fontWeight: '600', color: '#666' },
  tabTextActive: { color: '#fff' },
  tabBadge: { backgroundColor: '#EF4444', borderRadius: 10, paddingHorizontal: 6, paddingVertical: 2 },
  tabBadgeText: { fontSize: 11, fontWeight: '700', color: '#fff' },
  myJobsList: { paddingHorizontal: 16, gap: 10, paddingBottom: 20 },
  myJobCard: { backgroundColor: '#fff', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#E5E7EB', borderLeftWidth: 4, borderLeftColor: '#2563EB' },
  myJobTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 },
  myJobTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', flex: 1 },
  myJobBadge: { borderRadius: 8, paddingHorizontal: 8, paddingVertical: 3 },
  myJobBadgeText: { fontSize: 12, fontWeight: '700' },
  myJobSub: { fontSize: 13, color: '#666' },
  emptyState: {
    alignItems: 'center', justifyContent: 'center',
    paddingVertical: 60, paddingHorizontal: 32, gap: 10,
  },
  emptyStateIcon: { fontSize: 48, marginBottom: 8 },
  emptyStateTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a2e', textAlign: 'center' },
  emptyStateSub: { fontSize: 14, color: '#888', textAlign: 'center', lineHeight: 20 },
  emptyStateBtn: {
    marginTop: 8, backgroundColor: '#2563EB', borderRadius: 14,
    paddingHorizontal: 24, paddingVertical: 12,
  },
  emptyStateBtnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
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
