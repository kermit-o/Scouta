import { useEffect } from 'react'
import * as Notifications from 'expo-notifications'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/AuthContext'

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
})

export function useNotifications() {
  const { session } = useAuth()

  useEffect(() => {
    if (!session?.user.id) return
    registerPushToken(session.user.id)
  }, [session?.user.id])

  async function registerPushToken(userId: string) {
    try {
      const { status: existing } = await Notifications.getPermissionsAsync()
      let finalStatus = existing

      if (existing !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync()
        finalStatus = status
      }

      if (finalStatus !== 'granted') return

      const token = (await Notifications.getExpoPushTokenAsync()).data

      // Guarda token en DB
      await supabase.from('push_tokens').upsert({
        user_id: userId,
        token,
        platform: 'expo',
      }, { onConflict: 'user_id,token' })

    } catch (err) {
      console.log('Push token error:', err)
    }
  }
}

// Helper: envía notificación a un usuario desde el cliente
export async function notifyUser(userId: string, title: string, body: string, data?: Record<string, string>) {
  await supabase.functions.invoke('send-notification', {
    body: { user_id: userId, title, body, data }
  })
}
