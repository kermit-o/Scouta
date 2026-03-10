import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'
import { useState } from 'react'
import { supabase } from '../../lib/supabase'

export default function SecurityScreen() {
  const insets = useSafeAreaInsets()
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showNew, setShowNew] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState<{ text: string; ok: boolean } | null>(null)

  async function changePassword() {
    if (newPassword.length < 8) { setMsg({ text: 'La contraseña debe tener al menos 8 caracteres.', ok: false }); return }
    if (newPassword !== confirmPassword) { setMsg({ text: 'Las contraseñas no coinciden.', ok: false }); return }
    setLoading(true)
    const { error } = await supabase.auth.updateUser({ password: newPassword })
    setLoading(false)
    if (error) setMsg({ text: 'Error al cambiar contraseña. Inténtalo de nuevo.', ok: false })
    else { setMsg({ text: '✅ Contraseña actualizada correctamente.', ok: true }); setNewPassword(''); setConfirmPassword('') }
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={styles.title}>Seguridad</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Cambiar contraseña</Text>
          {msg && <View style={[styles.msgBox, { backgroundColor: msg.ok ? '#F0FDF4' : '#FEF2F2' }]}>
            <Text style={{ color: msg.ok ? '#16A34A' : '#DC2626', fontSize: 13 }}>{msg.text}</Text>
          </View>}
          <Text style={styles.label}>Nueva contraseña</Text>
          <View style={styles.inputRow}>
            <Ionicons name="lock-closed-outline" size={18} color="#888" />
            <TextInput style={styles.input} value={newPassword} onChangeText={setNewPassword} secureTextEntry={!showNew} placeholder="Mínimo 8 caracteres" placeholderTextColor="#aaa" />
            <TouchableOpacity onPress={() => setShowNew(!showNew)}>
              <Ionicons name={showNew ? 'eye-off-outline' : 'eye-outline'} size={18} color="#888" />
            </TouchableOpacity>
          </View>
          <Text style={styles.label}>Confirmar contraseña</Text>
          <View style={styles.inputRow}>
            <Ionicons name="lock-closed-outline" size={18} color="#888" />
            <TextInput style={styles.input} value={confirmPassword} onChangeText={setConfirmPassword} secureTextEntry={!showConfirm} placeholder="Repite la contraseña" placeholderTextColor="#aaa" />
            <TouchableOpacity onPress={() => setShowConfirm(!showConfirm)}>
              <Ionicons name={showConfirm ? 'eye-off-outline' : 'eye-outline'} size={18} color="#888" />
            </TouchableOpacity>
          </View>
          <TouchableOpacity style={[styles.btn, loading && { opacity: 0.6 }]} onPress={changePassword} disabled={loading} activeOpacity={0.85}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Actualizar contraseña</Text>}
          </TouchableOpacity>
        </View>

        <View style={[styles.card, { marginTop: 16 }]}>
          <Text style={styles.sectionTitle}>Sesiones activas</Text>
          <TouchableOpacity style={styles.dangerRow} onPress={async () => { await supabase.auth.signOut({ scope: 'global' }); router.replace('/(auth)/login') }}>
            <Ionicons name="log-out-outline" size={20} color="#DC2626" />
            <Text style={styles.dangerText}>Cerrar todas las sesiones</Text>
          </TouchableOpacity>
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
  card: { backgroundColor: '#fff', borderRadius: 20, padding: 20, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 16 },
  msgBox: { borderRadius: 10, padding: 12, marginBottom: 12 },
  label: { fontSize: 13, fontWeight: '600', color: '#555', marginBottom: 8, marginTop: 8 },
  inputRow: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#F6F7FB', borderRadius: 12, paddingHorizontal: 14, borderWidth: 1, borderColor: '#E5E7EB', marginBottom: 4 },
  input: { flex: 1, paddingVertical: 14, fontSize: 14, color: '#1a1a2e' },
  btn: { backgroundColor: '#2563EB', borderRadius: 14, height: 50, alignItems: 'center', justifyContent: 'center', marginTop: 16 },
  btnText: { color: '#fff', fontSize: 15, fontWeight: '700' },
  dangerRow: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 4 },
  dangerText: { fontSize: 14, fontWeight: '600', color: '#DC2626' },
})
