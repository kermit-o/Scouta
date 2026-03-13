import { useTranslation } from 'react-i18next'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useState } from 'react'

const FAQS = [
  { q: '¿Cómo publico un job?', a: 'Ve a la pestaña Jobs → pulsa el botón "+" → rellena el formulario con el título, descripción, categoría y presupuesto. Tu job estará visible para todos los profesionales de tu zona.' },
  { q: '¿Cómo funciona el pago?', a: 'El pago queda retenido en Solva hasta que confirmas que el trabajo se ha completado. Solo entonces se libera al profesional. Esto protege a ambas partes.' },
  { q: '¿Cómo verifico mi identidad (KYC)?', a: 'Ve al menú → Verificación KYC → sube una foto de tu documento de identidad. El proceso tarda entre 24 y 48 horas. Los usuarios verificados generan más confianza.' },
  { q: '¿Qué es la suscripción Pro?', a: 'La suscripción Pro desbloquea funciones avanzadas como prioridad en búsquedas, estadísticas detalladas, y sin comisiones adicionales. Puedes gestionarla desde el menú → Mi Suscripción.' },
  { q: '¿Cómo abro una disputa?', a: 'Si tienes un problema con un job, ve al job correspondiente → Disputa → describe el problema. Nuestro equipo revisará el caso en un máximo de 48 horas.' },
  { q: '¿Puedo cancelar un job?', a: 'Puedes cancelar un job antes de que sea aceptado por un profesional sin coste. Una vez aceptado, puede aplicarse una penalización según los términos del contrato.' },
]

export default function HelpScreen() {
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  const [open, setOpen] = useState<number | null>(null)

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>{t('help.title')}</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.contactCard}>
          <Text style={styles.contactTitle}>¿Necesitas ayuda?</Text>
          <Text style={styles.contactDesc}>{t('help.contactDesc')}</Text>
          <TouchableOpacity style={styles.contactBtn} onPress={() => router.push('/(app)/messages')}>
            <Ionicons name="chatbubble-outline" size={18} color="#fff" />
            <Text style={styles.contactBtnText}>{t('help.chat')}</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.faqTitle}>{t('help.faq')}</Text>
        <View style={styles.card}>
          {FAQS.map((faq, i) => (
            <TouchableOpacity
              key={i}
              style={[styles.faqRow, i < FAQS.length - 1 && styles.rowBorder]}
              onPress={() => setOpen(open === i ? null : i)}
              activeOpacity={0.7}
            >
              <View style={styles.faqHeader}>
                <Text style={styles.faqQ}>{faq.q}</Text>
                <Ionicons name={open === i ? 'chevron-up' : 'chevron-down'} size={18} color="#9CA3AF" />
              </View>
              {open === i && <Text style={styles.faqA}>{faq.a}</Text>}
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity style={styles.emailBtn} onPress={() => {}}>
          <Ionicons name="mail-outline" size={18} color="#2563EB" />
          <Text style={styles.emailBtnText}>soporte@solva.app</Text>
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
  contactCard: { backgroundColor: '#1a1a2e', borderRadius: 20, padding: 24, gap: 10 },
  contactTitle: { fontSize: 18, fontWeight: '800', color: '#fff' },
  contactDesc: { fontSize: 13, color: 'rgba(255,255,255,0.6)' },
  contactBtn: { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: '#2563EB', borderRadius: 12, paddingHorizontal: 20, paddingVertical: 12, alignSelf: 'flex-start', marginTop: 4 },
  contactBtnText: { color: '#fff', fontSize: 14, fontWeight: '700' },
  faqTitle: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  card: { backgroundColor: '#fff', borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  faqRow: { padding: 16 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  faqHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 12 },
  faqQ: { flex: 1, fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  faqA: { fontSize: 13, color: '#6B7280', lineHeight: 20, marginTop: 10 },
  emailBtn: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, backgroundColor: '#EEF4FF', borderRadius: 14, padding: 14 },
  emailBtnText: { color: '#2563EB', fontSize: 14, fontWeight: '700' },
})
