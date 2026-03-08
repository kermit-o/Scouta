import { useEffect, useState } from 'react'
import {
  View, Text, StyleSheet, FlatList, TouchableOpacity,
  ActivityIndicator, TextInput
} from 'react-native'
import { router } from 'expo-router'
import { supabase } from '../../lib/supabase'
import { useAuth } from '../../lib/AuthContext'
import { Ionicons } from '@expo/vector-icons'
import { useSafeAreaInsets } from 'react-native-safe-area-context'

export default function MessagesScreen() {
  const { session } = useAuth()
  const insets = useSafeAreaInsets()
  const [contracts, setContracts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    async function load() {
      const { data } = await supabase
        .from('contracts')
        .select(`
          id, status, amount, currency, job_id, created_at,
          jobs(title),
          client:client_id(id, full_name),
          pro:pro_id(id, full_name)
        `)
        .or(`client_id.eq.${session!.user.id},pro_id.eq.${session!.user.id}`)
        .in('status', ['active', 'completed'])
        .order('created_at', { ascending: false })

      if (data) setContracts(data)
      setLoading(false)
    }
    load()
  }, [])

  if (loading) return (
    <View style={styles.center}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  )

  const filtered = contracts.filter(c => {
    if (!search.trim()) return true
    const isClient = c.client?.id === session!.user.id
    const otherName = isClient ? c.pro?.full_name : c.client?.full_name
    return (
      otherName?.toLowerCase().includes(search.toLowerCase()) ||
      c.jobs?.title?.toLowerCase().includes(search.toLowerCase())
    )
  })

  return (
    <View style={[styles.screen, { paddingTop: insets.top }]}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mensajes</Text>
        <Text style={styles.headerSub}>Tus conversaciones activas</Text>
      </View>

      {/* Search */}
      <View style={styles.searchRow}>
        <Ionicons name="search-outline" size={18} color="#888" />
        <TextInput
          style={styles.searchInput}
          value={search}
          onChangeText={setSearch}
          placeholder="Buscar mensajes..."
          placeholderTextColor="#aaa"
        />
        {search.length > 0 && (
          <TouchableOpacity onPress={() => setSearch('')}>
            <Ionicons name="close-circle" size={18} color="#ccc" />
          </TouchableOpacity>
        )}
      </View>

      <FlatList
        data={filtered}
        keyExtractor={item => item.id}
        contentContainerStyle={filtered.length === 0 ? styles.emptyContainer : styles.list}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={
          <View style={styles.empty}>
            <Ionicons name="chatbubbles-outline" size={52} color="#ddd" />
            <Text style={styles.emptyTitle}>
              {search ? 'Sin resultados' : 'No hay conversaciones'}
            </Text>
            <Text style={styles.emptySub}>
              {search
                ? 'Prueba con otro término'
                : 'Los chats aparecen cuando se acepta un bid'}
            </Text>
          </View>
        }
        renderItem={({ item }) => {
          const isClient = item.client?.id === session!.user.id
          const otherName = isClient ? item.pro?.full_name : item.client?.full_name
          const initial = (otherName ?? '?')[0].toUpperCase()
          const isActive = item.status === 'active'
          const timeAgo = formatTime(item.created_at)

          return (
            <TouchableOpacity
              style={styles.card}
              onPress={() => router.push(`/(app)/jobs/${item.job_id}/chat`)}
              activeOpacity={0.85}
            >
              {/* Avatar */}
              <View style={styles.avatarWrapper}>
                <View style={styles.avatar}>
                  <Text style={styles.avatarText}>{initial}</Text>
                </View>
                {isActive && <View style={styles.activeDot} />}
              </View>

              {/* Info */}
              <View style={styles.info}>
                <View style={styles.infoTop}>
                  <Text style={styles.name} numberOfLines={1}>{otherName ?? 'Usuario'}</Text>
                  <Text style={styles.time}>{timeAgo}</Text>
                </View>
                <Text style={styles.jobTitle} numberOfLines={1}>
                  {item.jobs?.title ?? 'Trabajo'}
                </Text>
                <View style={styles.infoBottom}>
                  <Text style={styles.amount}>
                    {item.amount} {item.currency}
                  </Text>
                  <View style={[styles.statusBadge, isActive ? styles.statusActive : styles.statusDone]}>
                    <Text style={[styles.statusText, isActive ? styles.statusTextActive : styles.statusTextDone]}>
                      {isActive ? 'Activo' : 'Completado'}
                    </Text>
                  </View>
                </View>
              </View>

              <Ionicons name="chevron-forward" size={16} color="#ccc" />
            </TouchableOpacity>
          )
        }}
      />
    </View>
  )
}

function formatTime(dateStr: string): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (diff < 60) return 'ahora'
  if (diff < 3600) return `${Math.floor(diff / 60)}m`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`
  return date.toLocaleDateString('es', { day: 'numeric', month: 'short' })
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB' },

  // Header
  header: { paddingHorizontal: 24, paddingTop: 16, paddingBottom: 12 },
  headerTitle: { fontSize: 24, fontWeight: '800', color: '#1a1a2e' },
  headerSub: { fontSize: 13, color: '#888', marginTop: 2 },

  // Search
  searchRow: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    marginHorizontal: 24, marginBottom: 16,
    backgroundColor: '#fff', borderRadius: 14, paddingHorizontal: 14,
    borderWidth: 1, borderColor: '#E5E7EB',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 6, elevation: 2,
  },
  searchInput: { flex: 1, paddingVertical: 12, fontSize: 15, color: '#1a1a2e' },

  // List
  list: { paddingHorizontal: 24, paddingBottom: 30, gap: 10 },
  emptyContainer: { flex: 1, paddingHorizontal: 24 },

  // Card
  card: {
    flexDirection: 'row', alignItems: 'center', gap: 14,
    backgroundColor: '#fff', borderRadius: 20, padding: 16,
    borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.04, shadowRadius: 8, elevation: 2,
  },

  // Avatar
  avatarWrapper: { position: 'relative' },
  avatar: {
    width: 52, height: 52, borderRadius: 16,
    backgroundColor: '#1a1a2e', alignItems: 'center', justifyContent: 'center',
  },
  avatarText: { color: '#fff', fontSize: 20, fontWeight: '800' },
  activeDot: {
    position: 'absolute', bottom: -2, right: -2,
    width: 14, height: 14, borderRadius: 7,
    backgroundColor: '#10B981', borderWidth: 2, borderColor: '#fff',
  },

  // Info
  info: { flex: 1, gap: 3 },
  infoTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  name: { fontSize: 15, fontWeight: '700', color: '#1a1a2e', flex: 1 },
  time: { fontSize: 11, color: '#aaa' },
  jobTitle: { fontSize: 13, color: '#666' },
  infoBottom: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 2 },
  amount: { fontSize: 13, fontWeight: '700', color: '#10B981' },
  statusBadge: { borderRadius: 6, paddingHorizontal: 7, paddingVertical: 3 },
  statusActive: { backgroundColor: '#D1FAE5' },
  statusDone: { backgroundColor: '#F3F4F6' },
  statusText: { fontSize: 10, fontWeight: '700', letterSpacing: 0.3 },
  statusTextActive: { color: '#059669' },
  statusTextDone: { color: '#888' },

  // Empty
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingTop: 80, gap: 10 },
  emptyTitle: { fontSize: 17, fontWeight: '700', color: '#333' },
  emptySub: { fontSize: 14, color: '#aaa', textAlign: 'center', paddingHorizontal: 32 },
})