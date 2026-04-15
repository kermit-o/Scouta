import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native'
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

/**
 * Native fallback: renders a scrollable list of job locations instead of a map.
 * react-native-maps requires a Google Maps API key in AndroidManifest.xml;
 * without one the app crashes with IllegalStateException. This component is
 * safe to render without any external API keys.
 * The web version (JobsMap.web.tsx) uses Leaflet/OpenStreetMap.
 */
export default function JobsMap({ jobs, onJobPress, height = 300 }: JobsMapProps) {
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
      <View style={styles.header}>
        <Ionicons name="location" size={14} color="#2563EB" />
        <Text style={styles.headerText}>{jobs.length} trabajo{jobs.length !== 1 ? 's' : ''} con ubicación</Text>
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        nestedScrollEnabled
      >
        {jobs.map(job => (
          <TouchableOpacity
            key={job.id}
            style={styles.item}
            onPress={() => onJobPress?.(job.id)}
            activeOpacity={0.8}
          >
            <View style={[styles.dot, { backgroundColor: CATEGORY_COLOR[job.category] ?? '#6B7280' }]} />
            <View style={styles.itemContent}>
              <Text style={styles.itemTitle} numberOfLines={1}>{job.title}</Text>
              {job.city && (
                <View style={styles.cityRow}>
                  <Ionicons name="location-outline" size={11} color="#888" />
                  <Text style={styles.itemCity}>{job.city}</Text>
                </View>
              )}
            </View>
            {(job.budget_min || job.budget_max) && (
              <Text style={styles.itemBudget}>
                {job.budget_min ?? '?'}–{job.budget_max ?? '?'} {job.currency}
              </Text>
            )}
            <Ionicons name="chevron-forward" size={14} color="#ccc" />
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    borderRadius: 16, overflow: 'hidden', backgroundColor: '#fff',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  header: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 10,
    borderBottomWidth: 1, borderBottomColor: '#F3F4F6',
    backgroundColor: '#FAFBFC',
  },
  headerText: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  scroll: { flex: 1 },
  scrollContent: { paddingVertical: 4 },
  item: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 14, paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth, borderBottomColor: '#F3F4F6',
  },
  dot: { width: 8, height: 8, borderRadius: 4 },
  itemContent: { flex: 1, gap: 2 },
  itemTitle: { fontSize: 13, fontWeight: '600', color: '#1a1a2e' },
  cityRow: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  itemCity: { fontSize: 11, color: '#888' },
  itemBudget: { fontSize: 12, fontWeight: '700', color: '#2563EB' },
  empty: {
    borderRadius: 16, backgroundColor: '#F6F7FB',
    alignItems: 'center', justifyContent: 'center', gap: 8,
    borderWidth: 1, borderColor: '#E5E7EB', borderStyle: 'dashed',
  },
  emptyText: { fontSize: 13, color: '#aaa' },
})
