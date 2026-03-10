import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Switch
} from 'react-native'
import { router } from 'expo-router'
import { supabase, ProAnalytics } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'
import { useSubscription } from '../../hooks/useSubscription'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const PRICES: Record<string, { pro: string; company: string }> = {
  ES: { pro: '14,99€/mes', company: '39,99€/mes' },
  FR: { pro: '14,99€/mes', company: '39,99€/mes' },
  BE: { pro: '14,99€/mes', company: '39,99€/mes' },
  NL: { pro: '14,99€/mes', company: '39,99€/mes' },
  DE: { pro: '14,99€/mes', company: '39,99€/mes' },
  PT: { pro: '14,99€/mes', company: '39,99€/mes' },
  IT: { pro: '14,99€/mes', company: '39,99€/mes' },
  GB: { pro: '£12.99/mo',  company: '£34.99/mo'  },
  MX: { pro: '$299/mes',   company: '$799/mes'    },
  CO: { pro: '$59.900/mes',company: '$159.900/mes'},
  AR: { pro: '$2.999/mes', company: '$7.999/mes'  },
  BR: { pro: 'R$79,90/mes',company: 'R$219,90/mes'},
  CL: { pro: '$12.990/mes',company: '$34.990/mes' },
}

const PRO_FEATURES = [
  { icon: 'flash',              color: '#2563EB', text: 'Bids ilimitados (Free: solo 3)' },
  { icon: 'trending-down',      color: '#059669', text: 'Comisión 5% (Free: 10%)' },
  { icon: 'sparkles',           color: '#7C3AED', text: 'IA genera tu descripción y SEO' },
  { icon: 'bar-chart',          color: '#D97706', text: 'Estadísticas y tasa de conversión' },
  { icon: 'images',             color: '#2563EB', text: 'Portfolio 20 fotos (Free: 3)' },
  { icon: 'ribbon',             color: '#059669', text: 'Badge Pro + posición preferente' },
  { icon: 'chatbubble-ellipses',color: '#7C3AED', text: '5 respuestas rápidas guardadas' },
  { icon: 'headset',            color: '#D97706', text: 'Soporte prioritario' },
]

const COMPANY_EXTRAS = [
  { icon: 'people',       color: '#7C3AED', text: 'Equipo de hasta 5 miembros' },
  { icon: 'document-text',color: '#059669', text: 'Facturación automática PDF' },
  { icon: 'layers',       color: '#2563EB', text: 'IA: catálogo completo de servicios' },
  { icon: 'person',       color: '#D97706', text: 'Account manager dedicado' },
]

export default function SubscriptionScreen() {
  const { session } = useAuth()
  const { profile } = useProfile()
  const { subscription, loading, isPro, isTrialing, isBusiness, trialDaysLeft, startTrial } = useSubscription()
  const insets = useSafeAreaInsets()
  const [analytics, setAnalytics] = useState<ProAnalytics | null>(null)
  const [upgrading, setUpgrading] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState('')
  const [errorMsg, setErrorMsg] = useState('')
  const [annual, setAnnual] = useState(false)

  useEffect(() => {
    if (!session?.user.id || !isPro) return
    supabase.from('pro_analytics').select('*').eq('user_id', session.user.id).single()
      .then(({ data }) => setAnalytics(data as ProAnalytics))
  }, [session?.user.id, isPro])

  async function handleUpgrade(plan: 'pro' | 'company') {
    setUpgrading(plan)
    setErrorMsg('')

    // Intentar trial primero
    const { success, error } = await startTrial(plan)
    if (success) {
      setSuccessMsg(`🎉 Trial de 14 días activado. Disfruta de Solva ${plan === 'pro' ? 'Pro' : 'Business'} sin coste.`)
      setUpgrading(null)
      return
    }

    // Si ya usó trial, ir a Stripe
    const { data, error: fnError } = await supabase.functions.invoke('create-subscription', {
      body: { user_id: session!.user.id, plan, country: profile?.country ?? 'ES', email: session!.user.email }
    })
    setUpgrading(null)
    if (fnError) {
      setErrorMsg('Error al procesar: ' + fnError.message)
    } else {
      setSuccessMsg('✅ Suscripción activada correctamente.')
    }
  }

  const prices = PRICES[profile?.country ?? 'ES'] ?? PRICES['ES']
  const isProUser = profile?.role === 'pro' || profile?.role === 'company'

  if (loading) return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Planes Solva</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>

        {/* Mensajes */}
        {errorMsg ? <View style={s.errorBox}><Text style={s.errorText}>⚠️ {errorMsg}</Text></View> : null}
        {successMsg ? <View style={s.successBox}><Text style={s.successText}>{successMsg}</Text></View> : null}

        {/* Plan actual */}
        <View style={[s.currentCard, isPro && s.currentCardPro]}>
          <View style={s.currentLeft}>
            <Text style={s.currentEmoji}>{isBusiness ? '🏢' : isPro ? '⚡' : '🆓'}</Text>
            <View>
              <Text style={[s.currentName, isPro && s.currentNamePro]}>
                {isBusiness ? 'Business' : isPro ? 'Pro' : 'Free'}
              </Text>
              {isTrialing && trialDaysLeft !== null && (
                <Text style={s.trialBadge}>⏳ {trialDaysLeft} días de trial restantes</Text>
              )}
              {isPro && !isTrialing && (
                <Text style={s.periodText}>Próxima renovación: {
                  subscription?.current_period_end
                    ? new Date(subscription.current_period_end).toLocaleDateString('es')
                    : '—'
                }</Text>
              )}
            </View>
          </View>
          {isPro && (
            <View style={s.activePill}>
              <View style={s.activeDot} />
              <Text style={s.activePillText}>Activo</Text>
            </View>
          )}
        </View>

        {/* ROI card para pros free */}
        {isProUser && !isPro && (
          <View style={s.roiCard}>
            <Ionicons name="calculator-outline" size={20} color="#059669" />
            <View style={{ flex: 1 }}>
              <Text style={s.roiTitle}>¿Cuánto te cuesta el plan Free?</Text>
              <Text style={s.roiDesc}>
                Con 10% de comisión, si facturas 500€/mes pagas 50€ a Solva.{'
'}
                Pro cuesta 14,99€ y reduce la comisión al 5% → pagas solo 25€.{'
'}
                <Text style={s.roiBold}>Ahorro neto: 10,01€/mes desde el primer mes.</Text>
              </Text>
            </View>
          </View>
        )}

        {/* Stats si es Pro */}
        {isPro && analytics && (
          <View style={s.statsCard}>
            <Text style={s.statsTitle}>Tu rendimiento este mes</Text>
            <View style={s.statsRow}>
              {[
                { value: analytics.bids_this_month, label: 'Bids enviados', color: '#2563EB' },
                { value: analytics.jobs_active,     label: 'Contratos activos', color: '#059669' },
                { value: `${analytics.earned_this_month}€`, label: 'Ingresos', color: '#D97706' },
              ].map((stat, i) => (
                <View key={i} style={s.statItem}>
                  <Text style={[s.statValue, { color: stat.color }]}>{stat.value}</Text>
                  <Text style={s.statLabel}>{stat.label}</Text>
                </View>
              ))}
            </View>
          </View>
        )}

        {/* Toggle anual/mensual */}
        {!isPro && (
          <View style={s.toggleRow}>
            <Text style={[s.toggleLabel, !annual && s.toggleActive]}>Mensual</Text>
            <Switch
              value={annual}
              onValueChange={setAnnual}
              trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
              thumbColor={annual ? '#2563EB' : '#9CA3AF'}
            />
            <Text style={[s.toggleLabel, annual && s.toggleActive]}>Anual</Text>
            {annual && <View style={s.savePill}><Text style={s.savePillText}>-20%</Text></View>}
          </View>
        )}

        {/* Cards de planes */}
        {!isPro && (
          <>
            {/* PRO */}
            <View style={s.planCard}>
              <View style={s.popularBadge}>
                <Ionicons name="star" size={10} color="#fff" />
                <Text style={s.popularText}>MÁS POPULAR</Text>
              </View>
              <View style={s.planTop}>
                <Text style={s.planEmoji}>⚡</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.planName}>Pro</Text>
                  <Text style={s.planPrice}>
                    {annual
                      ? prices.pro.replace('/mes', '/mes · facturado anual')
                      : prices.pro}
                  </Text>
                </View>
              </View>

              <View style={s.divider} />

              {PRO_FEATURES.map((f, i) => (
                <View key={i} style={s.featureRow}>
                  <View style={[s.featureIcon, { backgroundColor: f.color + '15' }]}>
                    <Ionicons name={f.icon as any} size={14} color={f.color} />
                  </View>
                  <Text style={s.featureText}>{f.text}</Text>
                </View>
              ))}

              <TouchableOpacity
                style={[s.upgradeBtn, upgrading === 'pro' && s.upgradeBtnDisabled]}
                onPress={() => handleUpgrade('pro')}
                disabled={!!upgrading}
                activeOpacity={0.85}
              >
                {upgrading === 'pro'
                  ? <ActivityIndicator color="#fff" />
                  : <>
                      <Ionicons name="sparkles" size={16} color="#fff" />
                      <Text style={s.upgradeBtnText}>Empezar 14 días gratis</Text>
                    </>
                }
              </TouchableOpacity>
              <Text style={s.noCard}>Sin tarjeta de crédito</Text>
            </View>

            {/* BUSINESS */}
            <View style={[s.planCard, s.planCardBusiness]}>
              <View style={s.planTop}>
                <Text style={s.planEmoji}>🏢</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.planName}>Business</Text>
                  <Text style={s.planPrice}>{prices.company}</Text>
                </View>
              </View>

              <View style={s.divider} />

              <Text style={s.includedLabel}>Todo lo de Pro, más:</Text>
              {COMPANY_EXTRAS.map((f, i) => (
                <View key={i} style={s.featureRow}>
                  <View style={[s.featureIcon, { backgroundColor: f.color + '15' }]}>
                    <Ionicons name={f.icon as any} size={14} color={f.color} />
                  </View>
                  <Text style={s.featureText}>{f.text}</Text>
                </View>
              ))}

              <TouchableOpacity
                style={[s.upgradeBtn, s.upgradeBtnBusiness, upgrading === 'company' && s.upgradeBtnDisabled]}
                onPress={() => handleUpgrade('company')}
                disabled={!!upgrading}
                activeOpacity={0.85}
              >
                {upgrading === 'company'
                  ? <ActivityIndicator color="#fff" />
                  : <Text style={s.upgradeBtnText}>Empezar 14 días gratis</Text>
                }
              </TouchableOpacity>
            </View>

            {/* Garantía */}
            <View style={s.guaranteeCard}>
              <Ionicons name="shield-checkmark" size={20} color="#059669" />
              <Text style={s.guaranteeText}>
                Garantía de devolución 30 días. Si no ves resultados, te devolvemos el primer mes.
              </Text>
            </View>

            <Text style={s.cancelNote}>Cancela en cualquier momento. Sin permanencia.</Text>
          </>
        )}

        {/* Si ya es Pro — opciones de gestión */}
        {isPro && (
          <View style={s.manageCard}>
            <Text style={s.manageTitle}>Gestionar suscripción</Text>
            <TouchableOpacity style={s.manageRow} onPress={() => router.push('/(app)/payments')}>
              <Ionicons name="card-outline" size={20} color="#555" />
              <Text style={s.manageText}>Ver historial de pagos</Text>
              <Ionicons name="chevron-forward" size={16} color="#ccc" />
            </TouchableOpacity>
            <TouchableOpacity style={s.manageRow} onPress={() => router.push('/(app)/invoices')}>
              <Ionicons name="document-text-outline" size={20} color="#555" />
              <Text style={s.manageText}>Facturas</Text>
              <Ionicons name="chevron-forward" size={16} color="#ccc" />
            </TouchableOpacity>
            <TouchableOpacity style={[s.manageRow, s.cancelRow]}>
              <Ionicons name="pause-circle-outline" size={20} color="#DC2626" />
              <Text style={s.cancelRowText}>Pausar o cancelar suscripción</Text>
              <Ionicons name="chevron-forward" size={16} color="#FECACA" />
            </TouchableOpacity>
          </View>
        )}

      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  scroll: { flex: 1 },
  content: { paddingHorizontal: 20, paddingBottom: 40, gap: 14 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: '#E5E7EB' },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  errorBox: { backgroundColor: '#FEF2F2', borderRadius: 12, padding: 14 },
  errorText: { color: '#DC2626', fontSize: 13, fontWeight: '500' },
  successBox: { backgroundColor: '#F0FDF4', borderRadius: 12, padding: 14 },
  successText: { color: '#059669', fontSize: 13, fontWeight: '500' },
  currentCard: { backgroundColor: '#fff', borderRadius: 20, padding: 18, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', borderWidth: 1, borderColor: '#E5E7EB' },
  currentCardPro: { backgroundColor: '#1a1a2e', borderColor: '#1a1a2e' },
  currentLeft: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  currentEmoji: { fontSize: 32 },
  currentName: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  currentNamePro: { color: '#fff' },
  trialBadge: { fontSize: 12, color: '#F59E0B', fontWeight: '600', marginTop: 2 },
  periodText: { fontSize: 11, color: '#9CA3AF', marginTop: 2 },
  activePill: { flexDirection: 'row', alignItems: 'center', gap: 5, backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 5 },
  activeDot: { width: 7, height: 7, borderRadius: 4, backgroundColor: '#10B981' },
  activePillText: { fontSize: 12, fontWeight: '700', color: '#fff' },
  roiCard: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, backgroundColor: '#F0FDF4', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#BBF7D0' },
  roiTitle: { fontSize: 13, fontWeight: '700', color: '#1a1a2e', marginBottom: 6 },
  roiDesc: { fontSize: 12, color: '#555', lineHeight: 20 },
  roiBold: { fontWeight: '700', color: '#059669' },
  statsCard: { backgroundColor: '#fff', borderRadius: 20, padding: 18, gap: 14, borderWidth: 1, borderColor: '#E5E7EB' },
  statsTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  statsRow: { flexDirection: 'row' },
  statItem: { flex: 1, alignItems: 'center', gap: 4 },
  statValue: { fontSize: 22, fontWeight: '800' },
  statLabel: { fontSize: 11, color: '#888', textAlign: 'center' },
  toggleRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10 },
  toggleLabel: { fontSize: 14, fontWeight: '600', color: '#888' },
  toggleActive: { color: '#1a1a2e' },
  savePill: { backgroundColor: '#D1FAE5', borderRadius: 20, paddingHorizontal: 8, paddingVertical: 3 },
  savePillText: { fontSize: 11, fontWeight: '800', color: '#059669' },
  planCard: { backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 10, borderWidth: 2, borderColor: '#2563EB' },
  planCardBusiness: { borderColor: '#7C3AED' },
  popularBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, backgroundColor: '#2563EB', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4, alignSelf: 'flex-start' },
  popularText: { color: '#fff', fontSize: 9, fontWeight: '800', letterSpacing: 0.5 },
  planTop: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  planEmoji: { fontSize: 28 },
  planName: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  planPrice: { fontSize: 14, color: '#888', fontWeight: '600', marginTop: 2 },
  divider: { height: 1, backgroundColor: '#F3F4F6', marginVertical: 4 },
  includedLabel: { fontSize: 12, fontWeight: '700', color: '#888', marginBottom: 4 },
  featureRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  featureIcon: { width: 28, height: 28, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  featureText: { fontSize: 14, color: '#374151', flex: 1 },
  upgradeBtn: { backgroundColor: '#2563EB', borderRadius: 14, height: 52, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 6, shadowColor: '#2563EB', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.25, shadowRadius: 10, elevation: 4 },
  upgradeBtnBusiness: { backgroundColor: '#7C3AED', shadowColor: '#7C3AED' },
  upgradeBtnDisabled: { opacity: 0.5, shadowOpacity: 0 },
  upgradeBtnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  noCard: { fontSize: 11, color: '#aaa', textAlign: 'center' },
  guaranteeCard: { flexDirection: 'row', alignItems: 'flex-start', gap: 10, backgroundColor: '#F0FDF4', borderRadius: 14, padding: 14, borderWidth: 1, borderColor: '#BBF7D0' },
  guaranteeText: { flex: 1, fontSize: 13, color: '#374151', lineHeight: 20 },
  cancelNote: { fontSize: 12, color: '#aaa', textAlign: 'center' },
  manageCard: { backgroundColor: '#fff', borderRadius: 20, padding: 4, borderWidth: 1, borderColor: '#E5E7EB', overflow: 'hidden' },
  manageTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e', paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  manageRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingHorizontal: 16, paddingVertical: 14, borderTopWidth: 1, borderTopColor: '#F3F4F6' },
  manageText: { flex: 1, fontSize: 14, color: '#374151' },
  cancelRow: { backgroundColor: '#FFF5F5' },
  cancelRowText: { flex: 1, fontSize: 14, color: '#DC2626' },
})
