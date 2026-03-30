import { useEffect } from 'react'
import { View, ActivityIndicator, Text } from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'

export default function AuthCallback() {
  useEffect(() => {
    async function handleCallback() {
      if (typeof window !== 'undefined') {
        const hash = window.location.hash
        const params = new URLSearchParams(hash.replace('#', ''))
        const error = params.get('error')
        const errorCode = params.get('error_code')
        if (error && errorCode === 'otp_expired') {
          router.replace({ pathname: '/(auth)/login', params: { msg: 'otp_expired' } })
          return
        }
        const accessToken = params.get('access_token')
        const refreshToken = params.get('refresh_token')
        const type = params.get('type')

        if (accessToken && refreshToken) {
          const { data, error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          })
          if (!error && data.user) {
            if (type === 'recovery') {
              router.replace('/reset-password')
              return
            }
            // Verificar onboarding
            console.log('user id:', data.user.id)
            const { data: profile } = await supabase
              .from('users')
              .select('onboarding_completed')
              .eq('id', data.user.id)
              .single()
            console.log('profile:', JSON.stringify(profile))
            if (profile && !profile.onboarding_completed) {
              console.log('→ onboarding')
              router.replace('/(app)/onboarding')
            } else {
              console.log('→ home')
              router.replace('/(app)')
            }
            return
          }
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
