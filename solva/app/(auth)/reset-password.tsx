import { useState, useEffect } from 'react'
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useTranslation } from 'react-i18next'

export default function ResetPasswordScreen() {
  const { t } = useTranslation()
  const insets = useSafeAreaInsets()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(true)
  const [msg, setMsg] = useState('')
  const [showPwd, setShowPwd] = useState(false)

  useEffect(() => {
    // El callback ya seteó la sesión — solo verificamos que existe
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session) setChecking(false)
      else {
        setChecking(false)
        setMsg('expired')
      }
    })
  }, [])

  async function handleReset() {
    if (password !== confirm) { setMsg('no_match'); return }
    if (password.length < 8) { setMsg('too_short'); return }
    setLoading(true)
    const { error } = await supabase.auth.updateUser({ password })
    setLoading(false)
    if (error) setMsg('error:' + error.message)
    else {
      setMsg('success')
      await supabase.auth.signOut()
      setTimeout(() => router.replace('/(auth)/login'), 2000)
    }
  }

  const msgs: Record<string, { text: string; color: string }> = {
    expired: { text: t('resetPassword.expired'), color: '#DC2626' },
    no_match: { text: t('resetPassword.noMatch'), color: '#DC2626' },
    too_short: { text: t('resetPassword.tooShort'), color: '#DC2626' },
    success: { text: t('resetPassword.success'), color: '#059669' },
  }
  const display = msg.startsWith('error:') ? { text: msg.replace('error:', ''), color: '#DC2626' } : msgs[msg]

  return (
    <KeyboardAvoidingView style={[styles.screen, { paddingTop: insets.top + 24 }]} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.container}>
        <View style={styles.iconBox}>
          <Ionicons name="lock-closed" size={32} color="#2563EB" />
        </View>
        <Text style={styles.title}>{t('resetPassword.title')}</Text>
        <Text style={styles.sub}>{t('resetPassword.subtitle')}</Text>

        {checking && (
          <View style={styles.waitBox}>
            <ActivityIndicator color="#2563EB" />
            <Text style={styles.waitText}>{t('resetPassword.verifying')}</Text>
          </View>
        )}

        {display && (
          <View style={[styles.msgBox, { borderColor: display.color }]}>
            <Text style={[styles.msg, { color: display.color }]}>{display.text}</Text>
            {msg === 'expired' && (
              <TouchableOpacity onPress={() => router.replace('/(auth)/login')}>
                <Text style={styles.link}>{t('resetPassword.backToLogin')}</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        {!checking && msg !== 'expired' && msg !== 'success' && (
          <>
            <Text style={styles.label}>{t('security.newPassword')}</Text>
            <View style={styles.inputRow}>
              <Ionicons name="lock-closed-outline" size={18} color="#888" />
              <TextInput style={styles.input} value={password} onChangeText={setPassword} placeholder={t('auth.min8chars')} placeholderTextColor="#aaa" secureTextEntry={!showPwd} />
              <TouchableOpacity onPress={() => setShowPwd(!showPwd)}>
                <Ionicons name={showPwd ? 'eye-off-outline' : 'eye-outline'} size={18} color="#888" />
              </TouchableOpacity>
            </View>
            <Text style={styles.label}>{t('security.confirmPassword')}</Text>
            <View style={styles.inputRow}>
              <Ionicons name="lock-closed-outline" size={18} color="#888" />
              <TextInput style={styles.input} value={confirm} onChangeText={setConfirm} placeholder="Repite la contraseña" placeholderTextColor="#aaa" secureTextEntry={!showPwd} />
            </View>
            <TouchableOpacity style={[styles.btn, (!password || !confirm || loading) && styles.btnDisabled]} onPress={handleReset} disabled={!password || !confirm || loading}>
              {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>{t('resetPassword.submit')}</Text>}
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
  msgBox: { backgroundColor: '#fff', borderRadius: 12, padding: 14, borderWidth: 1, gap: 8 },
  msg: { fontSize: 13, fontWeight: '600', lineHeight: 20 },
  link: { fontSize: 13, fontWeight: '700', color: '#2563EB' },
  btn: { backgroundColor: '#2563EB', borderRadius: 16, height: 56, alignItems: 'center', justifyContent: 'center', marginTop: 16 },
  btnDisabled: { opacity: 0.45 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  waitBox: { flexDirection: 'row', alignItems: 'center', gap: 12, marginTop: 32 },
  waitText: { fontSize: 15, color: '#888' },
})
