import { useEffect, useRef } from 'react'
import { View, Text, StyleSheet } from 'react-native'
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
  const mapRef = useRef<HTMLDivElement>(null)
  const leafletRef = useRef<any>(null)

  useEffect(() => {
    if (!mapRef.current || typeof window === 'undefined') return

    // Dynamically load Leaflet CSS
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link')
      link.id = 'leaflet-css'
      link.rel = 'stylesheet'
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
      document.head.appendChild(link)
    }

    // Dynamically load Leaflet JS
    const loadLeaflet = (): Promise<any> => {
      if ((window as any).L) return Promise.resolve((window as any).L)
      return new Promise((resolve) => {
        if (document.getElementById('leaflet-js')) {
          const check = setInterval(() => {
            if ((window as any).L) { clearInterval(check); resolve((window as any).L) }
          }, 50)
          return
        }
        const script = document.createElement('script')
        script.id = 'leaflet-js'
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
        script.onload = () => resolve((window as any).L)
        document.head.appendChild(script)
      })
    }

    let map: any = null

    loadLeaflet().then((L) => {
      if (!mapRef.current) return

      const centerLat = userLat ?? jobs[0]?.latitude ?? 40.4168
      const centerLng = userLng ?? jobs[0]?.longitude ?? -3.7038

      // Clean up previous map
      if (leafletRef.current) {
        leafletRef.current.remove()
        leafletRef.current = null
      }

      map = L.map(mapRef.current).setView([centerLat, centerLng], 12)
      leafletRef.current = map

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap',
        maxZoom: 18,
      }).addTo(map)

      // User location marker
      if (userLat && userLng) {
        L.circleMarker([userLat, userLng], {
          radius: 8, color: '#2563EB', fillColor: '#2563EB',
          fillOpacity: 1, weight: 2,
        }).addTo(map).bindPopup('Tu ubicación')
      }

      // Job markers
      const bounds: [number, number][] = []
      jobs.forEach(job => {
        const color = CATEGORY_COLOR[job.category] ?? '#6B7280'
        const budget = job.budget_min || job.budget_max
          ? `${job.budget_min ?? '?'} – ${job.budget_max ?? '?'} ${job.currency}`
          : 'A negociar'

        const marker = L.circleMarker([job.latitude, job.longitude], {
          radius: 10, color, fillColor: color,
          fillOpacity: 0.8, weight: 2,
        }).addTo(map)

        marker.bindPopup(`
          <div style="font-family:sans-serif;min-width:160px">
            <strong style="font-size:13px">${job.title}</strong><br>
            <span style="font-size:11px;color:#666">${job.city ?? ''}</span><br>
            <span style="font-size:12px;font-weight:700;color:${color}">${budget}</span>
          </div>
        `)

        marker.on('click', () => onJobPress?.(job.id))
        bounds.push([job.latitude, job.longitude])
      })

      if (userLat && userLng) bounds.push([userLat, userLng])
      if (bounds.length > 1) {
        map.fitBounds(bounds, { padding: [30, 30] })
      }
    })

    return () => {
      if (leafletRef.current) {
        leafletRef.current.remove()
        leafletRef.current = null
      }
    }
  }, [jobs.length, userLat, userLng])

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
      {/* @ts-expect-error — div is valid on web */}
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
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
