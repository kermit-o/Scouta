import { useState, useEffect } from 'react'
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  ActivityIndicator, ScrollView, Image
} from 'react-native'
import * as ImagePicker from 'expo-image-picker'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { useProfile } from '../../hooks/useProfile'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useTranslation } from 'react-i18next'
import { Modal } from 'react-native'
import { LANGUAGES, changeLanguage } from '../../lib/i18n'
import i18n from '../../lib/i18n'

const FLAG: Record<string, string> = {
  ES: '🇪🇸', FR: '🇫🇷', MX: '🇲🇽', CO: '🇨🇴',
  AR: '🇦🇷', BR: '🇧🇷', CL: '🇨🇱', BE: '🇧🇪',
  NL: '🇳🇱', DE: '🇩🇪', PT: '🇵🇹', IT: '🇮🇹', GB: '🇬🇧'
}

const ROLE_LABEL: Record<string, string> = {
  client: 'Cliente', pro: 'Profesional', company: 'Empresa'
}

export default function ProfileScreen() {
  const { t } = useTranslation()
  const { session, signOut } = useAuth()
  const { profile, refreshProfile } = useProfile()
  const insets = useSafeAreaInsets()

  const [fullName, setFullName] = useState(profile?.full_name || '')
  const [bio, setBio] = useState(profile?.bio || '')
  const [skillsText, setSkillsText] = useState((profile?.skills ?? []).join(', '))
  const [phone, setPhone] = useState(profile?.phone || '')
  const [avatarUrl, setAvatarUrl] = useState(profile?.avatar_url || '')
  const [uploading, setUploading] = useState(false)

  // Sync state when profile loads asynchronously
  useEffect(() => {
    if (profile?.full_name) setFullName(profile.full_name)
    if (profile?.phone) setPhone(profile.phone)
    if (profile?.avatar_url) setAvatarUrl(profile.avatar_url)
    if (profile?.bio) setBio(profile.bio)
    if (profile?.skills) setSkillsText(profile.skills.join(', '))
  }, [profile])
  const [saving, setSaving] = useState(false)
  const [editing, setEditing] = useState(false)
  const [showLangModal, setShowLangModal] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  async function pickAndUploadAvatar() {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync()
    if (status !== 'granted') {
      setErrorMsg('Necesitamos acceso a tu galería para cambiar tu foto.')
      return
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true, aspect: [1, 1], quality: 0.7,
    })
    if (result.canceled || !result.assets[0]) return
    setUploading(true)
    try {
      const asset = result.assets[0]
      const ext = asset.uri.split('.').pop() || 'jpg'
      const fileName = `${session!.user.id}/avatar.${ext}`
      const response = await fetch(asset.uri)
      const blob = await response.blob()
      const { error } = await supabase.storage
        .from('avatars').upload(fileName, blob, { upsert: true, contentType: `image/${ext}` })
      if (error) throw error
      const { data: { publicUrl } } = supabase.storage.from('avatars').getPublicUrl(fileName)
      setAvatarUrl(publicUrl)
    } catch (e: any) {
      setErrorMsg('Error al subir imagen: ' + e.message)
    } finally {
      setUploading(false)
    }
  }

  async function handleSave() {
    if (!fullName.trim()) { setErrorMsg('El nombre no puede estar vacío'); return }
    setSaving(true)
    const { error } = await supabase.from('users').update({
      full_name: fullName.trim(),
      phone: phone.trim() || null,
      avatar_url: avatarUrl || null,
      bio: bio.trim() || null,
      skills: skillsText.split(',').map((s: string) => s.trim()).filter(Boolean),
    }).eq('id', session!.user.id)
    setSaving(false)
    if (error) {
      setErrorMsg('Error al guardar: ' + error.message)
    } else {
      await refreshProfile()
      setEditing(false)
      setSuccessMsg(t('profile.profileUpdated'))
      setTimeout(() => setSuccessMsg(''), 3000)
    }
  }

  const initials = (fullName || profile?.full_name || '?')[0].toUpperCase()

  const menuItems = [
    {
      icon: 'shield-checkmark-outline' as const,
      label: 'Verificación KYC',
      badge: profile?.is_verified ? 'Verificado' : 'Pendiente',
      badgeColor: profile?.is_verified ? '#10B981' : '#F59E0B',
      badgeBg: profile?.is_verified ? '#D1FAE5' : '#FEF3C7',
      onPress: () => router.push('/(app)/kyc'),
    },
    {
      icon: 'star-outline' as const,
      label: 'Mi Suscripción',
      badge: 'Free',
      badgeColor: '#2563EB',
      badgeBg: '#EEF4FF',
      onPress: () => router.push('/(app)/subscription'),
    },
    {
      icon: 'eye-outline' as const,
      label: 'Ver perfil público',
      onPress: () => router.push(`/(app)/pro/${session!.user.id}`),
    },
    {
      icon: 'briefcase-outline' as const,
      label: t('profile.myJobs'),
      onPress: () => router.push('/(app)/jobs?filter=mine'),
    },
    {
      icon: 'language-outline' as const,
      label: t('profile.language'),
      badge: LANGUAGES.find(l => l.code === i18n.language)?.flag + ' ' + LANGUAGES.find(l => l.code === i18n.language)?.label,
      badgeColor: '#2563EB',
      badgeBg: '#EEF4FF',
      onPress: () => setShowLangModal(true),
    },
  ]

  return (
    <>
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={[styles.container, { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 40 }]}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="handled"
    >
      {/* Header */}
      {errorMsg ? (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>⚠️ {errorMsg}</Text>
          <TouchableOpacity onPress={() => setErrorMsg('')}>
            <Ionicons name="close" size={16} color="#DC2626" />
          </TouchableOpacity>
        </View>
      ) : null}
      {successMsg ? (
        <View style={styles.successBox}>
          <Text style={styles.successText}>{successMsg}</Text>
        </View>
      ) : null}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mi Perfil</Text>
        <TouchableOpacity
          style={styles.editBtn}
          onPress={() => setEditing(!editing)}
        >
          <Ionicons name={editing ? 'close-outline' : 'create-outline'} size={20} color="#2563EB" />
        </TouchableOpacity>
      </View>

      {/* Profile Card */}
      <View style={styles.profileCard}>
        <View style={styles.profileTop}>
          {/* Avatar */}
          <TouchableOpacity
            style={styles.avatarWrapper}
            onPress={editing ? pickAndUploadAvatar : undefined}
            disabled={uploading}
            activeOpacity={editing ? 0.8 : 1}
          >
            {avatarUrl ? (
              <Image source={{ uri: avatarUrl }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarPlaceholder}>
                <Text style={styles.avatarInitial}>{initials}</Text>
              </View>
            )}
            {uploading && (
              <View style={styles.avatarLoading}>
                <ActivityIndicator color="#fff" size="small" />
              </View>
            )}
            {editing && !uploading && (
              <View style={styles.avatarEditBadge}>
                <Ionicons name="camera" size={12} color="#fff" />
              </View>
            )}
            {profile?.is_verified && (
              <View style={styles.verifiedBadge}>
                <Ionicons name="checkmark-circle" size={20} color="#2563EB" />
              </View>
            )}
          </TouchableOpacity>

          {/* Info */}
          <View style={styles.profileInfo}>
            <Text style={styles.profileName}>{profile?.full_name || 'Usuario'}</Text>
            <Text style={styles.profileEmail}>{profile?.email}</Text>
            <View style={styles.ratingRow}>
              <Ionicons name="star" size={14} color="#F59E0B" />
              <Text style={styles.ratingText}>4.9</Text>
              <Text style={styles.ratingLabel}>valoración</Text>
            </View>
          </View>
        </View>

        {/* Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{FLAG[profile?.country ?? 'ES']} {profile?.country}</Text>
            <Text style={styles.statLabel}>País</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{ROLE_LABEL[profile?.role ?? 'client']}</Text>
            <Text style={styles.statLabel}>Rol</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{profile?.currency ?? 'EUR'}</Text>
            <Text style={styles.statLabel}>Moneda</Text>
          </View>
        </View>
      </View>

      {/* Edit Form */}
      {editing && (
        <View style={styles.editCard}>
          <Text style={styles.editCardTitle}>Editar información</Text>

          <Text style={styles.label}>Nombre completo</Text>
          <TextInput
            style={styles.input}
            value={fullName}
            onChangeText={setFullName}
            placeholder="Tu nombre"
            placeholderTextColor="#aaa"
          />

          <Text style={styles.label}>Teléfono</Text>
          <Text style={styles.inputLabel}>Bio</Text>
          <TextInput
            style={[styles.input, { height: 90, textAlignVertical: 'top' }]}
            value={bio}
            onChangeText={setBio}
            placeholder={t('profile.bioPlaceholder')}
            multiline
            maxLength={300}
          />
          <Text style={styles.inputLabel}>Especialidades (separadas por coma)</Text>
          <TextInput
            style={styles.input}
            value={skillsText}
            onChangeText={setSkillsText}
            placeholder={t('profile.skillsPlaceholder')}
          />
          <Text style={styles.inputLabel}>Teléfono</Text>
          <TextInput
            style={styles.input}
            value={phone}
            onChangeText={setPhone}
            placeholder="+34 600 000 000"
            placeholderTextColor="#aaa"
            keyboardType="phone-pad"
          />

          <TouchableOpacity
            style={[styles.saveBtn, saving && { opacity: 0.6 }]}
            onPress={handleSave}
            disabled={saving}
          >
            {saving
              ? <ActivityIndicator color="#fff" />
              : <Text style={styles.saveBtnText}>{t('common.save')}</Text>
            }
          </TouchableOpacity>
        </View>
      )}

      {/* Menu Items */}
      <View style={styles.menuCard}>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={item.label}
            style={[styles.menuItem, index < menuItems.length - 1 && styles.menuItemBorder]}
            onPress={item.onPress}
            activeOpacity={0.7}
          >
            <View style={styles.menuIconWrapper}>
              <Ionicons name={item.icon} size={20} color="#1a1a2e" />
            </View>
            <Text style={styles.menuLabel}>{item.label}</Text>
            {item.badge && (
              <View style={[styles.menuBadge, { backgroundColor: item.badgeBg }]}>
                <Text style={[styles.menuBadgeText, { color: item.badgeColor }]}>{item.badge}</Text>
              </View>
            )}
            <Ionicons name="chevron-forward" size={16} color="#ccc" />
          </TouchableOpacity>
        ))}
      </View>

      {/* Logout */}
      <TouchableOpacity
        style={styles.logoutBtn}
        onPress={() => { if (typeof window !== 'undefined' && window.confirm('¿Cerrar sesión?')) signOut() }}
        activeOpacity={0.8}
      >
        <Ionicons name="log-out-outline" size={18} color="#EF4444" />
        <Text style={styles.logoutText}>Cerrar sesión</Text>
      </TouchableOpacity>
    </ScrollView>
    <Modal visible={showLangModal} transparent animationType="slide" onRequestClose={() => setShowLangModal(false)}>
        <TouchableOpacity style={styles.modalOverlay} activeOpacity={1} onPress={() => setShowLangModal(false)}>
          <View style={styles.modalSheet}>
            <View style={styles.modalHandle} />
            <Text style={styles.modalTitle}>{t('profile.language')}</Text>
            {LANGUAGES.map(lang => (
              <TouchableOpacity
                key={lang.code}
                style={[styles.langOption, i18n.language === lang.code && styles.langOptionActive]}
                onPress={async () => { await changeLanguage(lang.code); setShowLangModal(false) }}
              >
                <Text style={styles.langFlag}>{lang.flag}</Text>
                <Text style={[styles.langLabel, i18n.language === lang.code && styles.langLabelActive]}>{lang.label}</Text>
                {i18n.language === lang.code && <Ionicons name="checkmark" size={18} color="#2563EB" />}
              </TouchableOpacity>
            ))}
          </View>
        </TouchableOpacity>
      </Modal>
    </>
  )
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: '#F6F7FB' },
  errorBox: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#FEF2F2', borderRadius: 12, padding: 14, marginHorizontal: 24, marginTop: 12 },
  errorText: { flex: 1, color: '#DC2626', fontSize: 13, fontWeight: '500' },
  successBox: { backgroundColor: '#F0FDF4', borderRadius: 12, padding: 14, marginHorizontal: 24, marginTop: 12 },
  successText: { color: '#16A34A', fontSize: 13, fontWeight: '500', textAlign: 'center' },
  container: { paddingHorizontal: 24 },

  // Header
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 },
  headerTitle: { fontSize: 24, fontWeight: '800', color: '#1a1a2e' },
  editBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center',
  },

  // Profile Card
  profileCard: {
    backgroundColor: '#fff', borderRadius: 24, padding: 20,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.06, shadowRadius: 16, elevation: 4,
    marginBottom: 16,
  },
  profileTop: { flexDirection: 'row', alignItems: 'center', gap: 16, marginBottom: 20 },
  avatarWrapper: { position: 'relative' },
  avatar: { width: 80, height: 80, borderRadius: 20 },
  avatarPlaceholder: {
    width: 80, height: 80, borderRadius: 20,
    backgroundColor: '#1a1a2e', alignItems: 'center', justifyContent: 'center',
  },
  avatarInitial: { fontSize: 32, fontWeight: '800', color: '#fff' },
  avatarLoading: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: 20, backgroundColor: 'rgba(0,0,0,0.4)',
    alignItems: 'center', justifyContent: 'center',
  },
  avatarEditBadge: {
    position: 'absolute', bottom: -4, right: -4,
    width: 24, height: 24, borderRadius: 8,
    backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center',
    borderWidth: 2, borderColor: '#fff',
  },
  verifiedBadge: {
    position: 'absolute', bottom: -4, right: -4,
    backgroundColor: '#fff', borderRadius: 10,
  },
  profileInfo: { flex: 1 },
  profileName: { fontSize: 18, fontWeight: '800', color: '#1a1a2e' },
  profileEmail: { fontSize: 13, color: '#888', marginTop: 2, marginBottom: 6 },
  ratingRow: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  ratingText: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  ratingLabel: { fontSize: 13, color: '#888' },

  // Stats
  statsRow: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#F6F7FB', borderRadius: 16, padding: 16,
  },
  statItem: { flex: 1, alignItems: 'center' },
  statValue: { fontSize: 15, fontWeight: '700', color: '#1a1a2e' },
  statLabel: { fontSize: 11, color: '#888', marginTop: 3 },
  statDivider: { width: 1, height: 32, backgroundColor: '#E5E7EB' },

  // Edit Form
  editCard: {
    backgroundColor: '#fff', borderRadius: 20, padding: 20,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
    marginBottom: 16,
  },
  editCardTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', marginBottom: 16 },
  label: { fontSize: 12, fontWeight: '700', color: '#888', marginBottom: 6, marginTop: 12, letterSpacing: 0.3 },
  input: {
    borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 14,
    padding: 14, fontSize: 15, backgroundColor: '#F9FAFB', color: '#1a1a2e',
  },
  saveBtn: {
    backgroundColor: '#2563EB', borderRadius: 14,
    padding: 16, alignItems: 'center', marginTop: 20,
  },
  saveBtnText: { color: '#fff', fontSize: 15, fontWeight: '700' },

  // Menu
  menuCard: {
    backgroundColor: '#fff', borderRadius: 20,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
    overflow: 'hidden', marginBottom: 16,
  },
  menuItem: {
    flexDirection: 'row', alignItems: 'center',
    gap: 14, paddingHorizontal: 20, paddingVertical: 16,
  },
  menuItemBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  menuIconWrapper: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#F6F7FB', alignItems: 'center', justifyContent: 'center',
  },
  menuLabel: { flex: 1, fontSize: 14, fontWeight: '600', color: '#1a1a2e' },
  menuBadge: { borderRadius: 8, paddingHorizontal: 8, paddingVertical: 4 },
  menuBadgeText: { fontSize: 11, fontWeight: '700', letterSpacing: 0.3 },

  // Logout
  logoutBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 8, padding: 16, borderRadius: 14,
    backgroundColor: '#FEF2F2',
  },
  logoutText: { fontSize: 14, fontWeight: '700', color: '#EF4444' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', justifyContent: 'flex-end' },
  modalSheet: { backgroundColor: '#fff', borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHandle: { width: 40, height: 4, backgroundColor: '#E5E7EB', borderRadius: 2, alignSelf: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 18, fontWeight: '800', color: '#1a1a2e', marginBottom: 16 },
  langOption: { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 12, paddingHorizontal: 16, borderRadius: 12, marginBottom: 4 },
  langOptionActive: { backgroundColor: '#EEF4FF' },
  langFlag: { fontSize: 24 },
  langLabel: { flex: 1, fontSize: 16, fontWeight: '500', color: '#1a1a2e' },
  langLabelActive: { color: '#2563EB', fontWeight: '700' },
})