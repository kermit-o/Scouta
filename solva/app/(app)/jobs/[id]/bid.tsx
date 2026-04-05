import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, ScrollView
} from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { supabase } from '../../../../lib/supabase'
import { useAuth } from '../../../../lib/AuthContext'
import { useProfile } from '../../../../hooks/useProfile'
import { notifyUser } from '../../../../hooks/useNotifications'
import { useSubscription } from '../../../../hooks/useSubscription'
import { checkPlanLimit } from '../../../../lib/planLimits'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { PaywallModal } from '../../../../components/PaywallModal'

export default function NewBidScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const { profile } = useProfile()
  const insets = useSafeAreaInsets()
  const { canSendBid } = useSubscription()

  const { t } = useTranslation()
  const [amount, setAmount] = useState('')
  const [message, setMessage] = useState('')
  const [deliveryDays, setDeliveryDays] = useState('')
  const [saving, setSaving] = useState(false)
  const [paywallFeature, setPaywallFeature] = useState<string | null>(null)

  async function handleSubmit() {
    // Verificar límite de bids
    const limit = await checkPlanLimit(session!.user.id, 'bid')
    if (!limit.allowed) {
      setPaywallFeature('bid')
      return
    }
    const { allowed, reason } = await canSendBid()
    if (!allowed) { setPaywallFeature('bid'); return }
    if (!amount) { setErrorMsg('El precio es obligatorio.'); return }
    if (parseFloat(amount) <= 0) { setErrorMsg('El precio debe ser mayor a 0.'); return }
    if (!message.trim()) { setErrorMsg('El mensaje es obligatorio.'); return }
    if (message.trim().length < 20) { setErrorMsg('El mensaje debe tener al menos 20 caracteres.'); return }

    setSaving(true)
    const { error } = await supabase.from('bids').insert({
      job_id: id,
      pro_id: session!.user.id,
      amount: parseFloat(amount),
      currency: profile?.currency ?? 'EUR',
      message: message.trim(),
      delivery_days: deliveryDays ? parseInt(deliveryDays) : null,
    })
    setSaving(false)

    if (error) {
      setErrorMsg(error.message)
    } else {
      const { data: job } = await supabase.from('jobs').select('client_id, title').eq('id', id).single()
      if (job) {
        await notifyUser(job.client_id, '💼 Nueva oferta recibida', `${profile?.full_name} hizo una oferta en: ${job.title}`, { job_id: id as string })
      }
      Alert.alert(t('bid.sent'), t('bid.sentDesc'), [
        { text: 'OK', onPress: () => router.back() }
      ])
    }
  }

  const canSubmit = !!amount && parseFloat(amount) > 0 && message.trim().length >= 20 && !saving

  return (
    <>
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>{t('bid.title')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>

        {/* Moneda badge */}
        <View style={s.currencyCard}>
          <View style={s.currencyIcon}>
            <Ionicons name="cash-outline" size={22} color="#2563EB" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={s.currencyLabel}>{t('bid.currency')}</Text>
            <Text style={s.currencyValue}>{profile?.currency ?? 'EUR'}</Text>
          </View>
        </View>

        {/* Precio */}
        <View style={s.card}>
          <Text style={s.label}>{t('bid.price')} <Text style={s.required}>*</Text></Text>
          <View style={s.inputRow}>
            <Ionicons name="cash-outline" size={20} color="#888" />
            <TextInput
              style={s.input}
              value={amount}
              onChangeText={setAmount}
              placeholder="0.00"
              keyboardType="numeric"
              placeholderTextColor="#bbb"
            />
            <Text style={s.currencyTag}>{profile?.currency ?? 'EUR'}</Text>
          </View>
        </View>

        {/* Días */}
        <View style={s.card}>
          <Text style={s.label}>{t('bid.days')} <Text style={s.optional}>({t('common.optional')})</Text></Text>
          <View style={s.inputRow}>
            <Ionicons name="time-outline" size={20} color="#888" />
            <TextInput
              style={s.input}
              value={deliveryDays}
              onChangeText={setDeliveryDays}
              placeholder={t("bid.daysPlaceholder")}
              keyboardType="numeric"
              placeholderTextColor="#bbb"
            />
          </View>
        </View>

        {/* Mensaje */}
        <View style={s.card}>
          <Text style={s.label}>{t('bid.message')} <Text style={s.required}>*</Text> <Text style={s.optional}>({t('bid.minChars')})</Text></Text>
          <TextInput
            style={s.textarea}
            value={message}
            onChangeText={setMessage}
            placeholder={t("bid.messagePlaceholder")}
            multiline
            numberOfLines={6}
            maxLength={500}
            textAlignVertical="top"
            placeholderTextColor="#bbb"
          />
          <Text style={[s.counter, message.length >= 20 && s.counterOk]}>
            {message.length}/500 {message.length >= 20 ? '✓' : `(faltan ${20 - message.length})`}
          </Text>
        </View>

        {/* Escrow info */}
        <View style={s.escrowCard}>
          <Ionicons name="shield-checkmark" size={18} color="#2563EB" />
          <View style={{ flex: 1 }}>
            <Text style={s.escrowTitle}>Pago protegido con escrow</Text>
            <Text style={s.escrowDesc}>Si el cliente acepta tu oferta, depositará el pago antes de que comiences. Se libera cuando confirma que el trabajo está completo.</Text>
          </View>
        </View>

        {/* Tips */}
        <View style={s.tipsCard}>
          <Text style={s.tipsTitle}>💡 Tips para ganar más bids</Text>
          {[
            'Sé específico sobre cómo resolverías el problema',
            'Menciona tu experiencia relevante',
            'Indica tu disponibilidad y tiempo estimado',
            'Un precio competitivo pero justo',
          ].map((tip, i) => (
            <View key={i} style={s.tipRow}>
              <View style={s.tipDot} />
              <Text style={s.tipText}>{tip}</Text>
            </View>
          ))}
        </View>

      </ScrollView>

      <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
        <TouchableOpacity
          style={[s.footerBtn, !canSubmit && s.footerBtnDisabled]}
          onPress={handleSubmit}
          disabled={!canSubmit}
          activeOpacity={0.85}
        >
          {saving
            ? <ActivityIndicator color="#fff" />
            : <>
                <Ionicons name="send-outline" size={20} color="#fff" />
                <Text style={s.footerBtnText}>{t('bid.submit')}</Text>
              </>
          }
        </TouchableOpacity>
      </View>
    </View>
      <PaywallModal feature={paywallFeature} onClose={() => setPaywallFeature(null)} />
    </>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
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
  currencyCard: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    backgroundColor: '#EEF4FF', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  currencyIcon: {
    width: 44, height: 44, borderRadius: 12,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
  },
  currencyLabel: { fontSize: 12, color: '#888', fontWeight: '600' },
  currencyValue: { fontSize: 18, fontWeight: '800', color: '#2563EB' },
  card: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18, gap: 10,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  label: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  required: { color: '#EF4444' },
  optional: { fontWeight: '400', color: '#888' },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: '#F9FAFB', borderRadius: 14, paddingHorizontal: 14, height: 52,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  input: { flex: 1, fontSize: 16, color: '#1a1a2e' },
  currencyTag: { fontSize: 13, fontWeight: '700', color: '#888' },
  textarea: {
    backgroundColor: '#F9FAFB', borderRadius: 14, padding: 14,
    fontSize: 15, color: '#1a1a2e', minHeight: 130,
    borderWidth: 1, borderColor: '#E5E7EB', lineHeight: 22,
  },
  counter: { fontSize: 12, color: '#bbb', textAlign: 'right' },
  counterOk: { color: '#059669', fontWeight: '600' },
  escrowCard: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 12,
    backgroundColor: '#EEF4FF', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  escrowTitle: { fontSize: 13, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  escrowDesc: { fontSize: 12, color: '#555', lineHeight: 17 },
  tipsCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 16, gap: 10,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  tipsTitle: { fontSize: 13, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  tipRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 8 },
  tipDot: { width: 5, height: 5, borderRadius: 3, backgroundColor: '#2563EB', marginTop: 6 },
  tipText: { flex: 1, fontSize: 12, color: '#666', lineHeight: 17 },
  footer: { paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)' },
  footerBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  footerBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  errorBox: { backgroundColor: '#FEF2F2', borderRadius: 12, padding: 12, margin: 16 },
  errorText: { color: '#DC2626', fontSize: 13, fontWeight: '500' },
})
