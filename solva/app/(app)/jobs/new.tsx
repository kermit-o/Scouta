import { useState } from 'react'
import {
  View, Text, StyleSheet, ScrollView, TouchableOpacity,
  TextInput, ActivityIndicator, Switch
} from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../../lib/supabase'
import { useAuth } from '../../../lib/AuthContext'
import { useProfile } from '../../../hooks/useProfile'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORIES = [
  { key: 'cleaning',   label: '🧹 Limpieza' },
  { key: 'plumbing',   label: '🔧 Fontanería' },
  { key: 'electrical', label: '⚡ Electricidad' },
  { key: 'painting',   label: '🎨 Pintura' },
  { key: 'moving',     label: '📦 Mudanza' },
  { key: 'gardening',  label: '🌿 Jardinería' },
  { key: 'carpentry',  label: '🪚 Carpintería' },
  { key: 'tech',       label: '💻 Tecnología' },
  { key: 'design',     label: '✏️ Diseño' },
  { key: 'other',      label: '🔹 Otro' },
]

export default function NewJobScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const { profile } = useProfile()

  const [title, setTitle]           = useState('')
  const [description, setDesc]      = useState('')
  const [category, setCategory]     = useState('')
  const [city, setCity]             = useState('')
  const [budgetMin, setBudgetMin]   = useState('')
  const [budgetMax, setBudgetMax]   = useState('')
  const [isRemote, setIsRemote]     = useState(false)
  const [loading, setLoading]       = useState(false)
  const [errorMsg, setErrorMsg]     = useState('')

  async function handlePublish() {
    setErrorMsg('')
    if (!title.trim())       { setErrorMsg('El título es obligatorio.'); return }
    if (!description.trim()) { setErrorMsg('La descripción es obligatoria.'); return }
    if (!category)           { setErrorMsg('Selecciona una categoría.'); return }
    if (!isRemote && !city.trim()) { setErrorMsg('Indica la ciudad o marca como remoto.'); return }

    setLoading(true)
    const { data, error } = await supabase.from('jobs').insert({
      client_id:   session!.user.id,
      title:       title.trim(),
      description: description.trim(),
      category,
      city:        city.trim() || null,
      budget_min:  budgetMin ? parseFloat(budgetMin) : null,
      budget_max:  budgetMax ? parseFloat(budgetMax) : null,
      currency:    profile?.currency ?? 'EUR',
      country:     profile?.country  ?? 'ES',
      is_remote:   isRemote,
      status:      'open',
    }).select().single()
    setLoading(false)

    if (error) {
      setErrorMsg('Error al publicar: ' + error.message)
    } else {
      router.replace(`/(app)/jobs/${data.id}`)
    }
  }

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Publicar trabajo</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView
        contentContainerStyle={s.container}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {errorMsg ? (
          <View style={s.errorBox}>
            <Text style={s.errorText}>⚠️ {errorMsg}</Text>
          </View>
        ) : null}

        {/* Título */}
        <Text style={s.label}>Título del trabajo *</Text>
        <View style={s.inputRow}>
          <Ionicons name="briefcase-outline" size={18} color="#888" />
          <TextInput
            style={s.input}
            value={title}
            onChangeText={setTitle}
            placeholder="ej: Limpieza de hogar 3 habitaciones"
            placeholderTextColor="#aaa"
            maxLength={80}
          />
        </View>

        {/* Descripción */}
        <Text style={s.label}>Descripción *</Text>
        <TextInput
          style={s.textarea}
          value={description}
          onChangeText={setDesc}
          placeholder="Describe el trabajo con detalle: qué necesitas, cuándo, condiciones especiales..."
          placeholderTextColor="#aaa"
          multiline
          numberOfLines={5}
          textAlignVertical="top"
          maxLength={500}
        />
        <Text style={s.charCount}>{description.length}/500</Text>

        {/* Categoría */}
        <Text style={s.label}>Categoría *</Text>
        <View style={s.categoriesGrid}>
          {CATEGORIES.map(c => (
            <TouchableOpacity
              key={c.key}
              style={[s.categoryChip, category === c.key && s.categoryChipActive]}
              onPress={() => setCategory(c.key)}
              activeOpacity={0.7}
            >
              <Text style={[s.categoryText, category === c.key && s.categoryTextActive]}>
                {c.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Remoto toggle */}
        <View style={s.switchRow}>
          <View>
            <Text style={s.switchLabel}>Trabajo remoto</Text>
            <Text style={s.switchDesc}>No requiere presencia física</Text>
          </View>
          <Switch
            value={isRemote}
            onValueChange={setIsRemote}
            trackColor={{ false: '#E5E7EB', true: '#BFDBFE' }}
            thumbColor={isRemote ? '#2563EB' : '#9CA3AF'}
          />
        </View>

        {/* Ciudad */}
        {!isRemote && (
          <>
            <Text style={s.label}>Ciudad *</Text>
            <View style={s.inputRow}>
              <Ionicons name="location-outline" size={18} color="#888" />
              <TextInput
                style={s.input}
                value={city}
                onChangeText={setCity}
                placeholder="ej: Madrid, Barcelona..."
                placeholderTextColor="#aaa"
              />
            </View>
          </>
        )}

        {/* Presupuesto */}
        <Text style={s.label}>Presupuesto ({profile?.currency ?? 'EUR'})</Text>
        <View style={s.budgetRow}>
          <View style={[s.inputRow, { flex: 1 }]}>
            <Text style={s.budgetPrefix}>Mín</Text>
            <TextInput
              style={s.input}
              value={budgetMin}
              onChangeText={setBudgetMin}
              placeholder="0"
              placeholderTextColor="#aaa"
              keyboardType="numeric"
            />
          </View>
          <Text style={s.budgetDash}>—</Text>
          <View style={[s.inputRow, { flex: 1 }]}>
            <Text style={s.budgetPrefix}>Máx</Text>
            <TextInput
              style={s.input}
              value={budgetMax}
              onChangeText={setBudgetMax}
              placeholder="0"
              placeholderTextColor="#aaa"
              keyboardType="numeric"
            />
          </View>
        </View>
        <Text style={s.budgetHint}>Déjalo vacío si prefieres negociar directamente.</Text>

        {/* Escrow info */}
        <View style={s.escrowCard}>
          <Ionicons name="shield-checkmark" size={20} color="#2563EB" />
          <View style={{ flex: 1 }}>
            <Text style={s.escrowTitle}>Pago protegido con escrow</Text>
            <Text style={s.escrowDesc}>
              El pago queda retenido hasta que confirmas que el trabajo está completado. Tu dinero está seguro.
            </Text>
          </View>
        </View>

        <View style={{ height: 20 }} />
      </ScrollView>

      {/* Footer */}
      <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
        <TouchableOpacity
          style={[s.publishBtn, loading && s.publishBtnDisabled]}
          onPress={handlePublish}
          disabled={loading}
          activeOpacity={0.85}
        >
          {loading
            ? <ActivityIndicator color="#fff" />
            : <>
                <Ionicons name="checkmark-circle-outline" size={20} color="#fff" />
                <Text style={s.publishBtnText}>Publicar trabajo</Text>
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
  container: { paddingHorizontal: 20, paddingBottom: 20, gap: 8 },
  errorBox: { backgroundColor: '#FEF2F2', borderRadius: 12, padding: 14 },
  errorText: { color: '#DC2626', fontSize: 13, fontWeight: '500' },
  label: { fontSize: 13, fontWeight: '700', color: '#555', marginTop: 8 },
  inputRow: { flexDirection: 'row', alignItems: 'center', gap: 10, backgroundColor: '#fff', borderRadius: 14, paddingHorizontal: 14, borderWidth: 1, borderColor: '#E5E7EB' },
  input: { flex: 1, paddingVertical: 14, fontSize: 15, color: '#1a1a2e' },
  textarea: { backgroundColor: '#fff', borderRadius: 14, padding: 14, fontSize: 14, color: '#1a1a2e', borderWidth: 1, borderColor: '#E5E7EB', minHeight: 120, lineHeight: 22 },
  charCount: { fontSize: 11, color: '#aaa', textAlign: 'right', marginTop: -4 },
  categoriesGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 4 },
  categoryChip: { borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB' },
  categoryChipActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  categoryText: { fontSize: 13, fontWeight: '500', color: '#374151' },
  categoryTextActive: { color: '#fff' },
  switchRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#fff', borderRadius: 14, padding: 16, borderWidth: 1, borderColor: '#E5E7EB', marginTop: 8 },
  switchLabel: { fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  switchDesc: { fontSize: 12, color: '#9CA3AF', marginTop: 2 },
  budgetRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 4 },
  budgetPrefix: { fontSize: 12, fontWeight: '600', color: '#888' },
  budgetDash: { fontSize: 18, color: '#ccc' },
  budgetHint: { fontSize: 12, color: '#9CA3AF', marginTop: 4 },
  escrowCard: { flexDirection: 'row', alignItems: 'flex-start', gap: 12, backgroundColor: '#EEF4FF', borderRadius: 14, padding: 16, borderWidth: 1, borderColor: '#DBEAFE', marginTop: 8 },
  escrowTitle: { fontSize: 13, fontWeight: '700', color: '#1a1a2e', marginBottom: 4 },
  escrowDesc: { fontSize: 12, color: '#555', lineHeight: 18 },
  footer: { paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)', backgroundColor: '#fff' },
  publishBtn: { backgroundColor: '#2563EB', borderRadius: 16, height: 56, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8, shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.3, shadowRadius: 14, elevation: 6 },
  publishBtnDisabled: { opacity: 0.5, shadowOpacity: 0 },
  publishBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
})
