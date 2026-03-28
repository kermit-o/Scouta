// v2
import { useTranslation } from 'react-i18next'
import { useState, useEffect } from 'react'
import { useLocalSearchParams } from 'expo-router'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, KeyboardAvoidingView, Modal, Platform, ScrollView
} from 'react-native'
import { Link, router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

export default function LoginScreen() {
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [resetModal, setResetModal] = useState(false)
  const [resetEmail, setResetEmail] = useState('')
  const [resetLoading, setResetLoading] = useState(false)
  const [resetMsg, setResetMsg] = useState('')

  async function handleReset() {
    if (!resetEmail.trim()) return
    setResetLoading(true)
    setResetMsg('')
    try {
      const res = await supabase.functions.invoke('reset-password', { body: { email: resetEmail.trim().toLowerCase() } })
      if (res.error) throw res.error
      setResetMsg('✅ Email enviado. Revisa tu bandeja de entrada.')
    } catch (err: any) {
      setResetMsg('❌ ' + (err.message ?? 'Error al enviar email'))
    }
    setResetLoading(false)
  }

  async function handleResendConfirmation() {
    try {
      const { error } = await supabase.auth.resend({ type: 'signup', email })
      if (error) {
        setErrorMsg('Error al reenviar: ' + error.message)
      } else {
        setSuccessMsg('✅ Email de confirmación reenviado. Revisa tu bandeja de entrada.')
        setShowResend(false)
      }
    } catch (e: any) {
      setErrorMsg('Error inesperado: ' + e.message)
    }
  }

  async function handleLogin() {
    if (!email || !password) { setErrorMsg('Completa todos los campos'); return }
    setLoading(true)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    setLoading(false)
    if (error) {
      const msg = error.message.toLowerCase()
      if (msg.includes('invalid login') || msg.includes('invalid credentials') || msg.includes('wrong password'))
        setErrorMsg('Email o contraseña incorrectos. Inténtalo de nuevo.')
      else if (msg.includes('email not confirmed')) {
        setErrorMsg('Confirma tu email antes de iniciar sesión.')
        setShowResend(true)
      }
      else if (msg.includes('too many') || msg.includes('rate limit'))
        setErrorMsg('Demasiados intentos. Espera unos minutos.')
      else if (msg.includes('user not found') || msg.includes('no user'))
        setErrorMsg(t('auth.noAccount'))
      else
        setErrorMsg('Algo salió mal. Inténtalo de nuevo.')
    }
    else router.replace('/(app)')
  }

  async function handleOAuth(provider: 'google' | 'apple') {
    const redirectTo = typeof window !== 'undefined'
      ? window.location.origin + '/auth/callback'
      : 'https://www.getsolva.co/auth/callback'
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: { redirectTo }
    })
    if (error) setErrorMsg('Error al conectar con ' + provider + '. Inténtalo de nuevo.')
  }

  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')
  const [showResend, setShowResend] = useState(false)
  const params = useLocalSearchParams()
  useEffect(() => {
    if (params.msg === 'confirm_email') {
      setSuccessMsg('✅ Cuenta creada. Revisa tu email y confirma tu cuenta para iniciar sesión.')
    }
    if (params.msg === 'otp_expired') {
      setErrorMsg('⏱ El link de confirmación ha caducado. Inicia sesión para recibir uno nuevo.')
    }
  }, [])
  const canLogin = email.trim().length > 0 && password.length >= 6

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={[styles.container, { paddingTop: insets.top + 40, paddingBottom: insets.bottom + 32 }]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Logo */}
        <View style={styles.logoSection}>
          <View style={styles.logoBox}>
            <Text style={styles.logoLetter}>S</Text>
          </View>
          <Text style={styles.title}>Bienvenido</Text>
          <Text style={styles.subtitle}>Inicia sesión para continuar</Text>
        </View>

        {/* Form */}
        <View style={styles.form}>
          <Text style={styles.label}>{t('auth.email')}</Text>
          <View style={styles.inputRow}>
            <Ionicons name="mail-outline" size={18} color="#888" />
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              placeholder={t('auth.email')}
              placeholderTextColor="#aaa"
              autoCapitalize="none"
              keyboardType="email-address"
              autoCorrect={false}
            />
          </View>

          <Text style={styles.label}>{t('auth.password')}</Text>
          <View style={styles.inputRow}>
            <Ionicons name="lock-closed-outline" size={18} color="#888" />
            <TextInput
              style={styles.input}
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••"
              placeholderTextColor="#aaa"
              secureTextEntry={!showPassword}
            />
            <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
              <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={18} color="#888" />
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.forgotBtn} onPress={() => { setResetEmail(''); setResetMsg(''); setResetModal(true) }}>
            <Text style={styles.forgotText}>{t('auth.forgotPassword')}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.loginBtn, (!canLogin || loading) && styles.loginBtnDisabled]}
            onPress={handleLogin}
            disabled={!canLogin || loading}
            activeOpacity={0.85}
          >
            {loading
              ? <ActivityIndicator color="#fff" />
              : <>
                  <Text style={styles.loginBtnText}>{t('auth.signIn')}</Text>
                  <Ionicons name="arrow-forward" size={18} color="#fff" />
                </>
            }
          </TouchableOpacity>
        </View>

        {/* Divider */}
        <View style={styles.divider}>
          <View style={styles.dividerLine} />
          <Text style={styles.dividerText}>o continúa con</Text>
          <View style={styles.dividerLine} />
        </View>

        {/* Social */}
        {showResend && (
        <TouchableOpacity onPress={handleResendConfirmation} style={styles.resendBtn}>
          <Text style={styles.resendBtnText}>📧 Reenviar email de confirmación</Text>
        </TouchableOpacity>
      )}
      {successMsg ? (
        <View style={styles.successBox}>
          <Text style={styles.successText}>{successMsg}</Text>
        </View>
      ) : null}
      {errorMsg ? (
          <View style={styles.errorBox}>
            <Text style={styles.errorText}>{errorMsg}</Text>
          </View>
        ) : null}
        <View style={styles.socialRow}>
          <TouchableOpacity style={styles.socialBtn} onPress={() => handleOAuth('google')}>
            <Text style={styles.socialIcon}>G</Text>
            <Text style={styles.socialText}>Google</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.socialBtn} onPress={() => handleOAuth('apple')}>
            <Ionicons name="logo-apple" size={18} color="#1a1a2e" />
            <Text style={styles.socialText}>Apple</Text>
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>{t('auth.noAccount')} </Text>
          <Link href="/(auth)/register" asChild>
            <TouchableOpacity>
              <Text style={styles.footerLink}>Regístrate</Text>
            </TouchableOpacity>
          </Link>
        </View>
      </ScrollView>
    {/* Modal Reset Password */}
    <Modal visible={resetModal} transparent animationType="slide" onRequestClose={() => setResetModal(false)}>
      <TouchableOpacity style={styles.modalOverlay} activeOpacity={1} onPress={() => setResetModal(false)}>
        <TouchableOpacity style={styles.modalBox} activeOpacity={1}>
          <Text style={styles.modalTitle}>¿Olvidaste tu contraseña?</Text>
          <Text style={styles.modalSub}>Te enviaremos un link para restablecerla en tu idioma.</Text>
          <TextInput
            style={styles.modalInput}
            value={resetEmail}
            onChangeText={setResetEmail}
            placeholder="tu@email.com"
            placeholderTextColor="#aaa"
            autoCapitalize="none"
            keyboardType="email-address"
          />
          {resetMsg ? <Text style={[styles.modalMsg, { color: resetMsg.startsWith('✅') ? '#059669' : '#DC2626' }]}>{resetMsg}</Text> : null}
          <TouchableOpacity
            style={[styles.modalBtn, (!resetEmail.trim() || resetLoading) && styles.loginBtnDisabled]}
            onPress={handleReset}
            disabled={!resetEmail.trim() || resetLoading}
          >
            {resetLoading ? <ActivityIndicator color="#fff" /> : <Text style={styles.modalBtnText}>Enviar link →</Text>}
          </TouchableOpacity>
          <TouchableOpacity style={{ marginTop: 12 }} onPress={() => setResetModal(false)}>
            <Text style={{ color: '#888', textAlign: 'center', fontSize: 14 }}>Cancelar</Text>
          </TouchableOpacity>
        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  container: { paddingHorizontal: 32 },

  logoSection: { alignItems: 'center', marginBottom: 40 },
  logoBox: {
    width: 64, height: 64, borderRadius: 20,
    backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center',
    marginBottom: 24,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3, shadowRadius: 16, elevation: 8,
  },
  logoLetter: { fontSize: 28, fontWeight: '800', color: '#fff' },
  title: { fontSize: 30, fontWeight: '700', color: '#1a1a2e', marginBottom: 6 },
  subtitle: { fontSize: 16, color: '#888' },

  form: { gap: 6, marginBottom: 28 },
  label: { fontSize: 13, fontWeight: '700', color: '#555', marginTop: 14, marginBottom: 6, letterSpacing: 0.2 },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: '#fff', borderRadius: 16, paddingHorizontal: 16,
    borderWidth: 1, borderColor: '#E5E7EB',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 6, elevation: 1,
  },
  input: { flex: 1, paddingVertical: 16, fontSize: 15, color: '#1a1a2e' },

  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalBox: { backgroundColor: '#fff', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 28, gap: 12 },
  modalTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  modalSub: { fontSize: 14, color: '#888', lineHeight: 20 },
  modalInput: { backgroundColor: '#F3F4F6', borderRadius: 14, paddingHorizontal: 16, paddingVertical: 14, fontSize: 15, color: '#1a1a2e', borderWidth: 1, borderColor: '#E5E7EB' },
  modalMsg: { fontSize: 13, fontWeight: '600' },
  modalBtn: { backgroundColor: '#2563EB', borderRadius: 14, paddingVertical: 15, alignItems: 'center' },
  modalBtnText: { fontSize: 15, fontWeight: '700', color: '#fff' },
  forgotBtn: { alignSelf: 'flex-end', marginTop: 4 },
  forgotText: { fontSize: 13, fontWeight: '600', color: '#2563EB' },

  loginBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10,
    marginTop: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  loginBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  loginBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },

  divider: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 20 },
  dividerLine: { flex: 1, height: 1, backgroundColor: '#E5E7EB' },
  dividerText: { fontSize: 13, color: '#aaa', fontWeight: '500' },

  socialRow: { flexDirection: 'row', gap: 12, marginBottom: 32 },
  socialBtn: {
    flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    backgroundColor: '#fff', borderRadius: 14, height: 52,
    borderWidth: 1, borderColor: '#E5E7EB',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 6, elevation: 1,
  },
  socialIcon: { fontSize: 16, fontWeight: '800', color: '#1a1a2e' },
  socialText: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },

  footer: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center' },
  resendBtn: { backgroundColor: '#EEF4FF', borderRadius: 12, padding: 14, marginBottom: 12, alignItems: 'center', borderWidth: 1, borderColor: '#BFDBFE' },
  resendBtnText: { color: '#2563EB', fontSize: 14, fontWeight: '600' },
  successBox: { backgroundColor: '#D1FAE5', borderRadius: 12, padding: 14, marginBottom: 16, borderWidth: 1, borderColor: '#6EE7B7' },
  successText: { color: '#065F46', fontSize: 14, lineHeight: 20 },
  errorBox: { backgroundColor: '#FEF2F2', borderRadius: 10, padding: 12, marginBottom: 12 },
  errorText: { color: '#DC2626', fontSize: 13, textAlign: 'center' },
  footerText: { fontSize: 14, color: '#888' },
  footerLink: { fontSize: 14, fontWeight: '700', color: '#2563EB' },
})