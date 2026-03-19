import { useEffect, useRef } from 'react'
import { Stack, router } from 'expo-router'
import 'react-native-url-polyfill/auto'
import { initI18n } from '../lib/i18n'
import { I18nextProvider } from 'react-i18next'
import i18n from '../lib/i18n'
import { AuthProvider, useAuth } from '../lib/AuthContext'
import * as Font from 'expo-font'
import { Ionicons } from '@expo/vector-icons'
import * as SplashScreen from 'expo-splash-screen'
import { SafeAreaProvider } from 'react-native-safe-area-context'

SplashScreen.preventAutoHideAsync()


function RootLayoutNav() {
  const { session, loading } = useAuth()
  useEffect(() => { initI18n() }, [])
  const prevSessionId = useRef<string | null>(null)

  useEffect(() => {
    if (loading) return
    const currentId = session?.user?.id ?? null
    if (currentId === prevSessionId.current) return
    prevSessionId.current = currentId
    if (!currentId) {
      router.replace('/(auth)/login')
    }
    // Si hay sesión, no redirigir — dejar que la ruta actual se mantenga
  }, [session?.user?.id, loading])

  if (loading) return null

  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="(auth)" />
      <Stack.Screen name="(app)" />
      <Stack.Screen name="auth/callback" options={{ headerShown: false }} />
      <Stack.Screen name="terms" options={{ presentation: 'modal', headerShown: false }} />
      <Stack.Screen name="privacy" options={{ presentation: 'modal', headerShown: false }} />
    </Stack>
  )
}

export default function RootLayout() {
  const [fontsLoaded] = Font.useFonts({
    ...Ionicons.font,
  })

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync()
    }
  }, [fontsLoaded])

  if (!fontsLoaded) return null

  return (
    <SafeAreaProvider>
      <AuthProvider>
        <RootLayoutNav />
      </AuthProvider>
    </SafeAreaProvider>
  )
}

