import { useState, useEffect } from 'react'
import * as Location from 'expo-location'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/AuthContext'

export interface Coords {
  latitude: number
  longitude: number
}

export function useLocation(autoUpdate = false) {
  const { session } = useAuth()
  const [coords, setCoords] = useState<Coords | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function requestLocation(): Promise<Coords | null> {
    setLoading(true)
    setError(null)
    try {
      const { status } = await Location.requestForegroundPermissionsAsync()
      if (status !== 'granted') {
        setError('Permiso de ubicacion denegado')
        setLoading(false)
        return null
      }

      const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced })
      const c = { latitude: loc.coords.latitude, longitude: loc.coords.longitude }
      setCoords(c)

      // Actualiza ubicacion del usuario en DB
      if (session?.user.id) {
        await supabase.from('users').update({
          latitude: c.latitude,
          longitude: c.longitude,
        }).eq('id', session.user.id)
      }

      setLoading(false)
      return c
    } catch (err: any) {
      setError(err.message)
      setLoading(false)
      return null
    }
  }

  useEffect(() => {
    if (autoUpdate) requestLocation()
  }, [])

  return { coords, loading, error, requestLocation }
}

export async function searchJobsNearby(lat: number, lng: number, radiusKm = 25) {
  const { data, error } = await supabase.rpc('jobs_nearby', {
    lat,
    lng,
    radius_km: radiusKm,
    max_results: 50,
  })
  return { data, error }
}
