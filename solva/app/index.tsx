// landing placeholderimport React, { useEffect, useRef } from 'react'
import { View, Text, ScrollView, TouchableOpacity, StyleSheet, Dimensions, Animated } from 'react-native'
import { router } from 'expo-router'
import { useAuth } from '../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const { width } = Dimensions.get('window')

const CATEGORIES = [
  { icon: '🧹', label: 'Limpieza' },
  { icon: '🔧', label: 'Fontanería' },
  { icon: '⚡', label: 'Electricidad' },
  { icon: '🎨', label: 'Pintura' },
  { icon: '🌿', label: 'Jardinería' },
  { icon: '📦', label: 'Mudanzas' },
  { icon: '🪟', label: 'Reformas' },
  { icon: '❄️', label: 'Climatización' },
]

const STEPS = [
  { num: '01', icon: 'search-outline', title: 'Publica tu trabajo', desc: 'Describe lo que necesitas, tu presupuesto y cuándo lo necesitas. Es gratis y solo toma 2 minutos.' },
  { num: '02', icon: 'people-outline', title: 'Recibe ofertas', desc: 'Profesionales verificados de tu zona envían sus propuestas. Compara precios, perfiles y reseñas.' },
  { num: '03', icon: 'shield-checkmark-outline', title: 'Paga con seguridad', desc: 'Tu dinero queda protegido hasta que confirmes que el trabajo está bien hecho. Garantía total.' },
]

const STATS = [
  { value: '10K+', label: 'Profesionales' },
  { value: '50K+', label: 'Trabajos completados' },
  { value: '4.9★', label: 'Valoración media' },
  { value: '7', label: 'Países' },
]

export default function LandingScreen() {
  const { session, loading } = useAuth()
  const insets = useSafeAreaInsets()
  const fadeAnim = useRef(new Animated.Value(0)).current
  const slideAnim = useRef(new Animated.Value(40)).current

  useEffect(() => {
    if (!loading && session) { router.replace('/(app)'); return }
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 800, useNativeDriver: true }),
      Animated.timing(slideAnim, { toValue: 0, duration: 800, useNativeDriver: true }),
    ]).start()
  }, [loading, session])

  if (loading || session) return null

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.nav}>
        <Text style={s.navLogo}>solva</Text>
        <View style={s.navActions}>
          <TouchableOpacity style={s.navLogin} onPress={() => router.push('/(auth)/login')}>
            <Text style={s.navLoginText}>Entrar</Text>
          </TouchableOpacity>
          <TouchableOpacity style={s.navRegister} onPress={() => router.push('/(auth)/register')}>
            <Text style={s.navRegisterText}>Empezar gratis</Text>
          </TouchableOpacity>
        </View>
      </View>
      <ScrollView showsVerticalScrollIndicator={false} bounces={false}>
        <View style={s.hero}>
          <View style={s.heroBg} />
          <Animated.View style={[s.heroContent, { opacity: fadeAnim, transform: [{ translateY: slideAnim }] }]}>
            <View style={s.heroBadge}>
              <Text style={s.heroBadgeText}>🇧🇪 🇪🇸 🇫🇷 🇩🇪 🇳🇱 🇵🇹 🇮🇹</Text>
            </View>
            <Text style={s.heroTitle}>El profesional{'\n'}que necesitas,{'\n'}cerca de ti</Text>
            <Text style={s.heroSub}>Conectamos clientes con profesionales verificados para servicios del hogar. Pago seguro, garantía total.</Text>
            <View style={s.heroCtas}>
              <TouchableOpacity style={s.ctaPrimary} onPress={() => router.push('/(auth)/register')}>
                <Text style={s.ctaPrimaryText}>Publicar trabajo gratis</Text>
                <Ionicons name="arrow-forward" size={18} color="#fff" />
              </TouchableOpacity>
              <TouchableOpacity style={s.ctaSecondary} onPress={() => router.push('/(auth)/register')}>
                <Text style={s.ctaSecondaryText}>Soy profesional →</Text>
              </TouchableOpacity>
            </View>
          </Animated.View>
        </View>
        <View style={s.stats}>
          {STATS.map((stat, i) => (
            <View key={i} style={s.stat}>
              <Text style={s.statValue}>{stat.value}</Text>
              <Text style={s.statLabel}>{stat.label}</Text>
            </View>
          ))}
        </View>
        <View style={s.section}>
          <Text style={s.sectionTitle}>¿Qué necesitas?</Text>
          <Text style={s.sectionSub}>Profesionales para cualquier servicio del hogar</Text>
          <View style={s.categories}>
            {CATEGORIES.map((cat, i) => (
              <TouchableOpacity key={i} style={s.catCard} onPress={() => router.push('/(auth)/register')}>
                <Text style={s.catIcon}>{cat.icon}</Text>
                <Text style={s.catLabel}>{cat.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        <View style={[s.section, s.sectionDark]}>
          <Text style={[s.sectionTitle, { color: '#fff' }]}>Cómo funciona</Text>
          <Text style={[s.sectionSub, { color: 'rgba(255,255,255,0.6)' }]}>Simple, seguro y transparente</Text>
          {STEPS.map((step, i) => (
            <View key={i} style={s.stepCard}>
              <View style={s.stepNum}><Text style={s.stepNumText}>{step.num}</Text></View>
              <View style={s.stepContent}>
                <View style={s.stepIconWrap}>
                  <Ionicons name={step.icon as any} size={20} color="#2563EB" />
                </View>
                <Text style={s.stepTitle}>{step.title}</Text>
                <Text style={s.stepDesc}>{step.desc}</Text>
              </View>
            </View>
          ))}
        </View>
        <View style={s.section}>
          <View style={s.guarantee}>
            <View style={s.guaranteeIcon}>
              <Ionicons name="shield-checkmark" size={32} color="#2563EB" />
            </View>
            <Text style={s.guaranteeTitle}>Pago 100% seguro</Text>
            <Text style={s.guaranteeDesc}>Tu dinero queda retenido hasta que confirmes que el trabajo está bien hecho. Si hay algún problema, te devolvemos el dinero.</Text>
            <View style={s.guaranteeFeatures}>
              {['Pago en custodia (escrow)', 'Profesionales verificados KYC', 'Soporte 24/7', 'Garantía de devolución'].map((f, i) => (
                <View key={i} style={s.guaranteeFeature}>
                  <Ionicons name="checkmark-circle" size={16} color="#10B981" />
                  <Text style={s.guaranteeFeatureText}>{f}</Text>
                </View>
              ))}
            </View>
          </View>
        </View>
        <View style={[s.section, s.ctaFinal]}>
          <Text style={s.ctaFinalTitle}>Listo para empezar</Text>
          <Text style={s.ctaFinalSub}>Únete a miles de usuarios que ya confían en Solva</Text>
          <TouchableOpacity style={s.ctaFinalBtn} onPress={() => router.push('/(auth)/register')}>
            <Text style={s.ctaFinalBtnText}>Crear cuenta gratis</Text>
            <Ionicons name="arrow-forward" size={20} color="#fff" />
          </TouchableOpacity>
          <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
            <Text style={s.ctaFinalLogin}>¿Ya tienes cuenta? Inicia sesión</Text>
          </TouchableOpacity>
        </View>
        <View style={s.footer}>
          <Text style={s.footerLogo}>solva</Text>
          <View style={s.footerLinks}>
            <TouchableOpacity onPress={() => router.push('/terms')}><Text style={s.footerLink}>Términos</Text></TouchableOpacity>
            <TouchableOpacity onPress={() => router.push('/privacy')}><Text style={s.footerLink}>Privacidad</Text></TouchableOpacity>
          </View>
          <Text style={s.footerCopy}>© 2026 Solva SRL · Bruselas, Bélgica</Text>
        </View>
      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#fff' },
  nav: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.06)' },
  navLogo: { fontSize: 22, fontWeight: '800', color: '#1a1a2e', letterSpacing: -1 },
  navActions: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  navLogin: { paddingHorizontal: 16, paddingVertical: 8 },
  navLoginText: { fontSize: 14, fontWeight: '600', color: '#555' },
  navRegister: { backgroundColor: '#2563EB', borderRadius: 20, paddingHorizontal: 16, paddingVertical: 8 },
  navRegisterText: { fontSize: 14, fontWeight: '700', color: '#fff' },
  hero: { minHeight: 520, justifyContent: 'center', overflow: 'hidden' },
  heroBg: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#0f172a' },
  heroContent: { padding: 28, paddingTop: 48, paddingBottom: 56 },
  heroBadge: { backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6, alignSelf: 'flex-start', marginBottom: 20 },
  heroBadgeText: { fontSize: 16, letterSpacing: 2 },
  heroTitle: { fontSize: width > 400 ? 44 : 36, fontWeight: '900', color: '#fff', lineHeight: width > 400 ? 50 : 42, letterSpacing: -1.5, marginBottom: 16 },
  heroSub: { fontSize: 16, color: 'rgba(255,255,255,0.65)', lineHeight: 24, marginBottom: 32, maxWidth: 340 },
  heroCtas: { gap: 12 },
  ctaPrimary: { backgroundColor: '#2563EB', borderRadius: 16, paddingVertical: 16, paddingHorizontal: 24, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8 },
  ctaPrimaryText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  ctaSecondary: { paddingVertical: 12, alignItems: 'center' },
  ctaSecondaryText: { fontSize: 15, fontWeight: '600', color: 'rgba(255,255,255,0.7)' },
  stats: { flexDirection: 'row', backgroundColor: '#2563EB', paddingVertical: 24 },
  stat: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 20, fontWeight: '900', color: '#fff', marginBottom: 2 },
  statLabel: { fontSize: 11, color: 'rgba(255,255,255,0.7)', textAlign: 'center' },
  section: { padding: 28, paddingVertical: 40 },
  sectionDark: { backgroundColor: '#0f172a' },
  sectionTitle: { fontSize: 26, fontWeight: '800', color: '#1a1a2e', marginBottom: 6, letterSpacing: -0.5 },
  sectionSub: { fontSize: 15, color: '#888', marginBottom: 24 },
  categories: { flexDirection: 'row', flexWrap: 'wrap', gap: 12 },
  catCard: { width: (width - 56 - 12) / 2, backgroundColor: '#F8F9FC', borderRadius: 16, padding: 18, alignItems: 'center', gap: 8, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  catIcon: { fontSize: 28 },
  catLabel: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  stepCard: { flexDirection: 'row', gap: 16, marginBottom: 28 },
  stepNum: { width: 36, height: 36, borderRadius: 10, backgroundColor: 'rgba(37,99,235,0.15)', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 4 },
  stepNumText: { fontSize: 12, fontWeight: '800', color: '#2563EB' },
  stepContent: { flex: 1 },
  stepIconWrap: { width: 36, height: 36, borderRadius: 10, backgroundColor: 'rgba(37,99,235,0.1)', alignItems: 'center', justifyContent: 'center', marginBottom: 8 },
  stepTitle: { fontSize: 17, fontWeight: '700', color: '#fff', marginBottom: 6 },
  stepDesc: { fontSize: 14, color: 'rgba(255,255,255,0.6)', lineHeight: 20 },
  guarantee: { backgroundColor: '#F0F7FF', borderRadius: 24, padding: 28, alignItems: 'center' },
  guaranteeIcon: { width: 64, height: 64, borderRadius: 20, backgroundColor: '#DBEAFE', alignItems: 'center', justifyContent: 'center', marginBottom: 16 },
  guaranteeTitle: { fontSize: 22, fontWeight: '800', color: '#1a1a2e', marginBottom: 10, textAlign: 'center' },
  guaranteeDesc: { fontSize: 15, color: '#555', lineHeight: 22, textAlign: 'center', marginBottom: 20 },
  guaranteeFeatures: { gap: 10, width: '100%' },
  guaranteeFeature: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  guaranteeFeatureText: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  ctaFinal: { backgroundColor: '#0f172a', alignItems: 'center' },
  ctaFinalTitle: { fontSize: 28, fontWeight: '900', color: '#fff', textAlign: 'center', marginBottom: 8, letterSpacing: -0.5 },
  ctaFinalSub: { fontSize: 15, color: 'rgba(255,255,255,0.6)', textAlign: 'center', marginBottom: 28 },
  ctaFinalBtn: { backgroundColor: '#2563EB', borderRadius: 16, paddingVertical: 16, paddingHorizontal: 32, flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 16 },
  ctaFinalBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  ctaFinalLogin: { fontSize: 14, color: 'rgba(255,255,255,0.5)', textDecorationLine: 'underline' },
  footer: { backgroundColor: '#0a0f1e', padding: 28, alignItems: 'center', gap: 12 },
  footerLogo: { fontSize: 20, fontWeight: '800', color: '#fff', letterSpacing: -1 },
  footerLinks: { flexDirection: 'row', gap: 24 },
  footerLink: { fontSize: 13, color: 'rgba(255,255,255,0.4)' },
  footerCopy: { fontSize: 12, color: 'rgba(255,255,255,0.25)' },
})