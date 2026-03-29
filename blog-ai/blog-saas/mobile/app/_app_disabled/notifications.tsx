import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getNotifications, markAllRead } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { Notification } from "@/lib/types";

export default function NotificationsScreen() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      const data = await getNotifications();
      const items = Array.isArray(data) ? data : data.notifications || [];
      setNotifications(items);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, []);

  async function handleMarkAllRead() {
    try {
      await markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch {}
  }

  function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "now";
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h / 24)}d`;
  }

  function handlePress(item: Notification) {
    if (item.post_id) {
      router.push(`/(app)/post/${item.post_id}`);
    }
  }

  function renderNotification({ item }: { item: Notification }) {
    const typeColor = item.type === "comment" ? Colors.green : item.type === "vote" ? Colors.blue : Colors.gold;
    return (
      <TouchableOpacity
        onPress={() => handlePress(item)}
        style={{
          backgroundColor: item.read ? Colors.card : Colors.card + "ee",
          borderWidth: 1, borderColor: item.read ? Colors.border : Colors.blue + "44",
          padding: 14, marginBottom: 6,
        }}
      >
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
          <View style={{ backgroundColor: typeColor + "22", paddingHorizontal: 6, paddingVertical: 2 }}>
            <Text style={{ color: typeColor, fontSize: 9, fontFamily: Fonts.mono, fontWeight: "700", textTransform: "uppercase" }}>
              {item.type}
            </Text>
          </View>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>{timeAgo(item.created_at)}</Text>
        </View>
        <Text style={{ color: Colors.text, fontSize: 13, lineHeight: 18 }}>{item.message}</Text>
        {!item.read ? (
          <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: Colors.blue, position: "absolute", top: 8, right: 8 }} />
        ) : null}
      </TouchableOpacity>
    );
  }

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" }}>
          <View>
            <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>SCOUTA</Text>
            <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Notifications</Text>
          </View>
          {unreadCount > 0 ? (
            <TouchableOpacity onPress={handleMarkAllRead}>
              <Text style={{ color: Colors.blue, fontSize: 11, fontFamily: Fonts.mono }}>Mark all read</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderNotification}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          ListEmptyComponent={
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>
              No notifications yet.
            </Text>
          }
        />
      )}
    </View>
  );
}
