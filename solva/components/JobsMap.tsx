import { useEffect, useRef } from 'react'
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native'
import MapView, { Marker, Region } from 'react-native-maps'
import { Ionicons } from '@expo/vector-icons'

export interface MapJob {
  id: string
  title: string
  category: string
  latitude: number
  longitude: number
  budget_min: number | null
  budget_max: number | null
  currency: string
  city: string | null
}

interface JobsMapProps {
  jobs: MapJob[]
  userLat?: number | null
  userLng?: number | null
  onJobPress?: (jobId: string) => void
  height?: number
}

const CATEGORY_COLOR: Record<string, string> = {
  cleaning: '#059669', plumbing: '#2563EB', electrical: '#D97706',
  painting: '#7C3AED', moving: '#DC2626', gardening: '#16A34A',
  carpentry: '#92400E', tech: '#0891B2', design: '#DB2777', other: '#6B7280',
}

export default function JobsMap({ jobs, userLat, userLng, onJobPress, height = 300 }: JobsMapProps) {
  const mapRef = useRef<MapView>(null)

  const initialRegion: Region = {
    latitude: userLat ?? jobs[0]?.latitude ?? 40.4168,
    longitude: userLng ?? jobs[0]?.longitude ?? -3.7038,
    latitudeDelta: 0.15,
    longitudeDelta: 0.15,
  }

  useEffect(() => {
    if (mapRef.current && jobs.length > 0) {
      const coords = jobs.map(j => ({ latitude: j.latitude, longitude: j.longitude }))
      if (userLat && userLng) coords.push({ latitude: userLat, longitude: userLng })
      mapRef.current.fitToCoordinates(coords, {
        edgePadding: { top: 50, right: 50, bottom: 50, left: 50 },
        animated: true,
      })
    }
  }, [jobs.length])

  if (jobs.length === 0) {
    return (
      <View style={[styles.empty, { height }]}>
        <Ionicons name="map-outline" size={32} color="#ccc" />
        <Text style={styles.emptyText}>Sin trabajos con ubicación</Text>
      </View>
    )
  }

  return (
    <View style={[styles.container, { height }]}>
      <MapView
        ref={mapRef}
        style={StyleSheet.absoluteFillObject}
        initialRegion={initialRegion}
        showsUserLocation
        showsMyLocationButton
      >
        {jobs.map(job => (
          <Marker
            key={job.id}
            coordinate={{ latitude: job.latitude, longitude: job.longitude }}
            title={job.title}
            description={job.city ?? undefined}
            pinColor={CATEGORY_COLOR[job.category] ?? '#6B7280'}
            onCalloutPress={() => onJobPress?.(job.id)}
          />
        ))}
      </MapView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { borderRadius: 16, overflow: 'hidden', backgroundColor: '#F6F7FB' },
  empty: {
    borderRadius: 16, backgroundColor: '#F6F7FB',
    alignItems: 'center', justifyContent: 'center', gap: 8,
    borderWidth: 1, borderColor: '#E5E7EB', borderStyle: 'dashed',
  },
  emptyText: { fontSize: 13, color: '#aaa' },
})
