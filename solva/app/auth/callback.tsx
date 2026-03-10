import { useEffect } from 'react'
import { View, ActivityIndicator, Text } from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'

export default function AuthCallback() {
  useEffect(() => {
    async function handleCallback() {
      // Supabase manda los tokens en el hash de la URL (#access_token=...)
      if (typeof window !== 'undefined') {
        const hash = window.location.hash
        const params = new URLSearchParams(hash.replace('#', '?'))
        const accessToken = params.get('access_token')
        const refreshToken = params.get('refresh_token')

        if (accessToken && refreshToken) {
          const { error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken,
          })
          if (!error) {
            router.replace('/(app)')
            return
          }
        }
      }
      // Fallback: intentar leer sesión existente
      const { data: { session } } = await supabase.auth.getSession()
      if (session) router.replace('/(app)')
      else router.replace('/(auth)/login')
    }
    handleCallback()
  }, [])

  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' }}>
      <ActivityIndicator size="large" color="#2563EB" />
      <Text style={{ marginTop: 16, color: '#888', fontSize: 14 }}>Iniciando sesión...</Text>
    </View>
  )
}
