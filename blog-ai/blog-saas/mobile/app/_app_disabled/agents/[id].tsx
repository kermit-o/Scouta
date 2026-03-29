import { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, ActivityIndicator, ScrollView } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getAgent, followAgent, unfollowAgent } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { Agent } from "@/lib/types";

export default function AgentProfileScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const data = await getAgent(Number(id));
      setAgent(data);
    } catch {}
    setLoading(false);
  }

  useEffect(() => { load(); }, [id]);

  async function handleFollow() {
    if (!agent) return;
    try {
      if (agent.is_following) {
        await unfollowAgent(agent.id);
      } else {
        await followAgent(agent.id);
      }
      setAgent(prev => prev ? { ...prev, is_following: !prev.is_following } : prev);
    } catch {}
  }

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  if (!agent) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 12 }}>Agent not found</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 8 }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
      </View>

      <ScrollView contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}>
        <View style={{ alignItems: "center", marginBottom: 24, marginTop: 8 }}>
          <View style={{
            width: 64, height: 64, borderRadius: 12, backgroundColor: Colors.blue + "33",
            alignItems: "center", justifyContent: "center", marginBottom: 12,
          }}>
            <Text style={{ color: Colors.blue, fontSize: 28, fontWeight: "700" }}>
              {(agent.display_name || "?").charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600" }}>{agent.display_name}</Text>
          <Text style={{ color: Colors.textSecondary, fontSize: 12, fontFamily: Fonts.mono, marginTop: 4 }}>@{agent.handle}</Text>
        </View>

        {agent.bio ? (
          <Text style={{ color: Colors.textSecondary, fontSize: 14, lineHeight: 20, textAlign: "center", marginBottom: 20 }}>
            {agent.bio}
          </Text>
        ) : null}

        {/* Stats */}
        <View style={{
          flexDirection: "row", justifyContent: "space-around",
          backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
          paddingVertical: 16, marginBottom: 20,
        }}>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {agent.reputation_score}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Reputation</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {agent.total_comments ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Comments</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {agent.total_upvotes ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Upvotes</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {agent.follower_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Followers</Text>
          </View>
        </View>

        {agent.topics ? (
          <View style={{ marginBottom: 16 }}>
            <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>TOPICS</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 13 }}>{agent.topics}</Text>
          </View>
        ) : null}

        {agent.style ? (
          <View style={{ marginBottom: 20 }}>
            <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>STYLE</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 13 }}>{agent.style}</Text>
          </View>
        ) : null}

        <TouchableOpacity
          onPress={handleFollow}
          style={{
            paddingVertical: 14, alignItems: "center",
            backgroundColor: agent.is_following ? "transparent" : Colors.blue,
            borderWidth: 1, borderColor: agent.is_following ? Colors.border : Colors.blue,
          }}
        >
          <Text style={{
            color: agent.is_following ? Colors.textSecondary : Colors.text,
            fontSize: 14, fontFamily: Fonts.mono, fontWeight: "700",
          }}>
            {agent.is_following ? "Unfollow" : "Follow"}
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}
