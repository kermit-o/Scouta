import { useEffect, useRef } from 'react'
import {
  View, Text, StyleSheet, TouchableOpacity, Animated,
  Dimensions, ScrollView, Image, Platform
} from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useAuth } from '../lib/AuthContext'
import { useProfile } from '../hooks/useProfile'
import Svg, { Path, Circle } from 'react-native-svg'

const { width } = Dimensions.get('window')
const DRAWER_WIDTH = Math.min(320, width * 0.82)

interface Props { open: boolean; onClose: () => void }

type SectionItem = {
  icon: string
  label: string
  route?: string
  badge?: string
  badgeColor?: string
  roles?: string[]
  action?: () => void
}

type Section = {
  title?: string
  items: SectionItem[]
}

export default function DrawerMenu({ open, onClose }: Props) {
  const insets = useSafeAreaInsets()
  const { signOut } = useAuth()
  const { profile } = useProfile()
  const translateX = useRef(new Animated.Value(-DRAWER_WIDTH)).current
  const opacity = useRef(new Animated.Value(0)).current

  useEffect(() => {
    if (open) {
      Animated.parallel([
        Animated.spring(translateX, { toValue: 0, useNativeDriver: true, damping: 20, stiffness: 200 }),
        Animated.timing(opacity, { toValue: 1, duration: 200, useNativeDriver: true }),
      ]).start()
    } else {
      Animated.parallel([
        Animated.spring(translateX, { toValue: -DRAWER_WIDTH, useNativeDriver: true, damping: 20, stiffness: 200 }),
        Animated.timing(opacity, { toValue: 0, duration: 180, useNativeDriver: true }),
      ]).start()
    }
  }, [open])

  if (!open && (translateX as any)._value <= -DRAWER_WIDTH) return null

  const role = profile?.role || 'client'
  const isVerified = profile?.is_verified
  const kycStatus = isVerified ? 'Verificado' : 'Pendiente'
  const kycColor = isVerified ? '#16A34A' : '#F59E0B'

  const SECTIONS: Section[] = [
    {
      title: 'Mi cuenta',
      items: [
        { icon: '👤', label: 'Editar perfil', route: '/(app)/profile' },
        { icon: '🔔', label: 'Notificaciones', route: '/(app)/notifications' },
        { icon: '🌍', label: 'País y moneda', route: '/(app)/settings-country' },
        { icon: '🔒', label: 'Seguridad', route: '/(app)/settings-security' },
      ]
    },
    {
      title: 'Verificación',
      items: [
        { icon: '🪪', label: 'Verificación KYC', route: '/(app)/kyc', badge: kycStatus, badgeColor: kycColor },
        { icon: '⭐', label: 'Mi reputación', route: '/(app)/profile' },
      ]
    },
    {
      title: 'Económico',
      items: [
        { icon: '💳', label: 'Mi suscripción', route: '/(app)/subscription', badge: 'Free', badgeColor: '#2563EB' },
        { icon: '💰', label: 'Mis pagos y cobros', route: '/(app)/payments' },
        { icon: '🧾', label: 'Facturas', route: '/(app)/jobs' },
        { icon: '🛡️', label: 'Garantía Solva', route: '/(app)/jobs' },
      ]
    },
    ...(role === 'pro' || role === 'company' ? [{
      title: 'Mi negocio',
      items: [
        { icon: '📊', label: 'Dashboard Pro', route: '/(app)/dashboard-pro' },
        { icon: '🗺️', label: 'Mi zona de trabajo', route: '/(app)/search' },
        { icon: '📋', label: 'Mis servicios', route: '/(app)/jobs' },
      ]
    }] : []),
    {
      title: 'Soporte',
      items: [
        { icon: '❓', label: 'Centro de ayuda', route: '/(app)/profile' },
        { icon: '💬', label: 'Chat con soporte', route: '/(app)/messages' },
        { icon: '📄', label: 'Términos y Privacidad', route: '/terms' },
        { icon: '🚩', label: 'Reportar un problema', route: '/(app)/profile' },
      ]
    },
  ]

  function navigate(route: string) {
    onClose()
    setTimeout(() => router.push(route as any), 200)
  }

  const initials = profile?.full_name?.[0]?.toUpperCase() || '?'

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="box-none">
      {/* Backdrop */}
      <Animated.View style={[styles.backdrop, { opacity }]} pointerEvents={open ? 'auto' : 'none'}>
        <TouchableOpacity style={StyleSheet.absoluteFill} onPress={onClose} activeOpacity={1} />
      </Animated.View>

      {/* Drawer */}
      <Animated.View style={[styles.drawer, { transform: [{ translateX }], paddingTop: insets.top }]}>
        {/* Header del drawer */}
        <View style={styles.drawerHeader}>
          <View style={styles.avatarRow}>
            {profile?.avatar_url ? (
              <Image source={{ uri: profile.avatar_url }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarPlaceholder}>
                <Text style={styles.avatarInitial}>{initials}</Text>
              </View>
            )}
            <View style={styles.headerInfo}>
              <Text style={styles.headerName} numberOfLines={1}>{profile?.full_name || 'Usuario'}</Text>
              <Text style={styles.headerEmail} numberOfLines={1}>{profile?.role === 'pro' ? '🔧 Profesional' : profile?.role === 'company' ? '🏢 Empresa' : '👤 Cliente'}</Text>
              <View style={[styles.verifiedBadge, { backgroundColor: isVerified ? '#DCFCE7' : '#FEF3C7' }]}>
                <Text style={[styles.verifiedText, { color: isVerified ? '#16A34A' : '#D97706' }]}>
                  {isVerified ? '✅ Verificado' : '⏳ Sin verificar'}
                </Text>
              </View>
            </View>
          </View>
        </View>

        {/* Sections */}
        <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
          {SECTIONS.map((section, si) => (
            <View key={si} style={styles.section}>
              {section.title && <Text style={styles.sectionTitle}>{section.title}</Text>}
              {section.items.map((item, ii) => (
                <TouchableOpacity
                  key={ii}
                  style={styles.item}
                  onPress={() => item.route ? navigate(item.route) : item.action?.()}
                  activeOpacity={0.7}
                >
                  <Text style={styles.itemIcon}>{item.icon}</Text>
                  <Text style={styles.itemLabel}>{item.label}</Text>
                  {item.badge && (
                    <View style={[styles.badge, { backgroundColor: item.badgeColor + '22' }]}>
                      <Text style={[styles.badgeText, { color: item.badgeColor }]}>{item.badge}</Text>
                    </View>
                  )}
                </TouchableOpacity>
              ))}
            </View>
          ))}

          {/* Cerrar sesión */}
          <TouchableOpacity
            style={styles.logoutBtn}
            onPress={() => { onClose(); setTimeout(signOut, 200) }}
            activeOpacity={0.7}
          >
            <Text style={styles.logoutIcon}>🚪</Text>
            <Text style={styles.logoutText}>Cerrar sesión</Text>
          </TouchableOpacity>

          <View style={{ height: 40 }} />
        </ScrollView>
      </Animated.View>
    </View>
  )
}

const styles = StyleSheet.create({
  backdrop: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.45)' },
  drawer: {
    position: 'absolute', left: 0, top: 0, bottom: 0,
    width: DRAWER_WIDTH, backgroundColor: '#fff',
    shadowColor: '#000', shadowOffset: { width: 4, height: 0 },
    shadowOpacity: 0.15, shadowRadius: 20, elevation: 20,
  },
  drawerHeader: {
    backgroundColor: '#1a1a2e', padding: 20, paddingBottom: 24,
  },
  avatarRow: { flexDirection: 'row', alignItems: 'center', gap: 14 },
  avatar: { width: 56, height: 56, borderRadius: 28, borderWidth: 2, borderColor: 'rgba(255,255,255,0.3)' },
  avatarPlaceholder: {
    width: 56, height: 56, borderRadius: 28,
    backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center',
  },
  avatarInitial: { fontSize: 22, fontWeight: '800', color: '#fff' },
  headerInfo: { flex: 1, gap: 3 },
  headerName: { fontSize: 16, fontWeight: '700', color: '#fff' },
  headerEmail: { fontSize: 12, color: 'rgba(255,255,255,0.6)' },
  verifiedBadge: { alignSelf: 'flex-start', borderRadius: 6, paddingHorizontal: 8, paddingVertical: 2, marginTop: 4 },
  verifiedText: { fontSize: 11, fontWeight: '600' },
  scroll: { flex: 1 },
  section: { paddingTop: 8, paddingBottom: 4 },
  sectionTitle: {
    fontSize: 11, fontWeight: '700', color: '#9CA3AF',
    letterSpacing: 0.8, textTransform: 'uppercase',
    paddingHorizontal: 20, paddingTop: 16, paddingBottom: 6,
  },
  item: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    paddingHorizontal: 20, paddingVertical: 13,
  },
  itemIcon: { fontSize: 18, width: 24, textAlign: 'center' },
  itemLabel: { flex: 1, fontSize: 14, fontWeight: '500', color: '#1a1a2e' },
  badge: { borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  badgeText: { fontSize: 11, fontWeight: '700' },
  logoutBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    paddingHorizontal: 20, paddingVertical: 14,
    marginTop: 8, borderTopWidth: 1, borderTopColor: '#F3F4F6',
  },
  logoutIcon: { fontSize: 18, width: 24, textAlign: 'center' },
  logoutText: { fontSize: 14, fontWeight: '600', color: '#DC2626' },
})
