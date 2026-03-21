import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, ActivityIndicator, ScrollView,
  TouchableOpacity, Dimensions, TextInput, FlatList
} from 'react-native'
import { useAuth } from '../../lib/AuthContext'
import { useNotifications } from '../../hooks/useNotifications'
import { router } from 'expo-router'
import { useProfile } from '../../hooks/useProfile'
import { Ionicons } from '@expo/vector-icons'
import { useDrawer } from '../../lib/DrawerContext'
import { supabase } from '../../lib/supabase'
import { useSubscription } from '../../hooks/useSubscription'
import { useTranslation } from 'react-i18next'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const { width } = Dimensions.get('window')

const CATEGORIES = [
  { icon: '🧹', label: 'Limpieza', key: 'cleaning' },
  { icon: '🔧', label: 'Fontanería', key: 'plumbing' },
  { icon: '⚡', label: 'Electricidad', key: 'electrical' },
  { icon: '🎨', label: 'Pintura', key: 'painting' },
  { icon: '🌿', label: 'Jardinería', key: 'gardening' },
  { icon: '📦', label: 'Mudanzas', key: 'moving' },
  { icon: '🪚', label: 'Carpintería', key: 'carpentry' },
  { icon: '❄️', label: 'Climatización', key: 'hvac' },
]

const FLAG: Record<string, string> = {
  ES: '🇪🇸', FR: '🇫🇷', MX: '🇲🇽', CO: '🇨🇴',
  AR: '🇦🇷', BR: '🇧🇷', CL: '🇨🇱', BE: '🇧🇪',
  NL: '🇳🇱', DE: '🇩🇪', PT: '🇵🇹', IT: '🇮🇹', GB: '🇬🇧'
}

export default function HomeScreen() {
  const { t } = useTranslation()
  const insets = useSafeAreaInsets()
  useNotifications()
  const { profile, loading } = useProfile()
  const { openDrawer } = useDrawer()
  const { isTrialing, trialDaysLeft } = useSubscription()
  const [recentJobs, setRecentJobs] = useState<any[]>([])
  const [activeContracts, setActiveContracts] = useState<any[]>([])
  const [pendingBids, setPendingBids] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [monthEarnings, setMonthEarnings] = useState(0)
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null)

  useEffect(() => {
    if (typeof navigator !== 'undefined' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        pos => setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {}
      )
    }
  }, [])

  function getDistanceKm(lat1: number, lng1: number, lat2: number, lng2: number): number {
    const R = 6371
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLng = (lng2 - lng1) * Math.PI / 180
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLng/2) * Math.sin(dLng/2)
    return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * 10) / 10
  }

  const isPro = profile?.role === 'pro' || profile?.role === 'company'
  const firstName = profile?.full_name?.split(' ')[0] || 'Usuario'
  const hour = new Date().getHours()
  const greeting = hour < 12 ? '☀️ Buenos días' : hour < 20 ? '👋 Buenas tardes' : '🌙 Buenas noches'

  useEffect(() => {
    if (!profile?.id) return
    if (isPro) loadProData()
    else loadClientData()
  }, [profile?.id, isPro, selectedCategory])

  async function loadClientData() {
    const [jobsRes, contractsRes] = await Promise.all([
      supabase.from('jobs')
        .select('id, title, category, city, budget_min, budget_max, currency, created_at, status, client:client_id(id, full_name, avatar_url, country)')
        .eq('client_id', profile!.id)
        .order('created_at', { ascending: false })
        .limit(5),
      supabase.from('contracts')
        .select('id, job_id, status, amount, currency, jobs(id, title, category)')
        .eq('client_id', profile!.id)
        .eq('status', 'active')
        .limit(3),
    ])
    if (jobsRes.data) setRecentJobs(jobsRes.data)
    if (contractsRes.data) setActiveContracts(contractsRes.data)
  }

  async function loadProData() {
    const now = new Date()
    const firstOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString()
    let query = supabase.from('jobs')
      .select('id, title, category, city, budget_min, budget_max, currency, created_at, status')
      .eq('status', 'open')
      .order('created_at', { ascending: false })
      .limit(10)
    if (selectedCategory) query = query.eq('category', selectedCategory)
    const [jobsRes, bidsRes, earningsRes] = await Promise.all([
      query,
      supabase.from('bids')
        .select('id, job_id, amount, currency, status, jobs(title, city)')
        .eq('pro_id', profile!.id)
        .eq('status', 'pending')
        .limit(3),
      supabase.from('payments')
        .select('pro_amount')
        .eq('pro_id', profile!.id)
        .eq('status', 'released')
        .gte('created_at', firstOfMonth),
    ])
    if (jobsRes.data) setRecentJobs(jobsRes.data)
    if (bidsRes.data) setPendingBids(bidsRes.data)
    if (earningsRes.data) setMonthEarnings(earningsRes.data.reduce((s, p) => s + (p.pro_amount || 0), 0))
  }

  if (loading) return (
    <View style={s.center}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  )

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      {/* Navbar */}
      <View style={s.navbar}>
        <View>
          <Text style={s.greeting}>{greeting}</Text>
          <Text style={s.navName}>{firstName} {FLAG[profile?.country ?? 'ES']}</Text>
        </View>
        <View style={s.navRight}>
          {isPro && monthEarnings > 0 && (
            <View style={s.earningsBadge}>
              <Text style={s.earningsBadgeText}>{monthEarnings.toFixed(0)}€ mes</Text>
            </View>
          )}
          <TouchableOpacity style={s.avatarBtn} onPress={openDrawer}>
            <Text style={s.avatarText}>{firstName[0]?.toUpperCase()}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={s.content}>

        {/* Trial Banner */}
        {isTrialing && (
          <TouchableOpacity style={s.trialBanner} onPress={() => router.push('/(app)/subscription')}>
            <Ionicons name="star" size={14} color="#92400E" />
            <Text style={s.trialText}>{trialDaysLeft === 0 ? 'Tu trial expira hoy' : `${trialDaysLeft} días Pro gratis`}</Text>
            <Text style={s.trialCta}>Activar →</Text>
          </TouchableOpacity>
        )}

        {/* KYC Banner */}
        {!profile?.is_verified && (
          <TouchableOpacity style={s.kycBanner} onPress={() => router.push('/(app)/kyc')}>
            <Ionicons name="shield-checkmark-outline" size={16} color="#2563EB" />
            <Text style={s.kycText}>Verifica tu identidad para más funciones</Text>
            <Ionicons name="chevron-forward" size={16} color="#2563EB" />
          </TouchableOpacity>
        )}

        {/* ═══ VISTA CLIENTE ═══ */}
        {!isPro && (
          <>
            {/* Search */}
            <View style={s.searchBox}>
              <Ionicons name="search-outline" size={18} color="#888" />
              <TextInput
                style={s.searchInput}
                placeholder="¿Qué servicio necesitas?"
                placeholderTextColor="#aaa"
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={() => router.push(`/(app)/search?q=${searchQuery}`)}
              />
              {searchQuery.length > 0 && (
                <TouchableOpacity onPress={() => setSearchQuery('')}>
                  <Ionicons name="close-circle" size={18} color="#aaa" />
                </TouchableOpacity>
              )}
            </View>

            {/* Categorías */}
            <Text style={s.sectionTitle}>¿Qué necesitas?</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.catScroll}>
              {CATEGORIES.map((cat, i) => (
                <TouchableOpacity
                  key={i}
                  style={s.catChip}
                  onPress={() => router.push(`/(app)/search?category=${cat.key}`)}
                >
                  <Text style={s.catChipIcon}>{cat.icon}</Text>
                  <Text style={s.catChipLabel}>{cat.label}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* CTA Publicar */}
            <TouchableOpacity style={s.ctaCard} onPress={() => router.push('/(app)/jobs/new')}>
              <View style={s.ctaLeft}>
                <Text style={s.ctaTitle}>Publica un trabajo</Text>
                <Text style={s.ctaSub}>Recibe ofertas de pros verificados en minutos</Text>
              </View>
              <View style={s.ctaIcon}>
                <Ionicons name="add-circle" size={32} color="#fff" />
              </View>
            </TouchableOpacity>

            {/* Contratos activos */}
            {activeContracts.length > 0 && (
              <>
                <Text style={s.sectionTitle}>Trabajos en curso</Text>
                {activeContracts.map((c: any) => (
                  <TouchableOpacity key={c.id} style={s.contractCard} onPress={() => router.push(`/(app)/jobs/${c.job_id}/contract`)}>
                    <View style={s.contractDot} />
                    <View style={{ flex: 1 }}>
                      <Text style={s.contractTitle}>{c.jobs?.title ?? 'Trabajo'}</Text>
                      <Text style={s.contractSub}>En curso · {c.amount} {c.currency}</Text>
                    </View>
                    <Ionicons name="chevron-forward" size={18} color="#2563EB" />
                  </TouchableOpacity>
                ))}
              </>
            )}

            {/* Mis jobs */}
            <View style={s.sectionRow}>
              <Text style={s.sectionTitle}>Mis trabajos</Text>
              <TouchableOpacity onPress={() => router.push('/(app)/jobs?filter=mine')}>
                <Text style={s.sectionLink}>Ver todos →</Text>
              </TouchableOpacity>
            </View>
            {recentJobs.length === 0 ? (
              <View style={s.emptyCard}>
                <Text style={s.emptyEmoji}>📋</Text>
                <Text style={s.emptyText}>Aún no tienes trabajos publicados</Text>
                <TouchableOpacity style={s.emptyBtn} onPress={() => router.push('/(app)/jobs/new')}>
                  <Text style={s.emptyBtnText}>Publicar ahora</Text>
                </TouchableOpacity>
              </View>
            ) : recentJobs.map((job: any) => (
              <TouchableOpacity key={job.id} style={s.jobCard} onPress={() => router.push(`/(app)/jobs/${job.id}`)}>
                <View style={s.jobLeft}>
                  <View style={[s.jobStatus, { backgroundColor: job.status === 'open' ? '#D1FAE5' : '#F3F4F6' }]}>
                    <Text style={[s.jobStatusText, { color: job.status === 'open' ? '#065F46' : '#888' }]}>
                      {job.status === 'open' ? 'Abierto' : job.status}
                    </Text>
                  </View>
                  <Text style={s.jobTitle} numberOfLines={1}>{job.title}</Text>
                  <Text style={s.jobMeta}>{job.city ?? '—'}</Text>
                </View>
                <Text style={s.jobBudget}>{job.budget_min}–{job.budget_max} {job.currency}</Text>
              </TouchableOpacity>
            ))}
          </>
        )}

        {/* ═══ VISTA PRO ═══ */}
        {isPro && (
          <>
            {/* Stats rápidas */}
            <View style={s.proStatsRow}>
              <TouchableOpacity style={s.proStatCard} onPress={() => router.push('/(app)/dashboard-pro')}>
                <Text style={s.proStatValue}>{monthEarnings.toFixed(0)}€</Text>
                <Text style={s.proStatLabel}>Ganado este mes</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[s.proStatCard, { backgroundColor: '#F0FDF4' }]} onPress={() => router.push('/(app)/jobs')}>
                <Text style={[s.proStatValue, { color: '#16A34A' }]}>{recentJobs.length}</Text>
                <Text style={s.proStatLabel}>Jobs disponibles</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[s.proStatCard, { backgroundColor: '#FEF3C7' }]} onPress={() => router.push('/(app)/jobs?filter=bids')}>
                <Text style={[s.proStatValue, { color: '#D97706' }]}>{pendingBids.length}</Text>
                <Text style={s.proStatLabel}>Ofertas enviadas</Text>
              </TouchableOpacity>
            </View>

            {/* Filtros categoría */}
            <Text style={s.sectionTitle}>Trabajos cerca de ti</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.catScroll}>
              <TouchableOpacity
                style={[s.filterChip, !selectedCategory && s.filterChipActive]}
                onPress={() => setSelectedCategory(null)}
              >
                <Text style={[s.filterChipText, !selectedCategory && s.filterChipTextActive]}>Todos</Text>
              </TouchableOpacity>
              {CATEGORIES.map((cat, i) => (
                <TouchableOpacity
                  key={i}
                  style={[s.filterChip, selectedCategory === cat.key && s.filterChipActive]}
                  onPress={() => setSelectedCategory(selectedCategory === cat.key ? null : cat.key)}
                >
                  <Text style={s.filterChipIcon}>{cat.icon}</Text>
                  <Text style={[s.filterChipText, selectedCategory === cat.key && s.filterChipTextActive]}>{cat.label}</Text>
                </TouchableOpacity>
              ))}
            </ScrollView>

            {/* Feed de jobs */}
            {recentJobs.length === 0 ? (
              <View style={s.emptyCard}>
                <Text style={s.emptyEmoji}>🔍</Text>
                <Text style={s.emptyText}>No hay trabajos disponibles ahora</Text>
              </View>
            ) : recentJobs.map((job: any) => (
              <TouchableOpacity key={job.id} style={s.proJobCard} onPress={() => router.push(`/(app)/jobs/${job.id}`)}>
                <View style={s.proJobTop}>
                  <View style={s.proJobCatBadge}>
                    <Text style={s.proJobCatText}>{CATEGORIES.find(c => c.key === job.category)?.icon ?? '🔧'} {job.category}</Text>
                  </View>
                  <Text style={s.proJobBudget}>{job.budget_min}–{job.budget_max} {job.currency}</Text>
                </View>
                <Text style={s.proJobTitle}>{job.title}</Text>
                <View style={s.clientRow}>
                  <View style={s.clientAvatar}>
                    <Text style={s.clientAvatarText}>{(job.client?.full_name ?? '?')[0].toUpperCase()}</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={s.clientName}>{job.client?.full_name ?? 'Cliente'}</Text>
                  </View>
                  <View style={s.clientRating}>
                    <Ionicons name="star" size={11} color="#F59E0B" />
                    <Text style={s.clientRatingText}>Nuevo</Text>
                  </View>
                </View>
                <View style={s.proJobBottom}>
                  <Ionicons name="location-outline" size={13} color="#888" />
                  <Text style={s.proJobCity}>{job.city ?? '—'}</Text>
                  {userLocation && job.latitude && job.longitude && (
                    <Text style={s.proJobDist}> · {getDistanceKm(userLocation.lat, userLocation.lng, job.latitude, job.longitude)} km</Text>
                  )}
                  <Text style={s.proJobTime}> · {(() => { const diff = Math.floor((Date.now() - new Date(job.created_at).getTime()) / 60000); return diff < 60 ? `${diff}m` : diff < 1440 ? `${Math.floor(diff/60)}h` : `${Math.floor(diff/1440)}d` })()}</Text>
                </View>
                <TouchableOpacity style={s.bidBtn} onPress={() => router.push(`/(app)/jobs/${job.id}/bid`)}>
                  <Text style={s.bidBtnText}>Enviar oferta →</Text>
                </TouchableOpacity>
              </TouchableOpacity>
            ))}

            {/* Ofertas pendientes */}
            {pendingBids.length > 0 && (
              <>
                <Text style={s.sectionTitle}>Mis ofertas pendientes</Text>
                {pendingBids.map((bid: any) => (
                  <TouchableOpacity key={bid.id} style={s.bidCard} onPress={() => router.push(`/(app)/jobs/${bid.job_id}`)}>
                    <View style={{ flex: 1 }}>
                      <Text style={s.bidTitle} numberOfLines={1}>{bid.jobs?.title ?? 'Trabajo'}</Text>
                      <Text style={s.bidSub}>{bid.jobs?.city ?? '—'} · Pendiente</Text>
                    </View>
                    <Text style={s.bidAmount}>{bid.amount} {bid.currency}</Text>
                  </TouchableOpacity>
                ))}
              </>
            )}
          </>
        )}

      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  content: { padding: 16, gap: 12, paddingBottom: 40 },

  // Navbar
  navbar: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.06)' },
  greeting: { fontSize: 12, color: '#888', fontWeight: '500' },
  navName: { fontSize: 18, fontWeight: '800', color: '#1a1a2e', letterSpacing: -0.3 },
  navRight: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  earningsBadge: { backgroundColor: '#D1FAE5', borderRadius: 10, paddingHorizontal: 10, paddingVertical: 4 },
  earningsBadgeText: { fontSize: 12, fontWeight: '700', color: '#065F46' },
  avatarBtn: { width: 38, height: 38, borderRadius: 19, backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center' },
  avatarText: { fontSize: 16, fontWeight: '800', color: '#fff' },

  // Banners
  trialBanner: { backgroundColor: '#FEF3C7', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, flexDirection: 'row', alignItems: 'center', gap: 8 },
  trialText: { flex: 1, fontSize: 13, fontWeight: '600', color: '#92400E' },
  trialCta: { fontSize: 13, fontWeight: '700', color: '#D97706' },
  kycBanner: { backgroundColor: '#EFF6FF', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, flexDirection: 'row', alignItems: 'center', gap: 8 },
  kycText: { flex: 1, fontSize: 13, fontWeight: '600', color: '#2563EB' },

  // Search
  searchBox: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#fff', borderRadius: 16, paddingHorizontal: 16, paddingVertical: 4, borderWidth: 1, borderColor: 'rgba(0,0,0,0.08)', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.04, shadowRadius: 8, elevation: 2 },
  searchInput: { flex: 1, paddingVertical: 14, fontSize: 15, color: '#1a1a2e' },

  // Categories
  catScroll: { marginHorizontal: -16, paddingHorizontal: 16 },
  catChip: { alignItems: 'center', backgroundColor: '#fff', borderRadius: 16, paddingHorizontal: 14, paddingVertical: 10, marginRight: 10, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)', gap: 4 },
  catChipIcon: { fontSize: 22 },
  catChipLabel: { fontSize: 11, fontWeight: '600', color: '#555' },

  // CTA Card cliente
  ctaCard: { backgroundColor: '#2563EB', borderRadius: 20, padding: 20, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  ctaLeft: { flex: 1 },
  ctaTitle: { fontSize: 18, fontWeight: '800', color: '#fff', marginBottom: 4 },
  ctaSub: { fontSize: 13, color: 'rgba(255,255,255,0.75)' },
  ctaIcon: { width: 52, height: 52, borderRadius: 16, backgroundColor: 'rgba(255,255,255,0.15)', alignItems: 'center', justifyContent: 'center' },

  // Section
  sectionTitle: { fontSize: 17, fontWeight: '800', color: '#1a1a2e', letterSpacing: -0.3 },
  sectionRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  sectionLink: { fontSize: 13, fontWeight: '600', color: '#2563EB' },

  // Contract cards
  contractCard: { backgroundColor: '#fff', borderRadius: 14, padding: 14, flexDirection: 'row', alignItems: 'center', gap: 12, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)' },
  contractDot: { width: 10, height: 10, borderRadius: 5, backgroundColor: '#10B981' },
  contractTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  contractSub: { fontSize: 12, color: '#888', marginTop: 2 },

  // Job cards cliente
  jobCard: { backgroundColor: '#fff', borderRadius: 14, padding: 14, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)' },
  jobLeft: { flex: 1, gap: 4 },
  jobStatus: { alignSelf: 'flex-start', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2 },
  jobStatusText: { fontSize: 11, fontWeight: '700' },
  jobTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  jobMeta: { fontSize: 12, color: '#888' },
  jobBudget: { fontSize: 14, fontWeight: '800', color: '#2563EB' },

  // Empty
  emptyCard: { backgroundColor: '#fff', borderRadius: 16, padding: 28, alignItems: 'center', gap: 8, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  emptyEmoji: { fontSize: 36 },
  emptyText: { fontSize: 14, color: '#888', textAlign: 'center' },
  emptyBtn: { backgroundColor: '#2563EB', borderRadius: 12, paddingHorizontal: 20, paddingVertical: 10, marginTop: 4 },
  emptyBtnText: { fontSize: 13, fontWeight: '700', color: '#fff' },

  // Pro stats
  proStatsRow: { flexDirection: 'row', gap: 10 },
  proStatCard: { flex: 1, backgroundColor: '#EFF6FF', borderRadius: 16, padding: 14, alignItems: 'center', gap: 4 },
  proStatValue: { fontSize: 22, fontWeight: '900', color: '#2563EB' },
  proStatLabel: { fontSize: 11, color: '#6B7280', textAlign: 'center' },

  // Pro filters
  filterChip: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#fff', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, marginRight: 8, borderWidth: 1, borderColor: 'rgba(0,0,0,0.08)' },
  filterChipActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  filterChipIcon: { fontSize: 14 },
  filterChipText: { fontSize: 13, fontWeight: '600', color: '#555' },
  filterChipTextActive: { color: '#fff' },

  // Pro job cards
  proJobCard: { backgroundColor: '#fff', borderRadius: 18, padding: 16, gap: 8, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.04, shadowRadius: 8, elevation: 2 },
  proJobTop: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  proJobCatBadge: { backgroundColor: '#F3F4F6', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4 },
  proJobCatText: { fontSize: 12, fontWeight: '600', color: '#555' },
  proJobBudget: { fontSize: 15, fontWeight: '800', color: '#2563EB' },
  proJobTitle: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  proJobBottom: { flexDirection: 'row', alignItems: 'center' },
  proJobCity: { fontSize: 12, color: '#888' },
  proJobTime: { fontSize: 12, color: '#aaa' },
  proJobDist: { fontSize: 12, color: '#2563EB', fontWeight: '600' },
  bidBtn: { backgroundColor: '#EFF6FF', borderRadius: 10, paddingVertical: 10, alignItems: 'center' },
  bidBtnText: { fontSize: 13, fontWeight: '700', color: '#2563EB' },

  // Bid cards
  clientRow: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 4 },
  clientAvatar: { width: 28, height: 28, borderRadius: 14, backgroundColor: '#EFF6FF', alignItems: 'center', justifyContent: 'center' },
  clientAvatarText: { fontSize: 12, fontWeight: '800', color: '#2563EB' },
  clientName: { fontSize: 12, fontWeight: '600', color: '#555' },
  clientRating: { flexDirection: 'row', alignItems: 'center', gap: 3, backgroundColor: '#FEF3C7', borderRadius: 8, paddingHorizontal: 6, paddingVertical: 2 },
  clientRatingText: { fontSize: 11, fontWeight: '600', color: '#92400E' },
  bidCard: { backgroundColor: '#fff', borderRadius: 14, padding: 14, flexDirection: 'row', alignItems: 'center', gap: 12, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)', borderLeftWidth: 3, borderLeftColor: '#F59E0B' },
  bidTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  bidSub: { fontSize: 12, color: '#888', marginTop: 2 },
  bidAmount: { fontSize: 15, fontWeight: '800', color: '#2563EB' },
})