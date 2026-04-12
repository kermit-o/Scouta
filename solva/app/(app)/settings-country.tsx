import { useTranslation } from 'react-i18next'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useState } from 'react'
import { useProfile } from '../../hooks/useProfile'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'

const COUNTRIES = [
  { code: 'ES', flag: '🇪🇸', name: 'España', currency: 'EUR', language: 'es' },
  { code: 'FR', flag: '🇫🇷', name: 'France', currency: 'EUR', language: 'fr' },
  { code: 'BE', flag: '🇧🇪', name: 'Belgique', currency: 'EUR', language: 'fr' },
  { code: 'NL', flag: '🇳🇱', name: 'Nederland', currency: 'EUR', language: 'nl' },
  { code: 'DE', flag: '🇩🇪', name: 'Deutschland', currency: 'EUR', language: 'de' },
  { code: 'PT', flag: '🇵🇹', name: 'Portugal', currency: 'EUR', language: 'pt' },
  { code: 'IT', flag: '🇮🇹', name: 'Italia', currency: 'EUR', language: 'it' },
  { code: 'GB', flag: '🇬🇧', name: 'United Kingdom', currency: 'GBP', language: 'en' },
  { code: 'MX', flag: '🇲🇽', name: 'México', currency: 'MXN', language: 'es' },
  { code: 'CO', flag: '🇨🇴', name: 'Colombia', currency: 'COP', language: 'es' },
  { code: 'AR', flag: '🇦🇷', name: 'Argentina', currency: 'ARS', language: 'es' },
  { code: 'CL', flag: '🇨🇱', name: 'Chile', currency: 'CLP', language: 'es' },
  { code: 'BR', flag: '🇧🇷', name: 'Brasil', currency: 'BRL', language: 'pt' },
]

export default function CountryScreen() {
  const insets = useSafeAreaInsets()
  const { profile, refreshProfile } = useProfile()
  const { session } = useAuth()
  const { t } = useTranslation()
  const [saving, setSaving] = useState(false)
  const [selected, setSelected] = useState(profile?.country || 'ES')

  async function save(code: string, currency: string, language: string) {
    if (!session?.user?.id) return
    setSaving(true)
    setSelected(code)
    await supabase.from('users').update({ country: code, currency, language }).eq('id', session.user.id)
    await refreshProfile()
    setSaving(false)
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>{t('settingsCountry.title')}</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.hint}>{t('settingsCountry.hint')}</Text>
        <View style={styles.card}>
          {COUNTRIES.map((c, i) => (
            <TouchableOpacity
              key={c.code}
              style={[styles.row, i < COUNTRIES.length - 1 && styles.rowBorder, selected === c.code && styles.rowSelected]}
              onPress={() => save(c.code, c.currency, c.language)}
              activeOpacity={0.7}
              disabled={saving}
            >
              <Text style={styles.flag}>{c.flag}</Text>
              <View style={styles.rowInfo}>
                <Text style={styles.rowName}>{c.name}</Text>
                <Text style={styles.rowCurrency}>{c.currency}</Text>
              </View>
              {selected === c.code && <Ionicons name="checkmark-circle" size={22} color="#2563EB" />}
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 16 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  title: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  container: { padding: 20 },
  hint: { fontSize: 14, color: '#9CA3AF', marginBottom: 16 },
  card: { backgroundColor: '#fff', borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  row: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 14 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  rowSelected: { backgroundColor: '#EEF4FF' },
  flag: { fontSize: 28 },
  rowInfo: { flex: 1 },
  rowName: { fontSize: 15, fontWeight: '600', color: '#1a1a2e' },
  rowCurrency: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
})
