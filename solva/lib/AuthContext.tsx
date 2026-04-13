import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { router } from 'expo-router'
import { Session } from '@supabase/supabase-js'
import { supabase, UserProfile } from './supabase'
import { changeLanguage } from './i18n'

interface AuthContextType {
  session: Session | null
  profile: UserProfile | null
  loading: boolean
  refreshProfile: () => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  session: null,
  profile: null,
  loading: true,
  refreshProfile: async () => {},
  signOut: async () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  async function fetchProfile(userId: string) {
    const { data, error } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .maybeSingle()

    if (error) {
      console.error('fetchProfile error:', error.message, 'userId:', userId)
      return
    }

    if (data) {
      setProfile(data as UserProfile)
      if ((data as UserProfile).language) changeLanguage((data as UserProfile).language)
      return
    }

    // No existe el perfil aún: crearlo a partir del auth user (flujo OAuth / signup sin trigger)
    const { data: authUser } = await supabase.auth.getUser()
    if (!authUser?.user) return

    const meta = authUser.user.user_metadata ?? {}
    const newRow = {
      id: userId,
      email: authUser.user.email ?? '',
      full_name:
        meta.full_name ??
        meta.name ??
        authUser.user.email?.split('@')[0] ??
        'Usuario',
      avatar_url: meta.avatar_url ?? meta.picture ?? null,
      role: 'client',
      country: 'ES',
      currency: 'EUR',
      language: 'es',
    }
    const { error: upsertError } = await supabase.from('users').upsert(newRow)
    if (upsertError) {
      console.error('fetchProfile upsert error:', upsertError.message)
      return
    }
    const { data: newProfile } = await supabase
      .from('users')
      .select('*')
      .eq('id', userId)
      .maybeSingle()
    if (newProfile) {
      setProfile(newProfile as UserProfile)
      if ((newProfile as UserProfile).language) {
        changeLanguage((newProfile as UserProfile).language)
      }
      // Send welcome email for new users
      supabase.functions.invoke('send-email', {
        body: {
          to: newRow.email,
          template: 'welcome',
          data: { userName: newRow.full_name },
        },
      }).catch(() => {})
    }
  }

  async function refreshProfile() {
    if (session?.user?.id) await fetchProfile(session.user.id)
  }

  async function signOut() {
    await supabase.auth.signOut()
    setProfile(null)
    setSession(null)
    router.replace('/(auth)/login')
  }

  useEffect(() => {
    let cancelled = false

    supabase.auth.getSession().then(async ({ data: { session } }) => {
      if (cancelled) return
      setSession(session)
      if (session?.user?.id) {
        await fetchProfile(session.user.id)
      }
      if (!cancelled) setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (cancelled) return
      if (event === 'SIGNED_OUT') {
        setSession(null)
        setProfile(null)
        return
      }
      if (event === 'TOKEN_REFRESHED' || event === 'SIGNED_IN' || event === 'INITIAL_SESSION') {
        setSession(session)
        if (session?.user?.id) await fetchProfile(session.user.id)
        else setProfile(null)
      }
    })

    return () => {
      cancelled = true
      subscription.unsubscribe()
    }
  }, [])

  return (
    <AuthContext.Provider value={{ session, profile, loading, refreshProfile, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
