import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
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
      .single()
    if (error) {
      console.error('fetchProfile error:', error.message, 'userId:', userId)
      // Si no existe el perfil en DB, cerrar sesión
      if (error.code === 'PGRST116') {
        await supabase.auth.signOut()
        setProfile(null)
        setSession(null)
        return
      }
      if (false) {
        const { data: authUser } = await supabase.auth.getUser()
        if (authUser?.user) {
          const meta = authUser.user.user_metadata
          await supabase.from('users').upsert({
            id: userId,
            email: authUser.user.email || '',
            full_name: meta?.full_name || meta?.name || authUser.user.email?.split('@')[0] || 'Usuario',
            avatar_url: meta?.avatar_url || meta?.picture || null,
            role: 'client',
            country: 'ES',
            currency: 'EUR',
            language: 'es',
          })
          const { data: newProfile } = await supabase.from('users').select('*').eq('id', userId).single()
          if (newProfile) {
        setProfile(newProfile as UserProfile)
        if ((newProfile as UserProfile).language) changeLanguage((newProfile as UserProfile).language)
      }
        }
      }
    } else if (data) {
      setProfile(data as UserProfile)
    }
  }

  async function refreshProfile() {
    if (session?.user?.id) await fetchProfile(session.user.id)
  }

  async function signOut() {
    await supabase.auth.signOut()
    setProfile(null)
    setSession(null)
  }

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setSession(session)
      if (session?.user?.id) {
        await fetchProfile(session.user.id)
      }
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_OUT' || event === 'USER_DELETED') {
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

    return () => subscription.unsubscribe()
  }, [])

  return (
    <AuthContext.Provider value={{ session, profile, loading, refreshProfile, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
