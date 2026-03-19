import { useEffect } from 'react'
import { Platform } from 'react-native'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/AuthContext'

export function useNotifications() {
  const { session } = useAuth()
  useEffect(() => {
    if (!session?.user.id || Platform.OS === 'web') return
    registerPushToken(session.user.id)
  }, [session?.user.id])

  async function registerPushToken(userId: string) {
    if (Platform.OS === 'web') return
    try {
      const Notifications = await import('expo-notifications')
      const { status: existing } = await Notifications.getPermissionsAsync()
      let finalStatus = existing
      if (existing !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync()
        finalStatus = status
      }
      if (finalStatus !== 'granted') return
      const token = (await Notifications.getExpoPushTokenAsync()).data
      await supabase.from('push_tokens').upsert({
        user_id: userId, token, platform: 'expo',
      }, { onConflict: 'user_id,token' })
    } catch (err) {
      console.log('Push token error:', err)
    }
  }
}

export async function notifyUser(userId: string, title: string, body: string, data?: Record<string, string>) {
  await supabase.functions.invoke('send-notification', {
    body: { user_id: userId, title, body, data }
  })
}
