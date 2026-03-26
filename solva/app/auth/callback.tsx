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
            const { data: profile } = await supabase
              .from('users')
              .select('onboarding_completed')
              .eq('id', data.user.id)
              .single()
            if (profile && !profile.onboarding_completed) {
              router.replace('/(app)/onboarding')
            } else {
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
