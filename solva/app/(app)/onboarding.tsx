import { useState } from 'react'
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, TextInput } from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORIES = [
  { key: 'plumbing', label: 'Fontanería', icon: '🔧' },
  { key: 'electrical', label: 'Electricidad', icon: '⚡' },
  { key: 'cleaning', label: 'Limpieza', icon: '🧹' },
  { key: 'carpentry', label: 'Carpintería', icon: '🪚' },
  { key: 'painting', label: 'Pintura', icon: '🎨' },
  { key: 'gardening', label: 'Jardinería', icon: '🌿' },
  { key: 'moving', label: 'Mudanzas', icon: '📦' },
  { key: 'tech', label: 'Tecnología', icon: '💻' },
  { key: 'other', label: 'Otro', icon: '✨' },
]

export default function OnboardingScreen() {
  const insets = useSafeAreaInsets()
  const { session, profile } = useAuth()
  const [step, setStep] = useState(1)
  const [selected, setSelected] = useState<string[]>([])
  const [specialty, setSpecialty] = useState('')
  const [years, setYears] = useState('')
  const [avgPrice, setAvgPrice] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiResult, setAiResult] = useState<any>(null)

  const isPro = profile?.role === 'pro' || profile?.role === 'company'

  async function handleStep1() {
    if (!isPro || selected.length === 0) {
      // Cliente o sin selección → terminar
      await supabase.from('users').update({ 
        ai_keywords: selected, onboarding_completed: true 
      }).eq('id', session!.user.id)
      router.replace('/(app)')
      return
    }
    setStep(2)
  }

  async function handleFinish() {
    setLoading(true)
    try {
      await supabase.from('users').update({
        ai_keywords: selected,
        onboarding_completed: true,
        bio: specialty || null,
      }).eq('id', session!.user.id)

      // Llamar generate-pro-content
      const { data } = await supabase.functions.invoke('generate-pro-content', {
        body: {
          user_id: session!.user.id,
          category: selected[0],
          years_experience: years ? parseInt(years) : 1,
          specialty: specialty || null,
          city: profile?.city || null,
          avg_price: avgPrice ? parseFloat(avgPrice) : null,
          currency: profile?.currency ?? 'EUR',
          language: profile?.language ?? 'es',
          is_onboarding: true,
        }
      })
      if (data) setAiResult(data)
      else router.replace('/(app)')
    } catch (_) {
      router.replace('/(app)')
    }
    setLoading(false)
  }

  if (aiResult) {
    return (
      <View style={[styles.screen, { paddingTop: insets.top + 24 }]}>
        <ScrollView contentContainerStyle={styles.container}>
          <Text style={styles.aiIcon}>✨</Text>
          <Text style={styles.title}>Tu perfil está listo</Text>
          <Text style={styles.sub}>La IA ha generado contenido optimizado para tu perfil</Text>

          <View style={styles.aiCard}>
            <Text style={styles.aiLabel}>Título sugerido</Text>
            <Text style={styles.aiValue}>{aiResult.profile_title}</Text>
          </View>
          <View style={styles.aiCard}>
            <Text style={styles.aiLabel}>Descripción</Text>
            <Text style={styles.aiValue}>{aiResult.short_description}</Text>
          </View>
          <View style={styles.aiCard}>
            <Text style={styles.aiLabel}>Tu propuesta única</Text>
            <Text style={styles.aiValueHighlight}>{aiResult.usp}</Text>
          </View>
          {aiResult.quality_tips?.length > 0 && (
            <View style={styles.aiCard}>
              <Text style={styles.aiLabel}>Consejos para mejorar tu perfil</Text>
              {aiResult.quality_tips.map((tip: string, i: number) => (
                <View key={i} style={styles.tipRow}>
                  <Ionicons name="bulb-outline" size={14} color="#D97706" />
                  <Text style={styles.tipText}>{tip}</Text>
                </View>
              ))}
            </View>
          )}

          <TouchableOpacity style={styles.btn} onPress={() => router.replace('/(app)')} activeOpacity={0.85}>
            <Text style={styles.btnText}>Empezar a trabajar</Text>
            <Ionicons name="arrow-forward" size={18} color="#fff" />
          </TouchableOpacity>
        </ScrollView>
      </View>
    )
  }

  return (
    <View style={[styles.screen, { paddingTop: insets.top + 24 }]}>
      <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
        <View style={styles.iconBox}>
          <Text style={styles.iconEmoji}>{step === 1 ? '👋' : '🤖'}</Text>
        </View>

        {step === 1 ? (
          <>
            <Text style={styles.title}>¡Bienvenido{profile?.full_name ? `, ${profile.full_name.split(' ')[0]}` : ''}!</Text>
            <Text style={styles.sub}>
              {isPro ? 'Selecciona tus áreas de trabajo' : 'Cuéntanos qué servicios buscas'}
            </Text>
            <View style={styles.grid}>
              {CATEGORIES.map(cat => (
                <TouchableOpacity
                  key={cat.key}
                  style={[styles.chip, selected.includes(cat.key) && styles.chipSelected]}
                  onPress={() => setSelected(prev =>
                    prev.includes(cat.key) ? prev.filter(s => s !== cat.key) : [...prev, cat.key]
                  )}
                  activeOpacity={0.8}
                >
                  <Text style={styles.chipIcon}>{cat.icon}</Text>
                  <Text style={[styles.chipLabel, selected.includes(cat.key) && styles.chipLabelSelected]}>{cat.label}</Text>
                  {selected.includes(cat.key) && (
                    <View style={styles.chipCheck}><Ionicons name="checkmark" size={10} color="#fff" /></View>
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </>
        ) : (
          <>
            <Text style={styles.title}>Cuéntanos más</Text>
            <Text style={styles.sub}>La IA generará tu perfil optimizado</Text>

            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>¿En qué te especializas?</Text>
              <TextInput style={styles.input} value={specialty} onChangeText={setSpecialty}
                placeholder="Ej: baños y cocinas, instalaciones eléctricas..." />
            </View>
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Años de experiencia</Text>
              <TextInput style={styles.input} value={years} onChangeText={setYears}
                placeholder="Ej: 5" keyboardType="numeric" />
            </View>
            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>Precio medio por trabajo ({profile?.currency ?? 'EUR'})</Text>
              <TextInput style={styles.input} value={avgPrice} onChangeText={setAvgPrice}
                placeholder="Ej: 80" keyboardType="numeric" />
            </View>
          </>
        )}

        <TouchableOpacity
          style={[styles.btn, loading && styles.btnDisabled]}
          onPress={step === 1 ? handleStep1 : handleFinish}
          disabled={loading}
          activeOpacity={0.85}
        >
          {loading
            ? <ActivityIndicator color="#fff" />
            : <>
                <Text style={styles.btnText}>
                  {step === 1
                    ? (isPro && selected.length > 0 ? 'Siguiente →' : 'Comenzar')
                    : '✨ Generar mi perfil con IA'}
                </Text>
              </>
          }
        </TouchableOpacity>
        {step === 2 && (
          <TouchableOpacity onPress={() => router.replace('/(app)')} style={{ marginTop: 12 }}>
            <Text style={{ color: '#888', textAlign: 'center' }}>Saltar por ahora</Text>
          </TouchableOpacity>
        )}
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  container: { paddingHorizontal: 24, paddingBottom: 40, alignItems: 'center' },
  iconBox: { width: 80, height: 80, borderRadius: 28, backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center', marginBottom: 24 },
  iconEmoji: { fontSize: 36 },
  aiIcon: { fontSize: 48, marginBottom: 16, textAlign: 'center' },
  title: { fontSize: 28, fontWeight: '800', color: '#1a1a2e', textAlign: 'center', marginBottom: 8 },
  sub: { fontSize: 15, color: '#666', textAlign: 'center', lineHeight: 22, marginBottom: 32, paddingHorizontal: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, justifyContent: 'center', marginBottom: 32 },
  chip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 50, backgroundColor: '#fff', borderWidth: 2, borderColor: '#E5E7EB', position: 'relative' },
  chipSelected: { borderColor: '#2563EB', backgroundColor: '#EEF4FF' },
  chipIcon: { fontSize: 18 },
  chipLabel: { fontSize: 14, fontWeight: '600', color: '#555' },
  chipLabelSelected: { color: '#2563EB' },
  chipCheck: { position: 'absolute', top: -4, right: -4, width: 16, height: 16, borderRadius: 8, backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center' },
  formGroup: { width: '100%', marginBottom: 16 },
  formLabel: { fontSize: 14, fontWeight: '600', color: '#1a1a2e', marginBottom: 6 },
  input: { backgroundColor: '#fff', borderRadius: 12, paddingHorizontal: 16, paddingVertical: 12, fontSize: 15, borderWidth: 1, borderColor: '#E5E7EB', width: '100%' },
  btn: { width: '100%', backgroundColor: '#2563EB', borderRadius: 16, height: 56, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.3, shadowRadius: 14, elevation: 6 },
  btnDisabled: { opacity: 0.6 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  aiCard: { width: '100%', backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#E5E7EB' },
  aiLabel: { fontSize: 12, fontWeight: '700', color: '#888', marginBottom: 6, textTransform: 'uppercase' },
  aiValue: { fontSize: 14, color: '#1a1a2e', lineHeight: 20 },
  aiValueHighlight: { fontSize: 16, fontWeight: '700', color: '#2563EB' },
  tipRow: { flexDirection: 'row', gap: 8, alignItems: 'flex-start', marginTop: 6 },
  tipText: { flex: 1, fontSize: 13, color: '#555', lineHeight: 18 },
})
