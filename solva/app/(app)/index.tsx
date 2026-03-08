import {
  View, Text, StyleSheet, ActivityIndicator, ScrollView,
  TouchableOpacity, Dimensions
} from 'react-native'
import { useAuth } from '../../lib/AuthContext'
import { useNotifications } from '../../hooks/useNotifications'
import { router } from 'expo-router'
import { useProfile } from '../../hooks/useProfile'
import { Ionicons } from '@expo/vector-icons'

const { width } = Dimensions.get('window')

const FLAG: Record<string, string> = {
  ES: '🇪🇸', FR: '🇫🇷', MX: '🇲🇽', CO: '🇨🇴',
  AR: '🇦🇷', BR: '🇧🇷', CL: '🇨🇱', BE: '🇧🇪',
  NL: '🇳🇱', DE: '🇩🇪', PT: '🇵🇹', IT: '🇮🇹', GB: '🇬🇧'
}

const MOCK_JOBS = [
  { id: '1', category: 'Limpieza', title: 'Limpieza hogar 3 habitaciones', distance: '0.8 km', duration: '3h', price: 85, time: 'Hace 5 min' },
  { id: '2', category: 'Fontanería', title: 'Reparar fuga en cocina urgente', distance: '1.2 km', duration: '2h', price: 120, time: 'Hace 12 min' },
  { id: '3', category: 'Electricidad', title: 'Instalación puntos de luz', distance: '2.1 km', duration: '4h', price: 200, time: 'Hace 28 min' },
]

export default function HomeScreen() {
  const { signOut } = useAuth()
  useNotifications()
  const { profile, loading } = useProfile()

  if (loading) return (
    <View style={styles.center}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  )

  const firstName = profile?.full_name?.split(' ')[0] || 'Usuario'
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Buenos días' : hour < 20 ? 'Buenas tardes' : 'Buenas noches'

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.container}
      showsVerticalScrollIndicator={false}
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>{greeting}</Text>
          <Text style={styles.name}>Hola, {firstName} 👋</Text>
        </View>
        <TouchableOpacity
          style={styles.notifBtn}
          onPress={() => router.push('/(app)/profile')}
        >
          <Ionicons name="notifications-outline" size={22} color="#1a1a2e" />
        </TouchableOpacity>
      </View>

      {/* KYC Banner */}
      {!profile?.is_verified && (
        <TouchableOpacity style={styles.kycBanner} onPress={() => router.push('/(app)/kyc')}>
          <Ionicons name="shield-checkmark-outline" size={16} color="#2563EB" />
          <Text style={styles.kycText}>Verifica tu identidad para mayor confianza</Text>
          <Ionicons name="chevron-forward" size={16} color="#2563EB" />
        </TouchableOpacity>
      )}

      {/* Quick Actions */}
      <View style={styles.actionsRow}>
        <TouchableOpacity
          style={[styles.actionCard, styles.actionCardPrimary]}
          onPress={() => router.push('/(app)/jobs/new')}
          activeOpacity={0.85}
        >
          <View style={styles.actionIconPrimary}>
            <Ionicons name="add-circle-outline" size={22} color="#fff" />
          </View>
          <Text style={styles.actionTitlePrimary}>Publicar Job</Text>
          <Text style={styles.actionSubPrimary}>Encuentra profesionales</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionCard, styles.actionCardSecondary]}
          onPress={() => router.push('/(app)/search')}
          activeOpacity={0.85}
        >
          <View style={styles.actionIconSecondary}>
            <Ionicons name="search-outline" size={22} color="#1a1a2e" />
          </View>
          <Text style={styles.actionTitleSecondary}>Buscar Pros</Text>
          <Text style={styles.actionSubSecondary}>Explora servicios</Text>
        </TouchableOpacity>
      </View>

      {/* Jobs Cercanos */}
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Jobs Disponibles</Text>
          <TouchableOpacity onPress={() => router.push('/(app)/jobs')}>
            <Text style={styles.sectionLink}>Ver todos</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.jobsList}>
          {MOCK_JOBS.map((job) => (
            <TouchableOpacity
              key={job.id}
              style={styles.jobCard}
              onPress={() => router.push('/(app)/jobs')}
              activeOpacity={0.85}
            >
              <View style={styles.jobTop}>
                <View style={styles.jobLeft}>
                  <View style={styles.categoryBadge}>
                    <Text style={styles.categoryText}>{job.category.toUpperCase()}</Text>
                  </View>
                  <Text style={styles.jobTitle} numberOfLines={1}>{job.title}</Text>
                  <View style={styles.jobMeta}>
                    <View style={styles.metaItem}>
                      <Ionicons name="location-outline" size={13} color="#888" />
                      <Text style={styles.metaText}>{job.distance}</Text>
                    </View>
                    <View style={styles.metaItem}>
                      <Ionicons name="time-outline" size={13} color="#888" />
                      <Text style={styles.metaText}>{job.duration}</Text>
                    </View>
                  </View>
                </View>
                <View style={styles.jobRight}>
                  <Text style={styles.jobPrice}>€{job.price}</Text>
                  <Text style={styles.jobTime}>{job.time}</Text>
                </View>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Stats del perfil */}
      {profile && (
        <View style={styles.statsCard}>
          <Text style={styles.statsTitle}>Tu perfil</Text>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{FLAG[profile.country ?? 'ES']} {profile.country}</Text>
              <Text style={styles.statLabel}>País</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{profile.currency ?? 'EUR'}</Text>
              <Text style={styles.statLabel}>Moneda</Text>
            </View>
            <View style={styles.statDivider} />
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{profile.is_verified ? '✅' : '⏳'}</Text>
              <Text style={styles.statLabel}>KYC</Text>
            </View>
          </View>
        </View>
      )}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' },
  container: { paddingHorizontal: 24, paddingTop: 64, paddingBottom: 40 },

  // Header
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 },
  greeting: { fontSize: 13, fontWeight: '600', color: '#888', letterSpacing: 0.3 },
  name: { fontSize: 24, fontWeight: '700', color: '#1a1a2e', marginTop: 2 },
  notifBtn: {
    width: 42, height: 42, borderRadius: 14,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06, shadowRadius: 8, elevation: 3,
  },

  // KYC Banner
  kycBanner: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    backgroundColor: '#EEF4FF', borderRadius: 14, padding: 14,
    marginBottom: 20, borderWidth: 1, borderColor: '#DBEAFE',
  },
  kycText: { flex: 1, fontSize: 13, fontWeight: '600', color: '#2563EB' },

  // Quick Actions
  actionsRow: { flexDirection: 'row', gap: 12, marginBottom: 28 },
  actionCard: {
    flex: 1, borderRadius: 20, padding: 20,
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08, shadowRadius: 12, elevation: 4,
  },
  actionCardPrimary: { backgroundColor: '#2563EB' },
  actionCardSecondary: {
    backgroundColor: '#fff',
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)',
  },
  actionIconPrimary: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center', justifyContent: 'center', marginBottom: 16,
  },
  actionIconSecondary: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#F6F7FB',
    alignItems: 'center', justifyContent: 'center', marginBottom: 16,
  },
  actionTitlePrimary: { fontSize: 14, fontWeight: '700', color: '#fff' },
  actionSubPrimary: { fontSize: 12, color: 'rgba(255,255,255,0.7)', marginTop: 2 },
  actionTitleSecondary: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  actionSubSecondary: { fontSize: 12, color: '#888', marginTop: 2 },

  // Section
  section: { marginBottom: 24 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  sectionLink: { fontSize: 13, fontWeight: '600', color: '#2563EB' },

  // Job Cards
  jobsList: { gap: 10 },
  jobCard: {
    backgroundColor: '#fff', borderRadius: 18, padding: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  jobTop: { flexDirection: 'row', alignItems: 'flex-start', gap: 12 },
  jobLeft: { flex: 1, minWidth: 0 },
  jobRight: { alignItems: 'flex-end' },
  categoryBadge: {
    backgroundColor: '#EEF4FF', borderRadius: 6,
    paddingHorizontal: 8, paddingVertical: 3,
    alignSelf: 'flex-start', marginBottom: 6,
  },
  categoryText: { fontSize: 10, fontWeight: '700', color: '#2563EB', letterSpacing: 0.5 },
  jobTitle: { fontSize: 14, fontWeight: '600', color: '#1a1a2e', marginBottom: 8 },
  jobMeta: { flexDirection: 'row', gap: 12 },
  metaItem: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  metaText: { fontSize: 12, color: '#888' },
  jobPrice: { fontSize: 18, fontWeight: '800', color: '#1a1a2e' },
  jobTime: { fontSize: 11, color: '#aaa', marginTop: 2 },

  // Stats Card
  statsCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  statsTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 16 },
  statsRow: { flexDirection: 'row', alignItems: 'center' },
  statItem: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  statLabel: { fontSize: 11, color: '#888', marginTop: 4 },
  statDivider: { width: 1, height: 36, backgroundColor: '#F0F0F0' },
})