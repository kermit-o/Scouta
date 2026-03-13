import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { getContract } from '../../../../hooks/useContract'
import { ContractTerms } from '../../../../lib/contracts/templates'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string; icon: string }> = {
  active:    { label: 'Activo',      color: '#2563EB', bg: '#DBEAFE', icon: 'flash' },
  completed: { label: 'Completado',  color: '#059669', bg: '#D1FAE5', icon: 'checkmark-circle' },
  cancelled: { label: 'Cancelado',   color: '#DC2626', bg: '#FEE2E2', icon: 'close-circle' },
  disputed:  { label: 'En disputa',  color: '#D97706', bg: '#FEF3C7', icon: 'warning' },
}

export default function ContractScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  const [contract, setContract] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    getContract(id!).then(({ data }) => {
      setContract(data)
      setLoading(false)
    })
  }, [id])

  if (loading) return (
    <View style={s.center}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  )
  if (!contract) return (
    <View style={s.center}>
      <Ionicons name="document-outline" size={48} color="#ccc" />
      <Text style={s.notFound}>{t('contract.notFound')}</Text>
    </View>
  )

  const terms: ContractTerms = contract.terms
  const statusCfg = STATUS_CONFIG[contract.status] ?? STATUS_CONFIG.active
  const serviceFee = contract.amount * ((terms.platform_fee_pct ?? 5) / 100)
  const total = contract.amount + serviceFee

  function Section({
    id: sid, icon, iconBg, iconColor, title, children
  }: {
    id: string; icon: string; iconBg: string; iconColor: string; title: string; children: React.ReactNode
  }) {
    const isOpen = expanded === sid
    return (
      <View style={s.section}>
        <TouchableOpacity
          style={s.sectionHeader}
          onPress={() => setExpanded(isOpen ? null : sid)}
          activeOpacity={0.8}
        >
          <View style={[s.sectionIcon, { backgroundColor: iconBg }]}>
            <Ionicons name={icon as any} size={18} color={iconColor} />
          </View>
          <Text style={s.sectionTitle}>{title}</Text>
          <Ionicons
            name={isOpen ? 'chevron-up' : 'chevron-down'}
            size={18} color="#aaa"
          />
        </TouchableOpacity>
        {isOpen && <View style={s.sectionBody}>{children}</View>}
      </View>
    )
  }

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>{t('contract.title')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>
        {/* Hero card */}
        <View style={s.heroCard}>
          <View style={s.heroTop}>
            <View style={s.heroIconWrap}>
              <Ionicons name="document-text" size={28} color="#2563EB" />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={s.contractId}>#{contract.id.slice(0, 8).toUpperCase()}</Text>
              <View style={[s.statusBadge, { backgroundColor: statusCfg.bg }]}>
                <Ionicons name={statusCfg.icon as any} size={13} color={statusCfg.color} />
                <Text style={[s.statusText, { color: statusCfg.color }]}>{statusCfg.label}</Text>
              </View>
            </View>
          </View>

          {/* Montos */}
          <View style={s.amountRow}>
            <View style={s.amountItem}>
              <Text style={s.amountLabel}>{t('contract.service')}</Text>
              <Text style={s.amountValue}>{contract.amount} {contract.currency}</Text>
            </View>
            <View style={s.amountDivider} />
            <View style={s.amountItem}>
              <Text style={s.amountLabel}>Comisión ({terms.platform_fee_pct}%)</Text>
              <Text style={s.amountValue}>{serviceFee.toFixed(2)} {contract.currency}</Text>
            </View>
            <View style={s.amountDivider} />
            <View style={s.amountItem}>
              <Text style={s.amountLabel}>{t('contract.total')}</Text>
              <Text style={[s.amountValue, s.amountTotal]}>{total.toFixed(2)} {contract.currency}</Text>
            </View>
          </View>

          {/* Plazo y fecha */}
          <View style={s.metaRow}>
            {contract.delivery_days && (
              <View style={s.metaChip}>
                <Ionicons name="time-outline" size={14} color="#666" />
                <Text style={s.metaChipText}>{contract.delivery_days} días</Text>
              </View>
            )}
            {contract.due_date && (
              <View style={s.metaChip}>
                <Ionicons name="calendar-outline" size={14} color="#666" />
                <Text style={s.metaChipText}>
                  {new Date(contract.due_date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}
                </Text>
              </View>
            )}
            <View style={s.metaChip}>
              <Ionicons name="flag-outline" size={14} color="#666" />
              <Text style={s.metaChipText}>{terms.jurisdiction}</Text>
            </View>
          </View>
        </View>

        {/* Garantía Solva */}
        <View style={s.guaranteeCard}>
          <Ionicons name="shield-checkmark" size={22} color="#059669" />
          <View style={{ flex: 1 }}>
            <Text style={s.guaranteeTitle}>{t('contract.guarantee')}</Text>
            <Text style={s.guaranteeDesc}>
              Tienes {terms.warranty_days} días para reportar problemas tras la entrega. Sin coste adicional.
            </Text>
          </View>
        </View>

        {/* Secciones colapsables */}
        <Section id="legal" icon="gavel" iconBg="#EDE9FE" iconColor="#7C3AED" title={t('contract.legal')}>
          <Text style={s.legalText}>{terms.law}</Text>
        </Section>

        <Section id="payment" icon="lock-closed" iconBg="#DBEAFE" iconColor="#2563EB" title={t('contract.paymentProtection')}>
          <Text style={s.legalText}>{terms.payment_protection}</Text>
        </Section>

        <Section id="cancel" icon="close-circle-outline" iconBg="#FEE2E2" iconColor="#DC2626" title={t('contract.cancellation')}>
          <Text style={s.legalText}>{terms.cancellation_policy}</Text>
        </Section>

        <Section id="dispute" icon="people-outline" iconBg="#FEF3C7" iconColor="#D97706" title="Resolución de disputas">
          <Text style={s.legalText}>{terms.dispute_resolution}</Text>
        </Section>

        {/* Rol de plataforma */}
        <Section id="platform" icon="globe-outline" iconBg="#EEF4FF" iconColor="#2563EB" title="Rol de Solva como intermediaria">
          <Text style={s.legalText}>{terms.platform_role}</Text>
        </Section>

        {/* Profesional independiente */}
        <Section id="contractor" icon="person-outline" iconBg="#F0FDF4" iconColor="#059669" title="Profesional independiente">
          <Text style={s.legalText}>{terms.independent_contractor}</Text>
        </Section>

        {/* Condiciones escrow */}
        <Section id="escrow" icon="lock-closed-outline" iconBg="#FFFBEB" iconColor="#D97706" title="Condiciones del escrow">
          <Text style={s.legalText}>{terms.escrow_conditions}</Text>
        </Section>

        {/* Confidencialidad domicilio */}
        <Section id="confidentiality" icon="home-outline" iconBg="#FFF1F2" iconColor="#E11D48" title="Confidencialidad del domicilio">
          <Text style={s.legalText}>{terms.home_access_confidentiality}</Text>
        </Section>

        {/* Tratamiento de datos */}
        <Section id="data" icon="shield-outline" iconBg="#F5F3FF" iconColor="#7C3AED" title="Tratamiento de datos personales">
          <Text style={s.legalText}>{terms.data_processing}</Text>
        </Section>

        {/* Límite de responsabilidad */}
        <Section id="liability" icon="warning-outline" iconBg="#FEF3C7" iconColor="#D97706" title="Límite de responsabilidad">
          <Text style={s.legalText}>{terms.liability_limit}</Text>
        </Section>

        {/* B2B — solo si existe */}
        {terms.b2b_clause ? (
          <Section id="b2b" icon="business-outline" iconBg="#F3F4F6" iconColor="#374151" title="Condiciones B2B (empresas)">
            <Text style={s.legalText}>{terms.b2b_clause}</Text>
          </Section>
        ) : null}

        {/* Disclaimer */}
        <View style={s.disclaimer}>
          <Ionicons name="warning-outline" size={16} color="#856404" />
          <Text style={s.disclaimerText}>
            Contrato generado automáticamente como placeholder. Los términos finales deben ser revisados por un abogado habilitado en {terms.jurisdiction}.
          </Text>
        </View>
      </ScrollView>

      {/* Acciones */}
      {contract.status === 'active' && (
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          <TouchableOpacity
            style={s.footerBtn}
            onPress={() => router.push(`/(app)/jobs/${id}/payment`)}
            activeOpacity={0.85}
          >
            <Ionicons name="card-outline" size={20} color="#fff" />
            <Text style={s.footerBtnText}>Gestionar pago escrow</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={s.outlineBtn}
            onPress={() => router.push(`/(app)/jobs/${id}/dispute`)}
            activeOpacity={0.85}
          >
            <Ionicons name="warning-outline" size={18} color="#DC2626" />
            <Text style={s.outlineBtnText}>Abrir disputa</Text>
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
  content: { paddingHorizontal: 20, paddingBottom: 24, gap: 12 },

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
    backgroundColor: '#fff', borderRadius: 20, padding: 20, gap: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06, shadowRadius: 16, elevation: 3,
  },
  heroTop: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  heroIconWrap: {
    width: 56, height: 56, borderRadius: 16,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },
  contractId: { fontSize: 12, color: '#888', fontFamily: 'monospace', marginBottom: 6 },
  statusBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    paddingHorizontal: 10, paddingVertical: 4, borderRadius: 20, alignSelf: 'flex-start',
  },
  statusText: { fontSize: 12, fontWeight: '700' },

  amountRow: {
    flexDirection: 'row', backgroundColor: '#F6F7FB', borderRadius: 14, padding: 14,
  },
  amountItem: { flex: 1, alignItems: 'center', gap: 4 },
  amountDivider: { width: 1, backgroundColor: '#E5E7EB' },
  amountLabel: { fontSize: 11, color: '#888', fontWeight: '600', textAlign: 'center' },
  amountValue: { fontSize: 14, fontWeight: '700', color: '#1a1a2e', textAlign: 'center' },
  amountTotal: { color: '#2563EB', fontSize: 15 },

  metaRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  metaChip: {
    flexDirection: 'row', alignItems: 'center', gap: 5,
    backgroundColor: '#F3F4F6', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 5,
  },
  metaChipText: { fontSize: 12, color: '#555', fontWeight: '500' },

  guaranteeCard: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 12,
    backgroundColor: '#F0FDF9', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: '#6EE7B7',
  },
  guaranteeTitle: { fontSize: 14, fontWeight: '700', color: '#059669', marginBottom: 3 },
  guaranteeDesc: { fontSize: 12, color: '#555', lineHeight: 17 },

  section: {
    backgroundColor: '#fff', borderRadius: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)', overflow: 'hidden',
  },
  sectionHeader: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    padding: 16,
  },
  sectionIcon: {
    width: 36, height: 36, borderRadius: 10,
    alignItems: 'center', justifyContent: 'center',
  },
  sectionTitle: { flex: 1, fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  sectionBody: {
    paddingHorizontal: 16, paddingBottom: 16, paddingTop: 4,
    borderTopWidth: 1, borderTopColor: '#F3F4F6',
  },
  legalText: { fontSize: 13, color: '#555', lineHeight: 20 },

  disclaimer: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 10,
    backgroundColor: '#FFFBEB', borderRadius: 14, padding: 14,
    borderWidth: 1, borderColor: '#FDE68A',
  },
  disclaimerText: { flex: 1, fontSize: 12, color: '#856404', lineHeight: 18 },

  footer: { paddingHorizontal: 20, paddingTop: 12, gap: 10, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)' },
  footerBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  outlineBtn: {
    borderRadius: 16, height: 48, flexDirection: 'row',
    alignItems: 'center', justifyContent: 'center', gap: 8,
    borderWidth: 1.5, borderColor: '#FECACA', backgroundColor: '#FEF2F2',
  },
  outlineBtnText: { fontSize: 15, fontWeight: '600', color: '#DC2626' },
})