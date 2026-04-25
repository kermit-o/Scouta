import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  ActivityIndicator, Linking, Platform
} from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'

interface Invoice {
  id: string
  invoice_number: string
  amount: number
  platform_fee: number
  pro_amount: number
  currency: string
  country: string
  job_title: string | null
  client_name: string | null
  pro_name: string | null
  pdf_url: string | null
  payment_id: string
  created_at: string
}

export default function InvoicesScreen() {
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  const { session } = useAuth()
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<string | null>(null)

  useEffect(() => {
    loadInvoices()
  }, [])

  async function loadInvoices() {
    if (!session?.user?.id) return
    const { data } = await supabase
      .from('invoices')
      .select('*')
      .eq('user_id', session.user.id)
      .order('created_at', { ascending: false })
    setInvoices((data ?? []) as Invoice[])
    setLoading(false)
  }

  async function generateInvoice(paymentId: string) {
    setGenerating(paymentId)
    const { data, error } = await supabase.functions.invoke('generate-invoice', {
      body: { payment_id: paymentId },
    })
    if (!error && data?.invoice) {
      await loadInvoices()
      if (data.invoice.pdf_url) {
        openInvoice(data.invoice.pdf_url)
      }
    }
    setGenerating(null)
  }

  function openInvoice(url: string) {
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      window.open(url, '_blank')
    } else {
      Linking.openURL(url)
    }
  }

  function formatCurrency(amount: number, currency: string): string {
    const symbol: Record<string, string> = {
      EUR: '€', GBP: '£', MXN: 'MX$', COP: 'COP$', ARS: 'AR$', BRL: 'R$', CLP: 'CLP$',
    }
    return `${symbol[currency] ?? currency} ${amount.toFixed(2)}`
  }

  if (loading) {
    return (
      <View style={[styles.screen, { paddingTop: insets.top }]}>
        <View style={styles.center}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      </View>
    )
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>{t('invoices.title')}</Text>
        <View style={{ width: 40 }} />
      </View>

      {invoices.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>🧾</Text>
          <Text style={styles.emptyTitle}>{t('invoices.empty')}</Text>
          <Text style={styles.emptyDesc}>{t('invoices.emptyDesc')}</Text>
          <TouchableOpacity style={styles.btn} onPress={() => router.push('/(app)/jobs')}>
            <Text style={styles.btnText}>{t('dashboardPro.viewJobs')}</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
          {invoices.map((inv) => (
            <TouchableOpacity
              key={inv.id}
              style={styles.card}
              onPress={() => inv.pdf_url ? openInvoice(inv.pdf_url) : generateInvoice(inv.payment_id)}
              activeOpacity={0.8}
            >
              <View style={styles.cardLeft}>
                <View style={styles.cardIcon}>
                  <Ionicons name="document-text-outline" size={20} color="#2563EB" />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.cardTitle} numberOfLines={1}>
                    {inv.job_title ?? inv.invoice_number}
                  </Text>
                  <Text style={styles.cardSub}>{inv.invoice_number}</Text>
                  <Text style={styles.cardDate}>
                    {new Date(inv.created_at).toLocaleDateString()}
                  </Text>
                </View>
              </View>
              <View style={styles.cardRight}>
                <Text style={styles.cardAmount}>{formatCurrency(inv.amount, inv.currency)}</Text>
                {generating === inv.payment_id ? (
                  <ActivityIndicator size="small" color="#2563EB" />
                ) : (
                  <Ionicons
                    name={inv.pdf_url ? 'download-outline' : 'refresh-outline'}
                    size={18}
                    color="#2563EB"
                  />
                )}
              </View>
            </TouchableOpacity>
          ))}
        </ScrollView>
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 16,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06, shadowRadius: 6, elevation: 2,
  },
  title: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40, gap: 14 },
  emptyIcon: { fontSize: 56 },
  emptyTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  emptyDesc: { fontSize: 14, color: '#9CA3AF', textAlign: 'center', lineHeight: 22 },
  btn: { backgroundColor: '#2563EB', borderRadius: 14, paddingHorizontal: 28, paddingVertical: 14, marginTop: 8 },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  list: { paddingHorizontal: 20, paddingBottom: 40, gap: 10 },
  card: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: '#fff', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  cardLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  cardIcon: {
    width: 44, height: 44, borderRadius: 12,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },
  cardTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e' },
  cardSub: { fontSize: 11, color: '#888', marginTop: 2 },
  cardDate: { fontSize: 11, color: '#aaa', marginTop: 1 },
  cardRight: { alignItems: 'flex-end', gap: 6 },
  cardAmount: { fontSize: 16, fontWeight: '800', color: '#1a1a2e' },
})
