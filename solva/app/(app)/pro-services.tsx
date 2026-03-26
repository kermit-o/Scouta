import React, { useEffect, useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, ActivityIndicator, Alert } from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { supabase, ProService } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'

const CATEGORIES = [
  { key: 'plumbing', label: '🔧 Fontanería' },
  { key: 'electrical', label: '⚡ Electricidad' },
  { key: 'cleaning', label: '🧹 Limpieza' },
  { key: 'painting', label: '🎨 Pintura' },
  { key: 'gardening', label: '🌿 Jardinería' },
  { key: 'moving', label: '📦 Mudanzas' },
  { key: 'carpentry', label: '🪚 Carpintería' },
  { key: 'hvac', label: '❄️ Climatización' },
  { key: 'other', label: '🔹 Otros' },
]

const PRICE_TYPES = [
  { key: 'fixed', label: 'Precio fijo' },
  { key: 'from', label: 'Desde' },
  { key: 'hourly', label: 'Por hora' },
  { key: 'quote', label: 'Presupuesto' },
]

const EMPTY: Partial<ProService> = {
  title: '', description: '', price_from: undefined, price_to: undefined,
  price_type: 'fixed', category: '', duration_hours: undefined, is_active: true,
}

export default function ProServicesScreen() {
  const insets = useSafeAreaInsets()
  const { session } = useAuth()
  const [services, setServices] = useState<ProService[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [editing, setEditing] = useState<Partial<ProService> | null>(null)
  const [isNew, setIsNew] = useState(false)

  useEffect(() => { loadServices() }, [session])

  async function loadServices() {
    if (!session?.user?.id) return
    const { data } = await supabase
      .from('pro_services')
      .select('*')
      .eq('pro_id', session.user.id)
      .order('created_at', { ascending: false })
    setServices(data ?? [])
    setLoading(false)
  }

  async function handleSave() {
    if (!editing?.title?.trim()) { Alert.alert('Error', 'El título es obligatorio'); return }
    setSaving(true)
    const payload = {
      pro_id: session!.user.id,
      title: editing.title!.trim(),
      description: editing.description?.trim() || null,
      price_from: editing.price_from ?? null,
      price_to: editing.price_to ?? null,
      price_type: editing.price_type ?? 'fixed',
      category: editing.category || null,
      duration_hours: editing.duration_hours ?? null,
      is_active: editing.is_active ?? true,
    }
    if (isNew) {
      await supabase.from('pro_services').insert(payload)
    } else {
      await supabase.from('pro_services').update(payload).eq('id', editing.id!)
    }
    setSaving(false)
    setEditing(null)
    loadServices()
  }

  async function handleDelete(id: string) {
    Alert.alert('Eliminar servicio', '¿Seguro?', [
      { text: 'Cancelar', style: 'cancel' },
      { text: 'Eliminar', style: 'destructive', onPress: async () => {
        await supabase.from('pro_services').delete().eq('id', id)
        loadServices()
      }},
    ])
  }

  async function toggleActive(svc: ProService) {
    await supabase.from('pro_services').update({ is_active: !svc.is_active }).eq('id', svc.id)
    loadServices()
  }

  function priceLabel(svc: ProService) {
    if (svc.price_type === 'quote') return 'Presupuesto'
    if (svc.price_type === 'hourly' && svc.price_from) return `${svc.price_from}€/h`
    if (svc.price_type === 'from' && svc.price_from) return `desde ${svc.price_from}€`
    if (svc.price_from && svc.price_to) return `${svc.price_from}–${svc.price_to}€`
    if (svc.price_from) return `${svc.price_from}€`
    return '—'
  }

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity onPress={() => router.back()} style={s.backBtn}>
          <Ionicons name="arrow-back" size={22} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Mis servicios</Text>
        <TouchableOpacity style={s.addBtn} onPress={() => { setEditing({ ...EMPTY }); setIsNew(true) }}>
          <Ionicons name="add" size={22} color="#fff" />
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={s.center}><ActivityIndicator color="#2563EB" /></View>
      ) : (
        <ScrollView contentContainerStyle={s.list} showsVerticalScrollIndicator={false}>
          {services.length === 0 && (
            <View style={s.empty}>
              <Text style={s.emptyEmoji}>🛠️</Text>
              <Text style={s.emptyTitle}>Sin servicios aún</Text>
              <Text style={s.emptySub}>Añade los servicios que ofreces con sus precios</Text>
              <TouchableOpacity style={s.emptyBtn} onPress={() => { setEditing({ ...EMPTY }); setIsNew(true) }}>
                <Text style={s.emptyBtnText}>+ Añadir primer servicio</Text>
              </TouchableOpacity>
            </View>
          )}
          {services.map(svc => (
            <View key={svc.id} style={[s.card, !svc.is_active && s.cardInactive]}>
              <View style={s.cardRow}>
                <View style={{ flex: 1 }}>
                  <View style={s.cardTop}>
                    <Text style={s.cardTitle}>{svc.title}</Text>
                    {!svc.is_active && (
                      <View style={s.inactiveBadge}><Text style={s.inactiveBadgeText}>Inactivo</Text></View>
                    )}
                  </View>
                  {svc.description && <Text style={s.cardDesc} numberOfLines={2}>{svc.description}</Text>}
                  <View style={s.cardMeta}>
                    {svc.category && <Text style={s.cardCat}>{CATEGORIES.find(c => c.key === svc.category)?.label ?? svc.category}</Text>}
                    {svc.duration_hours && <Text style={s.cardTime}>⏱ {svc.duration_hours}h</Text>}
                  </View>
                </View>
                <Text style={s.cardPrice}>{priceLabel(svc)}</Text>
              </View>
              <View style={s.cardActions}>
                <TouchableOpacity style={s.actionBtn} onPress={() => { setEditing({ ...svc }); setIsNew(false) }}>
                  <Ionicons name="pencil-outline" size={14} color="#2563EB" />
                  <Text style={s.actionBtnText}>Editar</Text>
                </TouchableOpacity>
                <TouchableOpacity style={s.actionBtn} onPress={() => toggleActive(svc)}>
                  <Ionicons name={svc.is_active ? 'eye-off-outline' : 'eye-outline'} size={14} color="#888" />
                  <Text style={[s.actionBtnText, { color: '#888' }]}>{svc.is_active ? 'Desactivar' : 'Activar'}</Text>
                </TouchableOpacity>
                <TouchableOpacity style={s.actionBtn} onPress={() => handleDelete(svc.id)}>
                  <Ionicons name="trash-outline" size={14} color="#DC2626" />
                  <Text style={[s.actionBtnText, { color: '#DC2626' }]}>Eliminar</Text>
                </TouchableOpacity>
              </View>
            </View>
          ))}
        </ScrollView>
      )}

      {/* Modal edición */}
      {editing && (
        <View style={s.modalOverlay}>
          <View style={s.modalBox}>
            <View style={s.modalHeader}>
              <Text style={s.modalTitle}>{isNew ? 'Nuevo servicio' : 'Editar servicio'}</Text>
              <TouchableOpacity onPress={() => setEditing(null)}>
                <Ionicons name="close" size={22} color="#888" />
              </TouchableOpacity>
            </View>
            <ScrollView showsVerticalScrollIndicator={false}>
              <Text style={s.label}>Título *</Text>
              <TextInput style={s.input} value={editing.title} onChangeText={v => setEditing(e => ({ ...e!, title: v }))} placeholder="Ej: Reparación de fugas" placeholderTextColor="#aaa" />

              <Text style={s.label}>Descripción</Text>
              <TextInput style={[s.input, { height: 70, textAlignVertical: 'top' }]} value={editing.description ?? ''} onChangeText={v => setEditing(e => ({ ...e!, description: v }))} placeholder="Describe el servicio..." placeholderTextColor="#aaa" multiline />

              <Text style={s.label}>Categoría</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 12 }}>
                {CATEGORIES.map(c => (
                  <TouchableOpacity key={c.key} style={[s.catChip, editing.category === c.key && s.catChipActive]} onPress={() => setEditing(e => ({ ...e!, category: c.key }))}>
                    <Text style={[s.catChipText, editing.category === c.key && s.catChipTextActive]}>{c.label}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>

              <Text style={s.label}>Tipo de precio</Text>
              <View style={s.priceTypeRow}>
                {PRICE_TYPES.map(pt => (
                  <TouchableOpacity key={pt.key} style={[s.priceTypeBtn, editing.price_type === pt.key && s.priceTypeBtnActive]} onPress={() => setEditing(e => ({ ...e!, price_type: pt.key as any }))}>
                    <Text style={[s.priceTypeBtnText, editing.price_type === pt.key && s.priceTypeBtnTextActive]}>{pt.label}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              {editing.price_type !== 'quote' && (
                <View style={s.priceRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={s.label}>{editing.price_type === 'from' ? 'Precio desde (€)' : 'Precio (€)'}</Text>
                    <TextInput style={s.input} value={editing.price_from?.toString() ?? ''} onChangeText={v => setEditing(e => ({ ...e!, price_from: v ? parseFloat(v) : undefined }))} placeholder="0" placeholderTextColor="#aaa" keyboardType="numeric" />
                  </View>
                  {editing.price_type === 'fixed' && (
                    <View style={{ flex: 1, marginLeft: 8 }}>
                      <Text style={s.label}>Hasta (€) — opcional</Text>
                      <TextInput style={s.input} value={editing.price_to?.toString() ?? ''} onChangeText={v => setEditing(e => ({ ...e!, price_to: v ? parseFloat(v) : undefined }))} placeholder="0" placeholderTextColor="#aaa" keyboardType="numeric" />
                    </View>
                  )}
                </View>
              )}

              <Text style={s.label}>Duración estimada (horas)</Text>
              <TextInput style={s.input} value={editing.duration_hours?.toString() ?? ''} onChangeText={v => setEditing(e => ({ ...e!, duration_hours: v ? parseFloat(v) : undefined }))} placeholder="Ej: 2" placeholderTextColor="#aaa" keyboardType="numeric" />

              <TouchableOpacity style={[s.saveBtn, saving && { opacity: 0.6 }]} onPress={handleSave} disabled={saving}>
                {saving ? <ActivityIndicator color="#fff" /> : <Text style={s.saveBtnText}>{isNew ? 'Añadir servicio' : 'Guardar cambios'}</Text>}
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      )}
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.06)' },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  addBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center' },
  list: { padding: 16, gap: 12 },
  empty: { alignItems: 'center', paddingVertical: 48, gap: 8 },
  emptyEmoji: { fontSize: 48 },
  emptyTitle: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  emptySub: { fontSize: 14, color: '#888', textAlign: 'center' },
  emptyBtn: { marginTop: 8, backgroundColor: '#2563EB', borderRadius: 14, paddingHorizontal: 24, paddingVertical: 12 },
  emptyBtnText: { fontSize: 14, fontWeight: '700', color: '#fff' },
  card: { backgroundColor: '#fff', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: 'rgba(0,0,0,0.06)', gap: 10 },
  cardInactive: { opacity: 0.55 },
  cardRow: { flexDirection: 'row', gap: 12, alignItems: 'flex-start' },
  cardTop: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 4 },
  cardTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e' },
  inactiveBadge: { backgroundColor: '#F3F4F6', borderRadius: 6, paddingHorizontal: 6, paddingVertical: 2 },
  inactiveBadgeText: { fontSize: 10, color: '#888' },
  cardDesc: { fontSize: 13, color: '#666', lineHeight: 18 },
  cardMeta: { flexDirection: 'row', gap: 8, marginTop: 6 },
  cardCat: { fontSize: 12, color: '#888' },
  cardTime: { fontSize: 12, color: '#888' },
  cardPrice: { fontSize: 16, fontWeight: '800', color: '#2563EB', flexShrink: 0 },
  cardActions: { flexDirection: 'row', gap: 8, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)', paddingTop: 10 },
  actionBtn: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: 10, paddingVertical: 6, borderRadius: 8, backgroundColor: '#F8F9FC' },
  actionBtnText: { fontSize: 12, fontWeight: '600', color: '#2563EB' },
  modalOverlay: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalBox: { backgroundColor: '#fff', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, maxHeight: '90%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  modalTitle: { fontSize: 18, fontWeight: '700', color: '#1a1a2e' },
  label: { fontSize: 12, fontWeight: '700', color: '#555', marginBottom: 6, marginTop: 12 },
  input: { backgroundColor: '#F8F9FC', borderRadius: 12, paddingHorizontal: 14, paddingVertical: 12, fontSize: 14, color: '#1a1a2e', borderWidth: 1, borderColor: '#E5E7EB' },
  catChip: { backgroundColor: '#F3F4F6', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 7, marginRight: 8, borderWidth: 1, borderColor: 'transparent' },
  catChipActive: { backgroundColor: '#EEF4FF', borderColor: '#2563EB' },
  catChipText: { fontSize: 12, color: '#555' },
  catChipTextActive: { color: '#2563EB', fontWeight: '700' },
  priceTypeRow: { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginBottom: 4 },
  priceTypeBtn: { borderRadius: 10, paddingHorizontal: 12, paddingVertical: 7, borderWidth: 1, borderColor: '#E5E7EB', backgroundColor: '#F8F9FC' },
  priceTypeBtnActive: { backgroundColor: '#EEF4FF', borderColor: '#2563EB' },
  priceTypeBtnText: { fontSize: 12, color: '#555' },
  priceTypeBtnTextActive: { color: '#2563EB', fontWeight: '700' },
  priceRow: { flexDirection: 'row', gap: 8 },
  saveBtn: { backgroundColor: '#2563EB', borderRadius: 14, paddingVertical: 15, alignItems: 'center', marginTop: 20, marginBottom: 8 },
  saveBtnText: { fontSize: 15, fontWeight: '700', color: '#fff' },
})