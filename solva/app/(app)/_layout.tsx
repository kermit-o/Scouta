import { Tabs, router } from 'expo-router'
import { useEffect } from 'react'
import { View } from 'react-native'
import { useProfile } from '../../hooks/useProfile'
import { useAuth } from '../../lib/AuthContext'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useTranslation } from 'react-i18next'
import { DrawerProvider, useDrawer } from '../../lib/DrawerContext'
import DrawerMenu from '../../components/DrawerMenu'
import { Ionicons } from '@expo/vector-icons'

const HomeIcon    = ({ color }: { color: string }) => <Ionicons name="home-outline" size={24} color={color} />
const SearchIcon  = ({ color }: { color: string }) => <Ionicons name="search-outline" size={24} color={color} />
const JobsIcon    = ({ color }: { color: string }) => <Ionicons name="briefcase-outline" size={24} color={color} />
const MsgIcon     = ({ color }: { color: string }) => <Ionicons name="chatbubble-outline" size={24} color={color} />
const ProfileIcon = ({ color }: { color: string }) => <Ionicons name="person-outline" size={24} color={color} />

function AppLayoutInner() {
  const { session } = useAuth()
  const { profile, loading } = useProfile()
  const { isOpen, closeDrawer } = useDrawer()
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()

  useEffect(() => {
    if (!loading && profile && profile.onboarding_completed === false && profile.created_at && (Date.now() - new Date(profile.created_at).getTime() < 60000)) {
      router.replace('/(app)/onboarding')
    }
  }, [profile, loading])

  // Redirigir si no hay sesión
  useEffect(() => {
    if (!session && !loading) {
      router.replace('/(auth)/login')
    }
  }, [session, loading])

  return (
    <View style={{ flex: 1 }}>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: '#2563EB',
          tabBarInactiveTintColor: '#9CA3AF',
          tabBarStyle: {
            backgroundColor: '#fff',
            borderTopColor: 'rgba(0,0,0,0.06)',
            borderTopWidth: 1,
            paddingBottom: insets.bottom + 4,
            paddingTop: 8,
            height: 62 + insets.bottom,
          },
          tabBarLabelStyle: { fontSize: 11, fontWeight: '600', marginTop: 2 },
        }}
      >
        <Tabs.Screen name="index"    options={{ title: t('home.title'),   tabBarIcon: ({ color }) => <HomeIcon    color={color} /> }} />
        <Tabs.Screen name="search"   options={{ title: t('search.title'),   tabBarIcon: ({ color }) => <SearchIcon  color={color} /> }} />
        <Tabs.Screen name="jobs"     options={{ title: t('jobs.title'),     tabBarIcon: ({ color }) => <JobsIcon    color={color} /> }} />
        <Tabs.Screen name="messages" options={{ title: t('messages.title'), tabBarIcon: ({ color }) => <MsgIcon     color={color} /> }} />
        <Tabs.Screen name="profile"  options={{ title: t('profile.title'),   tabBarIcon: ({ color }) => <ProfileIcon color={color} /> }} />
        <Tabs.Screen name="notifications"      options={{ href: null }} />
        <Tabs.Screen name="reputation"         options={{ href: null }} />
        <Tabs.Screen name="invoices"           options={{ href: null }} />
        <Tabs.Screen name="guarantee"          options={{ href: null }} />
        <Tabs.Screen name="help"               options={{ href: null }} />
        <Tabs.Screen name="report"             options={{ href: null }} />
        <Tabs.Screen name="settings-country"   options={{ href: null }} />
        <Tabs.Screen name="settings-security"  options={{ href: null }} />
        <Tabs.Screen name="payments"           options={{ href: null }} />
        <Tabs.Screen name="dashboard-pro"      options={{ href: null }} />
        <Tabs.Screen name="onboarding"         options={{ href: null }} />
        <Tabs.Screen name="kyc"                options={{ href: null }} />
        <Tabs.Screen name="subscription"       options={{ href: null }} />
        <Tabs.Screen name="pro/[id]"           options={{ href: null }} />
        <Tabs.Screen name="jobs/new"           options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]"          options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]/bid"      options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]/chat"     options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]/contract" options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]/dispute"  options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]/payment"  options={{ href: null }} />
        <Tabs.Screen name="jobs/[id]/review"   options={{ href: null }} />
        <Tabs.Screen name="pro-content"          options={{ href: null }} />
      </Tabs>
      <DrawerMenu open={isOpen} onClose={closeDrawer} />
    </View>
  )
}

export default function AppLayout() {
  return (
    <DrawerProvider>
      <AppLayoutInner />
    </DrawerProvider>
  )
}
