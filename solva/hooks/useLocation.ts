import { useCallback, useEffect, useState } from 'react'
import { Platform } from 'react-native'
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

  const requestLocation = useCallback(async (): Promise<Coords | null> => {
    setLoading(true)
    setError(null)
    try {
      let result: Coords | null = null

      if (Platform.OS === 'web') {
        // Web: usar Geolocation API nativa del browser
        if (typeof navigator === 'undefined' || !('geolocation' in navigator)) {
          setError('Geolocalización no soportada por el navegador')
          setLoading(false)
          return null
        }
        result = await new Promise<Coords | null>((resolve) => {
          navigator.geolocation.getCurrentPosition(
            (pos) => resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude }),
            () => resolve(null),
            { enableHighAccuracy: false, timeout: 8000 }
          )
        })
      } else {
        // Native: usar expo-location
        const { status } = await Location.requestForegroundPermissionsAsync()
        if (status !== 'granted') {
          setError('Permiso de ubicación denegado')
          setLoading(false)
          return null
        }
        const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced })
        result = { latitude: loc.coords.latitude, longitude: loc.coords.longitude }
      }

      if (!result) {
        setError('No se pudo obtener la ubicación')
        setLoading(false)
        return null
      }

      setCoords(result)

      // Actualizar ubicación del usuario en DB
      if (session?.user.id) {
        const { error: dbError } = await supabase
          .from('users')
          .update({
            latitude: result.latitude,
            longitude: result.longitude,
          })
          .eq('id', session.user.id)
        if (dbError) console.warn('useLocation update error:', dbError.message)
      }

      setLoading(false)
      return result
    } catch (err: any) {
      setError(err?.message ?? 'Error al obtener ubicación')
      setLoading(false)
      return null
    }
  }, [session?.user.id])

  useEffect(() => {
    if (autoUpdate) requestLocation()
  }, [autoUpdate, requestLocation])

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
