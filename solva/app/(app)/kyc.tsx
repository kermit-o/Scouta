import { useTranslation } from 'react-i18next'
import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  ActivityIndicator, Image
} from 'react-native'
import { router } from 'expo-router'
import * as ImagePicker from 'expo-image-picker'
import { supabase, KycDocType, KycVerification } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'

const DOC_TYPES: { label: string; value: KycDocType }[] = [
  { label: '🪪 DNI / Cédula', value: 'dni' },
  { label: '📘 Pasaporte', value: 'passport' },
  { label: '🏠 Permiso de residencia', value: 'residence_permit' },
  { label: '🚗 Licencia de conducir', value: 'drivers_license' },
]

const STATUS_INFO: Record<string, { label: string; color: string; desc: string }> = {
  pending:   { label: '⚪ Sin enviar',   color: '#999',    desc: 'Completa tu verificacion para acceder a todas las funciones' },
  submitted: { label: '🟡 En revision', color: '#f39c12', desc: 'Estamos revisando tus documentos. Tiempo estimado: 24-48h' },
  approved:  { label: '✅ Verificado',   color: '#2ecc71', desc: 'Tu identidad ha sido verificada correctamente' },
  rejected:  { label: '❌ Rechazado',    color: '#e74c3c', desc: 'Tu verificacion fue rechazada. Revisa el motivo y vuelve a intentarlo' },
}

export default function KycScreen() {
  const { session } = useAuth()
  const { profile, refreshProfile } = useProfile()
  const { t } = useTranslation()
  const [kyc, setKyc] = useState<KycVerification | null>(null)
  const [loading, setLoading] = useState(true)
  const [docType, setDocType] = useState<KycDocType>('dni')
  const [frontUrl, setFrontUrl] = useState('')
  const [backUrl, setBackUrl] = useState('')
  const [selfieUrl, setSelfieUrl] = useState('')
  const [uploading, setUploading] = useState('')
  const [saving, setSaving] = useState(false)

  async function loadKyc() {
    const { data } = await supabase
      .from('kyc_verifications')
      .select('*')
      .eq('user_id', session!.user.id)
      .maybeSingle()
    if (data) {
      setKyc(data as KycVerification)
      if (data.doc_type) setDocType(data.doc_type)
      if (data.doc_front_url) setFrontUrl(data.doc_front_url)
      if (data.doc_back_url) setBackUrl(data.doc_back_url)
      if (data.selfie_url) setSelfieUrl(data.selfie_url)
    }
    setLoading(false)
  }

  useEffect(() => { loadKyc() }, [])

  async function uploadDoc(type: 'front' | 'back' | 'selfie') {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
    if (status !== 'granted') return

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    })
    if (result.canceled || !result.assets[0]) return

    setUploading(type)
    const asset = result.assets[0]
    const ext = asset.uri.split('.').pop() || 'jpg'
    const fileName = `${session!.user.id}/${type}_${Date.now()}.${ext}`

    const response = await fetch(asset.uri)
    const blob = await response.blob()

    const { error } = await supabase.storage
      .from('kyc-docs')
      .upload(fileName, blob, { upsert: true, contentType: `image/${ext}` })

    if (!error) {
      const { data: { publicUrl } } = supabase.storage.from('kyc-docs').getPublicUrl(fileName)
      if (type === 'front') setFrontUrl(publicUrl)
      else if (type === 'back') setBackUrl(publicUrl)
      else setSelfieUrl(publicUrl)
    }
    setUploading('')
  }

  async function handleSubmit() {
    if (!frontUrl) { setErrorMsg('Sube la foto frontal del documento.'); return }
    if (!selfieUrl) { setErrorMsg('Sube una selfie con tu documento.'); return }

    setSaving(true)
    const payload = {
      user_id: session!.user.id,
      doc_type: docType,
      doc_front_url: frontUrl,
      doc_back_url: backUrl || null,
      selfie_url: selfieUrl,
      status: 'submitted' as const,
      submitted_at: new Date().toISOString(),
    }

    const { error } = kyc
      ? await supabase.from('kyc_verifications').update(payload).eq('user_id', session!.user.id)
      : await supabase.from('kyc_verifications').insert(payload)

    setSaving(false)
    if (error) {
      setErrorMsg(error.message)
    } else {
      Alert.alert('✅ Enviado', 'Revisaremos tus documentos en 24-48h', [
        { text: 'OK', onPress: () => { loadKyc(); router.back() } }
      ])
    }
  }

  if (loading) return <View style={s.center}><ActivityIndicator size="large" color="#1a1a2e" /></View>

  const statusInfo = STATUS_INFO[kyc?.status ?? 'pending']
  const canEdit = !kyc || kyc.status === 'pending' || kyc.status === 'rejected'

  return (
    <ScrollView contentContainerStyle={s.container} keyboardShouldPersistTaps="handled">
      <TouchableOpacity onPress={() => router.back()} style={s.back}>
        <Text style={s.backText}>← Volver</Text>
      </TouchableOpacity>

      <Text style={s.title}>🪪 Verificacion de identidad</Text>

      {/* Estado actual */}
      <View style={[s.statusCard, { borderColor: statusInfo.color }]}>
        <Text style={[s.statusLabel, { color: statusInfo.color }]}>{statusInfo.label}</Text>
        <Text style={s.statusDesc}>{statusInfo.desc}</Text>
        {kyc?.rejection_reason && (
          <Text style={s.rejection}>Motivo: {kyc.rejection_reason}</Text>
        )}
      </View>

      {canEdit && (
        <>
          {/* Tipo de documento */}
          <Text style={s.label}>{t('kyc.docType')}</Text>
          <View style={s.grid}>
            {DOC_TYPES.map(dt => (
              <TouchableOpacity
                key={dt.value}
                style={[s.chip, docType === dt.value && s.chipSelected]}
                onPress={() => setDocType(dt.value)}
              >
                <Text style={[s.chipText, docType === dt.value && s.chipTextSelected]}>
                  {dt.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Foto frontal */}
          <Text style={s.label}>{t('kyc.frontPhoto')}</Text>
          <TouchableOpacity style={s.uploadBtn} onPress={() => uploadDoc('front')} disabled={uploading === 'front'}>
            {frontUrl
              ? <Image source={{ uri: frontUrl }} style={s.docImage} />
              : <Text style={s.uploadText}>{uploading === 'front' ? t('kyc.uploading') : t('kyc.uploadFront')}</Text>
            }
          </TouchableOpacity>

          {/* Foto trasera */}
          <Text style={s.label}>{t('kyc.backPhoto')}</Text>
          <TouchableOpacity style={s.uploadBtn} onPress={() => uploadDoc('back')} disabled={uploading === 'back'}>
            {backUrl
              ? <Image source={{ uri: backUrl }} style={s.docImage} />
              : <Text style={s.uploadText}>{uploading === 'back' ? t('kyc.uploading') : t('kyc.uploadBack')}</Text>
            }
          </TouchableOpacity>

          {/* Selfie */}
          <Text style={s.label}>{t('kyc.selfie')}</Text>
          <TouchableOpacity style={[s.uploadBtn, s.selfieBtn]} onPress={() => uploadDoc('selfie')} disabled={uploading === 'selfie'}>
            {selfieUrl
              ? <Image source={{ uri: selfieUrl }} style={s.docImage} />
              : <Text style={s.uploadText}>{uploading === 'selfie' ? t('kyc.uploading') : t('kyc.uploadSelfie')}</Text>
            }
          </TouchableOpacity>

          <View style={s.infoBox}>
            <Text style={s.infoText}>
              🔒 Tus documentos son privados y se eliminan tras la verificacion.
              Solo son usados para confirmar tu identidad.
            </Text>
          </View>

          <TouchableOpacity
            style={[s.button, (saving || !frontUrl || !selfieUrl) && s.disabled]}
            onPress={handleSubmit}
            disabled={saving || !frontUrl || !selfieUrl}
          >
            {saving
              ? <ActivityIndicator color="#fff" />
              : <Text style={s.btnText}>{t('kyc.submit')}</Text>
            }
          </TouchableOpacity>
        </>
      )}
    </ScrollView>
  )
}

const s = StyleSheet.create({
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  container: { padding: 24, backgroundColor: '#fff', paddingBottom: 60 },
  back: { marginTop: 48, marginBottom: 8 },
  backText: { color: '#1a1a2e', fontSize: 16 },
  title: { fontSize: 26, fontWeight: '800', color: '#1a1a2e', marginBottom: 20 },
  statusCard: { borderWidth: 2, borderRadius: 16, padding: 16, marginBottom: 24, gap: 6 },
  statusLabel: { fontSize: 16, fontWeight: '800' },
  statusDesc: { fontSize: 14, color: '#555', lineHeight: 20 },
  rejection: { fontSize: 13, color: '#e74c3c', marginTop: 4 },
  label: { fontSize: 13, fontWeight: '700', color: '#666', marginBottom: 8, marginTop: 16 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chip: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#ddd', backgroundColor: '#f9f9f9' },
  chipSelected: { backgroundColor: '#1a1a2e', borderColor: '#1a1a2e' },
  chipText: { fontSize: 13, color: '#444' },
  chipTextSelected: { color: '#fff', fontWeight: '600' },
  uploadBtn: { borderWidth: 2, borderColor: '#ddd', borderStyle: 'dashed', borderRadius: 12, padding: 20, alignItems: 'center', backgroundColor: '#f9f9f9', minHeight: 80, justifyContent: 'center' },
  selfieBtn: { borderColor: '#1a1a2e' },
  uploadText: { fontSize: 15, color: '#666' },
  docImage: { width: '100%', height: 140, borderRadius: 8 },
  infoBox: { backgroundColor: '#f0f8ff', borderRadius: 12, padding: 14, marginTop: 16 },
  infoText: { fontSize: 12, color: '#2980b9', lineHeight: 18 },
  button: { backgroundColor: '#1a1a2e', borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 20 },
  disabled: { opacity: 0.4 },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
})
