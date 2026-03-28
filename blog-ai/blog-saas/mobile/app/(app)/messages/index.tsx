import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getConversations } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { Conversation } from "@/lib/types";

export default function ConversationsScreen() {
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      const data = await getConversations();
      const items = Array.isArray(data) ? data : data.conversations || [];
      setConversations(items);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, []);

  function timeAgo(dateStr: string | null) {
    if (!dateStr) return "";
    const diff = Date.now() - new Date(dateStr).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "now";
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h / 24)}d`;
  }

  function renderConversation({ item }: { item: Conversation }) {
    const other = item.other_user;
    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/messages/${item.id}`)}
        style={{
          backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
          padding: 14, marginBottom: 6, flexDirection: "row", alignItems: "center", gap: 12,
        }}
      >
        <View style={{
          width: 36, height: 36, borderRadius: 18, backgroundColor: Colors.green + "33",
          alignItems: "center", justifyContent: "center",
        }}>
          <Text style={{ color: Colors.green, fontSize: 14, fontWeight: "700" }}>
            {(other.display_name || other.username).charAt(0).toUpperCase()}
          </Text>
        </View>

        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
            <Text style={{ color: Colors.text, fontSize: 14, fontFamily: Fonts.serif }}>
              {other.display_name || other.username}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>
              {timeAgo(item.last_message_at)}
            </Text>
          </View>
          <Text style={{ color: Colors.textSecondary, fontSize: 12 }} numberOfLines={1}>
            {item.last_message_preview || "No messages yet"}
          </Text>
        </View>

        {item.unread > 0 ? (
          <View style={{
            backgroundColor: Colors.blue, minWidth: 20, height: 20, borderRadius: 10,
            alignItems: "center", justifyContent: "center", paddingHorizontal: 6,
          }}>
            <Text style={{ color: Colors.text, fontSize: 10, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {item.unread}
            </Text>
          </View>
        ) : null}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>SCOUTA</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontFamily: Fonts.serif, marginTop: 4 }}>Messages</Text>
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={conversations}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderConversation}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          ListEmptyComponent={
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>
              No conversations yet.
            </Text>
          }
        />
      )}
    </View>
  );
}
