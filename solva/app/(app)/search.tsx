import { useTranslation } from 'react-i18next'
import { useState } from 'react'
import {
  View, Text, StyleSheet, TextInput, TouchableOpacity,
  FlatList, ActivityIndicator, ScrollView
} from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { useProfile } from '../../hooks/useProfile'
import { useLocation } from '../../hooks/useLocation'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

const CATEGORIES = [
  { labelKey: 'search.catAll',         icon: '✨', value: null },
  { labelKey: 'search.catCleaning',     icon: '🧹', value: 'cleaning' },
  { labelKey: 'search.catPlumbing',     icon: '🔧', value: 'plumbing' },
  { labelKey: 'search.catElectrical',   icon: '⚡', value: 'electrical' },
  { labelKey: 'search.catMoving',       icon: '📦', value: 'moving' },
  { labelKey: 'search.catPainting',     icon: '🎨', value: 'painting' },
  { labelKey: 'search.catGardening',    icon: '🌿', value: 'gardening' },
]

const EXAMPLES = [
  'Fontanero urgente para mañana en Madrid',
  'Pintar 2 habitaciones este fin de semana',
  'Limpieza piso 80m² antes de mudarme',
  'Electricista para instalar enchufes en oficina',
]

function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLon/2)**2
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * 10) / 10
}

const CATEGORY_ICON: Record<string, string> = {
  cleaning: '🧹', plumbing: '🔧', electrical: '⚡',
  painting: '🎨', moving: '📦', gardening: '🌿',
  carpentry: '🪚', tech: '💻', design: '✏️', other: '🔹'
}

export default function SearchScreen() {
  const { profile } = useProfile()
  const { coords, requestLocation } = useLocation()
  const insets = useSafeAreaInsets()

  const { t } = useTranslation()
  const [query, setQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState<string | null>(null)
  const [results, setResults] = useState<any[]>([])
  const [parsed, setParsed] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  async function handleSearch(q?: string) {
    const searchQuery = q ?? query
    if (!searchQuery.trim()) return
    setLoading(true)
    setSearched(true)

    let location = coords
    if (!location) location = await requestLocation()

    const { data, error } = await supabase.functions.invoke('ai-search', {
      body: {
        query: searchQuery,
        country: profile?.country ?? 'ES',
        currency: profile?.currency ?? 'EUR',
        lat: location?.latitude ?? null,
        lng: location?.longitude ?? null,
      }
    })

    if (!error && data) {
      const jobs = data.jobs ?? []
      // Calcular distancia en cliente si tenemos coords y el job tiene lat/lng
      const enriched = jobs.map((j: any) => {
        if (location && j.latitude && j.longitude && j.distance_km == null) {
          return { ...j, distance_km: haversineKm(location.latitude, location.longitude, j.latitude, j.longitude) }
        }
        return j
      })
      setResults(enriched)
      setParsed(data.parsed)
    }
    setLoading(false)
  }

  const filteredResults = activeCategory
    ? results.filter(j => j.category === activeCategory)
    : results

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>{t('search.title')}</Text>
          <Text style={styles.headerSub}>{t('search.subtitle')}</Text>
        </View>
      </View>

      {/* Search input */}
      <View style={styles.searchBox}>
        <View style={styles.searchInputRow}>
          <Ionicons name="sparkles-outline" size={18} color="#2563EB" />
          <TextInput
            style={styles.searchInput}
            value={query}
            onChangeText={setQuery}
            placeholder={t("search.placeholder")}
            placeholderTextColor="#aaa"
            onSubmitEditing={() => handleSearch()}
            returnKeyType="search"
            autoFocus
          />
          {query.length > 0 && (
            <TouchableOpacity onPress={() => { setQuery(''); setSearched(false); setResults([]) }}>
              <Ionicons name="close-circle" size={18} color="#ccc" />
            </TouchableOpacity>
          )}
        </View>
        <TouchableOpacity
          style={[styles.searchBtn, (!query.trim() || loading) && styles.searchBtnDisabled]}
          onPress={() => handleSearch()}
          disabled={!query.trim() || loading}
          activeOpacity={0.85}
        >
          {loading
            ? <ActivityIndicator color="#fff" size="small" />
            : <>
                <Text style={styles.searchBtnText}>{t('common.search')}</Text>
                <Ionicons name="arrow-forward" size={16} color="#fff" />
              </>
          }
        </TouchableOpacity>
      </View>

      {/* Categories scroll */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.categoriesRow}
        style={styles.categoriesScroll}
      >
        {CATEGORIES.map(cat => (
          <TouchableOpacity
            key={t(cat.labelKey)}
            style={[styles.catChip, activeCategory === cat.value && styles.catChipActive]}
            onPress={() => setActiveCategory(cat.value)}
            activeOpacity={0.8}
          >
            <Text style={styles.catIcon}>{cat.icon}</Text>
            <Text style={[styles.catText, activeCategory === cat.value && styles.catTextActive]}>
              {t(cat.labelKey)}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Estado inicial — ejemplos */}
      {!searched && (
        <ScrollView style={styles.scroll} contentContainerStyle={styles.examplesContent} showsVerticalScrollIndicator={false}>
          <Text style={styles.sectionLabel}>{t('search.trySuggestions')}</Text>
          {EXAMPLES.map((ex, i) => (
            <TouchableOpacity
              key={i}
              style={styles.exampleCard}
              onPress={() => { setQuery(ex); handleSearch(ex) }}
              activeOpacity={0.85}
            >
              <Text style={styles.exampleText}>{ex}</Text>
              <Ionicons name="arrow-forward-circle-outline" size={20} color="#2563EB" />
            </TouchableOpacity>
          ))}

          <View style={styles.tipCard}>
            <View style={styles.tipHeader}>
              <Ionicons name="sparkles" size={16} color="#2563EB" />
              <Text style={styles.tipTitle}>{t('search.aiTip')}</Text>
            </View>
            {[
              'Urgencia — "para mañana", "urgente"',
              'Presupuesto — "menos de 200€"',
              'Ubicación — "cerca de mí", "en Madrid"',
              'Modalidad — "online", "por videollamada"',
            ].map((tip, i) => (
              <View key={i} style={styles.tipRow}>
                <View style={styles.tipDot} />
                <Text style={styles.tipText}>{tip}</Text>
              </View>
            ))}
          </View>
        </ScrollView>
      )}

      {/* Resultados */}
      {searched && (
        <FlatList
          data={filteredResults}
          keyExtractor={item => item.id}
          contentContainerStyle={filteredResults.length === 0 ? styles.emptyContainer : styles.list}
          showsVerticalScrollIndicator={false}
          ListHeaderComponent={
            parsed ? (
              <View style={styles.parsedCard}>
                <View style={styles.parsedHeader}>
                  <Ionicons name="sparkles" size={16} color="#2563EB" />
                  <Text style={styles.parsedSummary}>{parsed.summary}</Text>
                </View>
                {parsed.suggestions?.length > 0 && (
                  <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                    <View style={styles.suggestionsRow}>
                      {parsed.suggestions.map((sug: string, i: number) => (
                        <TouchableOpacity
                          key={i}
                          style={styles.suggestionChip}
                          onPress={() => { setQuery(sug); handleSearch(sug) }}
                        >
                          <Text style={styles.suggestionText}>{sug}</Text>
                        </TouchableOpacity>
                      ))}
                    </View>
                  </ScrollView>
                )}
                <Text style={styles.resultCount}>
                  {filteredResults.length} resultado{filteredResults.length !== 1 ? 's' : ''}
                </Text>
              </View>
            ) : null
          }
          ListEmptyComponent={
            <View style={styles.empty}>
              <Ionicons name="search-outline" size={48} color="#ddd" />
              <Text style={styles.emptyTitle}>{t('search.noResults')}</Text>
              <Text style={styles.emptySub}>{t('search.noResultsDesc')}</Text>
              {profile?.role !== 'pro' && (
                <TouchableOpacity
                  style={styles.emptyBtn}
                  onPress={() => router.push('/(app)/jobs/new')}
                >
                  <Text style={styles.emptyBtnText}>{t('jobs.postJob')}</Text>
                </TouchableOpacity>
              )}
            </View>
          }
          renderItem={({ item }) => (
            <TouchableOpacity
              style={styles.card}
              onPress={() => router.push(`/(app)/jobs/${item.id}`)}
              activeOpacity={0.85}
            >
              <View style={styles.cardTop}>
                <View style={styles.categoryBadge}>
                  <Text style={styles.categoryBadgeText}>
                    {CATEGORY_ICON[item.category]} {item.category?.toUpperCase()}
                  </Text>
                </View>
                {item.distance_km != null && (
                  <View style={styles.distanceBadge}>
                    <Ionicons name="navigate-outline" size={11} color="#2563EB" />
                    <Text style={styles.distanceText}>{item.distance_km}km</Text>
                  </View>
                )}
              </View>
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardDesc} numberOfLines={2}>{item.description}</Text>
              <View style={styles.cardBottom}>
                <Text style={styles.cardBudget}>
                  {item.budget_min || item.budget_max
                    ? `${item.budget_min ?? '?'} – ${item.budget_max ?? '?'} ${item.currency}`
                    : 'A negociar'}
                </Text>
                {item.city && (
                  <View style={styles.cityRow}>
                    <Ionicons name="location-outline" size={12} color="#888" />
                    <Text style={styles.cardCity}>{item.city}</Text>
                  </View>
                )}
              </View>
            </TouchableOpacity>
          )}
        />
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },

  // Header
  header: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    paddingHorizontal: 24, paddingTop: 16, paddingBottom: 12,
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#fff', alignItems: 'center', justifyContent: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06, shadowRadius: 6, elevation: 2,
  },
  headerTitle: { fontSize: 20, fontWeight: '800', color: '#1a1a2e' },
  headerSub: { fontSize: 12, color: '#888', marginTop: 1 },

  // Search
  searchBox: { paddingHorizontal: 24, gap: 10, marginBottom: 14 },
  searchInputRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: '#fff', borderRadius: 16, paddingHorizontal: 16,
    borderWidth: 1, borderColor: '#E5E7EB',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },
  searchInput: { flex: 1, paddingVertical: 14, fontSize: 15, color: '#1a1a2e' },
  searchBtn: {
    backgroundColor: '#2563EB', borderRadius: 14, height: 50,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25, shadowRadius: 10, elevation: 5,
  },
  searchBtnDisabled: { opacity: 0.4, shadowOpacity: 0 },
  searchBtnText: { color: '#fff', fontSize: 15, fontWeight: '700' },

  // Categories
  categoriesScroll: { marginBottom: 8 },
  categoriesRow: { paddingHorizontal: 24, gap: 8, paddingBottom: 4 },
  catChip: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    paddingHorizontal: 14, paddingVertical: 8, borderRadius: 12,
    backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB',
  },
  catChipActive: { backgroundColor: '#2563EB', borderColor: '#2563EB' },
  catIcon: { fontSize: 14 },
  catText: { fontSize: 13, fontWeight: '600', color: '#888' },
  catTextActive: { color: '#fff' },

  // Examples
  scroll: { flex: 1 },
  examplesContent: { paddingHorizontal: 24, paddingTop: 8, paddingBottom: 30, gap: 10 },
  sectionLabel: { fontSize: 14, fontWeight: '700', color: '#888', marginBottom: 4 },
  exampleCard: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: '#fff', borderRadius: 16, padding: 16, gap: 12,
    borderWidth: 1, borderColor: '#E5E7EB',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.03, shadowRadius: 6, elevation: 1,
  },
  exampleText: { flex: 1, fontSize: 14, color: '#1a1a2e', lineHeight: 20 },

  // Tip card
  tipCard: {
    backgroundColor: '#EEF4FF', borderRadius: 16, padding: 16,
    borderWidth: 1, borderColor: '#DBEAFE', gap: 8,
  },
  tipHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 4 },
  tipTitle: { fontSize: 13, fontWeight: '700', color: '#1a1a2e' },
  tipRow: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  tipDot: { width: 5, height: 5, borderRadius: 3, backgroundColor: '#2563EB' },
  tipText: { fontSize: 13, color: '#555' },

  // Results
  list: { paddingHorizontal: 24, paddingBottom: 30, gap: 12 },
  emptyContainer: { flex: 1, paddingHorizontal: 24 },

  // Parsed card
  parsedCard: {
    backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 12,
    borderWidth: 1, borderColor: '#E5E7EB', gap: 10,
  },
  parsedHeader: { flexDirection: 'row', alignItems: 'flex-start', gap: 8 },
  parsedSummary: { flex: 1, fontSize: 14, fontWeight: '600', color: '#1a1a2e', lineHeight: 20 },
  suggestionsRow: { flexDirection: 'row', gap: 8 },
  suggestionChip: {
    backgroundColor: '#EEF4FF', borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 7,
  },
  suggestionText: { fontSize: 12, fontWeight: '600', color: '#2563EB' },
  resultCount: { fontSize: 12, color: '#aaa' },

  // Job card
  card: {
    backgroundColor: '#fff', borderRadius: 20, padding: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2, gap: 8,
  },
  cardTop: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  categoryBadge: {
    backgroundColor: '#EEF4FF', borderRadius: 6,
    paddingHorizontal: 8, paddingVertical: 3,
  },
  categoryBadgeText: { fontSize: 10, fontWeight: '700', color: '#2563EB', letterSpacing: 0.5 },
  distanceBadge: {
    flexDirection: 'row', alignItems: 'center', gap: 3,
    backgroundColor: '#EEF4FF', borderRadius: 6, paddingHorizontal: 7, paddingVertical: 3,
  },
  distanceText: { fontSize: 11, fontWeight: '700', color: '#2563EB' },
  cardTitle: { fontSize: 15, fontWeight: '700', color: '#1a1a2e' },
  cardDesc: { fontSize: 13, color: '#666', lineHeight: 18 },
  cardBottom: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  cardBudget: { fontSize: 14, fontWeight: '800', color: '#1a1a2e' },
  cityRow: { flexDirection: 'row', alignItems: 'center', gap: 3 },
  cardCity: { fontSize: 12, color: '#888' },

  // Empty
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 10 },
  emptyTitle: { fontSize: 17, fontWeight: '700', color: '#333' },
  emptySub: { fontSize: 14, color: '#aaa', textAlign: 'center', paddingHorizontal: 24 },
  emptyBtn: {
    marginTop: 8, backgroundColor: '#2563EB', borderRadius: 14,
    paddingHorizontal: 24, paddingVertical: 12,
  },
  emptyBtnText: { color: '#fff', fontSize: 14, fontWeight: '700' },
})