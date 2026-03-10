import { useState } from 'react'
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator } from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORIES = [
  { label: 'Fontanería', icon: '🔧' },
  { label: 'Electricidad', icon: '⚡' },
  { label: 'Limpieza', icon: '🧹' },
  { label: 'Carpintería', icon: '🪚' },
  { label: 'Pintura', icon: '🎨' },
  { label: 'Jardinería', icon: '🌿' },
  { label: 'Mudanzas', icon: '📦' },
  { label: 'Reformas', icon: '🏠' },
  { label: 'Tecnología', icon: '💻' },
  { label: 'Otro', icon: '✨' },
]

export default function OnboardingScreen() {
  const insets = useSafeAreaInsets()
  const { profile } = useAuth()
  const [selected, setSelected] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  async function handleContinue() {
    setLoading(true)
    if (profile?.id && selected.length > 0) {
      await supabase.from('users').update({ 
        ai_keywords: selected,
        onboarding_completed: true 
      }).eq('id', profile.id)
    }
    setLoading(false)
    router.replace('/(app)')
  }

  const isPro = profile?.role === 'pro' || profile?.role === 'company'

  return (
    <View style={[styles.screen, { paddingTop: insets.top + 24 }]}>
      <ScrollView contentContainerStyle={styles.container} showsVerticalScrollIndicator={false}>
        <View style={styles.iconBox}>
          <Text style={styles.iconEmoji}>👋</Text>
        </View>
        <Text style={styles.title}>
          ¡Bienvenido{profile?.full_name ? `, ${profile.full_name.split(' ')[0]}` : ''}!
        </Text>
        <Text style={styles.sub}>
          {isPro 
            ? 'Selecciona tus áreas de trabajo para encontrar los mejores trabajos cerca de ti'
            : 'Cuéntanos qué tipo de servicios buscas con más frecuencia'
          }
        </Text>

        <View style={styles.grid}>
          {CATEGORIES.map(cat => (
            <TouchableOpacity
              key={cat.label}
              style={[styles.chip, selected.includes(cat.label) && styles.chipSelected]}
              onPress={() => setSelected(prev =>
                prev.includes(cat.label)
                  ? prev.filter(s => s !== cat.label)
                  : [...prev, cat.label]
              )}
              activeOpacity={0.8}
            >
              <Text style={styles.chipIcon}>{cat.icon}</Text>
              <Text style={[styles.chipLabel, selected.includes(cat.label) && styles.chipLabelSelected]}>
                {cat.label}
              </Text>
              {selected.includes(cat.label) && (
                <View style={styles.chipCheck}>
                  <Ionicons name="checkmark" size={10} color="#fff" />
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={[styles.btn, loading && styles.btnDisabled]}
          onPress={handleContinue}
          disabled={loading}
          activeOpacity={0.85}
        >
          {loading
            ? <ActivityIndicator color="#fff" />
            : <>
                <Text style={styles.btnText}>
                  {selected.length > 0 ? 'Comenzar' : 'Saltar por ahora'}
                </Text>
                <Ionicons name="arrow-forward" size={18} color="#fff" />
              </>
          }
        </TouchableOpacity>
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  container: { paddingHorizontal: 24, paddingBottom: 40, alignItems: 'center' },
  iconBox: {
    width: 80, height: 80, borderRadius: 28,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
    marginBottom: 24,
  },
  iconEmoji: { fontSize: 36 },
  title: { fontSize: 28, fontWeight: '800', color: '#1a1a2e', textAlign: 'center', marginBottom: 8 },
  sub: { fontSize: 15, color: '#666', textAlign: 'center', lineHeight: 22, marginBottom: 32, paddingHorizontal: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, justifyContent: 'center', marginBottom: 32 },
  chip: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 10, borderRadius: 50,
    backgroundColor: '#fff', borderWidth: 2, borderColor: '#E5E7EB',
    position: 'relative',
  },
  chipSelected: { borderColor: '#2563EB', backgroundColor: '#EEF4FF' },
  chipIcon: { fontSize: 18 },
  chipLabel: { fontSize: 14, fontWeight: '600', color: '#555' },
  chipLabelSelected: { color: '#2563EB' },
  chipCheck: {
    position: 'absolute', top: -4, right: -4,
    width: 16, height: 16, borderRadius: 8,
    backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center',
  },
  btn: {
    width: '100%', backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  btnDisabled: { opacity: 0.6 },
  btnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
})
