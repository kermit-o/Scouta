import { Tabs, router } from 'expo-router'
import { useEffect } from 'react'
import { View } from 'react-native'
import { useProfile } from '../../hooks/useProfile'
import { useAuth } from '../../lib/AuthContext'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { useTranslation } from 'react-i18next'
import { DrawerProvider, useDrawer } from '../../lib/DrawerContext'
import DrawerMenu from '../../components/DrawerMenu'
import Svg, { Path, Circle } from 'react-native-svg'

const HomeIcon    = ({ color }: { color: string }) => (<Svg width="24" height="24" viewBox="0 0 24 24" fill="none"><Path d="M3 9.5L12 3L21 9.5V20C21 20.55 20.55 21 20 21H15V15H9V21H4C3.45 21 3 20.55 3 20V9.5Z" stroke={color} strokeWidth="1.8" strokeLinejoin="round"/></Svg>)
const SearchIcon  = ({ color }: { color: string }) => (<Svg width="24" height="24" viewBox="0 0 24 24" fill="none"><Circle cx="11" cy="11" r="7" stroke={color} strokeWidth="1.8"/><Path d="M16.5 16.5L21 21" stroke={color} strokeWidth="1.8" strokeLinecap="round"/></Svg>)
const JobsIcon    = ({ color }: { color: string }) => (<Svg width="24" height="24" viewBox="0 0 24 24" fill="none"><Path d="M2 7C2 5.9 2.9 5 4 5H20C21.1 5 22 5.9 22 7V19C22 20.1 21.1 21 20 21H4C2.9 21 2 20.1 2 19V7Z" stroke={color} strokeWidth="1.8"/><Path d="M16 5V4C16 2.9 15.1 2 14 2H10C8.9 2 8 2.9 8 4V5" stroke={color} strokeWidth="1.8" strokeLinecap="round"/><Path d="M2 11H22" stroke={color} strokeWidth="1.8"/></Svg>)
const MsgIcon     = ({ color }: { color: string }) => (<Svg width="24" height="24" viewBox="0 0 24 24" fill="none"><Path d="M21 15C21 16.1 20.1 17 19 17H7L3 21V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5V15Z" stroke={color} strokeWidth="1.8" strokeLinejoin="round"/></Svg>)
const ProfileIcon = ({ color }: { color: string }) => (<Svg width="24" height="24" viewBox="0 0 24 24" fill="none"><Circle cx="12" cy="8" r="4" stroke={color} strokeWidth="1.8"/><Path d="M4 20C4 17 7.6 14 12 14C16.4 14 20 17 20 20" stroke={color} strokeWidth="1.8" strokeLinecap="round"/></Svg>)

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
        <Tabs.Screen name="pro-content"        options={{ href: null }} />
        <Tabs.Screen name="referrals"             options={{ href: null }} />
        <Tabs.Screen name="admin"                options={{ href: null }} />
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
