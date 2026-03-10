import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'

export default function InvoicesScreen() {
  const insets = useSafeAreaInsets()
  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Facturas</Text>
        <View style={{ width: 40 }} />
      </View>
      <View style={styles.empty}>
        <Text style={styles.emptyIcon}>🧾</Text>
        <Text style={styles.emptyTitle}>Sin facturas aún</Text>
        <Text style={styles.emptyDesc}>Tus facturas aparecerán aquí una vez completes tu primer pago.</Text>
        <TouchableOpacity style={styles.btn} onPress={() => router.push('/(app)/jobs')}>
          <Text style={styles.btnText}>Ver jobs disponibles</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 16 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 6, elevation: 2 },
  title: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 40, gap: 14 },
  emptyIcon: { fontSize: 56 },
  emptyTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  emptyDesc: { fontSize: 14, color: '#9CA3AF', textAlign: 'center', lineHeight: 22 },
  btn: { backgroundColor: '#2563EB', borderRadius: 14, paddingHorizontal: 28, paddingVertical: 14, marginTop: 8 },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
})
