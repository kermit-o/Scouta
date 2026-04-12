import { useEffect } from 'react'
import { Platform } from 'react-native'
import Constants from 'expo-constants'
import * as Notifications from 'expo-notifications'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/AuthContext'

if (Platform.OS !== 'web') {
  Notifications.setNotificationHandler({
    handleNotification: async () => ({
      shouldShowAlert: true,
      shouldPlaySound: true,
      shouldSetBadge: true,
    }),
  })
}

function getProjectId(): string | undefined {
  return (
    Constants.expoConfig?.extra?.eas?.projectId ??
    (Constants as any).easConfig?.projectId
  )
}

export function useNotifications() {
  const { session } = useAuth()
  useEffect(() => {
    if (!session?.user.id || Platform.OS === 'web') return
    registerPushToken(session.user.id)
  }, [session?.user.id])

  async function registerPushToken(userId: string) {
    if (Platform.OS === 'web') return
    try {
      const projectId = getProjectId()
      if (!projectId) {
        console.warn('useNotifications: missing EAS projectId in app config')
        return
      }
      const { status: existing } = await Notifications.getPermissionsAsync()
      let finalStatus = existing
      if (existing !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync()
        finalStatus = status
      }
      if (finalStatus !== 'granted') return
      const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data
      const { error } = await supabase.from('push_tokens').upsert(
        { user_id: userId, token, platform: 'expo' },
        { onConflict: 'user_id,token' }
      )
      if (error) console.warn('useNotifications upsert error:', error.message)
    } catch (err: any) {
      console.warn('useNotifications register error:', err?.message ?? err)
    }
  }
}

export async function notifyUser(userId: string, title: string, body: string, data?: Record<string, string>) {
  await supabase.functions.invoke('send-notification', {
    body: { user_id: userId, title, body, data }
  })
}
