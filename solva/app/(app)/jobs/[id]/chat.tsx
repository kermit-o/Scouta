import { useTranslation } from 'react-i18next'
import { useEffect, useRef, useState } from 'react'
import {
  View, Text, StyleSheet, FlatList, TextInput,
  TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform
} from 'react-native'
import { useLocalSearchParams, router } from 'expo-router'
import { notifyUser } from '../../../../hooks/useNotifications'
import { supabase, Message } from '../../../../lib/supabase'
import { useAuth } from '../../../../lib/AuthContext'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import Svg, { Path, Circle } from 'react-native-svg'

const BackIcon = () => (
  <Svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <Path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="#1a1a2e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
)
const SendIcon = ({ color }: { color: string }) => (
  <Svg width="20" height="20" viewBox="0 0 24 24" fill="none">
    <Path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
)

export default function ChatScreen() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { session } = useAuth()
  const insets = useSafeAreaInsets()
  const { t } = useTranslation()
  const [messages, setMessages] = useState<Message[]>([])
  const [contract, setContract] = useState<any>(null)
  const [otherUser, setOtherUser] = useState<any>(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const flatListRef = useRef<FlatList>(null)

  async function markAsRead(contractId: string) {
    await supabase.from('messages')
      .update({ read_at: new Date().toISOString() })
      .eq('contract_id', contractId)
      .neq('sender_id', session!.user.id)
      .is('read_at', null)
  }

  async function loadData() {
    const { data: c } = await supabase
      .from('contracts')
      .select('*, client:client_id(full_name), pro:pro_id(full_name)')
      .eq('job_id', id)
      .single()
    if (!c) { setLoading(false); return }
    setContract(c)
    const otherId = c.client_id === session!.user.id ? c.pro_id : c.client_id
    const otherName = c.client_id === session!.user.id ? c.pro?.full_name : c.client?.full_name
    setOtherUser({ id: otherId, full_name: otherName })
    const { data: msgs } = await supabase
      .from('messages').select('*').eq('contract_id', c.id).order('created_at', { ascending: true })
    if (msgs) setMessages(msgs as Message[])
    if (c?.id) markAsRead(c.id)
    setLoading(false)
  }

  useEffect(() => { loadData() }, [id])

  useEffect(() => {
    if (!contract?.id) return
    const channel = supabase.channel(`chat:${contract.id}`)
      .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'messages', filter: `contract_id=eq.${contract.id}` },
        (payload) => {
          setMessages(prev => prev.map(m => m.id === payload.new.id ? { ...m, read_at: payload.new.read_at } : m))
        }
      )
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'messages', filter: `contract_id=eq.${contract.id}` },
        (payload) => {
          const newMsg = payload.new as Message
          setMessages(prev => [...prev, newMsg])
          setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100)
          // Marcar como leído si el mensaje es del otro
          if (newMsg.sender_id !== session!.user.id) {
            supabase.from('messages').update({ read_at: new Date().toISOString() }).eq('id', newMsg.id)
          }
        }
      ).subscribe()
    return () => { supabase.removeChannel(channel) }
  }, [contract?.id])

  async function handleSend() {
    if (!text.trim() || !contract) return
    setSending(true)
    const content = text.trim()
    setText('')
    await supabase.from('messages').insert({ contract_id: contract.id, sender_id: session!.user.id, content })
    const otherId = session!.user.id === contract.client_id ? contract.pro_id : contract.client_id
    try { await notifyUser(otherId, '💬 Nuevo mensaje', content.slice(0, 80), { job_id: contract.job_id }) } catch (_) {}
    setSending(false)
    setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100)
  }

  function formatTime(ts: string) {
    return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  function formatDate(ts: string) {
    const d = new Date(ts)
    const today = new Date()
    const diff = today.getDate() - d.getDate()
    if (diff === 0) return 'Hoy'
    if (diff === 1) return 'Ayer'
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
  }

  const initials = (name: string) => name?.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() ?? '?'

  if (loading) return (
    <View style={s.center}>
      <ActivityIndicator size="large" color="#2563EB" />
    </View>
  )

  if (!contract) return (
    <View style={s.center}>
      <View style={s.emptyIcon}>
        <Svg width="32" height="32" viewBox="0 0 24 24" fill="none">
          <Path d="M21 15C21 16.1 20.1 17 19 17H7L3 21V5C3 3.9 3.9 3 5 3H19C20.1 3 21 3.9 21 5V15Z" stroke="#9CA3AF" strokeWidth="1.8" strokeLinejoin="round"/>
        </Svg>
      </View>
      <Text style={s.noContractTitle}>Sin contrato activo</Text>
      <Text style={s.noContractSub}>El chat estará disponible cuando se acepte un bid</Text>
      <TouchableOpacity onPress={() => router.back()} style={s.backPill}>
        <Text style={s.backPillText}>Volver</Text>
      </TouchableOpacity>
    </View>
  )

  // Agrupar mensajes por fecha
  type GroupedItem = { type: 'date'; date: string } | { type: 'msg'; item: Message }
  const grouped: GroupedItem[] = []
  let lastDate = ''
  messages.forEach(msg => {
    const d = formatDate(msg.created_at)
    if (d !== lastDate) { grouped.push({ type: 'date', date: d }); lastDate = d }
    grouped.push({ type: 'msg', item: msg })
  })

  return (
    <KeyboardAvoidingView
      style={s.screen}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={0}
    >
      {/* Header */}
      <View style={[s.header, { paddingTop: insets.top + 10 }]}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <BackIcon />
        </TouchableOpacity>
        <View style={s.avatarCircle}>
          <Text style={s.avatarText}>{initials(otherUser?.full_name ?? '?')}</Text>
        </View>
        <View style={s.headerInfo}>
          <Text style={s.headerName}>{otherUser?.full_name ?? 'Chat'}</Text>
          <View style={s.onlineRow}>
            <View style={s.onlineDot} />
            <Text style={s.onlineText}>Contrato activo</Text>
          </View>
        </View>
        <TouchableOpacity style={s.infoBtn} onPress={() => router.push(`/(app)/jobs/${id}/contract` as any)}>
          <Svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <Circle cx="12" cy="12" r="9" stroke="#2563EB" strokeWidth="1.8"/>
            <Path d="M12 11V17M12 8V8.5" stroke="#2563EB" strokeWidth="2" strokeLinecap="round"/>
          </Svg>
        </TouchableOpacity>
      </View>

      {/* Mensajes */}
      <FlatList
        ref={flatListRef}
        data={grouped}
        keyExtractor={(item, i) => i.toString()}
        contentContainerStyle={[s.list, { paddingBottom: 16 }]}
        onLayout={() => flatListRef.current?.scrollToEnd({ animated: false })}
        ListEmptyComponent={
          <View style={s.emptyChat}>
            <Text style={s.emptyChatText}>Di hola a {otherUser?.full_name?.split(' ')[0]} 👋</Text>
            <Text style={s.emptyChatSub}>Los mensajes están protegidos y solo visibles entre las partes</Text>
          </View>
        }
        renderItem={({ item }) => {
          if (item.type === 'date') {
            return (
              <View style={s.dateSeparator}>
                <View style={s.dateLine} />
                <Text style={s.dateText}>{item.date}</Text>
                <View style={s.dateLine} />
              </View>
            )
          }
          const msg = item.item
          const isMine = msg.sender_id === session!.user.id
          return (
            <View style={[s.row, isMine && s.rowMine]}>
              {!isMine && (
                <View style={s.avatarSmall}>
                  <Text style={s.avatarSmallText}>{initials(otherUser?.full_name ?? '?')}</Text>
                </View>
              )}
              <View style={[s.bubble, isMine ? s.bubbleMine : s.bubbleOther]}>
                <Text style={[s.bubbleText, isMine && s.bubbleTextMine]}>{msg.content}</Text>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: 3, justifyContent: 'flex-end' }}>
                  <Text style={[s.timeText, isMine && s.timeTextMine]}>{formatTime(msg.created_at)}</Text>
                  {isMine && (
                    <Text style={{ fontSize: 11, color: msg.read_at ? '#60A5FA' : 'rgba(255,255,255,0.5)', marginTop: 1 }}>
                      {msg.read_at ? '✓✓' : '✓'}
                    </Text>
                  )}
                </View>
              </View>
            </View>
          )
        }}
      />

      {/* Input */}
      <View style={[s.inputBar, { paddingBottom: insets.bottom + 12 }]}>
        <TextInput
          style={s.input}
          value={text}
          onChangeText={setText}
          placeholder={t("messages.typeMessage")}
          placeholderTextColor="#9CA3AF"
          multiline
          maxLength={500}
        />
        <TouchableOpacity
          style={[s.sendBtn, (!text.trim() || sending) && s.sendBtnDisabled]}
          onPress={handleSend}
          disabled={!text.trim() || sending}
          activeOpacity={0.8}
        >
          {sending
            ? <ActivityIndicator color="#fff" size="small" />
            : <SendIcon color="#fff" />
          }
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F6F7FB', gap: 12, padding: 32 },
  emptyIcon: { width: 72, height: 72, borderRadius: 24, backgroundColor: '#F3F4F6', justifyContent: 'center', alignItems: 'center', marginBottom: 8 },
  noContractTitle: { fontSize: 17, fontWeight: '700', color: '#1a1a2e' },
  noContractSub: { fontSize: 14, color: '#9CA3AF', textAlign: 'center' },
  backPill: { marginTop: 8, backgroundColor: '#EEF4FF', borderRadius: 20, paddingHorizontal: 20, paddingVertical: 10 },
  backPillText: { color: '#2563EB', fontWeight: '700', fontSize: 14 },
  header: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 16, paddingBottom: 14,
    backgroundColor: '#fff',
    borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.05)',
  },
  backBtn: { width: 38, height: 38, borderRadius: 12, backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center' },
  avatarCircle: { width: 40, height: 40, borderRadius: 14, backgroundColor: '#2563EB', alignItems: 'center', justifyContent: 'center' },
  avatarText: { color: '#fff', fontWeight: '700', fontSize: 14 },
  headerInfo: { flex: 1 },
  headerName: { fontSize: 15, fontWeight: '700', color: '#1a1a2e' },
  onlineRow: { flexDirection: 'row', alignItems: 'center', gap: 5, marginTop: 2 },
  onlineDot: { width: 7, height: 7, borderRadius: 4, backgroundColor: '#10B981' },
  onlineText: { fontSize: 11, color: '#10B981', fontWeight: '600' },
  infoBtn: { width: 36, height: 36, borderRadius: 10, backgroundColor: '#EEF4FF', alignItems: 'center', justifyContent: 'center' },
  list: { paddingHorizontal: 16, paddingTop: 16, gap: 4 },
  emptyChat: { paddingTop: 80, alignItems: 'center', gap: 8 },
  emptyChatText: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  emptyChatSub: { fontSize: 13, color: '#9CA3AF', textAlign: 'center', maxWidth: 260 },
  dateSeparator: { flexDirection: 'row', alignItems: 'center', gap: 10, marginVertical: 12 },
  dateLine: { flex: 1, height: 1, backgroundColor: '#E5E7EB' },
  dateText: { fontSize: 11, color: '#9CA3AF', fontWeight: '600' },
  row: { flexDirection: 'row', alignItems: 'flex-end', gap: 8, marginVertical: 2 },
  rowMine: { flexDirection: 'row-reverse' },
  avatarSmall: { width: 28, height: 28, borderRadius: 10, backgroundColor: '#DBEAFE', alignItems: 'center', justifyContent: 'center' },
  avatarSmallText: { fontSize: 10, fontWeight: '700', color: '#2563EB' },
  bubble: { maxWidth: '75%', padding: 12, borderRadius: 18, gap: 4 },
  bubbleMine: { backgroundColor: '#2563EB', borderBottomRightRadius: 4 },
  bubbleOther: { backgroundColor: '#fff', borderBottomLeftRadius: 4, borderWidth: 1, borderColor: 'rgba(0,0,0,0.05)' },
  bubbleText: { fontSize: 15, color: '#1a1a2e', lineHeight: 21 },
  bubbleTextMine: { color: '#fff' },
  timeText: { fontSize: 10, color: '#9CA3AF', textAlign: 'right' },
  timeTextMine: { color: 'rgba(255,255,255,0.6)' },
  inputBar: {
    flexDirection: 'row', paddingHorizontal: 16, paddingTop: 12, gap: 10,
    backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: 'rgba(0,0,0,0.05)',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1, backgroundColor: '#F6F7FB', borderRadius: 20,
    paddingHorizontal: 16, paddingVertical: 10, fontSize: 15,
    color: '#1a1a2e', maxHeight: 100,
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  sendBtn: {
    width: 46, height: 46, borderRadius: 16, backgroundColor: '#2563EB',
    alignItems: 'center', justifyContent: 'center',
    shadowColor: '#2563EB', shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3, shadowRadius: 8, elevation: 4,
  },
  sendBtnDisabled: { opacity: 0.35, shadowOpacity: 0 },
})
