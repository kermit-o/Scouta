import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { Session } from '@supabase/supabase-js'
import { supabase, UserProfile } from './supabase'

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
    if (!error && data) setProfile(data as UserProfile)
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
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      if (session?.user?.id) fetchProfile(session.user.id)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      if (session?.user?.id) fetchProfile(session.user.id)
      else setProfile(null)
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
