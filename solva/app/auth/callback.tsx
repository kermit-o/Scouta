import { useEffect } from 'react'
import { View, ActivityIndicator, Text, Platform } from 'react-native'
import { router, useLocalSearchParams } from 'expo-router'
import * as Linking from 'expo-linking'
import { supabase } from '../../lib/supabase'

export default function AuthCallback() {
  const params = useLocalSearchParams()

  useEffect(() => {
    async function handleCallback() {
      let accessToken: string | null = null
      let refreshToken: string | null = null
      let type: string | null = null
      let error: string | null = null
      let errorCode: string | null = null

      if (Platform.OS === 'web' && typeof window !== 'undefined') {
        const hash = window.location.hash
        const urlParams = new URLSearchParams(hash.replace('#', ''))
        accessToken = urlParams.get('access_token')
        refreshToken = urlParams.get('refresh_token')
        type = urlParams.get('type')
        error = urlParams.get('error')
        errorCode = urlParams.get('error_code')
      } else {
        const url = await Linking.getInitialURL()
        if (url) {
          try {
            const parsed = new URL(url)
            const hashParams = new URLSearchParams(parsed.hash.replace('#', ''))
            accessToken = hashParams.get('access_token') ?? parsed.searchParams.get('access_token')
            refreshToken = hashParams.get('refresh_token') ?? parsed.searchParams.get('refresh_token')
            type = hashParams.get('type') ?? parsed.searchParams.get('type')
            error = hashParams.get('error') ?? parsed.searchParams.get('error')
            errorCode = hashParams.get('error_code') ?? parsed.searchParams.get('error_code')
          } catch (_) {}
        }
        if (!accessToken) {
          accessToken = (params.access_token as string) ?? null
          refreshToken = (params.refresh_token as string) ?? null
          type = (params.type as string) ?? null
        }
      }

      if (error && errorCode === 'otp_expired') {
        router.replace({ pathname: '/(auth)/login', params: { msg: 'otp_expired' } })
        return
      }

      if (accessToken && refreshToken) {
        const { data, error: sessionErr } = await supabase.auth.setSession({
          access_token: accessToken,
          refresh_token: refreshToken,
        })
        if (!sessionErr && data.user) {
          if (type === 'recovery') {
            router.replace('/(auth)/reset-password')
            return
          }
          const { data: profile } = await supabase
            .from('users')
            .select('onboarding_completed')
            .eq('id', data.user.id)
            .maybeSingle()
          if (profile && !profile.onboarding_completed) {
            router.replace('/(app)/onboarding')
          } else {
            router.replace('/(app)')
          }
          return
        }
      }

      const { data: { session } } = await supabase.auth.getSession()
      if (session) router.replace('/(app)')
      else router.replace('/(auth)/login')
    }
    handleCallback()
  }, [])

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' }}>
      <ActivityIndicator size="large" color="#2563EB" />
      <Text style={{ marginTop: 16, color: '#888', fontSize: 14 }}>Cargando...</Text>
    </View>
  )
}
