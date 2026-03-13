import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import { View, Text, StyleSheet, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { supabase } from '../../../../lib/supabase'
import { useAuth } from '../../../../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'



export default function PaymentScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  const PAYMENT_STATUS = {
    pending:  { label: t('payments.statusPending'),  color: '#D97706', bg: '#FEF3C7', icon: 'time-outline' },
    held:     { label: t('payments.statusHeld'),     color: '#2563EB', bg: '#DBEAFE', icon: 'lock-closed' },
    released: { label: t('payments.statusReleased'), color: '#059669', bg: '#D1FAE5', icon: 'checkmark-circle' },
    refunded: { label: t('payments.statusRefunded'), color: '#DC2626', bg: '#FEE2E2', icon: 'arrow-undo' },
  }
  const [contract, setContract] = useState<any>(null)
  const [payment, setPayment] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [releasing, setReleasing] = useState(false)

  async function fetchData() {
    const { data: c } = await supabase.from('contracts').select('*').eq('job_id', id).single()
    setContract(c)
    if (c) {
      const { data: p } = await supabase.from('payments').select('*').eq('contract_id', c.id).maybeSingle()
      setPayment(p)
    }
    setLoading(false)
  }

  useEffect(() => { fetchData() }, [id])

  async function handlePay() {
    if (!contract) return
    setProcessing(true)
    try {
      const { data: fnData, error: fnError } = await supabase.functions.invoke('create-payment-intent', {
        body: { contract_id: contract.id, amount: contract.amount, currency: contract.currency, country: contract.country, client_id: contract.client_id, pro_id: contract.pro_id }
      })
      if (fnError) throw new Error(fnError.message)
      if (fnData.provider === 'mercadopago') { setErrorMsg('Pago con MercadoPago disponible próximamente.'); setProcessing(false); return }
      const stripe = await (window as any).Stripe?.(process.env.EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY)
      if (!stripe) {
        await supabase.from('payments').insert({
          contract_id: contract.id, client_id: contract.client_id, pro_id: contract.pro_id,
          amount: contract.amount, platform_fee: fnData.platform_fee, pro_amount: fnData.pro_amount,
          currency: contract.currency, country: contract.country, provider: 'stripe',
          provider_payment_id: fnData.payment_intent_id, status: 'held', held_at: new Date().toISOString(),
        })
        setSuccessMsg('✅ Pago retenido en escrow correctamente (modo test).')
        fetchData(); setProcessing(false); return
      }
      const { error } = await stripe.confirmPayment(fnData.client_secret, { payment_method: { type: 'card' } })
      if (error) throw new Error(error.message)
      await supabase.from('payments').insert({
        contract_id: contract.id, client_id: contract.client_id, pro_id: contract.pro_id,
        amount: contract.amount, platform_fee: fnData.platform_fee, pro_amount: fnData.pro_amount,
        currency: contract.currency, country: contract.country, provider: 'stripe',
        provider_payment_id: fnData.payment_intent_id, status: 'held', held_at: new Date().toISOString(),
      })
      fetchData()
    } catch (err: any) { setErrorMsg(err.message) }
    finally { setProcessing(false) }
  }

  async function handleRelease() {
    if (!payment || !contract) return
    if (!window.confirm('¿Confirmas que el trabajo está completado?')) return
    setReleasing(true)
    const { error } = await supabase.functions.invoke('release-payment', {
      body: { paymentId: payment.id, contractId: contract.id }
    })
    setReleasing(false)
    if (error) { setErrorMsg(error.message); return }
    setSuccessMsg('✅ Pago liberado. El profesional ha recibido su pago.')
    setTimeout(() => router.replace('/(app)/jobs'), 1500)
  }

  if (loading) return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>
  if (!contract) return <View style={s.center}><Ionicons name="card-outline" size={48} color="#ccc" /><Text style={s.notFound}>Contrato no encontrado</Text></View>

  const isClient = contract.client_id === session?.user.id
  const platformFee = contract.amount * 0.1
  const proAmount = contract.amount * 0.9
  const payStatus = payment ? (PAYMENT_STATUS[payment.status as keyof typeof PAYMENT_STATUS] ?? PAYMENT_STATUS.pending) : null

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Pago en escrow</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>

        {/* Amount hero */}
        <View style={s.heroCard}>
          <View style={s.heroIcon}>
            <Ionicons name="shield-checkmark" size={32} color="#2563EB" />
          </View>
          <Text style={s.heroLabel}>Total del contrato</Text>
          <Text style={s.heroAmount}>{contract.amount} <Text style={s.heroCurrency}>{contract.currency}</Text></Text>

          {payStatus && (
            <View style={[s.statusBadge, { backgroundColor: payStatus.bg }]}>
              <Ionicons name={payStatus.icon as any} size={14} color={payStatus.color} />
              <Text style={[s.statusText, { color: payStatus.color }]}>{payStatus.label}</Text>
            </View>
          )}
        </View>

        {/* Breakdown */}
        <View style={s.breakdownCard}>
          <Text style={s.breakdownTitle}>Desglose del pago</Text>
          <View style={s.breakdownRow}>
            <View style={s.breakdownLeft}>
              <Ionicons name="briefcase-outline" size={16} color="#666" />
              <Text style={s.breakdownLabel}>Servicio</Text>
            </View>
            <Text style={s.breakdownValue}>{contract.amount} {contract.currency}</Text>
          </View>
          <View style={s.breakdownRow}>
            <View style={s.breakdownLeft}>
              <Ionicons name="storefront-outline" size={16} color="#666" />
              <Text style={s.breakdownLabel}>Comisión Solva (10%)</Text>
            </View>
            <Text style={s.breakdownValue}>-{platformFee.toFixed(2)} {contract.currency}</Text>
          </View>
          <View style={s.divider} />
          <View style={s.breakdownRow}>
            <View style={s.breakdownLeft}>
              <Ionicons name="person-outline" size={16} color="#059669" />
              <Text style={[s.breakdownLabel, { color: '#059669', fontWeight: '700' }]}>Pro recibe</Text>
            </View>
            <Text style={[s.breakdownValue, { color: '#059669', fontSize: 17 }]}>{proAmount.toFixed(2)} {contract.currency}</Text>
          </View>
          <View style={s.breakdownMeta}>
            <Ionicons name="location-outline" size={13} color="#aaa" />
            <Text style={s.breakdownMetaText}>{contract.country}</Text>
          </View>
        </View>

        {/* Cómo funciona el escrow */}
        {!payment && (
          <View style={s.howCard}>
            <Text style={s.howTitle}>¿Cómo funciona el escrow?</Text>
            {[
              { icon: 'lock-closed-outline', color: '#2563EB', text: 'Pagas ahora — el dinero queda retenido de forma segura' },
              { icon: 'construct-outline', color: '#D97706', text: 'El profesional realiza el trabajo acordado' },
              { icon: 'checkmark-circle-outline', color: '#059669', text: 'Confirmas la entrega y el pago se libera al Pro' },
            ].map((step, i) => (
              <View key={i} style={s.howStep}>
                <View style={[s.howStepNum, { backgroundColor: step.color + '18' }]}>
                  <Text style={[s.howStepNumText, { color: step.color }]}>{i + 1}</Text>
                </View>
                <Ionicons name={step.icon as any} size={18} color={step.color} />
                <Text style={s.howStepText}>{step.text}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Estado: en escrow */}
        {payment?.status === 'held' && (
          <View style={s.heldCard}>
            <View style={s.heldTop}>
              <Ionicons name="lock-closed" size={24} color="#2563EB" />
              <View style={{ flex: 1 }}>
                <Text style={s.heldTitle}>Pago retenido de forma segura</Text>
                <Text style={s.heldDesc}>El dinero está protegido. Libéralo cuando el trabajo esté terminado y verificado.</Text>
              </View>
            </View>
            {payment.held_at && (
              <Text style={s.heldDate}>Retenido el {new Date(payment.held_at).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })}</Text>
            )}
          </View>
        )}

        {/* Estado: liberado */}
        {payment?.status === 'released' && (
          <View style={s.releasedCard}>
            <Ionicons name="checkmark-circle" size={48} color="#059669" />
            <Text style={s.releasedTitle}>Pago completado</Text>
            <Text style={s.releasedSub}>El profesional recibió {payment.pro_amount} {payment.currency}</Text>
            <TouchableOpacity style={s.reviewHint} onPress={() => router.push(`/(app)/jobs/${id}/review`)}>
              <Ionicons name="star-outline" size={16} color="#D97706" />
              <Text style={s.reviewHintText}>Deja una reseña del trabajo</Text>
              <Ionicons name="chevron-forward" size={14} color="#D97706" />
            </TouchableOpacity>
          </View>
        )}

      </ScrollView>

      {/* Footer CTA */}
      {!payment && isClient && (
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <View style={s.escrowNote}>
            <Ionicons name="shield-outline" size={14} color="#2563EB" />
            <Text style={s.escrowNoteText}>Pago 100% seguro — solo se libera cuando confirmas</Text>
          </View>
          <TouchableOpacity
            style={[s.footerBtn, processing && s.footerBtnDisabled]}
            onPress={handlePay}
            disabled={processing}
            activeOpacity={0.85}
          >
            {processing
              ? <ActivityIndicator color="#fff" />
              : <>
                  <Ionicons name="card-outline" size={20} color="#fff" />
                  <Text style={s.footerBtnText}>Pagar {contract.amount} {contract.currency}</Text>
                </>
            }
          </TouchableOpacity>
        </View>
      )}

      {payment?.status === 'held' && isClient && (
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <TouchableOpacity
            style={[s.footerBtnGreen, releasing && s.footerBtnDisabled]}
            onPress={handleRelease}
            disabled={releasing}
            activeOpacity={0.85}
          >
            {releasing
              ? <ActivityIndicator color="#fff" />
              : <>
                  <Ionicons name="checkmark-circle-outline" size={20} color="#fff" />
                  <Text style={s.footerBtnText}>Confirmar entrega y liberar pago</Text>
                </>
            }
          </TouchableOpacity>
        </View>
      )}
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
  heroCard: {
    backgroundColor: '#fff', borderRadius: 24, padding: 24,
    alignItems: 'center', gap: 8,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06, shadowRadius: 16, elevation: 3,
  },
  heroIcon: {
    width: 72, height: 72, borderRadius: 20,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
    marginBottom: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.15, shadowRadius: 16, elevation: 3,
  },
  heroLabel: { fontSize: 13, color: '#888', fontWeight: '600' },
  heroAmount: { fontSize: 42, fontWeight: '800', color: '#1a1a2e' },
  heroCurrency: { fontSize: 22, color: '#888' },
  statusBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20, marginTop: 4,
  },
  statusText: { fontSize: 13, fontWeight: '700' },
  breakdownCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 12,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  breakdownTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  breakdownRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  breakdownLeft: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  breakdownLabel: { fontSize: 14, color: '#555' },
  breakdownValue: { fontSize: 15, fontWeight: '600', color: '#1a1a2e' },
  divider: { height: 1, backgroundColor: '#F3F4F6' },
  breakdownMeta: { flexDirection: 'row', alignItems: 'center', gap: 4, marginTop: 4 },
  breakdownMetaText: { fontSize: 12, color: '#aaa' },
  howCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 14,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  howTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  howStep: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  howStepNum: {
    width: 26, height: 26, borderRadius: 8,
    alignItems: 'center', justifyContent: 'center',
  },
  howStepNumText: { fontSize: 12, fontWeight: '800' },
  howStepText: { flex: 1, fontSize: 13, color: '#555', lineHeight: 18 },
  heldCard: {
    backgroundColor: '#EEF4FF', borderRadius: 20, padding: 18, gap: 12,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  heldTop: { flexDirection: 'row', alignItems: 'flex-start', gap: 14 },
  heldTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  heldDesc: { fontSize: 13, color: '#555', lineHeight: 18 },
  heldDate: { fontSize: 12, color: '#888' },
  releasedCard: {
    backgroundColor: '#F0FDF9', borderRadius: 20, padding: 28,
    alignItems: 'center', gap: 8,
    borderWidth: 1, borderColor: '#6EE7B7',
  },
  releasedTitle: { fontSize: 22, fontWeight: '800', color: '#1a1a2e' },
  releasedSub: { fontSize: 15, color: '#555' },
  reviewHint: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    backgroundColor: '#FFFBEB', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10,
    borderWidth: 1, borderColor: '#FDE68A', marginTop: 8,
  },
  reviewHintText: { flex: 1, fontSize: 13, fontWeight: '600', color: '#D97706' },
  footer: { paddingHorizontal: 20, paddingTop: 12, gap: 10, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)' },
  escrowNote: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
  },
  escrowNoteText: { fontSize: 12, color: '#2563EB', fontWeight: '600' },
  footerBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnGreen: {
    backgroundColor: '#059669', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#059669', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  footerBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
})
