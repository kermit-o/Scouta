import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, ActivityIndicator
} from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORIES = [
  { key: 'cleaning',   label: '🧹 Limpieza'       },
  { key: 'plumbing',   label: '🔧 Fontanería'      },
  { key: 'electrical', label: '⚡ Electricidad'     },
  { key: 'painting',   label: '🎨 Pintura'         },
  { key: 'moving',     label: '📦 Mudanzas'        },
  { key: 'gardening',  label: '🌿 Jardinería'      },
  { key: 'carpentry',  label: '🪚 Carpintería'     },
  { key: 'tech',       label: '💻 Informática'     },
  { key: 'design',     label: '✏️ Diseño'          },
  { key: 'other',      label: '🔹 Otros servicios' },
]

const COUNTRY_LANG: Record<string, string> = {
  ES: 'es', MX: 'es', CO: 'es', AR: 'es', CL: 'es',
  FR: 'fr', BE: 'fr',
  BR: 'pt', PT: 'pt',
  GB: 'en', NL: 'en', DE: 'en', IT: 'en',
}

interface Generated {
  profile_title: string
  short_description: string
  long_description: string
  keywords: string[]
  bid_template: string
  usp: string
  quality_tips: string[]
  quality_score: number
}

export default function ProContentScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const { profile, refreshProfile } = useProfile()

  const { t } = useTranslation()
  const [step, setStep] = useState<'form' | 'result'>('form')
  const [category, setCategory] = useState('')
  const [specialty, setSpecialty] = useState('')
  const [years, setYears] = useState('')
  const [avgPrice, setAvgPrice] = useState('')
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [result, setResult] = useState<Generated | null>(null)
  const [applying, setApplying] = useState(false)
  const [applied, setApplied] = useState(false)

  async function handleGenerate() {
    if (!category) { setErrorMsg('Selecciona una categoría.'); return }
    setErrorMsg('')
    setLoading(true)

    const { data, error } = await supabase.functions.invoke('generate-pro-content', {
      body: {
        user_id: session!.user.id,
        category,
        specialty: specialty.trim() || null,
        years_experience: years ? parseInt(years) : 1,
        city: profile?.city ?? null,
        avg_price: avgPrice ? parseFloat(avgPrice) : null,
        currency: profile?.currency ?? 'EUR',
        language: COUNTRY_LANG[profile?.country ?? 'ES'] ?? 'es',
      }
    })

    setLoading(false)

    if (error || data?.error) {
      if (data?.upgrade_required) {
        router.push('/(app)/subscription')
        return
      }
      setErrorMsg(error?.message ?? data?.error ?? 'Error generando contenido')
      return
    }

    setResult(data as Generated)
    setStep('result')
  }

  async function handleApply() {
    if (!result) return
    setApplying(true)
    const { error } = await supabase.from('users').update({
      bio: result.long_description,
      ai_keywords: result.keywords,
      ai_description_generated: true,
    }).eq('id', session!.user.id)
    setApplying(false)
    if (!error) {
      setApplied(true)
      refreshProfile?.()
    }
  }

  if (step === 'result' && result) {
    return (
      <View style={[s.screen, { paddingTop: insets.top }]}>
        <View style={s.header}>
          <TouchableOpacity style={s.backBtn} onPress={() => setStep('form')}>
            <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
          </TouchableOpacity>
          <Text style={s.headerTitle}>{t('proContent.title')}</Text>
          <View style={{ width: 40 }} />
        </View>

        <ScrollView contentContainerStyle={s.container} showsVerticalScrollIndicator={false}>
          {/* Quality score */}
          <View style={s.scoreCard}>
            <View style={s.scoreLeft}>
              <Text style={s.scoreTitle}>{t('proContent.score')}</Text>
              <Text style={s.scoreDesc}>{t('proContent.scoreDesc')}</Text>
            </View>
            <View style={s.scoreCircle}>
              <Text style={s.scoreValue}>{result.quality_score}</Text>
              <Text style={s.scoreMax}>/100</Text>
            </View>
          </View>

          {/* USP */}
          <View style={s.uspCard}>
            <Ionicons name="sparkles" size={16} color="#7C3AED" />
            <Text style={s.uspText}>"{result.usp}"</Text>
          </View>

          {/* Título */}
          <View style={s.resultSection}>
            <Text style={s.resultLabel}>{t('proContent.profileTitle')}</Text>
            <View style={s.resultBox}>
              <Text style={s.resultText}>{result.profile_title}</Text>
            </View>
          </View>

          {/* Descripción corta */}
          <View style={s.resultSection}>
            <Text style={s.resultLabel}>{t('proContent.searchDesc')}</Text>
            <View style={s.resultBox}>
              <Text style={s.resultText}>{result.short_description}</Text>
            </View>
            <Text style={s.charHint}>{result.short_description.length}/140 chars</Text>
          </View>

          {/* Descripción larga */}
          <View style={s.resultSection}>
            <Text style={s.resultLabel}>{t('proContent.fullDesc')}</Text>
            <View style={s.resultBox}>
              <Text style={s.resultText}>{result.long_description}</Text>
            </View>
          </View>

          {/* Keywords */}
          <View style={s.resultSection}>
            <Text style={s.resultLabel}>{t('proContent.keywords')}</Text>
            <View style={s.keywordsRow}>
              {result.keywords.map((kw, i) => (
                <View key={i} style={s.kwChip}>
                  <Text style={s.kwText}>{kw}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Plantilla bid */}
          <View style={s.resultSection}>
            <Text style={s.resultLabel}>{t('proContent.bidTemplate')}</Text>
            <View style={[s.resultBox, s.resultBoxBlue]}>
              <Text style={s.resultTextBlue}>{result.bid_template}</Text>
            </View>
            <Text style={s.charHint}>Editable antes de enviar cada bid</Text>
          </View>

          {/* Tips */}
          <View style={s.tipsCard}>
            <View style={s.tipsHeader}>
              <Ionicons name="bulb-outline" size={16} color="#D97706" />
              <Text style={s.tipsTitle}>Consejos para mejorar tu perfil</Text>
            </View>
            {result.quality_tips.map((tip, i) => (
              <View key={i} style={s.tipRow}>
                <Text style={s.tipNum}>{i + 1}</Text>
                <Text style={s.tipText}>{tip}</Text>
              </View>
            ))}
          </View>

          <View style={{ height: 20 }} />
        </ScrollView>

        {/* Footer */}
        <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
          {applied ? (
            <View style={s.appliedRow}>
              <Ionicons name="checkmark-circle" size={22} color="#059669" />
              <Text style={s.appliedText}>Perfil actualizado con IA ✅</Text>
            </View>
          ) : (
            <TouchableOpacity
              style={[s.applyBtn, applying && s.applyBtnDisabled]}
              onPress={handleApply}
              disabled={applying}
              activeOpacity={0.85}
            >
              {applying
                ? <ActivityIndicator color="#fff" />
                : <>
                    <Ionicons name="checkmark-circle-outline" size={20} color="#fff" />
                    <Text style={s.applyBtnText}>Aplicar a mi perfil</Text>
                  </>
              }
            </TouchableOpacity>
          )}
          <TouchableOpacity style={s.regenBtn} onPress={() => { setStep('form'); setResult(null); setApplied(false) }}>
            <Text style={s.regenText}>Regenerar con otros datos</Text>
          </TouchableOpacity>
        </View>
      </View>
    )
  }

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Perfil con IA</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={s.container} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>

        {/* Hero */}
        <View style={s.heroCard}>
          <Text style={s.heroEmoji}>✨</Text>
          <View style={{ flex: 1 }}>
            <Text style={s.heroTitle}>Descripción profesional en 30 segundos</Text>
            <Text style={s.heroDesc}>La IA genera tu perfil optimizado para SEO. Más visibilidad, más contratos.</Text>
          </View>
        </View>

        {errorMsg ? <View style={s.errorBox}><Text style={s.errorText}>⚠️ {errorMsg}</Text></View> : null}

        {/* Categoría */}
        <Text style={s.label}>¿A qué te dedicas? *</Text>
        <View style={s.categoriesGrid}>
          {CATEGORIES.map(c => (
            <TouchableOpacity
              key={c.key}
              style={[s.catChip, category === c.key && s.catChipActive]}
              onPress={() => setCategory(c.key)}
              activeOpacity={0.7}
            >
              <Text style={[s.catText, category === c.key && s.catTextActive]}>{c.label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Especialidad */}
        <Text style={s.label}>Especialidad (opcional)</Text>
        <View style={s.inputRow}>
          <Ionicons name="ribbon-outline" size={18} color="#888" />
          <TextInput
            style={s.input}
            value={specialty}
            onChangeText={setSpecialty}
            placeholder="ej: baños y cocinas, instalaciones eléctricas..."
            placeholderTextColor="#aaa"
          />
        </View>

        {/* Años */}
        <Text style={s.label}>Años de experiencia</Text>
        <View style={s.inputRow}>
          <Ionicons name="time-outline" size={18} color="#888" />
          <TextInput
            style={s.input}
            value={years}
            onChangeText={setYears}
            placeholder="ej: 5"
            placeholderTextColor="#aaa"
            keyboardType="numeric"
          />
        </View>

        {/* Precio medio */}
        <Text style={s.label}>Precio medio por servicio ({profile?.currency ?? 'EUR'})</Text>
        <View style={s.inputRow}>
          <Ionicons name="cash-outline" size={18} color="#888" />
          <TextInput
            style={s.input}
            value={avgPrice}
            onChangeText={setAvgPrice}
            placeholder="ej: 80"
            placeholderTextColor="#aaa"
            keyboardType="numeric"
          />
        </View>

        {/* Info */}
        <View style={s.infoCard}>
          {[
            'Título de perfil optimizado',
            'Descripción corta para búsquedas',
            'Descripción completa del perfil',
            '5 keywords SEO para posicionarte',
            'Plantilla de respuesta a bids',
          ].map((item, i) => (
            <View key={i} style={s.infoRow}>
              <Ionicons name="checkmark-circle" size={16} color="#2563EB" />
              <Text style={s.infoText}>{item}</Text>
            </View>
          ))}
        </View>

        <View style={{ height: 100 }} />
      </ScrollView>

      <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
        <TouchableOpacity
          style={[s.generateBtn, (!category || loading) && s.generateBtnDisabled]}
          onPress={handleGenerate}
          disabled={!category || loading}
          activeOpacity={0.85}
        >
          {loading
            ? <>
                <ActivityIndicator color="#fff" size="small" />
                <Text style={s.generateBtnText}>Generando con IA...</Text>
              </>
            : <>
                <Ionicons name="sparkles" size={20} color="#fff" />
                <Text style={s.generateBtnText}>Generar mi perfil con IA</Text>
              </>
          }
        </TouchableOpacity>
      </View>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14 },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: '#E5E7EB' },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  container: { paddingHorizontal: 20, paddingBottom: 20, gap: 10 },
  heroCard: { flexDirection: 'row', alignItems: 'flex-start', gap: 14, backgroundColor: '#EEF4FF', borderRadius: 18, padding: 18, borderWidth: 1, borderColor: '#DBEAFE' },
  heroEmoji: { fontSize: 32 },
  heroTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  heroDesc: { fontSize: 13, color: '#555', lineHeight: 19 },
  errorBox: { backgroundColor: '#FEF2F2', borderRadius: 12, padding: 14 },
  errorText: { color: '#DC2626', fontSize: 13, fontWeight: '500' },
  label: { fontSize: 13, fontWeight: '700', color: '#555', marginTop: 6 },
  categoriesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  catChip: { borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB' },
  catChipActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  catText: { fontSize: 13, fontWeight: '500', color: '#374151' },
  catTextActive: { color: '#fff' },
  inputRow: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#fff', borderRadius: 14, paddingHorizontal: 14, borderWidth: 1, borderColor: '#E5E7EB' },
  input: { flex: 1, paddingVertical: 14, fontSize: 15, color: '#1a1a2e' },
  infoCard: { backgroundColor: '#F0FDF4', borderRadius: 16, padding: 16, gap: 10, borderWidth: 1, borderColor: '#BBF7D0' },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  infoText: { fontSize: 13, color: '#374151' },
  footer: { paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)', backgroundColor: '#fff', gap: 10 },
  generateBtn: { backgroundColor: '#7C3AED', borderRadius: 16, height: 56, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, shadowColor: '#7C3AED', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.3, shadowRadius: 14, elevation: 6 },
  generateBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  generateBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  // Result
  scoreCard: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#1a1a2e', borderRadius: 20, padding: 20 },
  scoreLeft: { flex: 1 },
  scoreTitle: { fontSize: 15, fontWeight: '700', color: '#fff' },
  scoreDesc: { fontSize: 12, color: '#9CA3AF', marginTop: 3 },
  scoreCircle: { width: 64, height: 64, borderRadius: 32, backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center' },
  scoreValue: { fontSize: 22, fontWeight: '800', color: '#fff' },
  scoreMax: { fontSize: 10, color: 'rgba(255,255,255,0.6)' },
  uspCard: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#F5F3FF', borderRadius: 14, padding: 14, borderWidth: 1, borderColor: '#DDD6FE' },
  uspText: { flex: 1, fontSize: 14, fontWeight: '600', color: '#7C3AED', fontStyle: 'italic' },
  resultSection: { gap: 6 },
  resultLabel: { fontSize: 12, fontWeight: '700', color: '#888' },
  resultBox: { backgroundColor: '#fff', borderRadius: 14, padding: 14, borderWidth: 1, borderColor: '#E5E7EB' },
  resultBoxBlue: { backgroundColor: '#EEF4FF', borderColor: '#DBEAFE' },
  resultText: { fontSize: 14, color: '#1a1a2e', lineHeight: 21 },
  resultTextBlue: { fontSize: 14, color: '#2563EB', lineHeight: 21 },
  charHint: { fontSize: 11, color: '#aaa', textAlign: 'right' },
  keywordsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  kwChip: { backgroundColor: '#EEF4FF', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 6 },
  kwText: { fontSize: 12, fontWeight: '600', color: '#2563EB' },
  tipsCard: { backgroundColor: '#FFFBEB', borderRadius: 16, padding: 16, gap: 12, borderWidth: 1, borderColor: '#FDE68A' },
  tipsHeader: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  tipsTitle: { fontSize: 13, fontWeight: '700', color: '#92400E' },
  tipRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 10 },
  tipNum: { width: 20, height: 20, borderRadius: 10, backgroundColor: '#D97706', color: '#fff', fontSize: 11, fontWeight: '800', textAlign: 'center', lineHeight: 20 },
  tipText: { flex: 1, fontSize: 13, color: '#78350F', lineHeight: 19 },
  applyBtn: { backgroundColor: '#059669', borderRadius: 16, height: 56, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, shadowColor: '#059669', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.25, shadowRadius: 10, elevation: 4 },
  applyBtnDisabled: { opacity: 0.5 },
  applyBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
  appliedRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10, height: 56 },
  appliedText: { fontSize: 15, fontWeight: '700', color: '#059669' },
  regenBtn: { alignItems: 'center', paddingVertical: 6 },
  regenText: { fontSize: 14, color: '#888' },
})
