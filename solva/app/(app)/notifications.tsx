import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useState } from 'react'

const SETTINGS = [
  { key: 'new_jobs', label: 'Nuevos jobs disponibles', desc: 'Cuando hay un job nuevo cerca de ti', icon: '💼' },
  { key: 'bids', label: 'Ofertas recibidas', desc: 'Cuando alguien oferta en tu job', icon: '📩' },
  { key: 'messages', label: 'Mensajes nuevos', desc: 'Cuando recibes un mensaje', icon: '💬' },
  { key: 'contracts', label: 'Contratos y pagos', desc: 'Actualizaciones de contratos activos', icon: '📄' },
  { key: 'reviews', label: 'Nuevas valoraciones', desc: 'Cuando alguien te deja una reseña', icon: '⭐' },
  { key: 'promotions', label: 'Ofertas y promociones', desc: 'Descuentos y novedades de Solva', icon: '🎁' },
]

export default function NotificationsScreen() {
  const insets = useSafeAreaInsets()
  const [settings, setSettings] = useState<Record<string, boolean>>({
    new_jobs: true, bids: true, messages: true,
    contracts: true, reviews: true, promotions: false,
  })

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Notificaciones</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.card}>
          {SETTINGS.map((s, i) => (
            <View key={s.key} style={[styles.row, i < SETTINGS.length - 1 && styles.rowBorder]}>
              <Text style={styles.rowIcon}>{s.icon}</Text>
              <View style={styles.rowInfo}>
                <Text style={styles.rowLabel}>{s.label}</Text>
                <Text style={styles.rowDesc}>{s.desc}</Text>
              </View>
              <Switch
                value={settings[s.key]}
                onValueChange={v => setSettings(p => ({ ...p, [s.key]: v }))}
                trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
                thumbColor={settings[s.key] ? '#2563EB' : '#9CA3AF'}
              />
            </View>
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
  card: { backgroundColor: '#fff', borderRadius: 20, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  row: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  rowBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  rowIcon: { fontSize: 22, width: 32, textAlign: 'center' },
  rowInfo: { flex: 1 },
  rowLabel: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  rowDesc: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
})
