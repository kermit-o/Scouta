import { useTranslation } from 'react-i18next'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'

const FEATURES = [
  { icon: '🔒', title: 'Pago seguro', desc: 'Tu dinero queda retenido hasta que confirmas que el trabajo está bien hecho.' },
  { icon: '✅', title: 'Pros verificados', desc: 'Todos los profesionales pasan por verificación de identidad y antecedentes.' },
  { icon: '⭐', title: 'Sistema de valoraciones', desc: 'Lee reseñas reales de otros clientes antes de contratar.' },
  { icon: '🛡️', title: 'Protección al cliente', desc: 'Si el trabajo no cumple lo acordado, te devolvemos el dinero.' },
  { icon: '💬', title: 'Soporte 24/7', desc: 'Nuestro equipo está disponible para resolver cualquier disputa.' },
  { icon: '📄', title: 'Contrato digital', desc: 'Cada job genera un contrato digital con los términos acordados.' },
]

export default function GuaranteeScreen() {
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>{t('guarantee.title')}</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.heroCard}>
          <Text style={styles.heroIcon}>🛡️</Text>
          <Text style={styles.heroTitle}>{t('guarantee.heroTitle')}</Text>
          <Text style={styles.heroDesc}>{t('guarantee.heroDesc')}</Text>
        </View>
        <View style={styles.card}>
          {FEATURES.map((f, i) => (
            <View key={i} style={[styles.row, i < FEATURES.length - 1 && styles.rowBorder]}>
              <Text style={styles.rowIcon}>{f.icon}</Text>
              <View style={styles.rowInfo}>
                <Text style={styles.rowTitle}>{f.title}</Text>
                <Text style={styles.rowDesc}>{f.desc}</Text>
              </View>
            </View>
          ))}
        </View>
        <TouchableOpacity style={styles.helpBtn} onPress={() => router.push('/(app)/help')}>
          <Text style={styles.helpBtnText}>¿Tienes dudas? Contáctanos</Text>
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
  container: { padding: 20, gap: 16 },
  heroCard: { backgroundColor: '#1a1a2e', borderRadius: 20, padding: 28, alignItems: 'center', gap: 12 },
  heroIcon: { fontSize: 48 },
  heroTitle: { fontSize: 20, fontWeight: '800', color: '#fff', textAlign: 'center' },
  heroDesc: { fontSize: 14, color: 'rgba(255,255,255,0.6)', textAlign: 'center', lineHeight: 22 },
  card: { backgroundColor: '#fff', borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  row: { flexDirection: 'row', alignItems: 'flex-start', padding: 16, gap: 14 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  rowIcon: { fontSize: 22, width: 32, textAlign: 'center', marginTop: 2 },
  rowInfo: { flex: 1 },
  rowTitle: { fontSize: 14, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  rowDesc: { fontSize: 13, color: '#6B7280', lineHeight: 20 },
  helpBtn: { backgroundColor: '#EEF4FF', borderRadius: 14, padding: 16, alignItems: 'center' },
  helpBtnText: { color: '#2563EB', fontSize: 14, fontWeight: '700' },
})
