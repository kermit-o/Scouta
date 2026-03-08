import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Alert, TextInput
} from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { supabase, Job, Bid } from '../../../lib/supabase'
import { useAuth } from '../../../lib/AuthContext'
import { useProfile } from '../../../hooks/useProfile'
import { createContract } from '../../../hooks/useContract'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORY_LABELS: Record<string, string> = {
  cleaning: '🧹 Limpieza', plumbing: '🔧 Fontanería', electrical: '⚡ Electricidad',
  painting: '🎨 Pintura', moving: '📦 Mudanza', gardening: '🌿 Jardinería',
  carpentry: '🪚 Carpintería', tech: '💻 Tecnología', design: '✏️ Diseño', other: '🔹 Otro'
}

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  open:        { label: 'Abierto',      color: '#059669', bg: '#D1FAE5' },
  in_progress: { label: 'En progreso',  color: '#2563EB', bg: '#DBEAFE' },
  completed:   { label: 'Completado',   color: '#7C3AED', bg: '#EDE9FE' },
  cancelled:   { label: 'Cancelado',    color: '#DC2626', bg: '#FEE2E2' },
}

type ViewMode = 'detail' | 'bid_form' | 'bid_detail'

export default function JobDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const { profile } = useProfile()
  const insets = useSafeAreaInsets()

  const [job, setJob] = useState<Job | null>(null)
  const [bids, setBids] = useState<Bid[]>([])
  const [myBid, setMyBid] = useState<Bid | null>(null)
  const [selectedBid, setSelectedBid] = useState<Bid | null>(null)
  const [loading, setLoading] = useState(true)
  const [accepting, setAccepting] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('detail')

  // Bid form state
  const [bidAmount, setBidAmount] = useState('')
  const [bidMessage, setBidMessage] = useState('')
  const [bidDays, setBidDays] = useState('')
  const [submittingBid, setSubmittingBid] = useState(false)

  async function fetchJob() {
    const { data } = await supabase.from('jobs').select('*').eq('id', id).single()
    if (data) setJob(data as Job)
  }

  async function fetchBids() {
    const { data } = await supabase
      .from('bids')
      .select('*, users(full_name, avatar_url, is_verified)')
      .eq('job_id', id)
      .order('created_at', { ascending: false })
    if (data) {
      setBids(data as Bid[])
      const mine = data.find((b: Bid) => b.pro_id === session?.user.id)
      setMyBid(mine ?? null)
    }
    setLoading(false)
  }

  useEffect(() => { fetchJob(); fetchBids() }, [id])

  async function handleAcceptBid(bid: Bid) {
    setAccepting(bid.id)
    await supabase.from('bids').update({ status: 'accepted' }).eq('id', bid.id)
    await supabase.from('bids').update({ status: 'rejected' }).eq('job_id', id).neq('id', bid.id)
    await supabase.from('jobs').update({ status: 'in_progress' }).eq('id', id)
    const { error } = await createContract({
      jobId: id!,
      bidId: bid.id,
      clientId: job!.client_id,
      proId: bid.pro_id,
      amount: bid.amount,
      currency: job!.currency,
      country: job!.country,
      deliveryDays: bid.delivery_days,
    })
    setAccepting(null)
    if (error) {
      Alert.alert('⚠️ Oferta aceptada', 'Bid aceptado pero error al crear contrato: ' + error.message)
    } else {
      Alert.alert('✅ Contrato creado', 'El contrato fue generado según las leyes de ' + job!.country, [
        { text: 'Ver contrato', onPress: () => router.push(`/(app)/jobs/${id}/contract`) },
        { text: 'OK', onPress: () => { fetchJob(); fetchBids(); setViewMode('detail') } }
      ])
    }
  }

  async function handleSubmitBid() {
    if (!bidAmount || !bidMessage) return
    setSubmittingBid(true)
    const { error } = await supabase.from('bids').insert({
      job_id: id,
      pro_id: session!.user.id,
      amount: parseFloat(bidAmount),
      currency: job!.currency,
      message: bidMessage,
      delivery_days: bidDays ? parseInt(bidDays) : null,
      status: 'pending',
    })
    setSubmittingBid(false)
    if (error) Alert.alert('Error', error.message)
    else { fetchBids(); setViewMode('detail') }
  }

  if (loading) return (
    <View style={s.center}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  )
  if (!job) return (
    <View style={s.center}>
      <Text style={s.notFound}>Job no encontrado</Text>
    </View>
  )

  const isOwner = job.client_id === session?.user.id
  const isPro = profile?.role === 'pro' || profile?.role === 'company'
  const canBid = isPro && !isOwner && job.status === 'open' && !myBid
  const statusCfg = STATUS_CONFIG[job.status] ?? STATUS_CONFIG.open

  // ── VISTA: HACER OFERTA ──
  if (viewMode === 'bid_form') {
    return (
      <View style={[s.screen, { paddingTop: insets.top }]}>
        <View style={s.header}>
          <TouchableOpacity style={s.backBtn} onPress={() => setViewMode('detail')}>
            <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
          </TouchableOpacity>
          <Text style={s.headerTitle}>Hacer oferta</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView style={s.scroll} contentContainerStyle={s.formContent} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
          {/* Resumen del job */}
          <View style={s.jobSummaryCard}>
            <Text style={s.jobSummaryTitle}>{job.title}</Text>
            {(job.budget_min || job.budget_max) && (
              <Text style={s.jobSummaryBudget}>
                Presupuesto: {job.budget_min ?? '?'} – {job.budget_max ?? '?'} {job.currency}
              </Text>
            )}
          </View>

          <Text style={s.inputLabel}>Tu oferta ({job.currency})</Text>
          <View style={s.inputRow}>
            <Ionicons name="cash-outline" size={20} color="#888" style={s.inputIcon} />
            <TextInput
              style={s.input}
              placeholder="0.00"
              value={bidAmount}
              onChangeText={setBidAmount}
              keyboardType="numeric"
              placeholderTextColor="#bbb"
            />
          </View>

          <Text style={s.inputLabel}>Días estimados de entrega</Text>
          <View style={s.inputRow}>
            <Ionicons name="time-outline" size={20} color="#888" style={s.inputIcon} />
            <TextInput
              style={s.input}
              placeholder="ej: 3"
              value={bidDays}
              onChangeText={setBidDays}
              keyboardType="numeric"
              placeholderTextColor="#bbb"
            />
          </View>

          <Text style={s.inputLabel}>Mensaje al cliente</Text>
          <TextInput
            style={s.textarea}
            placeholder="Describe tu experiencia, disponibilidad y cualquier detalle relevante..."
            value={bidMessage}
            onChangeText={setBidMessage}
            multiline
            numberOfLines={5}
            textAlignVertical="top"
            placeholderTextColor="#bbb"
          />

          <View style={s.escrowNote}>
            <Ionicons name="shield-checkmark" size={18} color="#2563EB" />
            <View style={{ flex: 1 }}>
              <Text style={s.escrowNoteTitle}>Pago protegido con escrow</Text>
              <Text style={s.escrowNoteDesc}>
                El cliente depositará el pago antes de que comiences. Se libera cuando confirma que el trabajo está completo.
              </Text>
            </View>
          </View>
        </ScrollView>

        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <TouchableOpacity
            style={[s.footerBtn, (!bidAmount || !bidMessage || submittingBid) && s.footerBtnDisabled]}
            onPress={handleSubmitBid}
            disabled={!bidAmount || !bidMessage || submittingBid}
            activeOpacity={0.85}
          >
            {submittingBid
              ? <ActivityIndicator color="#fff" />
              : <Text style={s.footerBtnText}>Enviar oferta</Text>
            }
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  // ── VISTA: DETALLE DE OFERTA ──
  if (viewMode === 'bid_detail' && selectedBid) {
    return (
      <View style={[s.screen, { paddingTop: insets.top }]}>
        <View style={s.header}>
          <TouchableOpacity style={s.backBtn} onPress={() => { setViewMode('detail'); setSelectedBid(null) }}>
            <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
          </TouchableOpacity>
          <Text style={s.headerTitle}>Detalle de oferta</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView style={s.scroll} contentContainerStyle={s.bidDetailContent} showsVerticalScrollIndicator={false}>
          {/* Pro info */}
          <View style={s.proCard}>
            <View style={s.proAvatar}>
              <Text style={s.proAvatarText}>
                {(selectedBid.users?.full_name ?? 'P')[0].toUpperCase()}
              </Text>
            </View>
            <View style={{ flex: 1 }}>
              <View style={s.proNameRow}>
                <Text style={s.proName}>{selectedBid.users?.full_name ?? 'Profesional'}</Text>
                {selectedBid.users?.is_verified && (
                  <Ionicons name="checkmark-circle" size={18} color="#2563EB" />
                )}
              </View>
              <Text style={s.proProfession}>Profesional verificado</Text>
            </View>
            <TouchableOpacity
              style={s.msgBtn}
              onPress={() => router.push(`/(app)/jobs/${id}/chat`)}
            >
              <Ionicons name="chatbubble-outline" size={18} color="#2563EB" />
            </TouchableOpacity>
          </View>

          {/* Detalles */}
          <View style={s.bidDetailsCard}>
            <Text style={s.bidDetailsTitle}>Detalles de la oferta</Text>
            <View style={s.bidDetailRow}>
              <Text style={s.bidDetailLabel}>Precio ofertado</Text>
              <Text style={s.bidDetailAmount}>{selectedBid.amount} {selectedBid.currency}</Text>
            </View>
            {selectedBid.delivery_days && (
              <View style={s.bidDetailRow}>
                <Text style={s.bidDetailLabel}>Tiempo estimado</Text>
                <View style={s.bidDetailRowRight}>
                  <Ionicons name="time-outline" size={16} color="#555" />
                  <Text style={s.bidDetailValue}>{selectedBid.delivery_days} días</Text>
                </View>
              </View>
            )}
            <View style={s.divider} />
            <Text style={s.bidDetailLabel}>Mensaje del profesional</Text>
            <Text style={s.bidDetailMessage}>{selectedBid.message}</Text>
          </View>

          {/* Escrow info */}
          <View style={s.escrowNote}>
            <Ionicons name="shield-checkmark" size={18} color="#2563EB" />
            <View style={{ flex: 1 }}>
              <Text style={s.escrowNoteTitle}>Pago seguro con escrow</Text>
              <Text style={s.escrowNoteDesc}>
                Al aceptar, depositarás {selectedBid.amount} {selectedBid.currency} en escrow. El pago solo se libera cuando confirmas que el trabajo está completo.
              </Text>
            </View>
          </View>
        </ScrollView>

        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <TouchableOpacity
            style={[s.footerBtn, accepting === selectedBid.id && s.footerBtnDisabled]}
            onPress={() => handleAcceptBid(selectedBid)}
            disabled={!!accepting}
            activeOpacity={0.85}
          >
            {accepting === selectedBid.id
              ? <ActivityIndicator color="#fff" />
              : <>
                  <Text style={s.footerBtnText}>Aceptar oferta y pagar</Text>
                  <Ionicons name="chevron-forward" size={20} color="#fff" />
                </>
            }
          </TouchableOpacity>
          <TouchableOpacity
            style={s.outlineBtn}
            onPress={() => { setViewMode('detail'); setSelectedBid(null) }}
            activeOpacity={0.85}
          >
            <Text style={s.outlineBtnText}>Ver otras ofertas</Text>
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  // ── VISTA PRINCIPAL: DETALLE JOB ──
  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <View style={s.headerCenter}>
          <Text style={s.headerTitle}>Detalle del trabajo</Text>
        </View>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.detailContent} showsVerticalScrollIndicator={false}>
        {/* Job card */}
        <View style={s.jobCard}>
          <View style={s.jobCardTop}>
            <Text style={s.categoryLabel}>{CATEGORY_LABELS[job.category] ?? '🔹 Otro'}</Text>
            <View style={[s.statusBadge, { backgroundColor: statusCfg.bg }]}>
              <Text style={[s.statusBadgeText, { color: statusCfg.color }]}>{statusCfg.label}</Text>
            </View>
          </View>
          <Text style={s.jobTitle}>{job.title}</Text>
          <Text style={s.jobDesc}>{job.description}</Text>
          <View style={s.jobMeta}>
            {(job.budget_min || job.budget_max) && (
              <View style={s.metaChip}>
                <Ionicons name="cash-outline" size={14} color="#059669" />
                <Text style={[s.metaChipText, { color: '#059669' }]}>
                  {job.budget_min ?? '?'} – {job.budget_max ?? '?'} {job.currency}
                </Text>
              </View>
            )}
            {job.city && (
              <View style={s.metaChip}>
                <Ionicons name="location-outline" size={14} color="#666" />
                <Text style={s.metaChipText}>{job.city}</Text>
              </View>
            )}
            {job.is_remote && (
              <View style={s.metaChip}>
                <Ionicons name="globe-outline" size={14} color="#2563EB" />
                <Text style={[s.metaChipText, { color: '#2563EB' }]}>Remoto</Text>
              </View>
            )}
          </View>
        </View>

        {/* Mi oferta (si existe) */}
        {myBid && (
          <View style={s.myBidCard}>
            <View style={s.myBidLeft}>
              <Text style={s.myBidLabel}>Tu oferta</Text>
              <Text style={s.myBidAmount}>{myBid.amount} {myBid.currency}</Text>
            </View>
            <View style={[s.myBidStatus,
              myBid.status === 'accepted' ? s.myBidStatusAccepted :
              myBid.status === 'rejected' ? s.myBidStatusRejected : s.myBidStatusPending
            ]}>
              <Text style={[s.myBidStatusText,
                myBid.status === 'accepted' ? { color: '#059669' } :
                myBid.status === 'rejected' ? { color: '#DC2626' } : { color: '#D97706' }
              ]}>
                {myBid.status === 'accepted' ? '✅ Aceptada' :
                 myBid.status === 'rejected' ? '❌ Rechazada' : '⏳ Pendiente'}
              </Text>
            </View>
          </View>
        )}

        {/* Acciones rápidas */}
        {(isOwner || isPro) && job.status === 'in_progress' && (
          <View style={s.actionsGrid}>
            <TouchableOpacity
              style={s.actionCard}
              onPress={() => router.push(`/(app)/jobs/${id}/chat`)}
            >
              <View style={[s.actionIcon, { backgroundColor: '#DBEAFE' }]}>
                <Ionicons name="chatbubbles-outline" size={22} color="#2563EB" />
              </View>
              <Text style={s.actionLabel}>Chat</Text>
            </TouchableOpacity>

            {isOwner && (
              <TouchableOpacity
                style={s.actionCard}
                onPress={() => router.push(`/(app)/jobs/${id}/payment`)}
              >
                <View style={[s.actionIcon, { backgroundColor: '#D1FAE5' }]}>
                  <Ionicons name="card-outline" size={22} color="#059669" />
                </View>
                <Text style={s.actionLabel}>Pago escrow</Text>
              </TouchableOpacity>
            )}

            <TouchableOpacity
              style={s.actionCard}
              onPress={() => router.push(`/(app)/jobs/${id}/contract`)}
            >
              <View style={[s.actionIcon, { backgroundColor: '#EDE9FE' }]}>
                <Ionicons name="document-text-outline" size={22} color="#7C3AED" />
              </View>
              <Text style={s.actionLabel}>Contrato</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={s.actionCard}
              onPress={() => router.push(`/(app)/jobs/${id}/dispute`)}
            >
              <View style={[s.actionIcon, { backgroundColor: '#FEE2E2' }]}>
                <Ionicons name="warning-outline" size={22} color="#DC2626" />
              </View>
              <Text style={s.actionLabel}>Disputa</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* Review (completado) */}
        {(isOwner || isPro) && job.status === 'completed' && (
          <TouchableOpacity
            style={s.reviewBanner}
            onPress={() => router.push(`/(app)/jobs/${id}/review`)}
            activeOpacity={0.85}
          >
            <Ionicons name="star" size={20} color="#D97706" />
            <Text style={s.reviewBannerText}>Deja una reseña del trabajo</Text>
            <Ionicons name="chevron-forward" size={18} color="#D97706" />
          </TouchableOpacity>
        )}

        {/* Bids list (owner) */}
        {isOwner && (
          <View style={s.bidsSection}>
            <Text style={s.bidsTitle}>Ofertas recibidas</Text>
            <Text style={s.bidsCount}>{bids.length} oferta{bids.length !== 1 ? 's' : ''}</Text>

            {bids.length === 0 ? (
              <View style={s.emptyBids}>
                <Ionicons name="time-outline" size={32} color="#ccc" />
                <Text style={s.emptyBidsText}>Aún no hay ofertas</Text>
                <Text style={s.emptyBidsDesc}>Los profesionales podrán enviar sus propuestas pronto</Text>
              </View>
            ) : (
              bids.map(bid => (
                <TouchableOpacity
                  key={bid.id}
                  style={[s.bidCard, bid.status === 'accepted' && s.bidCardAccepted]}
                  onPress={() => { setSelectedBid(bid); setViewMode('bid_detail') }}
                  activeOpacity={0.85}
                  disabled={job.status !== 'open' || bid.status !== 'pending'}
                >
                  <View style={s.bidCardLeft}>
                    <View style={s.bidAvatar}>
                      <Text style={s.bidAvatarText}>
                        {(bid.users?.full_name ?? 'P')[0].toUpperCase()}
                      </Text>
                    </View>
                    <View style={{ flex: 1 }}>
                      <View style={s.bidNameRow}>
                        <Text style={s.bidName}>{bid.users?.full_name ?? 'Profesional'}</Text>
                        {bid.users?.is_verified && (
                          <Ionicons name="checkmark-circle" size={14} color="#2563EB" />
                        )}
                      </View>
                      <Text style={s.bidMsg} numberOfLines={2}>{bid.message}</Text>
                      {bid.delivery_days && (
                        <Text style={s.bidDays}>⏱ {bid.delivery_days} días</Text>
                      )}
                    </View>
                  </View>
                  <View style={s.bidCardRight}>
                    <Text style={s.bidAmount}>{bid.amount}</Text>
                    <Text style={s.bidCurrency}>{bid.currency}</Text>
                    {bid.status === 'accepted' ? (
                      <Ionicons name="checkmark-circle" size={18} color="#059669" style={{ marginTop: 4 }} />
                    ) : bid.status === 'pending' && job.status === 'open' ? (
                      <Ionicons name="chevron-forward" size={16} color="#aaa" style={{ marginTop: 4 }} />
                    ) : null}
                  </View>
                </TouchableOpacity>
              ))
            )}
          </View>
        )}
      </ScrollView>

      {/* Footer */}
      {canBid && (
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <TouchableOpacity
            style={s.footerBtn}
            onPress={() => setViewMode('bid_form')}
            activeOpacity={0.85}
          >
            <Ionicons name="briefcase-outline" size={20} color="#fff" />
            <Text style={s.footerBtnText}>Hacer una oferta</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' },
  notFound: { fontSize: 16, color: '#888' },
  scroll: { flex: 1 },

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
  headerCenter: { alignItems: 'center' },

  // Detail
  detailContent: { paddingHorizontal: 20, paddingBottom: 24, gap: 14 },
  jobCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)', gap: 10,
  },
  jobCardTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  categoryLabel: { fontSize: 13, color: '#666', fontWeight: '600' },
  statusBadge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20 },
  statusBadgeText: { fontSize: 12, fontWeight: '700' },
  jobTitle: { fontSize: 22, fontWeight: '800', color: '#1a1a2e', lineHeight: 28 },
  jobDesc: { fontSize: 15, color: '#555', lineHeight: 22 },
  jobMeta: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 4 },
  metaChip: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    backgroundColor: '#F3F4F6', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 5,
  },
  metaChipText: { fontSize: 12, color: '#555', fontWeight: '500' },

  myBidCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 16,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  myBidLeft: { gap: 2 },
  myBidLabel: { fontSize: 12, color: '#888', fontWeight: '600' },
  myBidAmount: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  myBidStatus: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  myBidStatusPending: { backgroundColor: '#FEF3C7' },
  myBidStatusAccepted: { backgroundColor: '#D1FAE5' },
  myBidStatusRejected: { backgroundColor: '#FEE2E2' },
  myBidStatusText: { fontSize: 13, fontWeight: '700' },

  actionsGrid: { flexDirection: 'row', gap: 10 },
  actionCard: {
    flex: 1, backgroundColor: '#fff', borderRadius: 16, padding: 14,
    alignItems: 'center', gap: 8,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  actionIcon: { width: 44, height: 44, borderRadius: 12, alignItems: 'center', justifyContent: 'center' },
  actionLabel: { fontSize: 11, fontWeight: '600', color: '#555', textAlign: 'center' },

  reviewBanner: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: '#FFFBEB', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: '#FDE68A',
  },
  reviewBannerText: { flex: 1, fontSize: 14, fontWeight: '600', color: '#D97706' },

  bidsSection: { gap: 10 },
  bidsTitle: { fontSize: 18, fontWeight: '800', color: '#1a1a2e' },
  bidsCount: { fontSize: 13, color: '#888', marginTop: -6 },
  emptyBids: {
    alignItems: 'center', padding: 32, gap: 8,
    backgroundColor: '#fff', borderRadius: 16, borderWidth: 1, borderColor: '#E5E7EB',
  },
  emptyBidsText: { fontSize: 15, fontWeight: '700', color: '#999' },
  emptyBidsDesc: { fontSize: 13, color: '#bbb', textAlign: 'center' },

  bidCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 16,
    flexDirection: 'row', gap: 12,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  bidCardAccepted: { borderColor: '#6EE7B7', backgroundColor: '#F0FDF9' },
  bidCardLeft: { flex: 1, flexDirection: 'row', gap: 12, alignItems: 'flex-start' },
  bidCardRight: { alignItems: 'flex-end', justifyContent: 'center', minWidth: 60 },
  bidAvatar: {
    width: 44, height: 44, borderRadius: 12,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },
  bidAvatarText: { fontSize: 16, fontWeight: '700', color: '#2563EB' },
  bidNameRow: { flexDirection: 'row', alignItems: 'center', gap: 5, marginBottom: 4 },
  bidName: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  bidMsg: { fontSize: 13, color: '#666', lineHeight: 18 },
  bidDays: { fontSize: 12, color: '#888', marginTop: 4 },
  bidAmount: { fontSize: 18, fontWeight: '800', color: '#2563EB' },
  bidCurrency: { fontSize: 11, color: '#888', fontWeight: '600' },

  // Bid form
  formContent: { paddingHorizontal: 20, paddingBottom: 20, gap: 12 },
  jobSummaryCard: {
    backgroundColor: '#EEF4FF', borderRadius: 14, padding: 14, gap: 4,
  },
  jobSummaryTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  jobSummaryBudget: { fontSize: 13, color: '#666' },
  inputLabel: { fontSize: 13, fontWeight: '700', color: '#555' },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: '#fff', borderRadius: 14, paddingHorizontal: 14, height: 52,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  inputIcon: {},
  input: { flex: 1, fontSize: 16, color: '#1a1a2e' },
  textarea: {
    backgroundColor: '#fff', borderRadius: 14, padding: 14,
    fontSize: 15, color: '#1a1a2e', minHeight: 120,
    borderWidth: 1, borderColor: '#E5E7EB', lineHeight: 22,
  },

  escrowNote: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 12,
    backgroundColor: '#EEF4FF', borderRadius: 14, padding: 14,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  escrowNoteTitle: { fontSize: 13, fontWeight: '700', color: '#1a1a2e', marginBottom: 3 },
  escrowNoteDesc: { fontSize: 12, color: '#555', lineHeight: 17 },

  // Bid detail
  bidDetailContent: { paddingHorizontal: 20, paddingBottom: 20, gap: 14 },
  proCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20,
    flexDirection: 'row', alignItems: 'center', gap: 14,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  proAvatar: {
    width: 60, height: 60, borderRadius: 16,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },
  proAvatarText: { fontSize: 24, fontWeight: '700', color: '#2563EB' },
  proNameRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 },
  proName: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  proProfession: { fontSize: 13, color: '#888' },
  msgBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },
  bidDetailsCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 14,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  bidDetailsTitle: { fontSize: 16, fontWeight: '800', color: '#1a1a2e' },
  bidDetailRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  bidDetailRowRight: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  bidDetailLabel: { fontSize: 13, color: '#888', marginBottom: 4 },
  bidDetailAmount: { fontSize: 26, fontWeight: '800', color: '#1a1a2e' },
  bidDetailValue: { fontSize: 14, color: '#1a1a2e', fontWeight: '600' },
  bidDetailMessage: { fontSize: 15, color: '#555', lineHeight: 22, marginTop: 6 },
  divider: { height: 1, backgroundColor: '#F3F4F6' },

  // Footer
  footer: { paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)', gap: 10 },
  footerBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  footerBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  outlineBtn: {
    borderRadius: 16, height: 48,
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1.5, borderColor: '#E5E7EB', backgroundColor: '#fff',
  },
  outlineBtnText: { fontSize: 15, fontWeight: '600', color: '#555' },
})