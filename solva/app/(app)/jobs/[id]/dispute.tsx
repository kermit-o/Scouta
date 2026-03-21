import { useTranslation } from 'react-i18next'
import { useEffect, useRef, useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TextInput,
  TouchableOpacity, ActivityIndicator, Image
} from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import * as ImagePicker from 'expo-image-picker'
import { supabase, Dispute, DisputeReason } from '../../../../lib/supabase'
import { useAuth } from '../../../../lib/AuthContext'
import { notifyUser } from '../../../../hooks/useNotifications'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'





export default function DisputeScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const insets = useSafeAreaInsets()
  const scrollRef = useRef<ScrollView>(null)

  const { t } = useTranslation()
  const REASONS: { label: string; icon: string; value: DisputeReason; desc: string }[] = [
    { label: t('dispute.reasonNotDone'),        icon: '🚫', value: 'work_not_done',        desc: t('dispute.reasonNotDoneDesc') },
    { label: t('dispute.reasonPoorQuality'),    icon: '⚠️', value: 'work_poor_quality',    desc: t('dispute.reasonPoorQualityDesc') },
    { label: t('dispute.reasonPayment'),        icon: '💳', value: 'payment_not_released', desc: t('dispute.reasonPaymentDesc') },
    { label: t('dispute.reasonNoShow'),         icon: '❌', value: 'no_show',              desc: t('dispute.reasonNoShowDesc') },
    { label: t('dispute.reasonScope'),          icon: '📋', value: 'scope_change',         desc: t('dispute.reasonScopeDesc') },
    { label: t('dispute.reasonOther'),          icon: '🔹', value: 'other',                desc: t('dispute.reasonOtherDesc') },
  ]
  const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string; icon: string }> = {
    open:            { label: t('dispute.statusOpen'),           color: '#DC2626', bg: '#FEE2E2', icon: 'alert-circle' },
    under_review:    { label: t('dispute.statusReview'),         color: '#D97706', bg: '#FEF3C7', icon: 'time' },
    resolved_client: { label: t('dispute.statusResolvedClient'), color: '#059669', bg: '#D1FAE5', icon: 'checkmark-circle' },
    resolved_pro:    { label: t('dispute.statusResolvedPro'),    color: '#059669', bg: '#D1FAE5', icon: 'checkmark-circle' },
    resolved_split:  { label: t('dispute.statusResolvedSplit'),  color: '#059669', bg: '#D1FAE5', icon: 'checkmark-circle' },
    closed:          { label: t('dispute.statusClosed'),         color: '#888',    bg: '#F3F4F6', icon: 'close-circle' },
  }
  const [contract, setContract] = useState<any>(null)
  const [dispute, setDispute] = useState<Dispute | null>(null)
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const [reason, setReason] = useState<DisputeReason>('work_not_done')
  const [description, setDescription] = useState('')
  const [evidenceUrls, setEvidenceUrls] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [msgText, setMsgText] = useState('')
  const [sendingMsg, setSendingMsg] = useState(false)

  async function loadData() {
    const { data: c } = await supabase.from('contracts').select('*').eq('job_id', id).single()
    setContract(c)
    if (c) {
      const { data: d } = await supabase.from('disputes').select('*').eq('contract_id', c.id).maybeSingle()
      setDispute(d as Dispute | null)
      if (d) {
        const { data: msgs } = await supabase
          .from('dispute_messages')
          .select('*, sender:sender_id(full_name)')
          .eq('dispute_id', d.id)
          .order('created_at', { ascending: true })
        setMessages(msgs ?? [])
      }
    }
    setLoading(false)
  }

  useEffect(() => { loadData() }, [id])

  useEffect(() => {
    if (!dispute?.id) return
    const channel = supabase.channel(`dispute:${dispute.id}`)
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'dispute_messages', filter: `dispute_id=eq.${dispute.id}` },
        payload => setMessages(prev => [...prev, payload.new]))
      .subscribe()
    return () => { supabase.removeChannel(channel) }
  }, [dispute?.id])

  async function uploadEvidence() {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
    if (status !== 'granted') return
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, allowsMultipleSelection: true, quality: 0.8 })
    if (result.canceled) return
    setUploading(true)
    const urls: string[] = []
    for (const asset of result.assets) {
      const ext = asset.uri.split('.').pop() || 'jpg'
      const fileName = `${session!.user.id}/${id}/${Date.now()}.${ext}`
      const blob = await (await fetch(asset.uri)).blob()
      const { error } = await supabase.storage.from('dispute-evidence').upload(fileName, blob, { upsert: true, contentType: `image/${ext}` })
      if (!error) {
        const { data: { publicUrl } } = supabase.storage.from('dispute-evidence').getPublicUrl(fileName)
        urls.push(publicUrl)
      }
    }
    setEvidenceUrls(prev => [...prev, ...urls])
    setUploading(false)
  }

  async function handleOpenDispute() {
    if (description.trim().length < 30) { setErrorMsg('La descripción debe tener al menos 30 caracteres.'); return }
    if (!contract) return
    setSaving(true)
    const againstId = contract.client_id === session!.user.id ? contract.pro_id : contract.client_id
    const { data: newDispute, error } = await supabase.from('disputes').insert({
      contract_id: contract.id, payment_id: null,
      opened_by: session!.user.id, against: againstId,
      reason, description: description.trim(), evidence_urls: evidenceUrls,
    }).select().single()
    if (error) { setErrorMsg(error.message); setSaving(false); return }
    await supabase.from('contracts').update({ status: 'disputed' }).eq('id', contract.id)
    await notifyUser(againstId, '⚠️ Disputa abierta', 'Se ha abierto una disputa en uno de tus contratos.', { job_id: String(id) })
    // Email al afectado
    try {
      const { data: againstProfile } = await supabase.from('users').select('email, full_name').eq('id', againstId).single()
      if (againstProfile?.email) {
        await supabase.functions.invoke('send-email', { body: { to: againstProfile.email, template: 'dispute_opened', data: { userName: againstProfile.full_name ?? 'Usuario', jobTitle: 'tu contrato' } } })
      }
    } catch (_) {}
    setSaving(false)
    setDispute(newDispute as Dispute)
    loadData()
  }

  async function handleSendMessage() {
    if (!msgText.trim() || !dispute) return
    setSendingMsg(true)
    await supabase.from('dispute_messages').insert({ dispute_id: dispute.id, sender_id: session!.user.id, content: msgText.trim() })
    setMsgText('')
    setSendingMsg(false)
    setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 200)
  }

  if (loading) return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>
  if (!contract) return <View style={s.center}><Ionicons name="document-outline" size={48} color="#ccc" /><Text style={s.notFound}>Contrato no encontrado</Text></View>

  const statusCfg = dispute ? (STATUS_CONFIG[dispute.status] ?? STATUS_CONFIG.open) : null
  const isActive = dispute && ['open', 'under_review'].includes(dispute.status)

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>{t('dispute.title')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView ref={scrollRef} style={s.scroll} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>

        {dispute ? (
          <>
            {/* Status card */}
            <View style={[s.statusCard, { backgroundColor: statusCfg!.bg }]}>
              <View style={s.statusTop}>
                <Ionicons name={statusCfg!.icon as any} size={22} color={statusCfg!.color} />
                <Text style={[s.statusLabel, { color: statusCfg!.color }]}>{statusCfg!.label}</Text>
              </View>
              <Text style={s.statusReason}>{REASONS.find(r => r.value === dispute.reason)?.icon} {REASONS.find(r => r.value === dispute.reason)?.label}</Text>
              <Text style={s.statusDesc}>{dispute.description}</Text>
              {dispute.resolution_note && (
                <View style={s.resolutionBox}>
                  <Text style={s.resolutionTitle}>{t('dispute.resolution')}</Text>
                  <Text style={s.resolutionNote}>{dispute.resolution_note}</Text>
                  {dispute.refund_pct > 0 && (
                    <View style={s.refundBadge}>
                      <Ionicons name="cash-outline" size={14} color="#059669" />
                      <Text style={s.refundText}>Reembolso: {dispute.refund_pct}%</Text>
                    </View>
                  )}
                </View>
              )}
            </View>

            {/* Evidencias */}
            {dispute.evidence_urls?.length > 0 && (
              <View style={s.card}>
                <Text style={s.cardTitle}>{t('dispute.evidence')}</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  {dispute.evidence_urls.map((url: string, i: number) => (
                    <Image key={i} source={{ uri: url }} style={s.evidencePhoto} />
                  ))}
                </ScrollView>
              </View>
            )}

            {/* Mensajes */}
            <View style={s.card}>
              <Text style={s.cardTitle}>Comunicación ({messages.length})</Text>
              {messages.length === 0 ? (
                <View style={s.emptyMsgs}>
                  <Ionicons name="chatbubbles-outline" size={28} color="#ccc" />
                  <Text style={s.emptyMsgsText}>{t('dispute.noMessages')}</Text>
                </View>
              ) : (
                messages.map(msg => {
                  const isMine = msg.sender_id === session!.user.id
                  return (
                    <View key={msg.id} style={[s.msgRow, isMine && s.msgRowMine]}>
                      <View style={[s.bubble, isMine ? s.bubbleMine : s.bubbleOther]}>
                        {!isMine && <Text style={s.msgSender}>{msg.sender?.full_name ?? 'Soporte'}</Text>}
                        <Text style={[s.msgText, isMine && s.msgTextMine]}>{msg.content}</Text>
                        <Text style={[s.msgTime, isMine && s.msgTimeMine]}>
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </Text>
                      </View>
                    </View>
                  )
                })
              )}
            </View>

            <View style={s.infoCard}>
              <Ionicons name="time-outline" size={16} color="#2563EB" />
              <Text style={s.infoText}>{t('dispute.reviewTime')}</Text>
            </View>
          </>
        ) : (
          <>
            {/* Warning */}
            <View style={s.warningCard}>
              <Ionicons name="warning" size={20} color="#D97706" />
              <View style={{ flex: 1 }}>
                <Text style={s.warningTitle}>{t('dispute.warning')}</Text>
                <Text style={s.warningDesc}>{t('dispute.warningDesc')}</Text>
              </View>
            </View>

            {/* Motivo */}
            <Text style={s.label}>Motivo de la disputa *</Text>
            <View style={s.reasonsGrid}>
              {REASONS.map(r => (
                <TouchableOpacity
                  key={r.value}
                  style={[s.reasonCard, reason === r.value && s.reasonCardSelected]}
                  onPress={() => setReason(r.value)}
                  activeOpacity={0.8}
                >
                  <Text style={s.reasonIcon}>{r.icon}</Text>
                  <Text style={[s.reasonLabel, reason === r.value && s.reasonLabelSelected]}>{r.label}</Text>
                  <Text style={s.reasonDesc}>{r.desc}</Text>
                  {reason === r.value && (
                    <View style={s.reasonCheck}>
                      <Ionicons name="checkmark" size={10} color="#fff" />
                    </View>
                  )}
                </TouchableOpacity>
              ))}
            </View>

            {/* Descripción */}
            <View style={s.card}>
              <Text style={s.label}>Descripción detallada * <Text style={s.labelSub}>(mín. 30 caracteres)</Text></Text>
              <TextInput
                style={s.textarea}
                value={description}
                onChangeText={setDescription}
                placeholder={t("dispute.descPlaceholder")}
                multiline
                numberOfLines={5}
                maxLength={1000}
                textAlignVertical="top"
                placeholderTextColor="#bbb"
              />
              <Text style={[s.counter, description.length >= 30 && s.counterOk]}>
                {description.length}/1000 {description.length >= 30 ? '✓' : `(faltan ${30 - description.length})`}
              </Text>
            </View>

            {/* Evidencias */}
            <View style={s.card}>
              <Text style={s.label}>Evidencias (fotos, capturas)</Text>
              {evidenceUrls.length > 0 && (
                <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 12 }}>
                  {evidenceUrls.map((url, i) => (
                    <Image key={i} source={{ uri: url }} style={s.evidencePhoto} />
                  ))}
                </ScrollView>
              )}
              <TouchableOpacity
                style={s.uploadBtn}
                onPress={uploadEvidence}
                disabled={uploading}
                activeOpacity={0.8}
              >
                {uploading
                  ? <ActivityIndicator size="small" color="#DC2626" />
                  : <>
                      <Ionicons name="attach-outline" size={18} color="#DC2626" />
                      <Text style={s.uploadBtnText}>Agregar evidencias ({evidenceUrls.length})</Text>
                    </>
                }
              </TouchableOpacity>
            </View>
          </>
        )}
      </ScrollView>

      {/* Footer */}
      {isActive ? (
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <View style={s.msgInputRow}>
            <TextInput
              style={s.msgInput}
              value={msgText}
              onChangeText={setMsgText}
              placeholder={t("dispute.replyPlaceholder")}
              multiline
              maxLength={500}
              placeholderTextColor="#bbb"
            />
            <TouchableOpacity
              style={[s.sendBtn, (!msgText.trim() || sendingMsg) && s.sendBtnDisabled]}
              onPress={handleSendMessage}
              disabled={!msgText.trim() || sendingMsg}
            >
              {sendingMsg
                ? <ActivityIndicator color="#fff" size="small" />
                : <Ionicons name="send" size={18} color="#fff" />
              }
            </TouchableOpacity>
          </View>
        </View>
      ) : !dispute ? (
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <TouchableOpacity
            style={[s.footerBtn, (saving || description.trim().length < 30) && s.footerBtnDisabled]}
            onPress={handleOpenDispute}
            disabled={saving || description.trim().length < 30}
            activeOpacity={0.85}
          >
            {saving
              ? <ActivityIndicator color="#fff" />
              : <>
                  <Ionicons name="warning" size={20} color="#fff" />
                  <Text style={s.footerBtnText}>Abrir disputa</Text>
                </>
            }
          </TouchableOpacity>
        </View>
      ) : null}
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB', gap: 12 },
  notFound: { fontSize: 15, color: '#999' },
  scroll: { flex: 1 },
  content: { paddingHorizontal: 20, paddingBottom: 24, gap: 14 },
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
  statusCard: { borderRadius: 20, padding: 18, gap: 10 },
  statusTop: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  statusLabel: { fontSize: 16, fontWeight: '800' },
  statusReason: { fontSize: 14, fontWeight: '600', color: '#555' },
  statusDesc: { fontSize: 14, color: '#555', lineHeight: 20 },
  resolutionBox: {
    backgroundColor: '#fff', borderRadius: 12, padding: 14,
    marginTop: 4, gap: 6, borderWidth: 1, borderColor: '#6EE7B7',
  },
  resolutionTitle: { fontSize: 13, fontWeight: '700', color: '#059669' },
  resolutionNote: { fontSize: 14, color: '#333', lineHeight: 20 },
  refundBadge: { flexDirection: 'row', alignItems: 'center', gap: 6, marginTop: 2 },
  refundText: { fontSize: 14, fontWeight: '700', color: '#059669' },
  card: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18, gap: 12,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  cardTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e' },
  evidencePhoto: { width: 88, height: 88, borderRadius: 12, marginRight: 10 },
  emptyMsgs: { alignItems: 'center', paddingVertical: 20, gap: 8 },
  emptyMsgsText: { fontSize: 14, color: '#bbb' },
  msgRow: { flexDirection: 'row', justifyContent: 'flex-start', marginBottom: 8 },
  msgRowMine: { justifyContent: 'flex-end' },
  bubble: { maxWidth: '80%', padding: 12, borderRadius: 16, gap: 4 },
  bubbleMine: { backgroundColor: '#2563EB', borderBottomRightRadius: 4 },
  bubbleOther: { backgroundColor: '#F3F4F6', borderBottomLeftRadius: 4 },
  msgSender: { fontSize: 11, fontWeight: '700', color: '#888' },
  msgText: { fontSize: 14, color: '#333', lineHeight: 19 },
  msgTextMine: { color: '#fff' },
  msgTime: { fontSize: 10, color: '#aaa', textAlign: 'right' },
  msgTimeMine: { color: 'rgba(255,255,255,0.6)' },
  infoCard: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 10,
    backgroundColor: '#EEF4FF', borderRadius: 14, padding: 14,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  infoText: { flex: 1, fontSize: 12, color: '#555', lineHeight: 17 },
  warningCard: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 12,
    backgroundColor: '#FFFBEB', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: '#FDE68A',
  },
  warningTitle: { fontSize: 14, fontWeight: '700', color: '#D97706', marginBottom: 4 },
  warningDesc: { fontSize: 13, color: '#856404', lineHeight: 19 },
  label: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  labelSub: { fontWeight: '400', color: '#888' },
  reasonsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  reasonCard: {
    width: '47%', backgroundColor: '#fff', borderRadius: 16, padding: 14, gap: 4,
    borderWidth: 2, borderColor: '#E5E7EB', position: 'relative',
  },
  reasonCardSelected: { borderColor: '#DC2626', backgroundColor: '#FFF5F5' },
  reasonIcon: { fontSize: 20, marginBottom: 4 },
  reasonLabel: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  reasonLabelSelected: { color: '#DC2626' },
  reasonDesc: { fontSize: 11, color: '#888', lineHeight: 15 },
  reasonCheck: {
    position: 'absolute', top: 8, right: 8,
    width: 18, height: 18, borderRadius: 9,
    backgroundColor: '#DC2626', alignItems: 'center', justifyContent: 'center',
  },
  textarea: {
    borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 14,
    padding: 14, fontSize: 15, color: '#1a1a2e',
    minHeight: 120, backgroundColor: '#F9FAFB', lineHeight: 22,
  },
  counter: { fontSize: 12, color: '#bbb', textAlign: 'right' },
  counterOk: { color: '#059669', fontWeight: '600' },
  uploadBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    borderWidth: 1.5, borderStyle: 'dashed', borderColor: '#FECACA',
    borderRadius: 14, paddingVertical: 14, backgroundColor: '#FFF5F5',
  },
  uploadBtnText: { fontSize: 14, fontWeight: '600', color: '#DC2626' },
  footer: { paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)' },
  footerBtn: {
    backgroundColor: '#DC2626', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#DC2626', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  footerBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  msgInputRow: { flexDirection: 'row', gap: 10, alignItems: 'flex-end' },
  msgInput: {
    flex: 1, borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 12, fontSize: 15,
    backgroundColor: '#fff', maxHeight: 100, color: '#1a1a2e',
  },
  sendBtn: {
    width: 46, height: 46, borderRadius: 14,
    backgroundColor: '#2563EB', justifyContent: 'center', alignItems: 'center',
  },
  sendBtnDisabled: { opacity: 0.4 },
})
