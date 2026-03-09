import { useAuth } from '../lib/AuthContext'

export function useProfile() {
  const { profile, loading, refreshProfile } = useAuth()
  return { profile, loading, refreshProfile }
}
