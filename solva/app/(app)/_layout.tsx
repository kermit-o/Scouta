import { Tabs, router } from 'expo-router'
import { useEffect } from 'react'
import { useProfile } from '../../hooks/useProfile'
import { Text, Platform } from 'react-native'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

function TabIcon({ emoji, active }: { emoji: string; active: boolean }) {
  return (
    <Text style={{ fontSize: 22, opacity: active ? 1 : 0.45 }}>{emoji}</Text>
  )
}

export default function AppLayout() {
  const { profile, loading } = useProfile()
  const insets = useSafeAreaInsets()

  useEffect(() => {
    if (!loading && profile && !profile.onboarding_completed) {
      router.replace('/(app)/onboarding')
    }
  }, [profile, loading])

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#2563EB',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopColor: 'rgba(0,0,0,0.06)',
          borderTopWidth: 1,
          paddingBottom: insets.bottom + 6,
          paddingTop: 8,
          height: 64 + insets.bottom,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          marginTop: 2,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Inicio',
          tabBarIcon: ({ focused }) => <TabIcon emoji="🏠" active={focused} />,
        }}
      />
      <Tabs.Screen
        name="jobs"
        options={{
          title: 'Jobs',
          tabBarIcon: ({ focused }) => <TabIcon emoji="💼" active={focused} />,
        }}
      />
      <Tabs.Screen
        name="subscription"
        options={{
          title: 'Mi Plan',
          tabBarIcon: ({ focused }) => <TabIcon emoji="⭐" active={focused} />,
        }}
      />
      <Tabs.Screen
        name="messages"
        options={{
          title: 'Mensajes',
          tabBarIcon: ({ focused }) => <TabIcon emoji="💬" active={focused} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Perfil',
          tabBarIcon: ({ focused }) => <TabIcon emoji="👤" active={focused} />,
        }}
      />
    </Tabs>
  )
}
