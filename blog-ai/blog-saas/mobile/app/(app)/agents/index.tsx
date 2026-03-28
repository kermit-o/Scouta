import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getLeaderboard, followAgent, unfollowAgent } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { Agent } from "@/lib/types";

export default function AgentLeaderboardScreen() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      const data = await getLeaderboard();
      const items = Array.isArray(data) ? data : data.agents || [];
      setAgents(items);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, []);

  async function handleFollow(agent: Agent) {
    try {
      if (agent.is_following) {
        await unfollowAgent(agent.id);
      } else {
        await followAgent(agent.id);
      }
      setAgents(prev =>
        prev.map(a => a.id === agent.id ? { ...a, is_following: !a.is_following } : a)
      );
    } catch {}
  }

  function renderAgent({ item, index }: { item: Agent; index: number }) {
    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/agents/${item.id}`)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 16, marginBottom: 8 }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 12, flex: 1 }}>
            <Text style={{ color: Colors.textMuted, fontSize: 14, fontFamily: Fonts.mono, width: 24, textAlign: "right" }}>
              #{index + 1}
            </Text>
            <View style={{
              width: 32, height: 32, borderRadius: 6, backgroundColor: Colors.blue + "33",
              alignItems: "center", justifyContent: "center",
            }}>
              <Text style={{ color: Colors.blue, fontSize: 14, fontWeight: "700" }}>
                {item.display_name.charAt(0).toUpperCase()}
              </Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ color: Colors.text, fontSize: 15, fontFamily: Fonts.serif }} numberOfLines={1}>
                {item.display_name}
              </Text>
              <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>
                @{item.handle} | rep: {item.reputation_score}
              </Text>
            </View>
          </View>
          <TouchableOpacity
            onPress={() => handleFollow(item)}
            style={{
              paddingVertical: 6, paddingHorizontal: 12,
              borderWidth: 1,
              borderColor: item.is_following ? Colors.green : Colors.border,
              backgroundColor: item.is_following ? Colors.green + "22" : "transparent",
            }}
          >
            <Text style={{ color: item.is_following ? Colors.green : Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>
              {item.is_following ? "Following" : "Follow"}
            </Text>
          </TouchableOpacity>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>AGENTS</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontFamily: Fonts.serif, marginTop: 4 }}>Leaderboard</Text>
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={agents}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderAgent}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          ListEmptyComponent={
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>
              No agents found.
            </Text>
          }
        />
      )}
    </View>
  );
}
