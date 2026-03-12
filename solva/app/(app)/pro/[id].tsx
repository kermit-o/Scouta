import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, Image,
  TouchableOpacity, ActivityIndicator
} from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { supabase, Review } from '../../../lib/supabase'
import { useAuth } from '../../../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const FLAG: Record<string, string> = { ES: '🇪🇸', FR: '🇫🇷', MX: '🇲🇽', CO: '🇨🇴', AR: '🇦🇷', BR: '🇧🇷', CL: '🇨🇱', BE: '🇧🇪', NL: '🇳🇱', DE: '🇩🇪', PT: '🇵🇹', IT: '🇮🇹', GB: '🇬🇧' }

function Stars({ score, size = 16 }: { score: number; size?: number }) {
  return (
    <View style={s.starsRow}>
      {[1,2,3,4,5].map(i => (
        <Ionicons key={i} name={i <= Math.round(score) ? 'star' : 'star-outline'} size={size} color={i <= Math.round(score) ? '#F59E0B' : '#D1D5DB'} />
      ))}
      <Text style={s.scoreText}>{score > 0 ? score.toFixed(1) : 'Sin reseñas'}</Text>
    </View>
  )
}

export default function ProProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const insets = useSafeAreaInsets()
  const [pro, setPro] = useState<any>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [jobs, setJobs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const { data: proData } = await supabase.from('pro_profiles').select('*').eq('id', id).single()
      setPro(proData)
      const { data: reviewData } = await supabase.from('reviews')
        .select('*, reviewer:reviewer_id(full_name, avatar_url)')
        .eq('reviewed_id', id).order('created_at', { ascending: false }).limit(10)
      setReviews((reviewData ?? []) as Review[])
      const { data: jobData } = await supabase.from('contracts')
        .select('jobs(title, category, created_at)').eq('pro_id', id).eq('status', 'completed').limit(5)
      setJobs(jobData ?? [])
      setLoading(false)
    }
    load()
  }, [id])

  if (loading) return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>
  if (!pro) return <View style={s.center}><Ionicons name="person-outline" size={48} color="#ccc" /><Text style={s.notFound}>Perfil no encontrado</Text></View>

  const isOwnProfile = session?.user.id === id

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Perfil profesional</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>

        {/* Hero card */}
        <View style={s.heroCard}>
          {pro.avatar_url
            ? <Image source={{ uri: pro.avatar_url }} style={s.avatar} />
            : <View style={s.avatarPlaceholder}><Text style={s.avatarInitial}>{(pro.full_name ?? '?')[0].toUpperCase()}</Text></View>
          }
          <View style={s.heroInfo}>
            <View style={s.nameRow}>
              <Text style={s.name}>{pro.full_name}</Text>
              {pro.is_verified && <Ionicons name="checkmark-circle" size={20} color="#2563EB" />}
            </View>
            <View style={s.roleRow}>
              <Text style={s.roleText}>{pro.role === 'company' ? '🏢 Empresa' : '🔧 Profesional'}</Text>
              <Text style={s.locationText}>{FLAG[pro.country] ?? '🌍'} {pro.country}</Text>
            </View>
            <Stars score={Number(pro.score)} size={18} />
          </View>
        </View>

        {/* Bio */}
        {pro.bio && (
          <View style={s.bioCard}>
            <Text style={s.bioTitle}>Sobre mí</Text>
            <Text style={s.bioText}>{pro.bio}</Text>
          </View>
        )}

        {/* Skills */}
        {pro.skills?.length > 0 && (
          <View style={s.skillsCard}>
            <Text style={s.bioTitle}>Especialidades</Text>
            <View style={s.skillsRow}>
              {pro.skills.map((skill: string, i: number) => (
                <View key={i} style={s.skillChip}>
                  <Text style={s.skillChipText}>{skill}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Stats */}
        <View style={s.statsRow}>
          {[
            { value: pro.total_reviews ?? 0, label: 'Reseñas', icon: 'star', color: '#F59E0B', bg: '#FFFBEB' },
            { value: pro.total_jobs_done ?? 0, label: 'Trabajos', icon: 'briefcase', color: '#2563EB', bg: '#EEF4FF' },
            { value: pro.score > 0 ? Number(pro.score).toFixed(1) : '-', label: 'Score', icon: 'trending-up', color: '#059669', bg: '#F0FDF9' },
            { value: new Date(pro.created_at).getFullYear(), label: 'Desde', icon: 'calendar', color: '#7C3AED', bg: '#EDE9FE' },
          ].map((stat, i) => (
            <View key={i} style={[s.statCard, { backgroundColor: stat.bg }]}>
              <Ionicons name={stat.icon as any} size={16} color={stat.color} />
              <Text style={[s.statValue, { color: stat.color }]}>{stat.value}</Text>
              <Text style={s.statLabel}>{stat.label}</Text>
            </View>
          ))}
        </View>

        {/* CTA */}
        {!isOwnProfile && session && (
          <TouchableOpacity style={s.ctaBtn} onPress={() => router.push('/(app)/jobs')} activeOpacity={0.85}>
            <Ionicons name="briefcase-outline" size={20} color="#fff" />
            <Text style={s.ctaBtnText}>Ver jobs disponibles</Text>
          </TouchableOpacity>
        )}
        {isOwnProfile && (
          <TouchableOpacity style={s.editBtn} onPress={() => router.push('/(app)/profile')} activeOpacity={0.85}>
            <Ionicons name="create-outline" size={18} color="#2563EB" />
            <Text style={s.editBtnText}>Editar mi perfil</Text>
          </TouchableOpacity>
        )}

        {/* Trabajos completados */}
        {jobs.length > 0 && (
          <View style={s.section}>
            <Text style={s.sectionTitle}>Trabajos completados</Text>
            <View style={s.jobsList}>
              {jobs.map((item, i) => (
                <View key={i} style={s.jobItem}>
                  <View style={s.jobItemIcon}>
                    <Ionicons name="checkmark-circle" size={16} color="#059669" />
                  </View>
                  <Text style={s.jobItemTitle} numberOfLines={1}>{item.jobs?.title}</Text>
                  <Text style={s.jobItemDate}>
                    {item.jobs?.created_at ? new Date(item.jobs.created_at).toLocaleDateString('es-ES', { month: 'short', year: 'numeric' }) : ''}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Reviews */}
        <View style={s.section}>
          <View style={s.sectionHeader}>
            <Text style={s.sectionTitle}>Reseñas</Text>
            <Text style={s.sectionCount}>{reviews.length}</Text>
          </View>

          {reviews.length === 0 ? (
            <View style={s.emptyReviews}>
              <Ionicons name="star-outline" size={32} color="#ccc" />
              <Text style={s.emptyReviewsText}>Sin reseñas aún</Text>
            </View>
          ) : (
            reviews.map(review => (
              <View key={review.id} style={s.reviewCard}>
                <View style={s.reviewHeader}>
                  <View style={s.reviewerAvatar}>
                    <Text style={s.reviewerInitial}>
                      {((review as any).reviewer?.full_name ?? '?')[0].toUpperCase()}
                    </Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={s.reviewerName}>{(review as any).reviewer?.full_name ?? 'Usuario'}</Text>
                    <Stars score={review.rating} size={13} />
                  </View>
                  <Text style={s.reviewDate}>
                    {new Date(review.created_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                  </Text>
                </View>

                <Text style={s.reviewComment}>{review.comment}</Text>

                {(review as any).photos_verified && (
                  <View style={s.aiVerifiedBadge}>
                    <Ionicons name="sparkles" size={12} color="#2563EB" />
                    <Text style={s.aiVerifiedText}>Fotos verificadas con IA</Text>
                  </View>
                )}

                {(review.photos_before?.length > 0 || review.photos_after?.length > 0) && (
                  <View style={s.photosSection}>
                    {review.photos_before?.length > 0 && (
                      <View style={s.photosGroup}>
                        <Text style={s.photosGroupLabel}>ANTES</Text>
                        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                          {review.photos_before.map((url: string, i: number) => (
                            <Image key={i} source={{ uri: url }} style={s.reviewPhoto} />
                          ))}
                        </ScrollView>
                      </View>
                    )}
                    {review.photos_after?.length > 0 && (
                      <View style={s.photosGroup}>
                        <Text style={s.photosGroupLabel}>DESPUÉS</Text>
                        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                          {review.photos_after.map((url: string, i: number) => (
                            <Image key={i} source={{ uri: url }} style={s.reviewPhoto} />
                          ))}
                        </ScrollView>
                      </View>
                    )}
                  </View>
                )}
              </View>
            ))
          )}
        </View>

      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB', gap: 12 },
  notFound: { fontSize: 15, color: '#999' },
  scroll: { flex: 1 },
  content: { paddingHorizontal: 20, paddingBottom: 32, gap: 14 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  heroCard: {
    backgroundColor: '#fff', borderRadius: 24, padding: 20,
    flexDirection: 'row', gap: 16, alignItems: 'flex-start',
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06, shadowRadius: 16, elevation: 3,
  },
  avatar: { width: 80, height: 80, borderRadius: 20 },
  avatarPlaceholder: {
    width: 80, height: 80, borderRadius: 20,
    backgroundColor: '#2563EB', justifyContent: 'center', alignItems: 'center',
  },
  avatarInitial: { fontSize: 32, color: '#fff', fontWeight: '800' },
  heroInfo: { flex: 1, gap: 6 },
  nameRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  name: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  roleRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  roleText: { fontSize: 13, color: '#666' },
  locationText: { fontSize: 13, color: '#888' },
  starsRow: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  scoreText: { fontSize: 13, color: '#666', marginLeft: 6, fontWeight: '600' },
  statsRow: { flexDirection: 'row', gap: 8 },
  statCard: {
    flex: 1, borderRadius: 16, padding: 12,
    alignItems: 'center', gap: 4,
  },
  statValue: { fontSize: 18, fontWeight: '800' },
  statLabel: { fontSize: 10, color: '#888', fontWeight: '600' },
  ctaBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  ctaBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  editBtn: {
    borderRadius: 16, height: 52,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    borderWidth: 1.5, borderColor: '#DBEAFE', backgroundColor: '#EEF4FF',
  },
  editBtnText: { fontSize: 15, fontWeight: '700', color: '#2563EB' },
  section: { gap: 12 },
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  sectionTitle: { fontSize: 16, fontWeight: '800', color: '#1a1a2e', flex: 1 },
  sectionCount: {
    fontSize: 12, fontWeight: '700', color: '#888',
    backgroundColor: '#F3F4F6', paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10,
  },
  jobsList: {
    backgroundColor: '#fff', borderRadius: 16, overflow: 'hidden',
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  jobItem: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: 14, borderBottomWidth: 1, borderBottomColor: '#F3F4F6',
  },
  jobItemIcon: {
    width: 28, height: 28, borderRadius: 8,
    backgroundColor: '#D1FAE5', alignItems: 'center', justifyContent: 'center',
  },
  jobItemTitle: { flex: 1, fontSize: 14, color: '#1a1a2e', fontWeight: '500' },
  jobItemDate: { fontSize: 12, color: '#aaa' },
  bioCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 18,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  bioTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e', marginBottom: 8 },
  bioText: { fontSize: 14, color: '#555', lineHeight: 22 },
  skillsCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 18,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  skillsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  skillChip: {
    backgroundColor: '#EEF4FF', borderRadius: 20,
    paddingHorizontal: 12, paddingVertical: 6,
  },
  skillChipText: { fontSize: 13, color: '#2563EB', fontWeight: '600' },
  emptyReviews: {
    backgroundColor: '#fff', borderRadius: 16, padding: 32,
    alignItems: 'center', gap: 8, borderWidth: 1, borderColor: '#E5E7EB',
  },
  emptyReviewsText: { fontSize: 14, color: '#bbb' },
  reviewCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18, gap: 12,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  reviewHeader: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  reviewerAvatar: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#EEF4FF', justifyContent: 'center', alignItems: 'center',
  },
  reviewerInitial: { fontSize: 16, color: '#2563EB', fontWeight: '700' },
  reviewerName: { fontSize: 14, fontWeight: '700', color: '#1a1a2e', marginBottom: 3 },
  reviewDate: { fontSize: 11, color: '#aaa' },
  reviewComment: { fontSize: 14, color: '#555', lineHeight: 21 },
  aiVerifiedBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    backgroundColor: '#EEF4FF', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4, alignSelf: 'flex-start',
  },
  aiVerifiedText: { fontSize: 11, color: '#2563EB', fontWeight: '600' },
  photosSection: { gap: 10 },
  photosGroup: { gap: 6 },
  photosGroupLabel: { fontSize: 10, fontWeight: '800', color: '#888', letterSpacing: 0.5 },
  reviewPhoto: { width: 80, height: 80, borderRadius: 12, marginRight: 8 },
})
