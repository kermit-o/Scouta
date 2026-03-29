import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getActiveStreams } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { LiveStream } from "@/lib/types";

export default function LiveListScreen() {
  const router = useRouter();
  const [streams, setStreams] = useState<LiveStream[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      const data = await getActiveStreams();
      const items = Array.isArray(data) ? data : data.streams || [];
      setStreams(items);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, []);

  function renderStream({ item }: { item: LiveStream }) {
    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/live/${item.room_name}`)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 16, marginBottom: 8 }}
      >
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600", flex: 1 }} numberOfLines={1}>
            {item.title}
          </Text>
          {item.is_private ? (
            <View style={{ backgroundColor: Colors.gold + "33", paddingHorizontal: 8, paddingVertical: 2, marginLeft: 8 }}>
              <Text style={{ color: Colors.gold, fontSize: 9, fontFamily: Fonts.mono, fontWeight: "700" }}>PRIVATE</Text>
            </View>
          ) : null}
        </View>
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>
            {item.host_display_name || item.host_username}
          </Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
            <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: Colors.red }} />
            <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>
              {item.viewer_count} watching
            </Text>
          </View>
        </View>
        {item.entry_coin_cost > 0 ? (
          <Text style={{ color: Colors.gold, fontSize: 10, fontFamily: Fonts.mono, marginTop: 6 }}>
            Entry: {item.entry_coin_cost} coins
          </Text>
        ) : null}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.red, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>LIVE</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Streams</Text>
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={streams}
          keyExtractor={(item) => item.room_name}
          renderItem={renderStream}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          ListEmptyComponent={
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>
              No active streams right now.
            </Text>
          }
        />
      )}
    </View>
  );
}
