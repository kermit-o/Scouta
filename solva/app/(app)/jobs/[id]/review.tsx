import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import {
  View, Text, StyleSheet, TouchableOpacity, TextInput,
  ActivityIndicator, ScrollView, Image
} from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import * as ImagePicker from 'expo-image-picker'
import { supabase } from '../../../../lib/supabase'
import { useProfile } from '../../../../hooks/useProfile'
import { useAuth } from '../../../../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const RATING_COLORS = ['', '#DC2626', '#F59E0B', '#D97706', '#2563EB', '#059669']

function StarRating({ rating, onRate }: { rating: number; onRate: (r: number) => void }) {
  return (
    <View style={s.starsRow}>
      {[1, 2, 3, 4, 5].map(star => (
        <TouchableOpacity key={star} onPress={() => onRate(star)} activeOpacity={0.7}>
          <Ionicons
            name={star <= rating ? 'star' : 'star-outline'}
            size={42}
            color={star <= rating ? '#F59E0B' : '#D1D5DB'}
          />
        </TouchableOpacity>
      ))}
    </View>
  )
}

export default function ReviewScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const { profile } = useProfile()
  const insets = useSafeAreaInsets()

  const { t } = useTranslation()
  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')
  const [photosBefore, setPhotosBefore] = useState<string[]>([])
  const [photosAfter, setPhotosAfter] = useState<string[]>([])
  const [uploading, setUploading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [verifyResult, setVerifyResult] = useState<any>(null)
  const [contract, setContract] = useState<any>(null)
  const [loaded, setLoaded] = useState(false)

  async function loadContract() {
    if (loaded) return
    const { data } = await supabase.from('contracts').select('*').eq('job_id', id).single()
    setContract(data)
    setLoaded(true)
  }

  useState(() => { loadContract() })

  async function pickPhotos(type: 'before' | 'after') {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
    if (status !== 'granted') return
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsMultipleSelection: true,
      quality: 0.7,
    })
    if (result.canceled || !result.assets.length) return
    setUploading(true)
    const urls: string[] = []
    for (const asset of result.assets) {
      const ext = asset.uri.split('.').pop() || 'jpg'
      const fileName = `${session!.user.id}/${id}/${type}_${Date.now()}.${ext}`
      const response = await fetch(asset.uri)
      const blob = await response.blob()
      const { error } = await supabase.storage
        .from('reviews').upload(fileName, blob, { upsert: true, contentType: `image/${ext}` })
      if (!error) {
        const { data: { publicUrl } } = supabase.storage.from('reviews').getPublicUrl(fileName)
        urls.push(publicUrl)
      }
    }
    if (type === 'before') setPhotosBefore(prev => [...prev, ...urls])
    else setPhotosAfter(prev => [...prev, ...urls])
    setUploading(false)
  }

  async function handleSubmit() {
    if (rating === 0) { setErrorMsg('Selecciona una puntuación.'); return }
    if (comment.trim().length < 20) { setErrorMsg('El comentario debe tener al menos 20 caracteres.'); return }
    if (!contract) { setErrorMsg('Contrato no encontrado.'); return }

    const reviewedId = contract.client_id === session!.user.id ? contract.pro_id : contract.client_id

    if (photosBefore.length > 0 || photosAfter.length > 0) {
      setVerifying(true)
      const { data: verifyData } = await supabase.functions.invoke('verify-photos', {
        body: { photos_before: photosBefore, photos_after: photosAfter, job_category: 'other', job_title: 'Servicio' }
      })
      setVerifyResult(verifyData?.result ?? null)
      setVerifying(false)
      if (verifyData?.result && !verifyData.result.is_valid) {
        setErrorMsg('Las fotos no parecen ser reales o relevantes al trabajo. Por favor sube fotos del trabajo realizado.')
        return
      }
    }

    setSaving(true)
    const { error } = await supabase.from('reviews').insert({
      contract_id: contract.id,
      job_id: id,
      reviewer_id: session!.user.id,
      reviewed_id: reviewedId,
      rating,
      comment: comment.trim(),
      photos_before: photosBefore,
      photos_after: photosAfter,
      photos_verified: verifyResult?.is_valid ?? false,
      photos_verify_result: verifyResult ?? null,
      photos_verified_at: verifyResult ? new Date().toISOString() : null,
    })
    setSaving(false)
    if (error) { setErrorMsg(error.message); return }
    else Alert.alert(t('review.thanks'), t('review.thanksDesc'), [
      { text: 'OK', onPress: () => router.replace('/(app)/jobs') }
    ])
  }

  if (!loaded) return <View style={s.center}><ActivityIndicator size="large" color="#2563EB" /></View>

  const canSubmit = rating > 0 && comment.trim().length >= 20 && !saving && !verifying

  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>{t('review.title')}</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={s.scroll} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled" showsVerticalScrollIndicator={false}>
        {/* Hero */}
        <View style={s.heroCard}>
          <View style={s.heroIcon}>
            <Ionicons name="star" size={32} color="#F59E0B" />
          </View>
          <Text style={s.heroTitle}>¿Cómo fue el trabajo?</Text>
          <Text style={s.heroDesc}>{t('review.subtitle')}</Text>
        </View>

        {/* Rating */}
        <View style={s.ratingCard}>
          <Text style={s.label}>{t('review.score')}</Text>
          <StarRating rating={rating} onRate={setRating} />
          {rating > 0 && (
            <View style={[s.ratingBadge, { backgroundColor: RATING_COLORS[rating] + '18' }]}>
              <Text style={[s.ratingBadgeText, { color: RATING_COLORS[rating] }]}>
                {RATING_LABELS[rating]}
              </Text>
            </View>
          )}
        </View>

        {/* Comentario */}
        <View style={s.card}>
          <Text style={s.label}>{t('review.comment')} * <Text style={s.labelSub}>{t('review.commentMin')}</Text></Text>
          <TextInput
            style={s.textarea}
            value={comment}
            onChangeText={setComment}
            placeholder={t("review.commentPlaceholder")}
            multiline
            numberOfLines={5}
            maxLength={500}
            textAlignVertical="top"
            placeholderTextColor="#bbb"
          />
          <Text style={[s.counter, comment.length >= 20 && s.counterOk]}>
            {comment.length}/500 {comment.length >= 20 ? '✓' : `(faltan ${20 - comment.length})`}
          </Text>
        </View>

        {/* Fotos */}
        {[
          { type: 'before' as const, label: t('review.photosBefore'), icon: 'camera-outline', color: '#7C3AED', bg: '#EDE9FE', photos: photosBefore },
          { type: 'after' as const, label: t('review.photosAfter'), icon: 'checkmark-circle-outline', color: '#059669', bg: '#D1FAE5', photos: photosAfter },
        ].map(item => (
          <View key={item.type} style={s.card}>
            <View style={s.photoLabelRow}>
              <View style={[s.photoLabelIcon, { backgroundColor: item.bg }]}>
                <Ionicons name={item.icon as any} size={16} color={item.color} />
              </View>
              <Text style={s.label}>{item.label}</Text>
              <Text style={s.photoCount}>{item.photos.length} foto{item.photos.length !== 1 ? 's' : ''}</Text>
            </View>

            {item.photos.length > 0 && (
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.photoRow}>
                {item.photos.map((url, i) => (
                  <Image key={i} source={{ uri: url }} style={s.photo} />
                ))}
              </ScrollView>
            )}

            <TouchableOpacity
              style={[s.uploadBtn, { borderColor: item.color + '40', backgroundColor: item.bg + '60' }]}
              onPress={() => pickPhotos(item.type)}
              disabled={uploading}
              activeOpacity={0.8}
            >
              {uploading
                ? <ActivityIndicator size="small" color={item.color} />
                : <>
                    <Ionicons name="cloud-upload-outline" size={18} color={item.color} />
                    <Text style={[s.uploadBtnText, { color: item.color }]}>{t('review.addPhotos')}</Text>
                  </>
              }
            </TouchableOpacity>
          </View>
        ))}

        {/* Info verificación IA */}
        <View style={s.aiNote}>
          <Ionicons name="sparkles" size={16} color="#2563EB" />
          <Text style={s.aiNoteText}>Las fotos son verificadas con IA para garantizar autenticidad</Text>
        </View>

        {verifying && (
          <View style={s.verifyingCard}>
            <ActivityIndicator size="small" color="#2563EB" />
            <Text style={s.verifyingText}>Verificando fotos con IA...</Text>
          </View>
        )}
      </ScrollView>

      <View style={[s.footer, { paddingBottom: insets.bottom + 16 }]}>
        <TouchableOpacity
          style={[s.footerBtn, !canSubmit && s.footerBtnDisabled]}
          onPress={handleSubmit}
          disabled={!canSubmit}
          activeOpacity={0.85}
        >
          {saving || verifying
            ? <ActivityIndicator color="#fff" />
            : <>
                <Ionicons name="star" size={20} color="#fff" />
                <Text style={s.footerBtnText}>Publicar reseña</Text>
              </>
          }
        </TouchableOpacity>
      </View>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' },
  scroll: { flex: 1 },
  content: { paddingHorizontal: 20, paddingBottom: 24, gap: 14 },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  headerTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  heroCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 24,
    alignItems: 'center', gap: 8,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  heroIcon: {
    width: 72, height: 72, borderRadius: 20,
    backgroundColor: '#FFFBEB', alignItems: 'center', justifyContent: 'center',
    marginBottom: 4,
    shadowColor: '#F59E0B', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.2, shadowRadius: 16, elevation: 3,
  },
  heroTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  heroDesc: { fontSize: 14, color: '#888' },
  ratingCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20,
    alignItems: 'center', gap: 14,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  starsRow: { flexDirection: 'row', gap: 10 },
  ratingBadge: { paddingHorizontal: 16, paddingVertical: 6, borderRadius: 20 },
  ratingBadgeText: { fontSize: 14, fontWeight: '700' },
  card: {
    backgroundColor: '#fff', borderRadius: 20, padding: 18, gap: 12,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
  },
  label: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  labelSub: { fontWeight: '400', color: '#888' },
  textarea: {
    borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 14,
    padding: 14, fontSize: 15, color: '#1a1a2e',
    minHeight: 120, backgroundColor: '#F9FAFB', lineHeight: 22,
  },
  counter: { fontSize: 12, color: '#bbb', textAlign: 'right' },
  counterOk: { color: '#059669', fontWeight: '600' },
  photoLabelRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  photoLabelIcon: {
    width: 30, height: 30, borderRadius: 8,
    alignItems: 'center', justifyContent: 'center',
  },
  photoCount: { marginLeft: 'auto', fontSize: 12, color: '#888', fontWeight: '600' },
  photoRow: { marginBottom: 4 },
  photo: { width: 88, height: 88, borderRadius: 12, marginRight: 10 },
  uploadBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    borderWidth: 1.5, borderStyle: 'dashed', borderRadius: 14,
    paddingVertical: 14,
  },
  uploadBtnText: { fontSize: 14, fontWeight: '600' },
  aiNote: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    backgroundColor: '#EEF4FF', borderRadius: 12, padding: 12,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  aiNoteText: { flex: 1, fontSize: 12, color: '#555', lineHeight: 17 },
  verifyingCard: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: '#fff', borderRadius: 14, padding: 16,
    borderWidth: 1, borderColor: '#DBEAFE',
  },
  verifyingText: { fontSize: 14, color: '#2563EB', fontWeight: '600' },
  footer: { paddingHorizontal: 20, paddingTop: 12, borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)' },
  footerBtn: {
    backgroundColor: '#2563EB', borderRadius: 16, height: 56,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  footerBtnDisabled: { opacity: 0.45, shadowOpacity: 0 },
  footerBtnText: { fontSize: 16, fontWeight: '700', color: '#fff' },
})
