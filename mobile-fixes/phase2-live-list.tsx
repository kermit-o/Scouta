import { useEffect, useState } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getActiveStreams } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";
import type { LiveStream } from "@/lib/types";

export default function LiveListScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [streams, setStreams] = useState<LiveStream[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try { const d = await getActiveStreams(); setStreams(d.streams || []); } catch {}
    setLoading(false); setRefreshing(false);
  }

  useEffect(() => { load(); const i = setInterval(load, 10000); return () => clearInterval(i); }, []);

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 52, paddingHorizontal: 16, paddingBottom: 12, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" }}>
        <View>
          <Text style={{ color: Colors.red, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>LIVE</Text>
          <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Streams</Text>
        </View>
        {token && (
          <TouchableOpacity onPress={() => router.push("/(app)/live/start")}
            style={{ backgroundColor: Colors.red, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 4, flexDirection: "row", alignItems: "center", gap: 6 }}>
            <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: "#fff" }} />
            <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 12, fontWeight: "700" }}>Go Live</Text>
          </TouchableOpacity>
        )}
      </View>
      {loading ? <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} /> : (
        <FlatList data={streams} keyExtractor={item => item.room_name}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={Colors.green} />}
          ListEmptyComponent={<Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>No active streams right now.</Text>}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => router.push(`/(app)/live/${item.room_name}`)}
              style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 16, marginBottom: 8 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 8 }}>
                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: Colors.red }} />
                <Text style={{ color: Colors.red, fontFamily: Fonts.mono, fontSize: 10 }}>LIVE</Text>
                {item.is_private && <Text style={{ color: Colors.gold, fontFamily: Fonts.mono, fontSize: 9, borderWidth: 1, borderColor: Colors.gold + "44", paddingHorizontal: 6, paddingVertical: 1 }}>PRIVATE</Text>}
                <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 10, marginLeft: "auto" }}>{item.viewer_count} watching</Text>
              </View>
              <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600", marginBottom: 4 }}>{item.title}</Text>
              <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 11 }}>@{item.host_display_name || item.host_username}</Text>
            </TouchableOpacity>
          )} />
      )}
    </View>
  );
}
