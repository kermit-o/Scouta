import { useEffect, useRef, useState } from 'react'
import { Stack, router } from 'expo-router'
import 'react-native-url-polyfill/auto'
import { initI18n } from '../lib/i18n'
import { AuthProvider, useAuth } from '../lib/AuthContext'
import * as Font from 'expo-font'
import { Ionicons } from '@expo/vector-icons'
import * as SplashScreen from 'expo-splash-screen'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import PaymentProvider from '../components/PaymentProvider'

SplashScreen.preventAutoHideAsync()

function RootLayoutNav() {
  const { session, loading } = useAuth()
  const prevSessionId = useRef<string | null>(null)
  useEffect(() => {
    if (loading) return
    const currentId = session?.user?.id ?? null
    if (currentId === prevSessionId.current) return
    prevSessionId.current = currentId
    if (!currentId) {
      router.replace('/')
    }
  }, [session?.user?.id, loading])
  if (loading) return null
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)" />
      <Stack.Screen name="(app)" />
      <Stack.Screen name="auth/callback" options={{ headerShown: false }} />
      <Stack.Screen name="terms" options={{ presentation: 'modal', headerShown: false }} />
      <Stack.Screen name="privacy" options={{ presentation: 'modal', headerShown: false }} />
    </Stack>
  )
}

export default function RootLayout() {
  const [fontsLoaded] = Font.useFonts({ ...Ionicons.font })
  const [i18nReady, setI18nReady] = useState(false)

  useEffect(() => {
    let cancelled = false
    initI18n()
      .catch((err) => console.warn('initI18n error:', err))
      .finally(() => {
        if (!cancelled) setI18nReady(true)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (fontsLoaded && i18nReady) SplashScreen.hideAsync()
  }, [fontsLoaded, i18nReady])

  if (!fontsLoaded || !i18nReady) return null
  return (
    <SafeAreaProvider>
      <PaymentProvider>
        <AuthProvider>
          <RootLayoutNav />
        </AuthProvider>
      </PaymentProvider>
    </SafeAreaProvider>
  )
}
// stripe-live-1773973475
// rebuild Sun Mar 22 08:02:55 UTC 2026
