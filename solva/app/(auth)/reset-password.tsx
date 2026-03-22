import { useState, useEffect } from 'react'
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

export default function ResetPasswordScreen() {
  const insets = useSafeAreaInsets()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    // Detectar error en URL (token expirado)
    if (typeof window !== 'undefined') {
      const hash = window.location.hash
      if (hash.includes('error=access_denied') || hash.includes('otp_expired')) {
        setMsg('El enlace ha expirado. Solicita uno nuevo.')
        return
      }
    }
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') setReady(true)
    })
    return () => subscription.unsubscribe()
  }, [])

  async function handleReset() {
    if (password !== confirm) { setMsg('Las contraseñas no coinciden'); return }
    if (password.length < 6) { setMsg('Mínimo 6 caracteres'); return }
    setLoading(true)
    const { error } = await supabase.auth.updateUser({ password })
    setLoading(false)
    if (error) { setMsg('Error: ' + error.message) }
    else {
      setMsg('Contraseña actualizada correctamente')
      setTimeout(() => router.replace('/(auth)/login'), 2000)
    }
  }

  return (
    <KeyboardAvoidingView style={[styles.screen, { paddingTop: insets.top + 24 }]} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.container}>
        <View style={styles.iconBox}>
          <Ionicons name="lock-closed" size={32} color="#2563EB" />
        </View>
        <Text style={styles.title}>Nueva contraseña</Text>
        <Text style={styles.sub}>Elige una contraseña segura para tu cuenta</Text>
        {!ready && (
          <View style={styles.waitBox}>
            <ActivityIndicator color="#2563EB" />
            <Text style={styles.waitText}>Verificando enlace...</Text>
          </View>
        )}
        {ready && (
          <>
            <Text style={styles.label}>Nueva contraseña</Text>
            <View style={styles.inputRow}>
              <Ionicons name="lock-closed-outline" size={18} color="#888" />
              <TextInput style={styles.input} value={password} onChangeText={setPassword} placeholder="Mínimo 6 caracteres" placeholderTextColor="#aaa" secureTextEntry={!showPwd} />
              <TouchableOpacity onPress={() => setShowPwd(!showPwd)}>
                <Ionicons name={showPwd ? 'eye-off-outline' : 'eye-outline'} size={18} color="#888" />
              </TouchableOpacity>
            </View>
            <Text style={styles.label}>Confirmar contraseña</Text>
            <View style={styles.inputRow}>
              <Ionicons name="lock-closed-outline" size={18} color="#888" />
              <TextInput style={styles.input} value={confirm} onChangeText={setConfirm} placeholder="Repite la contraseña" placeholderTextColor="#aaa" secureTextEntry={!showPwd} />
            </View>
            {msg ? <Text style={[styles.msg, { color: msg.startsWith('Error') ? '#DC2626' : '#059669' }]}>{msg}</Text> : null}
            <TouchableOpacity style={[styles.btn, (!password || !confirm || loading) && styles.btnDisabled]} onPress={handleReset} disabled={!password || !confirm || loading}>
              {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Actualizar contraseña</Text>}
            </TouchableOpacity>
          </>
        )}
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  container: { flex: 1, paddingHorizontal: 24, gap: 8 },
  iconBox: { width: 64, height: 64, borderRadius: 20, backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center', marginBottom: 8 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a1a2e' },
  sub: { fontSize: 15, color: '#888', marginBottom: 16 },
  label: { fontSize: 12, fontWeight: '700', color: '#555', marginTop: 8 },
  inputRow: { flexDirection: 'row', alignItems: 'center', gap: 12, backgroundColor: '#fff', borderRadius: 16, paddingHorizontal: 16, borderWidth: 1, borderColor: '#E5E7EB' },
  input: { flex: 1, paddingVertical: 16, fontSize: 15, color: '#1a1a2e' },
  msg: { fontSize: 13, fontWeight: '600', marginTop: 4 },
  btn: { backgroundColor: '#2563EB', borderRadius: 16, height: 56, alignItems: 'center', justifyContent: 'center', marginTop: 16 },
  btnDisabled: { opacity: 0.45 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  waitBox: { flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 32 },
  waitText: { fontSize: 15, color: '#888' },
})
