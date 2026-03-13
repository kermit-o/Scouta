import { useTranslation } from 'react-i18next'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useState } from 'react'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'

const CATEGORIES = ['Bug / Error técnico', 'Problema con un job', 'Problema con un pago', 'Usuario inapropiado', 'Contenido inadecuado', 'Otro']

export default function ReportScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const { t } = useTranslation()
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  async function submit() {
    if (!category) { setError('Selecciona una categoría.'); return }
    if (description.trim().length < 10) { setError('Describe el problema con más detalle.'); return }
    setLoading(true)
    setError('')
    // Guardamos como mensaje al soporte
    const { error: err } = await supabase.from('messages').insert({
      sender_id: session?.user?.id,
      content: `[REPORTE - ${category}]\n${description}`,
    }).select()
    setLoading(false)
    if (err) setError('Error al enviar. Inténtalo de nuevo.')
    else setSent(true)
  }

  if (sent) return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>{t('report.title')}</Text>
        <View style={{ width: 40 }} />
      </View>
      <View style={styles.successContainer}>
        <Text style={styles.successIcon}>✅</Text>
        <Text style={styles.successTitle}>¡Reporte enviado!</Text>
        <Text style={styles.successDesc}>{t('report.successDesc')}</Text>
        <TouchableOpacity style={styles.btn} onPress={() => router.back()}>
          <Text style={styles.btnText}>{t('common.back')}</Text>
        </TouchableOpacity>
      </View>
    </View>
  )

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>{t('report.title')}</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        {error ? <View style={styles.errorBox}><Text style={styles.errorText}>⚠️ {error}</Text></View> : null}
        <Text style={styles.sectionLabel}>{t('report.category')}</Text>
        <View style={styles.categoriesGrid}>
          {CATEGORIES.map(c => (
            <TouchableOpacity
              key={c}
              style={[styles.categoryChip, category === c && styles.categoryChipSelected]}
              onPress={() => setCategory(c)}
              activeOpacity={0.7}
            >
              <Text style={[styles.categoryText, category === c && styles.categoryTextSelected]}>{c}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <Text style={styles.sectionLabel}>{t('report.description')}</Text>
        <TextInput
          style={styles.textarea}
          value={description}
          onChangeText={setDescription}
          placeholder={t("report.placeholder")}
          placeholderTextColor="#aaa"
          multiline
          numberOfLines={6}
          textAlignVertical="top"
        />
        <TouchableOpacity style={[styles.btn, loading && { opacity: 0.6 }]} onPress={submit} disabled={loading} activeOpacity={0.85}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>{t('report.submit')}</Text>}
        </TouchableOpacity>
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 16 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  title: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  container: { padding: 20, gap: 14 },
  errorBox: { backgroundColor: '#FEF2F2', borderRadius: 12, padding: 14 },
  errorText: { color: '#DC2626', fontSize: 13 },
  sectionLabel: { fontSize: 13, fontWeight: '700', color: '#555' },
  categoriesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  categoryChip: { borderRadius: 10, paddingHorizontal: 14, paddingVertical: 9, backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB' },
  categoryChipSelected: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  categoryText: { fontSize: 13, fontWeight: '500', color: '#374151' },
  categoryTextSelected: { color: '#fff' },
  textarea: { backgroundColor: '#fff', borderRadius: 16, padding: 16, fontSize: 14, color: '#1a1a2e', borderWidth: 1, borderColor: '#E5E7EB', minHeight: 140 },
  btn: { backgroundColor: '#2563EB', borderRadius: 16, height: 52, alignItems: 'center', justifyContent: 'center' },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  successContainer: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40, gap: 16 },
  successIcon: { fontSize: 56 },
  successTitle: { fontSize: 24, fontWeight: '800', color: '#1a1a2e' },
  successDesc: { fontSize: 14, color: '#9CA3AF', textAlign: 'center', lineHeight: 22 },
})
