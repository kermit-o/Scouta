import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Alert
} from 'react-native'
import { router } from 'expo-router'
import { supabase, ProAnalytics } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'
import { useSubscription } from '../../hooks/useSubscription'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CURRENCY_SYMBOL: Record<string, string> = { EUR: '€', MXN: '$', COP: '$', ARS: '$', BRL: 'R$', CLP: '$' }
const PLAN_PRICES: Record<string, Record<string, string>> = {
  ES: { pro: '14,99€/mes', company: '39,99€/mes' },
  FR: { pro: '14,99€/mes', company: '39,99€/mes' },
  MX: { pro: '$299/mes', company: '$799/mes' },
  CO: { pro: '$59.900/mes', company: '$159.900/mes' },
  AR: { pro: '$2.999/mes', company: '$7.999/mes' },
  BR: { pro: 'R$79,90/mes', company: 'R$219,90/mes' },
  CL: { pro: '$12.990/mes', company: '$34.990/mes' },
}

export default function SubscriptionScreen() {
  const { session } = useAuth()
  const { profile } = useProfile()
  const { subscription, loading: subLoading, isPro, isTrialing } = useSubscription()
  const insets = useSafeAreaInsets()
  const [analytics, setAnalytics] = useState<ProAnalytics | null>(null)
  const [upgrading, setUpgrading] = useState<string | null>(null)

  useEffect(() => {
    if (!session?.user.id) return
    supabase.from('pro_analytics').select('*').eq('user_id', session.user.id).single()
      .then(({ data }) => setAnalytics(data as ProAnalytics))
  }, [session?.user.id])

  async function handleUpgrade(plan: 'pro' | 'company') {
    setUpgrading(plan)
    const { data, error } = await supabase.functions.invoke('create-subscription', {
      body: { user_id: session!.user.id, plan, country: profile?.country ?? 'ES', email: session!.user.email }
    })
    setUpgrading(null)
    if (error) Alert.alert('Error', error.message)
    else Alert.alert('🎉 14 días gratis', `Tu prueba de Solva ${plan === 'pro' ? 'Pro' : 'Company'} ha comenzado.\n\nDespués: ${PLAN_PRICES[profile?.country ?? 'ES']?.[plan]}`, [{ text: '¡Genial!' }])
  }

  const symbol = CURRENCY_SYMBOL[profile?.currency ?? 'EUR']
  const prices = PLAN_PRICES[profile?.country ?? 'ES']
  const isProUser = profile?.role === 'pro' || profile?.role === 'company'

  if (subLoading) return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Mi plan</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>

        {/* Plan actual */}
        <View style={[s.currentPlanCard, isPro && s.currentPlanCardPro]}>
          <View style={s.currentPlanLeft}>
            <Text style={s.currentPlanIcon}>
              {subscription?.plan === 'company' ? '🏢' : subscription?.plan === 'pro' ? '⭐' : '🆓'}
            </Text>
            <View>
              <Text style={[s.currentPlanName, isPro && s.currentPlanNamePro]}>
                {subscription?.plan === 'free' ? 'Plan Gratuito' : subscription?.plan === 'pro' ? 'Solva Pro' : 'Solva Company'}
              </Text>
              {isTrialing && <Text style={s.trialBadge}>✨ Prueba gratuita activa</Text>}
              {subscription?.current_period_end && isPro && (
                <Text style={[s.periodText, isPro && { color: 'rgba(255,255,255,0.6)' }]}>
                  Renueva: {new Date(subscription.current_period_end).toLocaleDateString('es-ES')}
                </Text>
              )}
            </View>
          </View>
          {isPro && (
            <View style={s.activeChip}>
              <Ionicons name="checkmark-circle" size={14} color="#fff" />
              <Text style={s.activeChipText}>Activo</Text>
            </View>
          )}
        </View>

        {/* Analytics */}
        {analytics && isProUser && (
          <>
            <Text style={s.sectionTitle}>Tus stats este mes</Text>

            <View style={s.statsGrid}>
              {[
                { value: analytics.bids_this_month, label: 'Bids enviados', icon: 'send-outline', color: '#2563EB', bg: '#EEF4FF' },
                { value: analytics.jobs_active, label: 'Jobs activos', icon: 'briefcase-outline', color: '#D97706', bg: '#FFFBEB' },
                { value: analytics.jobs_completed, label: 'Completados', icon: 'checkmark-circle-outline', color: '#059669', bg: '#F0FDF9' },
                { value: Number(analytics.avg_rating).toFixed(1), label: 'Score', icon: 'star-outline', color: '#7C3AED', bg: '#EDE9FE' },
              ].map((stat, i) => (
                <View key={i} style={[s.statCard, { backgroundColor: stat.bg }]}>
                  <Ionicons name={stat.icon as any} size={18} color={stat.color} />
                  <Text style={[s.statValue, { color: stat.color }]}>{stat.value}</Text>
                  <Text style={s.statLabel}>{stat.label}</Text>
                </View>
              ))}
            </View>

            <View style={s.earningsCard}>
              <Text style={s.earningsCardTitle}>Ganancias</Text>
              <View style={s.earningsRow}>
                <View style={s.earningsItem}>
                  <Text style={s.earningsLabel}>Este mes</Text>
                  <Text style={s.earningsValue}>{symbol}{Number(analytics.earned_this_month).toFixed(2)}</Text>
                </View>
                <View style={s.earningsDivider} />
                <View style={s.earningsItem}>
                  <Text style={s.earningsLabel}>Total ganado</Text>
                  <Text style={s.earningsValue}>{symbol}{Number(analytics.total_earned).toFixed(2)}</Text>
                </View>
              </View>
              {Number(analytics.pending_payout) > 0 && (
                <View style={s.pendingRow}>
                  <Ionicons name="time-outline" size={14} color="#D97706" />
                  <Text style={s.pendingText}>Pendiente: {symbol}{Number(analytics.pending_payout).toFixed(2)}</Text>
                </View>
              )}
            </View>

            <View style={s.bidsCard}>
              <Text style={s.bidsCardTitle}>Tasa de aceptación</Text>
              <View style={s.bidsRow}>
                {[
                  { label: 'Aceptados', value: analytics.bids_accepted, color: '#059669', bg: '#D1FAE5' },
                  { label: 'Rechazados', value: analytics.bids_rejected, color: '#DC2626', bg: '#FEE2E2' },
                  { label: 'Pendientes', value: analytics.bids_pending, color: '#D97706', bg: '#FEF3C7' },
                ].map((item, i) => (
                  <View key={i} style={[s.bidChip, { backgroundColor: item.bg }]}>
                    <Text style={[s.bidChipValue, { color: item.color }]}>{item.value}</Text>
                    <Text style={[s.bidChipLabel, { color: item.color }]}>{item.label}</Text>
                  </View>
                ))}
              </View>
              {analytics.bids_accepted + analytics.bids_rejected > 0 && (
                <View style={s.progressTrack}>
                  <View style={[s.progressFill, {
                    width: `${Math.round(analytics.bids_accepted / (analytics.bids_accepted + analytics.bids_rejected) * 100)}%` as any
                  }]} />
                </View>
              )}
            </View>
          </>
        )}

        {/* Beneficios activos */}
        {isPro && (
          <View style={s.perksCard}>
            <Text style={s.sectionTitle}>Beneficios activos</Text>
            {[
              { icon: 'infinite-outline', text: 'Bids ilimitados este mes' },
              { icon: 'star', text: 'Badge Pro en tu perfil' },
              { icon: 'analytics-outline', text: 'Analytics en tiempo real' },
              { icon: 'trending-up-outline', text: 'Prioridad en resultados de búsqueda' },
            ].map((perk, i) => (
              <View key={i} style={s.perkRow}>
                <View style={s.perkIcon}>
                  <Ionicons name={perk.icon as any} size={16} color="#059669" />
                </View>
                <Text style={s.perkText}>{perk.text}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Planes de upgrade */}
        {!isPro && (
          <>
            <View style={s.upgradeHeader}>
              <Text style={s.sectionTitle}>Actualiza tu plan</Text>
              <View style={s.trialPill}>
                <Ionicons name="gift-outline" size={13} color="#7C3AED" />
                <Text style={s.trialPillText}>14 días gratis</Text>
              </View>
            </View>

            {/* Free */}
            <View style={s.planCard}>
              <View style={s.planTop}>
                <Text style={s.planEmoji}>🆓</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.planName}>Gratuito</Text>
                  <Text style={s.planPrice}>0{symbol}/mes</Text>
                </View>
              </View>
              {[
                { text: '3 bids por mes', ok: true },
                { text: 'Perfil básico', ok: true },
                { text: 'Badge verificado', ok: false },
                { text: 'Prioridad en búsquedas', ok: false },
                { text: 'Analytics', ok: false },
              ].map((f, i) => (
                <View key={i} style={s.featureRow}>
                  <Ionicons name={f.ok ? 'checkmark-circle' : 'close-circle'} size={16} color={f.ok ? '#059669' : '#D1D5DB'} />
                  <Text style={[s.featureText, !f.ok && s.featureTextMuted]}>{f.text}</Text>
                </View>
              ))}
            </View>

            {/* Pro */}
            <View style={[s.planCard, s.planCardPro]}>
              <View style={s.popularBadge}>
                <Ionicons name="flame" size={12} color="#fff" />
                <Text style={s.popularBadgeText}>MÁS POPULAR</Text>
              </View>
              <View style={s.planTop}>
                <Text style={s.planEmoji}>⭐</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.planName}>Solva Pro</Text>
                  <Text style={s.planPrice}>{prices?.pro}</Text>
                </View>
              </View>
              {['Bids ilimitados', 'Badge ⭐ Pro verificado', 'Prioridad en búsquedas', 'Analytics completos', 'Soporte prioritario'].map((f, i) => (
                <View key={i} style={s.featureRow}>
                  <Ionicons name="checkmark-circle" size={16} color="#2563EB" />
                  <Text style={s.featureText}>{f}</Text>
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
                  : <Text style={s.upgradeBtnText}>Empezar prueba gratis</Text>
                }
              </TouchableOpacity>
            </View>

            {/* Company */}
            <View style={[s.planCard, s.planCardCompany]}>
              <View style={s.planTop}>
                <Text style={s.planEmoji}>🏢</Text>
                <View style={{ flex: 1 }}>
                  <Text style={s.planName}>Solva Company</Text>
                  <Text style={s.planPrice}>{prices?.company}</Text>
                </View>
              </View>
              {['Todo lo de Pro', 'Hasta 5 empleados', 'Dashboard empresa', 'Facturación automática', 'API access'].map((f, i) => (
                <View key={i} style={s.featureRow}>
                  <Ionicons name="checkmark-circle" size={16} color="#7C3AED" />
                  <Text style={s.featureText}>{f}</Text>
                </View>
              ))}
              <TouchableOpacity
                style={[s.upgradeBtn, s.upgradeBtnCompany, upgrading === 'company' && s.upgradeBtnDisabled]}
                onPress={() => handleUpgrade('company')}
                disabled={!!upgrading}
                activeOpacity={0.85}
              >
                {upgrading === 'company'
                  ? <ActivityIndicator color="#fff" />
                  : <Text style={s.upgradeBtnText}>Empezar prueba gratis</Text>
                }
              </TouchableOpacity>
            </View>

            <Text style={s.cancelNote}>Cancela en cualquier momento. Sin compromiso.</Text>
          </>
        )}

      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' },
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
  currentPlanCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  currentPlanCardPro: { backgroundColor: '#1a1a2e' },
  currentPlanLeft: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  currentPlanIcon: { fontSize: 32 },
  currentPlanName: { fontSize: 18, fontWeight: '800', color: '#1a1a2e' },
  currentPlanNamePro: { color: '#fff' },
  trialBadge: { fontSize: 12, color: '#F59E0B', fontWeight: '600', marginTop: 2 },
  periodText: { fontSize: 11, color: '#999', marginTop: 2 },
  activeChip: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: 'rgba(255,255,255,0.15)', borderRadius: 20,
    paddingHorizontal: 10, paddingVertical: 5,
  },
  activeChipText: { fontSize: 12, fontWeight: '700', color: '#fff' },
  sectionTitle: { fontSize: 16, fontWeight: '800', color: '#1a1a2e' },
  statsGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  statCard: {
    width: '47%', borderRadius: 16, padding: 14,
    alignItems: 'center', gap: 6,
  },
  statValue: { fontSize: 24, fontWeight: '800' },
  statLabel: { fontSize: 11, color: '#888', fontWeight: '600', textAlign: 'center' },
  earningsCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 14,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  earningsCardTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  earningsRow: { flexDirection: 'row', alignItems: 'center' },
  earningsItem: { flex: 1, alignItems: 'center', gap: 4 },
  earningsDivider: { width: 1, height: 44, backgroundColor: '#E5E7EB' },
  earningsLabel: { fontSize: 12, color: '#888', fontWeight: '600' },
  earningsValue: { fontSize: 24, fontWeight: '800', color: '#1a1a2e' },
  pendingRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  pendingText: { fontSize: 13, color: '#D97706', fontWeight: '600' },
  bidsCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18, gap: 12,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  bidsCardTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  bidsRow: { flexDirection: 'row', gap: 8 },
  bidChip: { flex: 1, borderRadius: 14, padding: 12, alignItems: 'center', gap: 3 },
  bidChipValue: { fontSize: 20, fontWeight: '800' },
  bidChipLabel: { fontSize: 10, fontWeight: '600' },
  progressTrack: { height: 8, backgroundColor: '#F3F4F6', borderRadius: 4, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: '#059669', borderRadius: 4 },
  perksCard: {
    backgroundColor: '#F0FDF9', borderRadius: 20, padding: 18, gap: 12,
    borderWidth: 1, borderColor: '#6EE7B7',
  },
  perkRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  perkIcon: {
    width: 32, height: 32, borderRadius: 8,
    backgroundColor: '#D1FAE5', alignItems: 'center', justifyContent: 'center',
  },
  perkText: { fontSize: 14, color: '#1a1a2e', fontWeight: '500' },
  upgradeHeader: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  trialPill: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    backgroundColor: '#EDE9FE', borderRadius: 20,
    paddingHorizontal: 10, paddingVertical: 4,
  },
  trialPillText: { fontSize: 12, fontWeight: '700', color: '#7C3AED' },
  planCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 10,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  planCardPro: { borderColor: '#2563EB', borderWidth: 2 },
  planCardCompany: { borderColor: '#7C3AED', borderWidth: 2 },
  popularBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    backgroundColor: '#2563EB', borderRadius: 20,
    paddingHorizontal: 10, paddingVertical: 4, alignSelf: 'flex-start',
  },
  popularBadgeText: { color: '#fff', fontSize: 10, fontWeight: '800' },
  planTop: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  planEmoji: { fontSize: 28 },
  planName: { fontSize: 18, fontWeight: '800', color: '#1a1a2e' },
  planPrice: { fontSize: 14, color: '#888', fontWeight: '600', marginTop: 2 },
  featureRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  featureText: { fontSize: 14, color: '#1a1a2e' },
  featureTextMuted: { color: '#C0C0C0' },
  upgradeBtn: {
    backgroundColor: '#2563EB', borderRadius: 14, height: 52,
    alignItems: 'center', justifyContent: 'center', marginTop: 4,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25, shadowRadius: 10, elevation: 4,
  },
  upgradeBtnCompany: { backgroundColor: '#7C3AED', shadowColor: '#7C3AED' },
  upgradeBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  upgradeBtnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  cancelNote: { fontSize: 12, color: '#aaa', textAlign: 'center', paddingBottom: 8 },
})
