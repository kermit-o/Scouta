import { useState } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  Alert, ActivityIndicator, ScrollView, KeyboardAvoidingView, Platform
} from 'react-native'
import { Link, router } from 'expo-router'
import { supabase, UserRole, SupportedCountry, SupportedCurrency, SupportedLanguage } from '../../lib/supabase'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const COUNTRIES: { label: string; flag: string; value: SupportedCountry; currency: SupportedCurrency; language: SupportedLanguage }[] = [
  { label: 'España',       flag: '🇪🇸', value: 'ES', currency: 'EUR', language: 'es-ES' },
  { label: 'Francia',      flag: '🇫🇷', value: 'FR', currency: 'EUR', language: 'es' },
  { label: 'Bélgica',      flag: '🇧🇪', value: 'BE', currency: 'EUR', language: 'es' },
  { label: 'Holanda',      flag: '🇳🇱', value: 'NL', currency: 'EUR', language: 'es' },
  { label: 'Alemania',     flag: '🇩🇪', value: 'DE', currency: 'EUR', language: 'es' },
  { label: 'Portugal',     flag: '🇵🇹', value: 'PT', currency: 'EUR', language: 'pt-BR' },
  { label: 'Italia',       flag: '🇮🇹', value: 'IT', currency: 'EUR', language: 'es' },
  { label: 'Reino Unido',  flag: '🇬🇧', value: 'GB', currency: 'GBP', language: 'es' },
  { label: 'México',       flag: '🇲🇽', value: 'MX', currency: 'MXN', language: 'es' },
  { label: 'Colombia',     flag: '🇨🇴', value: 'CO', currency: 'COP', language: 'es' },
  { label: 'Argentina',    flag: '🇦🇷', value: 'AR', currency: 'ARS', language: 'es' },
  { label: 'Brasil',       flag: '🇧🇷', value: 'BR', currency: 'BRL', language: 'pt-BR' },
  { label: 'Chile',        flag: '🇨🇱', value: 'CL', currency: 'CLP', language: 'es' },
]

const ROLES: { label: string; icon: string; value: UserRole; desc: string; features: string[] }[] = [
  {
    label: 'Busco servicios',
    icon: '👤',
    value: 'client',
    desc: 'Publica trabajos y contrata profesionales verificados',
    features: ['Publica trabajos gratis', 'Recibe ofertas de profesionales', 'Pago seguro con escrow'],
  },
  {
    label: 'Ofrezco servicios',
    icon: '🔧',
    value: 'pro',
    desc: 'Encuentra trabajos cerca de ti y genera ingresos',
    features: ['Accede a trabajos cercanos', 'Cobra de forma segura', 'Construye tu reputación'],
  },
  {
    label: 'Empresa',
    icon: '🏢',
    value: 'company',
    desc: 'Gestiona un equipo o empresa en Solva',
    features: ['Multi-usuario', 'Dashboard empresa', 'Facturación centralizada'],
  },
]

function passwordStrength(pwd: string): number {
  if (pwd.length === 0) return 0
  let s = 0
  if (pwd.length >= 8) s++
  if (/[A-Z]/.test(pwd)) s++
  if (/[0-9]/.test(pwd)) s++
  if (/[^A-Za-z0-9]/.test(pwd)) s++
  return s
}

const STRENGTH_COLOR = ['#EF4444', '#F97316', '#EAB308', '#10B981']
const STRENGTH_LABEL = ['Muy débil', 'Débil', 'Buena', 'Fuerte']

export default function RegisterScreen() {
  const insets = useSafeAreaInsets()
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [country, setCountry] = useState<SupportedCountry>('ES')
  const [role, setRole] = useState<UserRole>('client')
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [loading, setLoading] = useState(false)

  const strength = passwordStrength(password)
  const selectedCountry = COUNTRIES.find(c => c.value === country)!
  const canStep1 = fullName.trim().length > 0 && email.trim().length > 0 && password.length >= 6

  async function handleRegister() {
    if (!acceptTerms) { Alert.alert('Error', 'Debes aceptar los términos'); return }
    setLoading(true)
    const { data, error } = await supabase.auth.signUp({
      email, password,
      options: {
        data: {
          full_name: fullName,
          role,
          country: selectedCountry.value,
          currency: selectedCountry.currency,
          language: selectedCountry.language,
        }
      }
    })
    setLoading(false)
    if (error) Alert.alert('Error', error.message)
    else if (data.user) {
      Alert.alert('✅ Cuenta creada', 'Tu cuenta fue creada exitosamente', [
        { text: 'OK', onPress: () => router.replace('/(auth)/login') }
      ])
    } else {
      Alert.alert('Info', 'Revisa tu email para confirmar tu cuenta')
    }
  }

  return (
    <KeyboardAvoidingView style={styles.screen} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <ScrollView
        contentContainerStyle={[styles.container, { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 32 }]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity
            style={styles.backBtn}
            onPress={() => step > 1 ? setStep((step - 1) as 1 | 2) : router.back()}
          >
            <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
          </TouchableOpacity>
          <View style={styles.progressRow}>
            {[1, 2, 3].map(s => (
              <View key={s} style={[styles.progressBar, s <= step && styles.progressBarActive]} />
            ))}
          </View>
        </View>

        {/* ── PASO 1: Datos personales ── */}
        {step === 1 && (
          <View style={styles.stepContent}>
            <Text style={styles.stepTitle}>Crear cuenta</Text>
            <Text style={styles.stepSub}>Únete a la comunidad Solva</Text>

            <Text style={styles.label}>Nombre completo</Text>
            <View style={styles.inputRow}>
              <Ionicons name="person-outline" size={18} color="#888" />
              <TextInput
                style={styles.input}
                value={fullName}
                onChangeText={setFullName}
                placeholder="Tu nombre"
                placeholderTextColor="#aaa"
              />
            </View>

            <Text style={styles.label}>Correo electrónico</Text>
            <View style={styles.inputRow}>
              <Ionicons name="mail-outline" size={18} color="#888" />
              <TextInput
                style={styles.input}
                value={email}
                onChangeText={setEmail}
                placeholder="tu@email.com"
                placeholderTextColor="#aaa"
                autoCapitalize="none"
                keyboardType="email-address"
              />
            </View>

            <Text style={styles.label}>Contraseña</Text>
            <View style={styles.inputRow}>
              <Ionicons name="lock-closed-outline" size={18} color="#888" />
              <TextInput
                style={styles.input}
                value={password}
                onChangeText={setPassword}
                placeholder="Mínimo 6 caracteres"
                placeholderTextColor="#aaa"
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons name={showPassword ? 'eye-off-outline' : 'eye-outline'} size={18} color="#888" />
              </TouchableOpacity>
            </View>

            {/* Password strength */}
            {password.length > 0 && (
              <View style={styles.strengthContainer}>
                <View style={styles.strengthBars}>
                  {[0, 1, 2, 3].map(i => (
                    <View
                      key={i}
                      style={[
                        styles.strengthBar,
                        i < strength && { backgroundColor: STRENGTH_COLOR[strength - 1] }
                      ]}
                    />
                  ))}
                </View>
                <Text style={[styles.strengthLabel, { color: STRENGTH_COLOR[strength - 1] ?? '#aaa' }]}>
                  {STRENGTH_LABEL[strength - 1] ?? 'Muy débil'}
                </Text>
              </View>
            )}

            <TouchableOpacity
              style={[styles.btn, !canStep1 && styles.btnDisabled]}
              onPress={() => setStep(2)}
              disabled={!canStep1}
              activeOpacity={0.85}
            >
              <Text style={styles.btnText}>Continuar</Text>
              <Ionicons name="arrow-forward" size={18} color="#fff" />
            </TouchableOpacity>

            <View style={styles.switchRow}>
              <Text style={styles.switchText}>¿Ya tienes cuenta? </Text>
              <Link href="/(auth)/login" asChild>
                <TouchableOpacity>
                  <Text style={styles.switchLink}>Inicia sesión</Text>
                </TouchableOpacity>
              </Link>
            </View>
          </View>
        )}

        {/* ── PASO 2: País ── */}
        {step === 2 && (
          <View style={styles.stepContent}>
            <View style={styles.stepIcon}>
              <Ionicons name="location" size={28} color="#2563EB" />
            </View>
            <Text style={styles.stepTitle}>¿Dónde te encuentras?</Text>
            <Text style={styles.stepSub}>Personaliza tu experiencia según tu país</Text>

            <View style={styles.countriesGrid}>
              {COUNTRIES.map(c => (
                <TouchableOpacity
                  key={c.value}
                  style={[styles.countryCard, country === c.value && styles.countryCardSelected]}
                  onPress={() => setCountry(c.value)}
                  activeOpacity={0.8}
                >
                  <Text style={styles.countryFlag}>{c.flag}</Text>
                  <Text style={[styles.countryName, country === c.value && styles.countryNameSelected]}>
                    {c.label}
                  </Text>
                  <Text style={styles.countryCurrency}>{c.currency}</Text>
                  {country === c.value && (
                    <View style={styles.countryCheck}>
                      <Ionicons name="checkmark" size={12} color="#fff" />
                    </View>
                  )}
                </TouchableOpacity>
              ))}
            </View>

            <TouchableOpacity
              style={styles.btn}
              onPress={() => setStep(3)}
              activeOpacity={0.85}
            >
              <Text style={styles.btnText}>Continuar</Text>
              <Ionicons name="arrow-forward" size={18} color="#fff" />
            </TouchableOpacity>
          </View>
        )}

        {/* ── PASO 3: Rol + términos ── */}
        {step === 3 && (
          <View style={styles.stepContent}>
            <View style={styles.stepIcon}>
              <Ionicons name="person-circle" size={28} color="#2563EB" />
            </View>
            <Text style={styles.stepTitle}>¿Cómo usarás Solva?</Text>
            <Text style={styles.stepSub}>Podrás cambiar esto más adelante</Text>

            {ROLES.map(r => (
              <TouchableOpacity
                key={r.value}
                style={[styles.roleCard, role === r.value && styles.roleCardSelected]}
                onPress={() => setRole(r.value)}
                activeOpacity={0.85}
              >
                <View style={styles.roleTop}>
                  <View style={[styles.roleIconBox, role === r.value && styles.roleIconBoxSelected]}>
                    <Text style={styles.roleIcon}>{r.icon}</Text>
                  </View>
                  <View style={styles.roleInfo}>
                    <Text style={styles.roleLabel}>{r.label}</Text>
                    <Text style={styles.roleDesc}>{r.desc}</Text>
                  </View>
                  {role === r.value && (
                    <View style={styles.roleCheck}>
                      <Ionicons name="checkmark" size={14} color="#fff" />
                    </View>
                  )}
                </View>
                {role === r.value && (
                  <View style={styles.roleFeatures}>
                    {r.features.map((f, i) => (
                      <View key={i} style={styles.featureRow}>
                        <Ionicons name="chevron-forward" size={14} color="#2563EB" />
                        <Text style={styles.featureText}>{f}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </TouchableOpacity>
            ))}

            {/* Terms */}
            <TouchableOpacity
              style={styles.termsRow}
              onPress={() => setAcceptTerms(!acceptTerms)}
              activeOpacity={0.8}
            >
              <View style={[styles.checkbox, acceptTerms && styles.checkboxActive]}>
                {acceptTerms && <Ionicons name="checkmark" size={14} color="#fff" />}
              </View>
              <Text style={styles.termsText}>
                Acepto los <Text style={styles.termsLink}>Términos de Servicio</Text> y la{' '}
                <Text style={styles.termsLink}>Política de Privacidad</Text>
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.btn, (!acceptTerms || loading) && styles.btnDisabled]}
              onPress={handleRegister}
              disabled={!acceptTerms || loading}
              activeOpacity={0.85}
            >
              {loading
                ? <ActivityIndicator color="#fff" />
                : <>
                    <Text style={styles.btnText}>Crear cuenta</Text>
                    <Ionicons name="arrow-forward" size={18} color="#fff" />
                  </>
              }
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  container: { paddingHorizontal: 24 },

  header: { flexDirection: 'row', alignItems: 'center', gap: 16, marginBottom: 32 },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  progressRow: { flex: 1, flexDirection: 'row', gap: 6 },
  progressBar: { flex: 1, height: 4, borderRadius: 2, backgroundColor: '#E5E7EB' },
  progressBarActive: { backgroundColor: '#2563EB' },

  stepContent: { gap: 4 },
  stepIcon: {
    width: 56, height: 56, borderRadius: 18,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
    marginBottom: 16,
  },
  stepTitle: { fontSize: 28, fontWeight: '800', color: '#1a1a2e', marginBottom: 4 },
  stepSub: { fontSize: 15, color: '#888', marginBottom: 20 },

  label: { fontSize: 12, fontWeight: '700', color: '#555', marginTop: 14, marginBottom: 6, letterSpacing: 0.2 },
  inputRow: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: '#fff', borderRadius: 16, paddingHorizontal: 16,
    borderWidth: 1, borderColor: '#E5E7EB',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 6, elevation: 1,
  },
  input: { flex: 1, paddingVertical: 16, fontSize: 15, color: '#1a1a2e' },

  strengthContainer: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 8 },
  strengthBars: { flex: 1, flexDirection: 'row', gap: 4 },
  strengthBar: { flex: 1, height: 4, borderRadius: 2, backgroundColor: '#E5E7EB' },
  strengthLabel: { fontSize: 12, fontWeight: '600' },

  btn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10,
    marginTop: 20,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  btnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#fff' },

  switchRow: { flexDirection: 'row', justifyContent: 'center', marginTop: 20 },
  switchText: { fontSize: 14, color: '#888' },
  switchLink: { fontSize: 14, fontWeight: '700', color: '#2563EB' },

  // Countries
  countriesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20 },
  countryCard: {
    width: '47%', borderRadius: 16, padding: 14,
    backgroundColor: '#fff', borderWidth: 2, borderColor: '#E5E7EB',
    alignItems: 'center', gap: 4, position: 'relative',
  },
  countryCardSelected: { borderColor: '#2563EB', backgroundColor: '#EEF4FF' },
  countryFlag: { fontSize: 28 },
  countryName: { fontSize: 13, fontWeight: '600', color: '#555', textAlign: 'center' },
  countryNameSelected: { color: '#2563EB' },
  countryCurrency: { fontSize: 11, color: '#aaa' },
  countryCheck: {
    position: 'absolute', top: 8, right: 8,
    width: 20, height: 20, borderRadius: 10,
    backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center',
  },

  // Roles
  roleCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18,
    borderWidth: 2, borderColor: '#E5E7EB', marginBottom: 12,
  },
  roleCardSelected: { borderColor: '#2563EB', backgroundColor: '#EEF4FF' },
  roleTop: { flexDirection: 'row', alignItems: 'flex-start', gap: 14 },
  roleIconBox: {
    width: 48, height: 48, borderRadius: 14,
    backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center',
  },
  roleIconBoxSelected: { backgroundColor: '#2563EB' },
  roleIcon: { fontSize: 22 },
  roleInfo: { flex: 1 },
  roleLabel: { fontSize: 16, fontWeight: '700', color: '#1a1a2e', marginBottom: 3 },
  roleDesc: { fontSize: 13, color: '#666', lineHeight: 18 },
  roleCheck: {
    width: 24, height: 24, borderRadius: 12,
    backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center',
  },
  roleFeatures: {
    marginTop: 14, paddingTop: 14,
    borderTopWidth: 1, borderTopColor: '#E5E7EB', gap: 6,
  },
  featureRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  featureText: { fontSize: 13, color: '#555' },

  // Terms
  termsRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginTop: 16, marginBottom: 4 },
  checkbox: {
    width: 24, height: 24, borderRadius: 8,
    borderWidth: 2, borderColor: '#E5E7EB',
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    flexShrink: 0,
  },
  checkboxActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  termsText: { flex: 1, fontSize: 13, color: '#666', lineHeight: 20 },
  termsLink: { color: '#2563EB', fontWeight: '600' },
})