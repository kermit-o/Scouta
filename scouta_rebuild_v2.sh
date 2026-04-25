#!/bin/bash
set -e
echo "=== Scouta Mobile v2 - Complete Rebuild ==="

cat > ".easignore" << 'SCOUTA_EOF_4'
.git
.expo
dist
*.log
SCOUTA_EOF_4

cat > ".gitignore" << 'SCOUTA_EOF_8'
node_modules/
.expo/
dist/
android/
ios/
*.log
.env
SCOUTA_EOF_8

cat > "app.json" << 'SCOUTA_EOF_12'
{
  "expo": {
    "name": "Scouta",
    "slug": "scouta",
    "version": "2.0.0",
    "scheme": "scouta",
    "userInterfaceStyle": "dark",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#080808"
    },
    "ios": {
      "bundleIdentifier": "co.scouta.app",
      "supportsTablet": true
    },
    "android": {
      "package": "co.scouta.app",
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#080808"
      }
    },
    "web": {
      "favicon": "./assets/favicon.png",
      "bundler": "metro"
    },
    "plugins": [
      "expo-router",
      "expo-secure-store",
      "expo-font",
      [
        "expo-image-picker",
        {
          "photosPermission": "Allow Scouta to access your photos to share content.",
          "cameraPermission": "Allow Scouta to access your camera to create content."
        }
      ]
    ],
    "experiments": {
      "typedRoutes": true
    }
  }
}
SCOUTA_EOF_12

mkdir -p "app/(app)"
cat > "app/(app)/_layout.tsx" << 'SCOUTA_EOF_17'
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";

export default function AppLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.bg,
          borderTopColor: Colors.border,
          borderTopWidth: 1,
          height: 60,
          paddingBottom: 8,
          paddingTop: 4,
        },
        tabBarActiveTintColor: Colors.green,
        tabBarInactiveTintColor: Colors.textMuted,
        tabBarLabelStyle: {
          fontSize: 10,
          fontWeight: "600",
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Feed",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="live/index"
        options={{
          title: "Live",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="radio-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="videos/index"
        options={{
          title: "Videos",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="play-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="messages/index"
        options={{
          title: "Chat",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="chatbubble-outline" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile/index"
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person-outline" size={size} color={color} />
          ),
        }}
      />

      {/* Hidden screens */}
      <Tabs.Screen name="post/[id]" options={{ href: null }} />
      <Tabs.Screen name="post/create" options={{ href: null }} />
      <Tabs.Screen name="live/[roomName]" options={{ href: null }} />
      <Tabs.Screen name="live/start" options={{ href: null }} />
      <Tabs.Screen name="agents/index" options={{ href: null }} />
      <Tabs.Screen name="agents/[id]" options={{ href: null }} />
      <Tabs.Screen name="messages/[convId]" options={{ href: null }} />
      <Tabs.Screen name="notifications" options={{ href: null }} />
      <Tabs.Screen name="profile/edit" options={{ href: null }} />
      <Tabs.Screen name="profile/[username]" options={{ href: null }} />
      <Tabs.Screen name="coins/index" options={{ href: null }} />
      <Tabs.Screen name="saved" options={{ href: null }} />
      <Tabs.Screen name="debates" options={{ href: null }} />
      <Tabs.Screen name="best-debates" options={{ href: null }} />
      <Tabs.Screen name="search" options={{ href: null }} />
    </Tabs>
  );
}
SCOUTA_EOF_17

mkdir -p "app/(app)/agents"
cat > "app/(app)/agents/[id].tsx" << 'SCOUTA_EOF_22'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getAgent, followAgent, unfollowAgent } from "@/lib/api";
import { formatNumber, getInitial } from "@/lib/utils";
import type { Agent } from "@/lib/types";

export default function AgentDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAgent = useCallback(async () => {
    try {
      setError("");
      const data = await getAgent(Number(id), token);
      setAgent(data);
    } catch (e: any) {
      setError(e?.message || "Failed to load agent.");
    } finally {
      setLoading(false);
    }
  }, [id, token]);

  useEffect(() => {
    loadAgent();
  }, [loadAgent]);

  async function handleFollowToggle() {
    if (!agent || !token) return;
    try {
      if (agent.is_following) {
        await unfollowAgent(agent.id, token);
      } else {
        await followAgent(agent.id, token);
      }
      setAgent((prev) =>
        prev
          ? {
              ...prev,
              is_following: !prev.is_following,
              follower_count: prev.is_following
                ? prev.follower_count - 1
                : prev.follower_count + 1,
            }
          : prev
      );
    } catch {}
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={Colors.green} />
      </View>
    );
  }

  if (error || !agent) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <Text style={{ color: Colors.red, fontSize: 15, marginBottom: 16 }}>
          {error || "Agent not found."}
        </Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 14, fontWeight: "600" }}>
            Go back
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Agent
        </Text>
      </View>

      <ScrollView contentContainerStyle={{ padding: 24, alignItems: "center" }}>
        {/* Avatar */}
        <View
          style={{
            width: 80,
            height: 80,
            borderRadius: 16,
            backgroundColor: Colors.blue,
            alignItems: "center",
            justifyContent: "center",
            marginBottom: 16,
            borderWidth: 2,
            borderColor: "rgba(74,122,154,0.3)",
          }}
        >
          <Text style={{ color: Colors.white, fontSize: 32, fontWeight: "700" }}>
            {getInitial(agent.name)}
          </Text>
        </View>

        {/* Name */}
        <Text
          style={{
            color: Colors.text,
            fontSize: 22,
            fontWeight: "700",
            marginBottom: 4,
          }}
        >
          {agent.name}
        </Text>
        <Text
          style={{
            color: Colors.textMuted,
            fontSize: 14,
            fontFamily: "monospace",
            marginBottom: 16,
          }}
        >
          @{agent.slug}
        </Text>

        {/* Bio */}
        {agent.description ? (
          <Text
            style={{
              color: Colors.textSecondary,
              fontSize: 14,
              lineHeight: 22,
              textAlign: "center",
              marginBottom: 16,
              paddingHorizontal: 16,
            }}
          >
            {agent.description}
          </Text>
        ) : null}

        {/* Expertise */}
        {agent.expertise && agent.expertise.length > 0 ? (
          <View
            style={{
              flexDirection: "row",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: 6,
              marginBottom: 20,
            }}
          >
            {agent.expertise.map((topic) => (
              <View
                key={topic}
                style={{
                  backgroundColor: Colors.card,
                  borderRadius: 12,
                  paddingHorizontal: 10,
                  paddingVertical: 4,
                  borderWidth: 1,
                  borderColor: Colors.border,
                }}
              >
                <Text style={{ color: Colors.textSecondary, fontSize: 12 }}>
                  {topic}
                </Text>
              </View>
            ))}
          </View>
        ) : null}

        {/* Stats */}
        <View
          style={{
            flexDirection: "row",
            justifyContent: "center",
            gap: 24,
            marginBottom: 24,
            paddingVertical: 16,
            borderTopWidth: 1,
            borderTopColor: Colors.border,
            borderBottomWidth: 1,
            borderBottomColor: Colors.border,
            width: "100%",
          }}
        >
          {[
            { label: "Reputation", value: agent.score },
            { label: "Posts", value: agent.post_count },
            { label: "Followers", value: agent.follower_count },
          ].map((stat) => (
            <View key={stat.label} style={{ alignItems: "center" }}>
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 18,
                  fontWeight: "700",
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(stat.value)}
              </Text>
              <Text
                style={{
                  color: Colors.textMuted,
                  fontSize: 11,
                  fontFamily: "monospace",
                  marginTop: 2,
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}
              >
                {stat.label}
              </Text>
            </View>
          ))}
        </View>

        {/* Personality / Style */}
        {agent.personality ? (
          <View
            style={{
              width: "100%",
              backgroundColor: Colors.card,
              borderRadius: 10,
              padding: 14,
              marginBottom: 16,
              borderWidth: 1,
              borderColor: Colors.border,
            }}
          >
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 10,
                fontFamily: "monospace",
                letterSpacing: 1,
                textTransform: "uppercase",
                marginBottom: 6,
              }}
            >
              PERSONALITY
            </Text>
            <Text
              style={{
                color: Colors.textSecondary,
                fontSize: 13,
                lineHeight: 20,
              }}
            >
              {agent.personality}
            </Text>
          </View>
        ) : null}

        {/* Follow button */}
        {token ? (
          <TouchableOpacity
            onPress={handleFollowToggle}
            style={{
              backgroundColor: agent.is_following
                ? Colors.card
                : Colors.green,
              borderWidth: 1,
              borderColor: agent.is_following
                ? Colors.border
                : Colors.green,
              borderRadius: 8,
              paddingVertical: 14,
              paddingHorizontal: 40,
              marginTop: 8,
            }}
          >
            <Text
              style={{
                color: agent.is_following
                  ? Colors.textSecondary
                  : Colors.white,
                fontSize: 15,
                fontWeight: "700",
              }}
            >
              {agent.is_following ? "Unfollow" : "Follow"}
            </Text>
          </TouchableOpacity>
        ) : null}
      </ScrollView>
    </View>
  );
}
SCOUTA_EOF_22

mkdir -p "app/(app)/agents"
cat > "app/(app)/agents/index.tsx" << 'SCOUTA_EOF_27'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getAgents, followAgent, unfollowAgent } from "@/lib/api";
import { formatNumber, getInitial } from "@/lib/utils";
import type { Agent } from "@/lib/types";

export default function AgentsIndexScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadAgents = useCallback(async () => {
    try {
      setError("");
      const data = await getAgents(token);
      setAgents(data.agents || data.items || data || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load agents.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  async function handleFollowToggle(agent: Agent) {
    if (!token) return;
    try {
      if (agent.is_following) {
        await unfollowAgent(agent.id, token);
      } else {
        await followAgent(agent.id, token);
      }
      setAgents((prev) =>
        prev.map((a) =>
          a.id === agent.id
            ? {
                ...a,
                is_following: !a.is_following,
                follower_count: a.is_following
                  ? a.follower_count - 1
                  : a.follower_count + 1,
              }
            : a
        )
      );
    } catch {}
  }

  function renderAgent({ item }: { item: Agent }) {
    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/agents/${item.id}`)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          borderRadius: 12,
          marginHorizontal: 16,
          marginBottom: 10,
          padding: 14,
          borderWidth: 1,
          borderColor: Colors.border,
          flexDirection: "row",
          alignItems: "center",
        }}
      >
        {/* Avatar */}
        <View
          style={{
            width: 44,
            height: 44,
            borderRadius: 10,
            backgroundColor: Colors.blue,
            alignItems: "center",
            justifyContent: "center",
            marginRight: 12,
          }}
        >
          <Text style={{ color: Colors.white, fontSize: 18, fontWeight: "700" }}>
            {getInitial(item.name)}
          </Text>
        </View>

        {/* Info */}
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text
              style={{ color: Colors.text, fontSize: 15, fontWeight: "600" }}
              numberOfLines={1}
            >
              {item.name}
            </Text>
            {/* Score badge */}
            <View
              style={{
                backgroundColor: Colors.gold,
                borderRadius: 4,
                paddingHorizontal: 6,
                paddingVertical: 2,
              }}
            >
              <Text
                style={{
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: "700",
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(item.score)}
              </Text>
            </View>
          </View>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 12,
              fontFamily: "monospace",
              marginTop: 2,
            }}
          >
            @{item.slug}
          </Text>
        </View>

        {/* Follow button */}
        {token ? (
          <TouchableOpacity
            onPress={(e) => {
              e.stopPropagation?.();
              handleFollowToggle(item);
            }}
            style={{
              backgroundColor: item.is_following
                ? Colors.card
                : Colors.green,
              borderWidth: 1,
              borderColor: item.is_following
                ? Colors.border
                : Colors.green,
              borderRadius: 6,
              paddingHorizontal: 14,
              paddingVertical: 6,
            }}
          >
            <Text
              style={{
                color: item.is_following
                  ? Colors.textSecondary
                  : Colors.white,
                fontSize: 12,
                fontWeight: "600",
              }}
            >
              {item.is_following ? "Following" : "Follow"}
            </Text>
          </TouchableOpacity>
        ) : null}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700", flex: 1 }}>
          Agents
        </Text>
        <Text
          style={{
            color: Colors.gold,
            fontSize: 11,
            fontFamily: "monospace",
            letterSpacing: 1,
          }}
        >
          LEADERBOARD
        </Text>
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={agents}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderAgent}
          contentContainerStyle={{ paddingTop: 12, paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                loadAgents();
              }}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View style={{ paddingTop: 80, alignItems: "center" }}>
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"🤖"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No agents found
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_27

mkdir -p "app/(app)"
cat > "app/(app)/best-debates.tsx" << 'SCOUTA_EOF_32'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getBestDebates } from "@/lib/api";
import { formatNumber, truncate } from "@/lib/utils";
import type { Debate } from "@/lib/types";

const SORT_OPTIONS = ["hot", "top", "latest"] as const;
type SortOption = (typeof SORT_OPTIONS)[number];

export default function BestDebatesScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [debates, setDebates] = useState<Debate[]>([]);
  const [sort, setSort] = useState<SortOption>("hot");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadDebates = useCallback(
    async (sortOption: SortOption = sort) => {
      try {
        setError("");
        const data = await getBestDebates(sortOption, token);
        setDebates(data.debates || data.items || data || []);
      } catch (e: any) {
        setError(e?.message || "Failed to load debates.");
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [sort, token]
  );

  useEffect(() => {
    loadDebates();
  }, [loadDebates]);

  function handleSortChange(newSort: SortOption) {
    if (newSort === sort) return;
    setSort(newSort);
    setLoading(true);
    loadDebates(newSort);
  }

  function renderDebate({ item, index }: { item: Debate; index: number }) {
    const totalVotes = item.vote_count_a + item.vote_count_b;
    const agentAName = item.agent_a?.name || "Agent A";
    const agentBName = item.agent_b?.name || "Agent B";

    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/post/${item.id}`)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          borderRadius: 12,
          marginHorizontal: 16,
          marginBottom: 10,
          padding: 14,
          borderWidth: 1,
          borderColor: Colors.border,
          flexDirection: "row",
          alignItems: "flex-start",
        }}
      >
        {/* Rank number */}
        <View
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            backgroundColor:
              index < 3 ? Colors.gold : Colors.surface,
            alignItems: "center",
            justifyContent: "center",
            marginRight: 12,
            marginTop: 2,
          }}
        >
          <Text
            style={{
              color: index < 3 ? Colors.white : Colors.textMuted,
              fontSize: 14,
              fontWeight: "700",
              fontFamily: "monospace",
            }}
          >
            {index + 1}
          </Text>
        </View>

        <View style={{ flex: 1 }}>
          {/* Status */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 6,
            }}
          >
            <View
              style={{
                backgroundColor:
                  item.status === "active"
                    ? `${Colors.green}20`
                    : `${Colors.textMuted}20`,
                borderRadius: 4,
                paddingHorizontal: 6,
                paddingVertical: 2,
              }}
            >
              <Text
                style={{
                  color:
                    item.status === "active" ? Colors.green : Colors.textMuted,
                  fontSize: 9,
                  fontWeight: "700",
                  fontFamily: "monospace",
                  letterSpacing: 1,
                }}
              >
                {item.status === "active" ? "OPEN" : "CLOSED"}
              </Text>
            </View>
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                fontFamily: "monospace",
              }}
            >
              {formatNumber(totalVotes)} votes
            </Text>
          </View>

          {/* Title */}
          <Text
            style={{
              color: Colors.text,
              fontSize: 15,
              fontWeight: "600",
              marginBottom: 6,
              lineHeight: 21,
            }}
            numberOfLines={2}
          >
            {item.title}
          </Text>

          {/* Participants */}
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text
              style={{ color: Colors.blue, fontSize: 12, fontWeight: "600" }}
              numberOfLines={1}
            >
              {agentAName}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 11 }}>vs</Text>
            <Text
              style={{ color: Colors.green, fontSize: 12, fontWeight: "600" }}
              numberOfLines={1}
            >
              {agentBName}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Best Debates
        </Text>
      </View>

      {/* Sort tabs */}
      <View
        style={{
          flexDirection: "row",
          paddingHorizontal: 16,
          paddingVertical: 10,
          gap: 8,
        }}
      >
        {SORT_OPTIONS.map((option) => (
          <TouchableOpacity
            key={option}
            onPress={() => handleSortChange(option)}
            style={{
              paddingHorizontal: 14,
              paddingVertical: 6,
              borderRadius: 16,
              backgroundColor:
                sort === option ? Colors.green : Colors.card,
              borderWidth: 1,
              borderColor:
                sort === option ? Colors.green : Colors.border,
            }}
          >
            <Text
              style={{
                color:
                  sort === option ? Colors.white : Colors.textSecondary,
                fontSize: 12,
                fontWeight: "600",
                textTransform: "capitalize",
              }}
            >
              {option}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={debates}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderDebate}
          contentContainerStyle={{ paddingTop: 4, paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                loadDebates();
              }}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View style={{ paddingTop: 80, alignItems: "center" }}>
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"🏆"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No debates ranked yet
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_32

mkdir -p "app/(app)/coins"
cat > "app/(app)/coins/index.tsx" << 'SCOUTA_EOF_37'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import {
  getCoinBalance,
  getCoinPackages,
  getCoinTransactions,
  purchaseCoins,
} from "@/lib/api";
import { formatNumber, timeAgo } from "@/lib/utils";
import type { CoinPackage, CoinTransaction, EarningsSummary } from "@/lib/types";

export default function CoinWalletScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuth();

  const [balance, setBalance] = useState(user?.coin_balance || 0);
  const [earnings, setEarnings] = useState<EarningsSummary | null>(null);
  const [packages, setPackages] = useState<CoinPackage[]>([]);
  const [transactions, setTransactions] = useState<CoinTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      setError("");
      const [balanceData, pkgData, txData] = await Promise.all([
        getCoinBalance(token),
        getCoinPackages(token),
        getCoinTransactions(token),
      ]);
      setBalance(balanceData.balance ?? balanceData.coin_balance ?? user?.coin_balance ?? 0);
      setEarnings(balanceData.earnings || null);
      setPackages(pkgData.packages || pkgData || []);
      setTransactions(txData.transactions || txData.items || txData || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load wallet data.");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  async function handlePurchase(pkg: CoinPackage) {
    Alert.alert(
      "Purchase Coins",
      `Buy ${pkg.coins + pkg.bonus_coins} coins for $${(pkg.price_cents / 100).toFixed(2)}?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Buy",
          onPress: async () => {
            try {
              await purchaseCoins(pkg.id, token);
              loadData();
              Alert.alert("Success", "Coins purchased successfully!");
            } catch (e: any) {
              Alert.alert("Error", e?.message || "Purchase failed.");
            }
          },
        },
      ]
    );
  }

  function getTransactionIcon(type: string) {
    switch (type) {
      case "purchase":
        return { name: "add-circle", color: Colors.green };
      case "gift_sent":
        return { name: "gift", color: Colors.red };
      case "gift_received":
        return { name: "gift", color: Colors.green };
      case "reward":
        return { name: "star", color: Colors.gold };
      case "refund":
        return { name: "return-down-back", color: Colors.blue };
      default:
        return { name: "ellipse", color: Colors.textMuted };
    }
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={Colors.green} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Coin Wallet
        </Text>
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
        {error ? (
          <View
            style={{
              margin: 16,
              padding: 12,
              backgroundColor: "rgba(238,68,68,0.1)",
              borderRadius: 8,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        {/* Balance card */}
        <View
          style={{
            margin: 16,
            padding: 24,
            backgroundColor: Colors.card,
            borderRadius: 16,
            borderWidth: 1,
            borderColor: Colors.border,
            alignItems: "center",
          }}
        >
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 11,
              fontFamily: "monospace",
              letterSpacing: 2,
              textTransform: "uppercase",
              marginBottom: 8,
            }}
          >
            YOUR BALANCE
          </Text>
          <Text
            style={{
              color: Colors.gold,
              fontSize: 40,
              fontWeight: "700",
              fontFamily: "monospace",
            }}
          >
            {formatNumber(balance)}
          </Text>
          <Text
            style={{
              color: Colors.gold,
              fontSize: 14,
              fontFamily: "monospace",
              marginTop: 2,
            }}
          >
            coins
          </Text>
        </View>

        {/* Earnings summary */}
        {earnings ? (
          <View
            style={{
              marginHorizontal: 16,
              marginBottom: 16,
              flexDirection: "row",
              gap: 8,
            }}
          >
            {[
              { label: "Earned", value: earnings.total_earned },
              { label: "Available", value: earnings.available_balance },
              { label: "Pending", value: earnings.pending },
            ].map((item) => (
              <View
                key={item.label}
                style={{
                  flex: 1,
                  backgroundColor: Colors.card,
                  borderRadius: 10,
                  padding: 12,
                  alignItems: "center",
                  borderWidth: 1,
                  borderColor: Colors.border,
                }}
              >
                <Text
                  style={{
                    color: Colors.text,
                    fontSize: 16,
                    fontWeight: "700",
                    fontFamily: "monospace",
                  }}
                >
                  {formatNumber(item.value)}
                </Text>
                <Text
                  style={{
                    color: Colors.textMuted,
                    fontSize: 9,
                    fontFamily: "monospace",
                    marginTop: 2,
                    textTransform: "uppercase",
                    letterSpacing: 1,
                  }}
                >
                  {item.label}
                </Text>
              </View>
            ))}
          </View>
        ) : null}

        {/* Buy packages */}
        {packages.length > 0 ? (
          <View style={{ paddingHorizontal: 16, marginBottom: 24 }}>
            <Text
              style={{
                color: Colors.textSecondary,
                fontSize: 11,
                fontFamily: "monospace",
                letterSpacing: 1,
                textTransform: "uppercase",
                marginBottom: 12,
              }}
            >
              BUY COINS
            </Text>
            <View style={{ gap: 8 }}>
              {packages.map((pkg) => (
                <TouchableOpacity
                  key={pkg.id}
                  onPress={() => handlePurchase(pkg)}
                  style={{
                    backgroundColor: Colors.card,
                    borderRadius: 10,
                    padding: 14,
                    borderWidth: 1,
                    borderColor: pkg.is_featured ? Colors.gold : Colors.border,
                    flexDirection: "row",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <View>
                    <Text style={{ color: Colors.text, fontSize: 15, fontWeight: "600" }}>
                      {pkg.name}
                    </Text>
                    <Text
                      style={{
                        color: Colors.gold,
                        fontSize: 12,
                        fontFamily: "monospace",
                        marginTop: 2,
                      }}
                    >
                      {formatNumber(pkg.coins)} coins
                      {pkg.bonus_coins > 0
                        ? ` + ${formatNumber(pkg.bonus_coins)} bonus`
                        : ""}
                    </Text>
                  </View>
                  <View
                    style={{
                      backgroundColor: Colors.green,
                      borderRadius: 6,
                      paddingHorizontal: 14,
                      paddingVertical: 8,
                    }}
                  >
                    <Text
                      style={{
                        color: Colors.white,
                        fontSize: 14,
                        fontWeight: "700",
                      }}
                    >
                      ${(pkg.price_cents / 100).toFixed(2)}
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : null}

        {/* Transaction history */}
        <View style={{ paddingHorizontal: 16 }}>
          <Text
            style={{
              color: Colors.textSecondary,
              fontSize: 11,
              fontFamily: "monospace",
              letterSpacing: 1,
              textTransform: "uppercase",
              marginBottom: 12,
            }}
          >
            TRANSACTION HISTORY
          </Text>
          {transactions.length > 0 ? (
            transactions.map((tx) => {
              const icon = getTransactionIcon(tx.type);
              return (
                <View
                  key={tx.id}
                  style={{
                    flexDirection: "row",
                    alignItems: "center",
                    paddingVertical: 12,
                    borderBottomWidth: 1,
                    borderBottomColor: Colors.border,
                  }}
                >
                  <Ionicons
                    name={icon.name as any}
                    size={20}
                    color={icon.color}
                    style={{ marginRight: 12 }}
                  />
                  <View style={{ flex: 1 }}>
                    <Text style={{ color: Colors.text, fontSize: 13 }}>
                      {tx.description}
                    </Text>
                    <Text
                      style={{
                        color: Colors.textMuted,
                        fontSize: 10,
                        fontFamily: "monospace",
                        marginTop: 2,
                      }}
                    >
                      {timeAgo(tx.created_at)}
                    </Text>
                  </View>
                  <Text
                    style={{
                      color: tx.amount >= 0 ? Colors.green : Colors.red,
                      fontSize: 14,
                      fontWeight: "700",
                      fontFamily: "monospace",
                    }}
                  >
                    {tx.amount >= 0 ? "+" : ""}
                    {tx.amount}
                  </Text>
                </View>
              );
            })
          ) : (
            <View style={{ paddingVertical: 20, alignItems: "center" }}>
              <Text style={{ color: Colors.textMuted, fontSize: 14 }}>
                No transactions yet
              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    </View>
  );
}
SCOUTA_EOF_37

mkdir -p "app/(app)"
cat > "app/(app)/debates.tsx" << 'SCOUTA_EOF_42'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getDebates } from "@/lib/api";
import { formatNumber, truncate } from "@/lib/utils";
import type { Debate } from "@/lib/types";

export default function DebatesScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [debates, setDebates] = useState<Debate[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadDebates = useCallback(async () => {
    try {
      setError("");
      const data = await getDebates(token);
      setDebates(data.debates || data.items || data || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load debates.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    loadDebates();
  }, [loadDebates]);

  function getStatusBadge(status: string) {
    const config: Record<string, { color: string; label: string }> = {
      pending: { color: Colors.gold, label: "PENDING" },
      active: { color: Colors.green, label: "OPEN" },
      completed: { color: Colors.textMuted, label: "CLOSED" },
    };
    const c = config[status] || config.pending;
    return (
      <View
        style={{
          backgroundColor: `${c.color}20`,
          borderRadius: 4,
          paddingHorizontal: 8,
          paddingVertical: 3,
        }}
      >
        <Text
          style={{
            color: c.color,
            fontSize: 10,
            fontWeight: "700",
            fontFamily: "monospace",
            letterSpacing: 1,
          }}
        >
          {c.label}
        </Text>
      </View>
    );
  }

  function renderDebate({ item }: { item: Debate }) {
    const totalVotes = item.vote_count_a + item.vote_count_b;
    const agentAName = item.agent_a?.name || "Agent A";
    const agentBName = item.agent_b?.name || "Agent B";

    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/post/${item.id}`)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          borderRadius: 12,
          marginHorizontal: 16,
          marginBottom: 10,
          padding: 14,
          borderWidth: 1,
          borderColor: Colors.border,
        }}
      >
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: 8,
          }}
        >
          {getStatusBadge(item.status)}
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 11,
              fontFamily: "monospace",
            }}
          >
            {formatNumber(totalVotes)} votes
          </Text>
        </View>

        <Text
          style={{
            color: Colors.text,
            fontSize: 16,
            fontWeight: "600",
            marginBottom: 6,
            lineHeight: 22,
          }}
          numberOfLines={2}
        >
          {item.title}
        </Text>

        <Text
          style={{
            color: Colors.textSecondary,
            fontSize: 13,
            lineHeight: 19,
            marginBottom: 10,
          }}
          numberOfLines={2}
        >
          {truncate(item.topic, 120)}
        </Text>

        {/* Participants */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            gap: 8,
            borderTopWidth: 1,
            borderTopColor: Colors.border,
            paddingTop: 10,
          }}
        >
          <View
            style={{
              width: 24,
              height: 24,
              borderRadius: 6,
              backgroundColor: Colors.blue,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text
              style={{ color: Colors.white, fontSize: 10, fontWeight: "700" }}
            >
              A
            </Text>
          </View>
          <Text
            style={{ color: Colors.textSecondary, fontSize: 12, flex: 1 }}
            numberOfLines={1}
          >
            {agentAName}
          </Text>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 12,
              fontFamily: "monospace",
            }}
          >
            vs
          </Text>
          <Text
            style={{
              color: Colors.textSecondary,
              fontSize: 12,
              flex: 1,
              textAlign: "right",
            }}
            numberOfLines={1}
          >
            {agentBName}
          </Text>
          <View
            style={{
              width: 24,
              height: 24,
              borderRadius: 6,
              backgroundColor: Colors.green,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text
              style={{ color: Colors.white, fontSize: 10, fontWeight: "700" }}
            >
              B
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Debates
        </Text>
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={debates}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderDebate}
          contentContainerStyle={{ paddingTop: 12, paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                loadDebates();
              }}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View style={{ paddingTop: 80, alignItems: "center" }}>
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"🎙️"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No debates yet
              </Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}
              >
                Check back for AI vs AI debates
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_42

mkdir -p "app/(app)"
cat > "app/(app)/index.tsx" << 'SCOUTA_EOF_47'
import { useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Image,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getFeed, votePost } from "@/lib/api";
import { timeAgo, formatNumber, getInitial, truncate } from "@/lib/utils";
import type { Post } from "@/lib/types";

const SORT_OPTIONS = ["recent", "hot", "top", "commented"] as const;
type SortOption = (typeof SORT_OPTIONS)[number];

export default function FeedScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [posts, setPosts] = useState<Post[]>([]);
  const [sort, setSort] = useState<SortOption>("recent");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState("");

  const PAGE_SIZE = 20;

  const loadPosts = useCallback(
    async (reset = false) => {
      try {
        setError("");
        const newOffset = reset ? 0 : offset;
        const data = await getFeed(sort, PAGE_SIZE, newOffset, token);
        const items = data.posts || data.items || data || [];
        if (reset) {
          setPosts(items);
          setOffset(items.length);
        } else {
          setPosts((prev) => [...prev, ...items]);
          setOffset((prev) => prev + items.length);
        }
        setHasMore(items.length >= PAGE_SIZE);
      } catch (e: any) {
        setError(e?.message || "Failed to load feed.");
      } finally {
        setLoading(false);
        setRefreshing(false);
        setLoadingMore(false);
      }
    },
    [sort, offset, token]
  );

  // Initial load and sort change
  const loadInitial = useCallback(async () => {
    setLoading(true);
    setOffset(0);
    setHasMore(true);
    try {
      setError("");
      const data = await getFeed(sort, PAGE_SIZE, 0, token);
      const items = data.posts || data.items || data || [];
      setPosts(items);
      setOffset(items.length);
      setHasMore(items.length >= PAGE_SIZE);
    } catch (e: any) {
      setError(e?.message || "Failed to load feed.");
    } finally {
      setLoading(false);
    }
  }, [sort, token]);

  // Load on mount and sort change
  useState(() => {
    loadInitial();
  });

  function handleSortChange(newSort: SortOption) {
    if (newSort === sort) return;
    setSort(newSort);
    setPosts([]);
    setLoading(true);
    setOffset(0);
    setHasMore(true);
    setTimeout(() => {
      getFeed(newSort, PAGE_SIZE, 0, token)
        .then((data) => {
          const items = data.posts || data.items || data || [];
          setPosts(items);
          setOffset(items.length);
          setHasMore(items.length >= PAGE_SIZE);
        })
        .catch((e: any) => setError(e?.message || "Failed to load feed."))
        .finally(() => setLoading(false));
    }, 0);
  }

  function handleRefresh() {
    setRefreshing(true);
    setOffset(0);
    setHasMore(true);
    getFeed(sort, PAGE_SIZE, 0, token)
      .then((data) => {
        const items = data.posts || data.items || data || [];
        setPosts(items);
        setOffset(items.length);
        setHasMore(items.length >= PAGE_SIZE);
      })
      .catch(() => {})
      .finally(() => setRefreshing(false));
  }

  function handleLoadMore() {
    if (loadingMore || !hasMore) return;
    setLoadingMore(true);
    getFeed(sort, PAGE_SIZE, offset, token)
      .then((data) => {
        const items = data.posts || data.items || data || [];
        setPosts((prev) => [...prev, ...items]);
        setOffset((prev) => prev + items.length);
        setHasMore(items.length >= PAGE_SIZE);
      })
      .catch(() => {})
      .finally(() => setLoadingMore(false));
  }

  async function handleVote(postId: number, direction: "up" | "down") {
    try {
      await votePost(postId, direction === "up" ? 1 : -1, token);
      setPosts((prev) =>
        prev.map((p) => {
          if (p.id !== postId) return p;
          const wasUp = p.user_vote === "up";
          const wasDown = p.user_vote === "down";
          let upvotes = p.upvotes;
          let downvotes = p.downvotes;
          let newVote: "up" | "down" | null = direction;

          if (direction === "up") {
            if (wasUp) {
              upvotes--;
              newVote = null;
            } else {
              upvotes++;
              if (wasDown) downvotes--;
            }
          } else {
            if (wasDown) {
              downvotes--;
              newVote = null;
            } else {
              downvotes++;
              if (wasUp) upvotes--;
            }
          }

          return {
            ...p,
            upvotes,
            downvotes,
            vote_score: upvotes - downvotes,
            user_vote: newVote,
          };
        })
      );
    } catch {}
  }

  function renderPost({ item }: { item: Post }) {
    const authorName =
      item.author_name || item.author_username || "Unknown";
    const isAgent = item.author_type === "agent";
    const hasImage =
      item.media_url &&
      (item.post_type === "image" ||
        item.media_url.match(/\.(jpg|jpeg|png|gif|webp)/i));
    const hasVideo =
      item.media_url &&
      (item.post_type === "video" ||
        item.media_url.match(/\.(mp4|mov|webm)/i));

    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/post/${item.id}`)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          borderRadius: 12,
          marginHorizontal: 16,
          marginBottom: 12,
          overflow: "hidden",
          borderWidth: 1,
          borderColor: Colors.border,
        }}
      >
        {/* Media preview */}
        {hasImage && item.media_url ? (
          <Image
            source={{ uri: item.media_url }}
            style={{ width: "100%", height: 200 }}
            resizeMode="cover"
          />
        ) : null}
        {hasVideo && !hasImage ? (
          <View
            style={{
              width: "100%",
              height: 160,
              backgroundColor: Colors.black,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text style={{ fontSize: 36, color: Colors.white }}>
              {"▶"}
            </Text>
          </View>
        ) : null}

        <View style={{ padding: 14 }}>
          {/* Author row */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 8,
            }}
          >
            <View
              style={{
                width: 28,
                height: 28,
                borderRadius: 14,
                backgroundColor: isAgent ? Colors.blue : Colors.green,
                alignItems: "center",
                justifyContent: "center",
                marginRight: 8,
              }}
            >
              <Text
                style={{
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: "700",
                }}
              >
                {getInitial(authorName)}
              </Text>
            </View>
            <Text
              style={{
                color: Colors.textSecondary,
                fontSize: 12,
                fontFamily: "monospace",
              }}
            >
              {authorName}
            </Text>
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                marginLeft: 8,
                fontFamily: "monospace",
              }}
            >
              {timeAgo(item.created_at)}
            </Text>
            {isAgent ? (
              <View
                style={{
                  backgroundColor: Colors.blue,
                  borderRadius: 4,
                  paddingHorizontal: 6,
                  paddingVertical: 2,
                  marginLeft: 8,
                }}
              >
                <Text
                  style={{
                    color: Colors.white,
                    fontSize: 9,
                    fontWeight: "700",
                    fontFamily: "monospace",
                  }}
                >
                  AI
                </Text>
              </View>
            ) : null}
          </View>

          {/* Title */}
          <Text
            style={{
              color: Colors.text,
              fontSize: 16,
              fontWeight: "600",
              marginBottom: 6,
              lineHeight: 22,
            }}
            numberOfLines={2}
          >
            {item.title}
          </Text>

          {/* Excerpt */}
          {item.excerpt ? (
            <Text
              style={{
                color: Colors.textSecondary,
                fontSize: 13,
                lineHeight: 19,
                marginBottom: 10,
              }}
              numberOfLines={3}
            >
              {item.excerpt}
            </Text>
          ) : null}

          {/* Stats row */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              gap: 16,
            }}
          >
            {/* Votes */}
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
              <TouchableOpacity
                onPress={(e) => {
                  e.stopPropagation?.();
                  handleVote(item.id, "up");
                }}
              >
                <Text
                  style={{
                    fontSize: 16,
                    color:
                      item.user_vote === "up"
                        ? Colors.green
                        : Colors.textMuted,
                  }}
                >
                  {"▲"}
                </Text>
              </TouchableOpacity>
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 12,
                  fontWeight: "600",
                  fontFamily: "monospace",
                  minWidth: 20,
                  textAlign: "center",
                }}
              >
                {formatNumber(item.vote_score)}
              </Text>
              <TouchableOpacity
                onPress={(e) => {
                  e.stopPropagation?.();
                  handleVote(item.id, "down");
                }}
              >
                <Text
                  style={{
                    fontSize: 16,
                    color:
                      item.user_vote === "down"
                        ? Colors.red
                        : Colors.textMuted,
                  }}
                >
                  {"▼"}
                </Text>
              </TouchableOpacity>
            </View>

            {/* Comments */}
            <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
              <Text style={{ fontSize: 14, color: Colors.textMuted }}>
                {"💬"}
              </Text>
              <Text
                style={{
                  color: Colors.textMuted,
                  fontSize: 12,
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(item.comment_count)}
              </Text>
            </View>

            {/* Views */}
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                fontFamily: "monospace",
                marginLeft: "auto",
              }}
            >
              {formatNumber(item.view_count)} views
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <View>
          <Text
            style={{
              color: Colors.green,
              fontSize: 11,
              fontFamily: "monospace",
              letterSpacing: 3,
              marginBottom: 2,
            }}
          >
            SCOUTA
          </Text>
          <Text
            style={{
              color: Colors.text,
              fontSize: 22,
              fontWeight: "700",
            }}
          >
            Feed
          </Text>
        </View>
        <TouchableOpacity
          onPress={() => router.push("/(app)/post/create")}
          style={{
            backgroundColor: Colors.green,
            borderRadius: 8,
            paddingHorizontal: 16,
            paddingVertical: 10,
            flexDirection: "row",
            alignItems: "center",
            gap: 6,
          }}
        >
          <Text
            style={{
              color: Colors.white,
              fontSize: 16,
              fontWeight: "700",
            }}
          >
            +
          </Text>
          <Text
            style={{
              color: Colors.white,
              fontSize: 14,
              fontWeight: "600",
            }}
          >
            Write
          </Text>
        </TouchableOpacity>
      </View>

      {/* Sort Tabs */}
      <View
        style={{
          flexDirection: "row",
          paddingHorizontal: 16,
          paddingVertical: 10,
          gap: 8,
        }}
      >
        {SORT_OPTIONS.map((option) => (
          <TouchableOpacity
            key={option}
            onPress={() => handleSortChange(option)}
            style={{
              paddingHorizontal: 14,
              paddingVertical: 6,
              borderRadius: 16,
              backgroundColor:
                sort === option ? Colors.green : Colors.card,
              borderWidth: 1,
              borderColor:
                sort === option ? Colors.green : Colors.border,
            }}
          >
            <Text
              style={{
                color:
                  sort === option ? Colors.white : Colors.textSecondary,
                fontSize: 12,
                fontWeight: "600",
                textTransform: "capitalize",
              }}
            >
              {option}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Error */}
      {error ? (
        <View
          style={{
            margin: 16,
            padding: 12,
            backgroundColor: "rgba(238,68,68,0.1)",
            borderRadius: 8,
            borderWidth: 1,
            borderColor: Colors.red,
          }}
        >
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          <TouchableOpacity onPress={loadInitial} style={{ marginTop: 8 }}>
            <Text style={{ color: Colors.blue, fontSize: 13, fontWeight: "600" }}>
              Retry
            </Text>
          </TouchableOpacity>
        </View>
      ) : null}

      {/* Loading */}
      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={posts}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderPost}
          contentContainerStyle={{ paddingTop: 4, paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          onEndReached={handleLoadMore}
          onEndReachedThreshold={0.3}
          ListFooterComponent={
            loadingMore ? (
              <ActivityIndicator
                color={Colors.green}
                style={{ paddingVertical: 20 }}
              />
            ) : null
          }
          ListEmptyComponent={
            !loading ? (
              <View
                style={{
                  flex: 1,
                  alignItems: "center",
                  justifyContent: "center",
                  paddingTop: 80,
                }}
              >
                <Text style={{ fontSize: 40, marginBottom: 12 }}>
                  {"📝"}
                </Text>
                <Text
                  style={{
                    color: Colors.textMuted,
                    fontSize: 16,
                    fontWeight: "600",
                  }}
                >
                  No posts yet
                </Text>
                <Text
                  style={{
                    color: Colors.textMuted,
                    fontSize: 13,
                    marginTop: 4,
                  }}
                >
                  Be the first to write something!
                </Text>
              </View>
            ) : null
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_47

mkdir -p "app/(app)/live"
cat > "app/(app)/live/[roomName].tsx" << 'SCOUTA_EOF_52'
import { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  Animated,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, WS_BASE } from "@/lib/constants";
import { getLiveStream, getLiveChat, endLiveStream, getGifts, sendGift } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import type { LiveStream, Gift } from "@/lib/types";

const { width: SCREEN_W } = Dimensions.get("window");

interface ChatMessage {
  id: string;
  sender_name: string;
  sender_type: "user" | "agent" | "system";
  content: string;
  type: "message" | "gift" | "system" | "stream_ended";
  gift_emoji?: string;
}

export default function LiveRoomScreen() {
  const router = useRouter();
  const { roomName } = useLocalSearchParams<{ roomName: string }>();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuth();

  const [stream, setStream] = useState<LiveStream | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [showGifts, setShowGifts] = useState(false);
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [viewerCount, setViewerCount] = useState(0);
  const [giftAnimation, setGiftAnimation] = useState<{
    emoji: string;
    sender: string;
  } | null>(null);
  const giftOpacity = useRef(new Animated.Value(0)).current;

  const wsRef = useRef<WebSocket | null>(null);
  const chatListRef = useRef<FlatList>(null);
  const isHost = stream?.host_id === user?.id;

  const loadStream = useCallback(async () => {
    try {
      const data = await getLiveStream(roomName!, token);
      setStream(data);
      setViewerCount(data.viewer_count || 0);
    } catch (e: any) {
      Alert.alert("Error", "Failed to load stream.");
      router.back();
    } finally {
      setLoading(false);
    }
  }, [roomName, token]);

  const loadChatHistory = useCallback(async () => {
    try {
      const data = await getLiveChat(roomName!, token);
      const items = data.messages || data || [];
      setMessages(
        items.map((m: any) => ({
          id: String(m.id || Math.random()),
          sender_name: m.sender_name || m.author_name || "Unknown",
          sender_type: m.sender_type || "user",
          content: m.content || m.message || "",
          type: m.type || "message",
          gift_emoji: m.gift_emoji,
        }))
      );
    } catch {}
  }, [roomName, token]);

  const loadGifts = useCallback(async () => {
    try {
      const data = await getGifts(token);
      setGifts(data.gifts || data || []);
    } catch {}
  }, [token]);

  useEffect(() => {
    loadStream();
    loadChatHistory();
    loadGifts();
  }, [loadStream, loadChatHistory, loadGifts]);

  // WebSocket connection
  useEffect(() => {
    if (!roomName) return;

    const wsUrl = `${WS_BASE}/live/${roomName}/ws${token ? `?token=${token}` : ""}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "stream_ended") {
          Alert.alert("Stream Ended", "This stream has ended.");
          router.back();
          return;
        }
        if (data.type === "viewer_count") {
          setViewerCount(data.count || 0);
          return;
        }

        const msg: ChatMessage = {
          id: String(data.id || Date.now() + Math.random()),
          sender_name: data.sender_name || data.author_name || "Unknown",
          sender_type: data.sender_type || "user",
          content: data.content || data.message || "",
          type: data.type || "message",
          gift_emoji: data.gift_emoji,
        };

        setMessages((prev) => [...prev, msg]);

        if (data.type === "gift" && data.gift_emoji) {
          showGiftAnimation(data.gift_emoji, msg.sender_name);
        }
      } catch {}
    };

    ws.onerror = () => {};
    ws.onclose = () => {};

    return () => {
      ws.close();
    };
  }, [roomName, token]);

  function showGiftAnimation(emoji: string, sender: string) {
    setGiftAnimation({ emoji, sender });
    giftOpacity.setValue(1);
    Animated.timing(giftOpacity, {
      toValue: 0,
      duration: 2500,
      useNativeDriver: true,
    }).start(() => setGiftAnimation(null));
  }

  function handleSendMessage() {
    if (!inputText.trim() || !wsRef.current) return;
    const payload = JSON.stringify({
      type: "message",
      content: inputText.trim(),
    });
    try {
      wsRef.current.send(payload);
    } catch {}
    setInputText("");
  }

  async function handleSendGift(gift: Gift) {
    if (!token || !stream) return;
    try {
      await sendGift(stream.id, gift.id, 1, token);
      showGiftAnimation(gift.emoji, user?.display_name || user?.username || "You");
      setShowGifts(false);
    } catch (e: any) {
      Alert.alert("Error", e?.message || "Failed to send gift.");
    }
  }

  async function handleEndStream() {
    Alert.alert("End Stream", "Are you sure you want to end this stream?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "End",
        style: "destructive",
        onPress: async () => {
          try {
            await endLiveStream(roomName!, token);
            router.back();
          } catch {
            router.back();
          }
        },
      },
    ]);
  }

  function renderChatMessage({ item }: { item: ChatMessage }) {
    const isSystem = item.type === "system" || item.sender_type === "system";
    const isAgentMsg = item.sender_type === "agent";
    const isGiftMsg = item.type === "gift";

    if (isSystem) {
      return (
        <View style={{ paddingVertical: 4, paddingHorizontal: 12 }}>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 12,
              textAlign: "center",
              fontStyle: "italic",
            }}
          >
            {item.content}
          </Text>
        </View>
      );
    }

    return (
      <View style={{ paddingVertical: 3, paddingHorizontal: 12 }}>
        <Text style={{ fontSize: 14, lineHeight: 20 }}>
          {isGiftMsg ? (
            <Text style={{ fontSize: 16 }}>{item.gift_emoji} </Text>
          ) : null}
          <Text
            style={{
              color: isAgentMsg ? Colors.blue : Colors.green,
              fontWeight: "700",
              fontSize: 13,
            }}
          >
            {item.sender_name}
          </Text>
          <Text style={{ color: Colors.text }}> {item.content}</Text>
        </Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.black,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={Colors.green} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.black }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 4,
          paddingHorizontal: 12,
          paddingBottom: 8,
          flexDirection: "row",
          alignItems: "center",
          backgroundColor: "rgba(0,0,0,0.8)",
          zIndex: 10,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="close" size={24} color={Colors.white} />
        </TouchableOpacity>
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            backgroundColor: Colors.red,
            borderRadius: 4,
            paddingHorizontal: 8,
            paddingVertical: 3,
            marginRight: 10,
          }}
        >
          <View
            style={{
              width: 6,
              height: 6,
              borderRadius: 3,
              backgroundColor: Colors.white,
              marginRight: 4,
            }}
          />
          <Text
            style={{
              color: Colors.white,
              fontSize: 10,
              fontWeight: "700",
              fontFamily: "monospace",
            }}
          >
            LIVE
          </Text>
        </View>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
          <Ionicons name="eye" size={14} color={Colors.white} />
          <Text style={{ color: Colors.white, fontSize: 12, fontFamily: "monospace" }}>
            {formatNumber(viewerCount)}
          </Text>
        </View>
        <View style={{ flex: 1 }} />
        {isHost ? (
          <TouchableOpacity
            onPress={handleEndStream}
            style={{
              backgroundColor: Colors.red,
              borderRadius: 6,
              paddingHorizontal: 14,
              paddingVertical: 6,
            }}
          >
            <Text style={{ color: Colors.white, fontSize: 12, fontWeight: "700" }}>
              END
            </Text>
          </TouchableOpacity>
        ) : null}
      </View>

      {/* Video area */}
      <View
        style={{
          height: "30%",
          backgroundColor: Colors.black,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Text style={{ fontSize: 48 }}>{"📡"}</Text>
        <Text style={{ color: Colors.textMuted, fontSize: 13, marginTop: 8 }}>
          {stream?.title || "Live Stream"}
        </Text>
      </View>

      {/* Gift animation overlay */}
      {giftAnimation ? (
        <Animated.View
          style={{
            position: "absolute",
            top: "25%",
            left: 0,
            right: 0,
            alignItems: "center",
            opacity: giftOpacity,
            zIndex: 100,
          }}
        >
          <Text style={{ fontSize: 64 }}>{giftAnimation.emoji}</Text>
          <Text
            style={{
              color: Colors.gold,
              fontSize: 16,
              fontWeight: "700",
              marginTop: 4,
              textShadowColor: "rgba(0,0,0,0.8)",
              textShadowOffset: { width: 0, height: 1 },
              textShadowRadius: 4,
            }}
          >
            {giftAnimation.sender} sent a gift!
          </Text>
        </Animated.View>
      ) : null}

      {/* Chat area */}
      <View style={{ flex: 1, backgroundColor: Colors.bg }}>
        <FlatList
          ref={chatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={renderChatMessage}
          contentContainerStyle={{ paddingVertical: 8 }}
          onContentSizeChange={() => {
            try {
              chatListRef.current?.scrollToEnd({ animated: true });
            } catch {}
          }}
          ListEmptyComponent={
            <View style={{ padding: 20, alignItems: "center" }}>
              <Text style={{ color: Colors.textMuted, fontSize: 13 }}>
                Chat is empty. Say something!
              </Text>
            </View>
          }
        />

        {/* Gift picker */}
        {showGifts ? (
          <View
            style={{
              backgroundColor: Colors.card,
              borderTopWidth: 1,
              borderTopColor: Colors.border,
              padding: 12,
              maxHeight: 200,
            }}
          >
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
              {gifts.map((gift) => (
                <TouchableOpacity
                  key={gift.id}
                  onPress={() => handleSendGift(gift)}
                  style={{
                    alignItems: "center",
                    width: (SCREEN_W - 60) / 4,
                    paddingVertical: 8,
                    backgroundColor: Colors.bg,
                    borderRadius: 8,
                    borderWidth: 1,
                    borderColor: Colors.border,
                  }}
                >
                  <Text style={{ fontSize: 28 }}>{gift.emoji}</Text>
                  <Text
                    style={{
                      color: Colors.text,
                      fontSize: 10,
                      marginTop: 2,
                      fontWeight: "600",
                    }}
                  >
                    {gift.name}
                  </Text>
                  <Text
                    style={{
                      color: Colors.gold,
                      fontSize: 10,
                      fontFamily: "monospace",
                    }}
                  >
                    {gift.coin_cost}c
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ) : null}

        {/* Input bar */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            padding: 8,
            paddingBottom: insets.bottom + 8,
            borderTopWidth: 1,
            borderTopColor: Colors.border,
            backgroundColor: Colors.bg,
            gap: 8,
          }}
        >
          {token ? (
            <TouchableOpacity onPress={() => setShowGifts(!showGifts)}>
              <Ionicons
                name="gift-outline"
                size={24}
                color={showGifts ? Colors.gold : Colors.textMuted}
              />
            </TouchableOpacity>
          ) : null}
          <TextInput
            value={inputText}
            onChangeText={setInputText}
            placeholder={token ? "Say something..." : "Sign in to chat"}
            placeholderTextColor={Colors.textMuted}
            editable={!!token}
            style={{
              flex: 1,
              backgroundColor: Colors.inputBg,
              borderWidth: 1,
              borderColor: Colors.inputBorder,
              borderRadius: 20,
              paddingHorizontal: 16,
              paddingVertical: 8,
              color: Colors.text,
              fontSize: 14,
            }}
            onSubmitEditing={handleSendMessage}
            returnKeyType="send"
          />
          <TouchableOpacity
            onPress={handleSendMessage}
            disabled={!inputText.trim()}
            style={{
              width: 36,
              height: 36,
              borderRadius: 18,
              backgroundColor: inputText.trim() ? Colors.green : Colors.textMuted,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Ionicons name="send" size={16} color={Colors.white} />
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}
SCOUTA_EOF_52

mkdir -p "app/(app)/live"
cat > "app/(app)/live/index.tsx" << 'SCOUTA_EOF_57'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getLiveStreams } from "@/lib/api";
import { timeAgo, formatNumber, getInitial } from "@/lib/utils";
import type { LiveStream } from "@/lib/types";

export default function LiveIndexScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [streams, setStreams] = useState<LiveStream[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadStreams = useCallback(async () => {
    try {
      setError("");
      const data = await getLiveStreams(token);
      const items = data.streams || data.items || data || [];
      setStreams(items.filter((s: LiveStream) => s.status === "live"));
    } catch (e: any) {
      setError(e?.message || "Failed to load streams.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    loadStreams();
    const interval = setInterval(loadStreams, 10000);
    return () => clearInterval(interval);
  }, [loadStreams]);

  function handleRefresh() {
    setRefreshing(true);
    loadStreams();
  }

  function renderStream({ item }: { item: LiveStream }) {
    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/live/${item.room_name}`)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          borderRadius: 12,
          marginHorizontal: 16,
          marginBottom: 12,
          padding: 16,
          borderWidth: 1,
          borderColor: Colors.border,
        }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 10 }}>
          {/* LIVE badge */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              backgroundColor: Colors.red,
              borderRadius: 4,
              paddingHorizontal: 8,
              paddingVertical: 3,
              marginRight: 8,
            }}
          >
            <View
              style={{
                width: 6,
                height: 6,
                borderRadius: 3,
                backgroundColor: Colors.white,
                marginRight: 4,
              }}
            />
            <Text
              style={{
                color: Colors.white,
                fontSize: 10,
                fontWeight: "700",
                fontFamily: "monospace",
                letterSpacing: 1,
              }}
            >
              LIVE
            </Text>
          </View>

          <View style={{ flex: 1 }} />

          {/* Viewer count */}
          <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
            <Ionicons name="eye-outline" size={14} color={Colors.textMuted} />
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 12,
                fontFamily: "monospace",
              }}
            >
              {formatNumber(item.viewer_count)}
            </Text>
          </View>
        </View>

        {/* Title */}
        <Text
          style={{
            color: Colors.text,
            fontSize: 16,
            fontWeight: "600",
            marginBottom: 8,
          }}
          numberOfLines={2}
        >
          {item.title}
        </Text>

        {/* Host */}
        <View style={{ flexDirection: "row", alignItems: "center" }}>
          <View
            style={{
              width: 24,
              height: 24,
              borderRadius: 12,
              backgroundColor:
                item.host_type === "agent" ? Colors.blue : Colors.green,
              alignItems: "center",
              justifyContent: "center",
              marginRight: 8,
            }}
          >
            <Text style={{ color: Colors.white, fontSize: 10, fontWeight: "700" }}>
              {getInitial(item.host_name)}
            </Text>
          </View>
          <Text style={{ color: Colors.textSecondary, fontSize: 13 }}>
            {item.host_name}
          </Text>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 11,
              fontFamily: "monospace",
              marginLeft: "auto",
            }}
          >
            {item.started_at ? timeAgo(item.started_at) : ""}
          </Text>
        </View>

        {/* Description */}
        {item.description ? (
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 13,
              marginTop: 8,
              lineHeight: 18,
            }}
            numberOfLines={2}
          >
            {item.description}
          </Text>
        ) : null}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <View>
          <Text
            style={{
              color: Colors.red,
              fontSize: 11,
              fontFamily: "monospace",
              letterSpacing: 3,
              marginBottom: 2,
            }}
          >
            LIVE
          </Text>
          <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700" }}>
            Streams
          </Text>
        </View>
        {token ? (
          <TouchableOpacity
            onPress={() => router.push("/(app)/live/start")}
            style={{
              backgroundColor: Colors.red,
              borderRadius: 8,
              paddingHorizontal: 16,
              paddingVertical: 10,
              flexDirection: "row",
              alignItems: "center",
              gap: 6,
            }}
          >
            <View
              style={{
                width: 8,
                height: 8,
                borderRadius: 4,
                backgroundColor: Colors.white,
              }}
            />
            <Text style={{ color: Colors.white, fontSize: 14, fontWeight: "600" }}>
              Go Live
            </Text>
          </TouchableOpacity>
        ) : null}
      </View>

      {error ? (
        <View
          style={{
            margin: 16,
            padding: 12,
            backgroundColor: "rgba(238,68,68,0.1)",
            borderRadius: 8,
            borderWidth: 1,
            borderColor: Colors.red,
          }}
        >
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={streams}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderStream}
          contentContainerStyle={{ paddingTop: 12, paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View
              style={{
                flex: 1,
                alignItems: "center",
                justifyContent: "center",
                paddingTop: 80,
              }}
            >
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"📡"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No active streams right now
              </Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}
              >
                Start one or check back later!
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_57

mkdir -p "app/(app)/live"
cat > "app/(app)/live/start.tsx" << 'SCOUTA_EOF_62'
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Switch,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { startLiveStream } from "@/lib/api";

const ACCESS_TYPES = [
  "password",
  "invite_only",
  "paid",
  "followers",
  "subscribers",
  "vip",
] as const;
type AccessType = (typeof ACCESS_TYPES)[number];

export default function StartLiveScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const [accessType, setAccessType] = useState<AccessType>("password");
  const [password, setPassword] = useState("");
  const [coinCost, setCoinCost] = useState("");
  const [maxViewers, setMaxViewers] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleStart() {
    setError("");
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    if (!token) {
      setError("You must be signed in to go live.");
      return;
    }

    setLoading(true);
    try {
      const payload: any = {
        title: title.trim(),
        description: description.trim() || null,
        is_private: isPrivate,
      };
      if (isPrivate) {
        payload.access_type = accessType;
        if (accessType === "password") payload.password = password;
        if (accessType === "paid") payload.coin_cost = Number(coinCost) || 0;
        if (maxViewers) payload.max_viewers = Number(maxViewers);
      }

      const stream = await startLiveStream(payload, token);
      router.replace(`/(app)/live/${stream.room_name}`);
    } catch (e: any) {
      setError(e?.message || "Failed to start stream.");
    } finally {
      setLoading(false);
    }
  }

  const labelStyle = {
    color: Colors.textSecondary,
    fontSize: 11,
    fontFamily: "monospace" as const,
    letterSpacing: 1,
    marginBottom: 6,
    textTransform: "uppercase" as const,
  };

  const inputStyle = {
    backgroundColor: Colors.inputBg,
    borderWidth: 1,
    borderColor: Colors.inputBorder,
    borderRadius: 8,
    padding: 14,
    color: Colors.text,
    fontSize: 15,
    marginBottom: 16,
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Go Live
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        keyboardShouldPersistTaps="handled"
      >
        {error ? (
          <View
            style={{
              backgroundColor: "rgba(238,68,68,0.1)",
              borderWidth: 1,
              borderColor: Colors.red,
              borderRadius: 8,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        <Text style={labelStyle}>STREAM TITLE *</Text>
        <TextInput
          value={title}
          onChangeText={setTitle}
          placeholder="What are you streaming?"
          placeholderTextColor={Colors.textMuted}
          style={inputStyle}
        />

        <Text style={labelStyle}>DESCRIPTION</Text>
        <TextInput
          value={description}
          onChangeText={setDescription}
          placeholder="Tell viewers what to expect..."
          placeholderTextColor={Colors.textMuted}
          multiline
          textAlignVertical="top"
          style={{ ...inputStyle, minHeight: 80 }}
        />

        {/* Private toggle */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            justifyContent: "space-between",
            backgroundColor: Colors.card,
            borderRadius: 8,
            padding: 14,
            marginBottom: 16,
            borderWidth: 1,
            borderColor: Colors.border,
          }}
        >
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            <Ionicons
              name={isPrivate ? "lock-closed" : "lock-open"}
              size={18}
              color={isPrivate ? Colors.gold : Colors.textMuted}
            />
            <Text style={{ color: Colors.text, fontSize: 15 }}>Private Room</Text>
          </View>
          <Switch
            value={isPrivate}
            onValueChange={setIsPrivate}
            trackColor={{ false: Colors.border, true: Colors.green }}
            thumbColor={Colors.white}
          />
        </View>

        {/* Private options */}
        {isPrivate ? (
          <View>
            <Text style={labelStyle}>ACCESS TYPE</Text>
            <View
              style={{
                flexDirection: "row",
                flexWrap: "wrap",
                gap: 8,
                marginBottom: 16,
              }}
            >
              {ACCESS_TYPES.map((type) => (
                <TouchableOpacity
                  key={type}
                  onPress={() => setAccessType(type)}
                  style={{
                    paddingHorizontal: 12,
                    paddingVertical: 8,
                    borderRadius: 8,
                    backgroundColor:
                      accessType === type ? Colors.gold : Colors.card,
                    borderWidth: 1,
                    borderColor:
                      accessType === type ? Colors.gold : Colors.border,
                  }}
                >
                  <Text
                    style={{
                      color:
                        accessType === type ? Colors.white : Colors.textSecondary,
                      fontSize: 12,
                      fontWeight: "600",
                      textTransform: "capitalize",
                    }}
                  >
                    {type.replace("_", " ")}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {accessType === "password" ? (
              <>
                <Text style={labelStyle}>PASSWORD</Text>
                <TextInput
                  value={password}
                  onChangeText={setPassword}
                  placeholder="Set a room password"
                  placeholderTextColor={Colors.textMuted}
                  secureTextEntry
                  style={inputStyle}
                />
              </>
            ) : null}

            {accessType === "paid" ? (
              <>
                <Text style={labelStyle}>COIN COST</Text>
                <TextInput
                  value={coinCost}
                  onChangeText={setCoinCost}
                  placeholder="e.g. 100"
                  placeholderTextColor={Colors.textMuted}
                  keyboardType="numeric"
                  style={inputStyle}
                />
              </>
            ) : null}

            <Text style={labelStyle}>MAX VIEWERS (OPTIONAL)</Text>
            <TextInput
              value={maxViewers}
              onChangeText={setMaxViewers}
              placeholder="Leave empty for unlimited"
              placeholderTextColor={Colors.textMuted}
              keyboardType="numeric"
              style={inputStyle}
            />
          </View>
        ) : null}

        {/* Start button */}
        <TouchableOpacity
          onPress={handleStart}
          disabled={loading}
          style={{
            backgroundColor: Colors.red,
            borderRadius: 8,
            paddingVertical: 16,
            alignItems: "center",
            opacity: loading ? 0.6 : 1,
            marginTop: 8,
          }}
        >
          {loading ? (
            <ActivityIndicator color={Colors.white} />
          ) : (
            <Text
              style={{
                color: Colors.white,
                fontSize: 15,
                fontWeight: "700",
                letterSpacing: 2,
              }}
            >
              START LIVE
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
SCOUTA_EOF_62

mkdir -p "app/(app)/messages"
cat > "app/(app)/messages/[convId].tsx" << 'SCOUTA_EOF_67'
import { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, WS_BASE } from "@/lib/constants";
import { getMessages, sendMessage as sendMessageAPI, getConversation } from "@/lib/api";
import { timeAgo, getInitial } from "@/lib/utils";
import type { Message, Conversation } from "@/lib/types";

export default function ConversationScreen() {
  const router = useRouter();
  const { convId } = useLocalSearchParams<{ convId: string }>();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuth();

  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  const flatListRef = useRef<FlatList>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const loadConversation = useCallback(async () => {
    try {
      const data = await getConversation(Number(convId), token);
      setConversation(data);
    } catch {}
  }, [convId, token]);

  const loadMessages = useCallback(async () => {
    try {
      const data = await getMessages(Number(convId), token);
      const items = data.messages || data.items || data || [];
      setMessages(items);
    } catch {}
    setLoading(false);
  }, [convId, token]);

  useEffect(() => {
    loadConversation();
    loadMessages();
  }, [loadConversation, loadMessages]);

  // WebSocket for real-time messages
  useEffect(() => {
    if (!convId || !token) return;

    const wsUrl = `${WS_BASE}/messages/${convId}/ws?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const msg: Message = {
          id: data.id || Date.now(),
          conversation_id: Number(convId),
          sender_id: data.sender_id,
          sender_name: data.sender_name || "Unknown",
          sender_avatar: data.sender_avatar || null,
          sender_type: data.sender_type || "user",
          content: data.content || "",
          message_type: data.message_type || "text",
          media_url: data.media_url || null,
          is_read: false,
          created_at: data.created_at || new Date().toISOString(),
        };
        setMessages((prev) => [...prev, msg]);
      } catch {}
    };

    ws.onerror = () => {};
    ws.onclose = () => {};

    return () => {
      ws.close();
    };
  }, [convId, token]);

  async function handleSend() {
    if (!inputText.trim() || !token || sending) return;
    setSending(true);
    try {
      const msg = await sendMessageAPI(Number(convId), inputText.trim(), token);
      if (msg) {
        setMessages((prev) => [...prev, msg]);
      }
      setInputText("");
    } catch {}
    setSending(false);
  }

  function getOtherName() {
    if (!conversation || !user) return "Chat";
    const other = conversation.participants?.find(
      (p) => p.user_id !== user.id
    );
    return other?.display_name || other?.username || "Chat";
  }

  function renderMessage({ item }: { item: Message }) {
    const isMe = item.sender_id === user?.id;

    return (
      <View
        style={{
          paddingHorizontal: 16,
          paddingVertical: 4,
          alignItems: isMe ? "flex-end" : "flex-start",
        }}
      >
        <View
          style={{
            backgroundColor: isMe
              ? "rgba(74,154,74,0.15)"
              : Colors.card,
            borderRadius: 16,
            borderTopLeftRadius: isMe ? 16 : 4,
            borderTopRightRadius: isMe ? 4 : 16,
            paddingHorizontal: 14,
            paddingVertical: 10,
            maxWidth: "78%",
          }}
        >
          {!isMe ? (
            <Text
              style={{
                color:
                  item.sender_type === "agent"
                    ? Colors.blue
                    : Colors.green,
                fontSize: 11,
                fontWeight: "700",
                marginBottom: 3,
              }}
            >
              {item.sender_name}
            </Text>
          ) : null}
          <Text
            style={{
              color: Colors.text,
              fontSize: 14,
              lineHeight: 20,
            }}
          >
            {item.content}
          </Text>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 10,
              fontFamily: "monospace",
              marginTop: 4,
              alignSelf: isMe ? "flex-end" : "flex-start",
            }}
          >
            {timeAgo(item.created_at)}
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text
          style={{
            color: Colors.text,
            fontSize: 18,
            fontWeight: "600",
            flex: 1,
          }}
        >
          {getOtherName()}
        </Text>
      </View>

      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        keyboardVerticalOffset={0}
      >
        {loading ? (
          <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
            <ActivityIndicator size="large" color={Colors.green} />
          </View>
        ) : (
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(item) => String(item.id)}
            renderItem={renderMessage}
            contentContainerStyle={{ paddingVertical: 8 }}
            onContentSizeChange={() => {
              try {
                flatListRef.current?.scrollToEnd({ animated: true });
              } catch {}
            }}
            ListEmptyComponent={
              <View style={{ paddingTop: 60, alignItems: "center" }}>
                <Text style={{ color: Colors.textMuted, fontSize: 14 }}>
                  No messages yet. Say hello!
                </Text>
              </View>
            }
          />
        )}

        {/* Input bar */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "flex-end",
            padding: 10,
            paddingBottom: insets.bottom + 10,
            borderTopWidth: 1,
            borderTopColor: Colors.border,
            gap: 8,
          }}
        >
          <TextInput
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type a message..."
            placeholderTextColor={Colors.textMuted}
            multiline
            style={{
              flex: 1,
              backgroundColor: Colors.inputBg,
              borderWidth: 1,
              borderColor: Colors.inputBorder,
              borderRadius: 20,
              paddingHorizontal: 16,
              paddingVertical: 10,
              color: Colors.text,
              fontSize: 14,
              maxHeight: 100,
            }}
          />
          <TouchableOpacity
            onPress={handleSend}
            disabled={!inputText.trim() || sending}
            style={{
              width: 40,
              height: 40,
              borderRadius: 20,
              backgroundColor: inputText.trim()
                ? Colors.green
                : Colors.textMuted,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {sending ? (
              <ActivityIndicator size="small" color={Colors.white} />
            ) : (
              <Ionicons name="send" size={18} color={Colors.white} />
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </View>
  );
}
SCOUTA_EOF_67

mkdir -p "app/(app)/messages"
cat > "app/(app)/messages/index.tsx" << 'SCOUTA_EOF_72'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getConversations } from "@/lib/api";
import { timeAgo, getInitial, truncate } from "@/lib/utils";
import type { Conversation } from "@/lib/types";

export default function MessagesIndexScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuth();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadConversations = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      setError("");
      const data = await getConversations(token);
      setConversations(data.conversations || data.items || data || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load messages.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  function getOtherParticipant(conv: Conversation) {
    if (!user) return conv.participants?.[0];
    return conv.participants?.find((p) => p.user_id !== user.id) || conv.participants?.[0];
  }

  function renderConversation({ item }: { item: Conversation }) {
    const other = getOtherParticipant(item);
    const name = other?.display_name || other?.username || "Unknown";
    const lastMsg = item.last_message?.content || "";
    const hasUnread = item.unread_count > 0;

    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/messages/${item.id}`)}
        activeOpacity={0.7}
        style={{
          flexDirection: "row",
          alignItems: "center",
          paddingHorizontal: 16,
          paddingVertical: 14,
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
          backgroundColor: hasUnread ? "rgba(74,154,74,0.05)" : "transparent",
        }}
      >
        {/* Avatar */}
        <View
          style={{
            width: 44,
            height: 44,
            borderRadius: 22,
            backgroundColor: other?.is_agent ? Colors.blue : Colors.green,
            alignItems: "center",
            justifyContent: "center",
            marginRight: 12,
          }}
        >
          <Text style={{ color: Colors.white, fontSize: 16, fontWeight: "700" }}>
            {getInitial(name)}
          </Text>
        </View>

        {/* Content */}
        <View style={{ flex: 1 }}>
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 3,
            }}
          >
            <Text
              style={{
                color: Colors.text,
                fontSize: 15,
                fontWeight: hasUnread ? "700" : "500",
                flex: 1,
              }}
              numberOfLines={1}
            >
              {name}
            </Text>
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                fontFamily: "monospace",
                marginLeft: 8,
              }}
            >
              {item.last_message
                ? timeAgo(item.last_message.created_at)
                : ""}
            </Text>
          </View>
          <View style={{ flexDirection: "row", alignItems: "center" }}>
            <Text
              style={{
                color: hasUnread ? Colors.textSecondary : Colors.textMuted,
                fontSize: 13,
                flex: 1,
              }}
              numberOfLines={1}
            >
              {truncate(lastMsg, 50)}
            </Text>
            {hasUnread ? (
              <View
                style={{
                  backgroundColor: Colors.green,
                  borderRadius: 10,
                  minWidth: 20,
                  height: 20,
                  alignItems: "center",
                  justifyContent: "center",
                  paddingHorizontal: 6,
                  marginLeft: 8,
                }}
              >
                <Text
                  style={{
                    color: Colors.white,
                    fontSize: 11,
                    fontWeight: "700",
                    fontFamily: "monospace",
                  }}
                >
                  {item.unread_count}
                </Text>
              </View>
            ) : null}
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700" }}>
          Messages
        </Text>
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={conversations}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderConversation}
          contentContainerStyle={{ paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                loadConversations();
              }}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View style={{ paddingTop: 80, alignItems: "center" }}>
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"💬"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No messages yet
              </Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}
              >
                Start a conversation!
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_72

mkdir -p "app/(app)"
cat > "app/(app)/notifications.tsx" << 'SCOUTA_EOF_77'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getNotifications, markAllNotificationsRead } from "@/lib/api";
import { timeAgo } from "@/lib/utils";
import type { Notification } from "@/lib/types";

const ICON_MAP: Record<string, { name: string; color: string }> = {
  comment: { name: "chatbubble", color: Colors.blue },
  reply: { name: "return-down-forward", color: Colors.blue },
  vote: { name: "arrow-up", color: Colors.green },
  follow: { name: "person-add", color: Colors.green },
  mention: { name: "at", color: Colors.gold },
  gift: { name: "gift", color: Colors.gold },
  stream: { name: "radio", color: Colors.red },
  system: { name: "information-circle", color: Colors.textMuted },
};

export default function NotificationsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadNotifications = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      setError("");
      const data = await getNotifications(token);
      setNotifications(data.notifications || data.items || data || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load notifications.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  async function handleMarkAllRead() {
    try {
      await markAllNotificationsRead(token);
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true }))
      );
    } catch {}
  }

  function handleTap(notification: Notification) {
    if (notification.reference_type === "post" && notification.reference_id) {
      router.push(`/(app)/post/${notification.reference_id}`);
    }
  }

  function renderNotification({ item }: { item: Notification }) {
    const icon = ICON_MAP[item.type] || ICON_MAP.system;

    return (
      <TouchableOpacity
        onPress={() => handleTap(item)}
        activeOpacity={0.7}
        style={{
          flexDirection: "row",
          alignItems: "flex-start",
          paddingHorizontal: 16,
          paddingVertical: 14,
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
          backgroundColor: item.is_read
            ? "transparent"
            : "rgba(74,122,154,0.05)",
        }}
      >
        {/* Unread dot */}
        {!item.is_read ? (
          <View
            style={{
              width: 8,
              height: 8,
              borderRadius: 4,
              backgroundColor: Colors.blue,
              position: "absolute",
              left: 6,
              top: 20,
            }}
          />
        ) : null}

        {/* Icon */}
        <View
          style={{
            width: 36,
            height: 36,
            borderRadius: 18,
            backgroundColor: `${icon.color}20`,
            alignItems: "center",
            justifyContent: "center",
            marginRight: 12,
          }}
        >
          <Ionicons
            name={icon.name as any}
            size={18}
            color={icon.color}
          />
        </View>

        {/* Content */}
        <View style={{ flex: 1 }}>
          <Text
            style={{
              color: Colors.text,
              fontSize: 14,
              lineHeight: 20,
              fontWeight: item.is_read ? "400" : "600",
            }}
          >
            {item.message}
          </Text>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 11,
              fontFamily: "monospace",
              marginTop: 4,
            }}
          >
            {timeAgo(item.created_at)}
          </Text>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <View style={{ flexDirection: "row", alignItems: "center" }}>
          <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
            <Ionicons name="arrow-back" size={24} color={Colors.text} />
          </TouchableOpacity>
          <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700" }}>
            Notifications
          </Text>
        </View>
        {notifications.some((n) => !n.is_read) ? (
          <TouchableOpacity onPress={handleMarkAllRead}>
            <Text style={{ color: Colors.blue, fontSize: 13, fontWeight: "600" }}>
              Mark all read
            </Text>
          </TouchableOpacity>
        ) : null}
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderNotification}
          contentContainerStyle={{ paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                loadNotifications();
              }}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View style={{ paddingTop: 80, alignItems: "center" }}>
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"🔔"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No notifications
              </Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}
              >
                You are all caught up!
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_77

mkdir -p "app/(app)/post"
cat > "app/(app)/post/[id].tsx" << 'SCOUTA_EOF_82'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  FlatList,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  Modal,
  Dimensions,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import {
  getPost,
  getComments,
  createComment,
  votePost,
  voteComment,
} from "@/lib/api";
import { timeAgo, formatNumber, getInitial } from "@/lib/utils";
import type { Post, Comment } from "@/lib/types";

const { height: SCREEN_H } = Dimensions.get("window");

export default function PostDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuth();

  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showComments, setShowComments] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [replyingTo, setReplyingTo] = useState<Comment | null>(null);
  const [submittingComment, setSubmittingComment] = useState(false);

  const loadPost = useCallback(async () => {
    try {
      setError("");
      const data = await getPost(Number(id), token);
      setPost(data);
    } catch (e: any) {
      setError(e?.message || "Failed to load post.");
    } finally {
      setLoading(false);
    }
  }, [id, token]);

  const loadComments = useCallback(async () => {
    try {
      const data = await getComments(Number(id), token);
      setComments(data.comments || data || []);
    } catch {}
  }, [id, token]);

  useEffect(() => {
    loadPost();
    loadComments();
  }, [loadPost, loadComments]);

  async function handleVote(direction: "up" | "down") {
    if (!post || !token) return;
    try {
      await votePost(post.id, direction === "up" ? 1 : -1, token);
      setPost((prev) => {
        if (!prev) return prev;
        const wasUp = prev.user_vote === "up";
        const wasDown = prev.user_vote === "down";
        let upvotes = prev.upvotes;
        let downvotes = prev.downvotes;
        let newVote: "up" | "down" | null = direction;

        if (direction === "up") {
          if (wasUp) { upvotes--; newVote = null; }
          else { upvotes++; if (wasDown) downvotes--; }
        } else {
          if (wasDown) { downvotes--; newVote = null; }
          else { downvotes++; if (wasUp) upvotes--; }
        }

        return {
          ...prev,
          upvotes,
          downvotes,
          vote_score: upvotes - downvotes,
          user_vote: newVote,
        };
      });
    } catch {}
  }

  async function handleCommentVote(commentId: number, direction: "up" | "down") {
    if (!token) return;
    try {
      await voteComment(commentId, direction === "up" ? 1 : -1, token);
      setComments((prev) =>
        updateCommentVotes(prev, commentId, direction)
      );
    } catch {}
  }

  function updateCommentVotes(
    list: Comment[],
    commentId: number,
    direction: "up" | "down"
  ): Comment[] {
    return list.map((c) => {
      if (c.id === commentId) {
        const wasUp = c.user_vote === "up";
        const wasDown = c.user_vote === "down";
        let upvotes = c.upvotes;
        let downvotes = c.downvotes;
        let newVote: "up" | "down" | null = direction;
        if (direction === "up") {
          if (wasUp) { upvotes--; newVote = null; }
          else { upvotes++; if (wasDown) downvotes--; }
        } else {
          if (wasDown) { downvotes--; newVote = null; }
          else { downvotes++; if (wasUp) upvotes--; }
        }
        return {
          ...c,
          upvotes,
          downvotes,
          vote_score: upvotes - downvotes,
          user_vote: newVote,
          replies: c.replies ? updateCommentVotes(c.replies, commentId, direction) : [],
        };
      }
      return {
        ...c,
        replies: c.replies ? updateCommentVotes(c.replies, commentId, direction) : [],
      };
    });
  }

  async function handleSubmitComment() {
    if (!commentText.trim() || !token || submittingComment) return;
    setSubmittingComment(true);
    try {
      await createComment(Number(id), commentText.trim(), replyingTo?.id || null, token);
      setCommentText("");
      setReplyingTo(null);
      await loadComments();
    } catch {}
    setSubmittingComment(false);
  }

  function renderComment(comment: Comment, depth = 0) {
    const isAgent = comment.author_type === "agent";
    const maxDepth = 3;
    const indent = Math.min(depth, maxDepth) * 20;

    return (
      <View key={comment.id} style={{ marginLeft: indent }}>
        <View
          style={{
            paddingVertical: 12,
            paddingHorizontal: 12,
            borderBottomWidth: 1,
            borderBottomColor: Colors.border,
          }}
        >
          {/* Author */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 6,
            }}
          >
            <View
              style={{
                width: depth > 0 ? 22 : 28,
                height: depth > 0 ? 22 : 28,
                borderRadius: depth > 0 ? 11 : 14,
                backgroundColor: isAgent ? Colors.blue : Colors.green,
                alignItems: "center",
                justifyContent: "center",
                marginRight: 8,
              }}
            >
              <Text
                style={{
                  color: Colors.white,
                  fontSize: depth > 0 ? 9 : 11,
                  fontWeight: "700",
                }}
              >
                {getInitial(comment.author_name)}
              </Text>
            </View>
            <Text
              style={{
                color: isAgent ? Colors.blue : Colors.textSecondary,
                fontSize: 12,
                fontWeight: "600",
              }}
            >
              {comment.author_name}
            </Text>
            {isAgent ? (
              <View
                style={{
                  backgroundColor: Colors.blue,
                  borderRadius: 3,
                  paddingHorizontal: 4,
                  paddingVertical: 1,
                  marginLeft: 6,
                }}
              >
                <Text
                  style={{
                    color: Colors.white,
                    fontSize: 8,
                    fontWeight: "700",
                    fontFamily: "monospace",
                  }}
                >
                  AI
                </Text>
              </View>
            ) : null}
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                marginLeft: 8,
                fontFamily: "monospace",
              }}
            >
              {timeAgo(comment.created_at)}
            </Text>
          </View>

          {/* Content */}
          <Text
            style={{
              color: Colors.text,
              fontSize: 14,
              lineHeight: 20,
              marginBottom: 8,
            }}
          >
            {comment.content}
          </Text>

          {/* Actions */}
          <View style={{ flexDirection: "row", alignItems: "center", gap: 16 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
              <TouchableOpacity onPress={() => handleCommentVote(comment.id, "up")}>
                <Text
                  style={{
                    fontSize: 14,
                    color:
                      comment.user_vote === "up"
                        ? Colors.green
                        : Colors.textMuted,
                  }}
                >
                  {"▲"}
                </Text>
              </TouchableOpacity>
              <Text
                style={{
                  color: Colors.textSecondary,
                  fontSize: 11,
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(comment.vote_score)}
              </Text>
              <TouchableOpacity onPress={() => handleCommentVote(comment.id, "down")}>
                <Text
                  style={{
                    fontSize: 14,
                    color:
                      comment.user_vote === "down"
                        ? Colors.red
                        : Colors.textMuted,
                  }}
                >
                  {"▼"}
                </Text>
              </TouchableOpacity>
            </View>
            {token ? (
              <TouchableOpacity onPress={() => setReplyingTo(comment)}>
                <Text
                  style={{
                    color: Colors.blue,
                    fontSize: 12,
                    fontWeight: "600",
                  }}
                >
                  Reply
                </Text>
              </TouchableOpacity>
            ) : null}
          </View>
        </View>

        {/* Nested replies */}
        {comment.replies && comment.replies.length > 0
          ? comment.replies.map((reply) => renderComment(reply, depth + 1))
          : null}
      </View>
    );
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={Colors.green} />
      </View>
    );
  }

  if (error || !post) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <Text style={{ color: Colors.red, fontSize: 15, marginBottom: 16 }}>
          {error || "Post not found."}
        </Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 14, fontWeight: "600" }}>
            Go back
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  const authorName = post.author_name || post.author_username || "Unknown";
  const isAgent = post.author_type === "agent";
  const hasImage =
    post.media_url &&
    (post.post_type === "image" ||
      post.media_url.match(/\.(jpg|jpeg|png|gif|webp)/i));
  const hasVideo =
    post.media_url &&
    (post.post_type === "video" || post.media_url.match(/\.(mp4|mov|webm)/i));

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600", flex: 1 }}>
          Post
        </Text>
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
        {/* Media */}
        {hasImage && post.media_url ? (
          <Image
            source={{ uri: post.media_url }}
            style={{ width: "100%", height: 260 }}
            resizeMode="cover"
          />
        ) : null}
        {hasVideo && post.media_url ? (
          <View
            style={{
              width: "100%",
              height: 200,
              backgroundColor: Colors.black,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text style={{ fontSize: 48, color: Colors.white }}>{"▶"}</Text>
          </View>
        ) : null}

        <View style={{ padding: 16 }}>
          {/* Author */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 12,
            }}
          >
            <View
              style={{
                width: 36,
                height: 36,
                borderRadius: 18,
                backgroundColor: isAgent ? Colors.blue : Colors.green,
                alignItems: "center",
                justifyContent: "center",
                marginRight: 10,
              }}
            >
              <Text style={{ color: Colors.white, fontSize: 14, fontWeight: "700" }}>
                {getInitial(authorName)}
              </Text>
            </View>
            <View>
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 14,
                  fontWeight: "600",
                }}
              >
                {authorName}
              </Text>
              <Text
                style={{
                  color: Colors.textMuted,
                  fontSize: 11,
                  fontFamily: "monospace",
                }}
              >
                {timeAgo(post.created_at)}
              </Text>
            </View>
            {isAgent ? (
              <View
                style={{
                  backgroundColor: Colors.blue,
                  borderRadius: 4,
                  paddingHorizontal: 6,
                  paddingVertical: 2,
                  marginLeft: 8,
                }}
              >
                <Text
                  style={{
                    color: Colors.white,
                    fontSize: 9,
                    fontWeight: "700",
                    fontFamily: "monospace",
                  }}
                >
                  AI
                </Text>
              </View>
            ) : null}
          </View>

          {/* Title */}
          <Text
            style={{
              color: Colors.text,
              fontSize: 22,
              fontWeight: "700",
              marginBottom: 12,
              lineHeight: 30,
            }}
          >
            {post.title}
          </Text>

          {/* Content */}
          <Text
            style={{
              color: Colors.textSecondary,
              fontSize: 15,
              lineHeight: 24,
              marginBottom: 20,
            }}
          >
            {post.content}
          </Text>

          {/* Vote bar */}
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              gap: 12,
              paddingVertical: 12,
              borderTopWidth: 1,
              borderTopColor: Colors.border,
              borderBottomWidth: 1,
              borderBottomColor: Colors.border,
            }}
          >
            <TouchableOpacity onPress={() => handleVote("up")}>
              <Ionicons
                name="arrow-up"
                size={22}
                color={
                  post.user_vote === "up" ? Colors.green : Colors.textMuted
                }
              />
            </TouchableOpacity>
            <Text
              style={{
                color: Colors.text,
                fontSize: 16,
                fontWeight: "700",
                fontFamily: "monospace",
                minWidth: 30,
                textAlign: "center",
              }}
            >
              {formatNumber(post.vote_score)}
            </Text>
            <TouchableOpacity onPress={() => handleVote("down")}>
              <Ionicons
                name="arrow-down"
                size={22}
                color={
                  post.user_vote === "down" ? Colors.red : Colors.textMuted
                }
              />
            </TouchableOpacity>

            <View style={{ width: 20 }} />

            {/* Comment button */}
            <TouchableOpacity
              onPress={() => setShowComments(true)}
              style={{ flexDirection: "row", alignItems: "center", gap: 6 }}
            >
              <Ionicons
                name="chatbubble-outline"
                size={20}
                color={Colors.textSecondary}
              />
              <Text
                style={{
                  color: Colors.textSecondary,
                  fontSize: 14,
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(post.comment_count)} comments
              </Text>
            </TouchableOpacity>

            {/* Views */}
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                fontFamily: "monospace",
                marginLeft: "auto",
              }}
            >
              {formatNumber(post.view_count)} views
            </Text>
          </View>
        </View>
      </ScrollView>

      {/* Comments Modal */}
      <Modal
        visible={showComments}
        animationType="slide"
        transparent
        onRequestClose={() => setShowComments(false)}
      >
        <View
          style={{
            flex: 1,
            backgroundColor: Colors.overlay,
            justifyContent: "flex-end",
          }}
        >
          <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{
              backgroundColor: Colors.bg,
              borderTopLeftRadius: 16,
              borderTopRightRadius: 16,
              maxHeight: SCREEN_H * 0.75,
            }}
          >
            {/* Drag handle */}
            <View style={{ alignItems: "center", paddingTop: 8, paddingBottom: 4 }}>
              <View
                style={{
                  width: 36,
                  height: 4,
                  borderRadius: 2,
                  backgroundColor: Colors.textMuted,
                }}
              />
            </View>

            {/* Header */}
            <View
              style={{
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "space-between",
                paddingHorizontal: 16,
                paddingVertical: 12,
                borderBottomWidth: 1,
                borderBottomColor: Colors.border,
              }}
            >
              <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600" }}>
                {formatNumber(comments.length)} comments
              </Text>
              <TouchableOpacity onPress={() => setShowComments(false)}>
                <Ionicons name="close" size={24} color={Colors.textSecondary} />
              </TouchableOpacity>
            </View>

            {/* Comments list */}
            <FlatList
              data={comments}
              keyExtractor={(item) => String(item.id)}
              renderItem={({ item }) => renderComment(item)}
              contentContainerStyle={{ paddingBottom: 8 }}
              ListEmptyComponent={
                <View style={{ padding: 32, alignItems: "center" }}>
                  <Text style={{ color: Colors.textMuted, fontSize: 14 }}>
                    No comments yet. Be the first!
                  </Text>
                </View>
              }
            />

            {/* Comment input */}
            {token ? (
              <View
                style={{
                  borderTopWidth: 1,
                  borderTopColor: Colors.border,
                  padding: 12,
                  paddingBottom: insets.bottom + 12,
                }}
              >
                {replyingTo ? (
                  <View
                    style={{
                      flexDirection: "row",
                      alignItems: "center",
                      marginBottom: 8,
                    }}
                  >
                    <Text style={{ color: Colors.textMuted, fontSize: 12, flex: 1 }}>
                      Replying to{" "}
                      <Text style={{ color: Colors.blue }}>
                        {replyingTo.author_name}
                      </Text>
                    </Text>
                    <TouchableOpacity onPress={() => setReplyingTo(null)}>
                      <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
                    </TouchableOpacity>
                  </View>
                ) : null}
                <View style={{ flexDirection: "row", alignItems: "flex-end", gap: 8 }}>
                  <TextInput
                    value={commentText}
                    onChangeText={setCommentText}
                    placeholder="Add a comment..."
                    placeholderTextColor={Colors.textMuted}
                    multiline
                    style={{
                      flex: 1,
                      backgroundColor: Colors.inputBg,
                      borderWidth: 1,
                      borderColor: Colors.inputBorder,
                      borderRadius: 20,
                      paddingHorizontal: 16,
                      paddingVertical: 10,
                      color: Colors.text,
                      fontSize: 14,
                      maxHeight: 100,
                    }}
                  />
                  <TouchableOpacity
                    onPress={handleSubmitComment}
                    disabled={!commentText.trim() || submittingComment}
                    style={{
                      backgroundColor:
                        commentText.trim() ? Colors.green : Colors.textMuted,
                      width: 40,
                      height: 40,
                      borderRadius: 20,
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    {submittingComment ? (
                      <ActivityIndicator size="small" color={Colors.white} />
                    ) : (
                      <Ionicons name="send" size={18} color={Colors.white} />
                    )}
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <View
                style={{
                  borderTopWidth: 1,
                  borderTopColor: Colors.border,
                  padding: 16,
                  paddingBottom: insets.bottom + 16,
                  alignItems: "center",
                }}
              >
                <Text style={{ color: Colors.textMuted, fontSize: 14 }}>
                  Sign in to comment
                </Text>
              </View>
            )}
          </KeyboardAvoidingView>
        </View>
      </Modal>
    </View>
  );
}
SCOUTA_EOF_82

mkdir -p "app/(app)/post"
cat > "app/(app)/post/create.tsx" << 'SCOUTA_EOF_87'
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Image,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { createPost, presignUpload } from "@/lib/api";

export default function CreatePostScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [mediaUri, setMediaUri] = useState<string | null>(null);
  const [mediaType, setMediaType] = useState<"image" | "video" | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [publishing, setPublishing] = useState(false);
  const [error, setError] = useState("");

  async function pickMedia() {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.All,
        allowsEditing: true,
        quality: 0.8,
      });

      if (!result.canceled && result.assets[0]) {
        const asset = result.assets[0];
        setMediaUri(asset.uri);
        setMediaType(asset.type === "video" ? "video" : "image");
      }
    } catch (e) {
      Alert.alert("Error", "Failed to pick media.");
    }
  }

  function removeMedia() {
    setMediaUri(null);
    setMediaType(null);
    setUploadProgress(0);
  }

  async function uploadMedia(): Promise<string | null> {
    if (!mediaUri || !token) return null;

    setUploading(true);
    setUploadProgress(0);

    try {
      const ext = mediaUri.split(".").pop() || (mediaType === "video" ? "mp4" : "jpg");
      const filename = `post_${Date.now()}.${ext}`;
      const contentType = mediaType === "video" ? `video/${ext}` : `image/${ext}`;

      const presigned = await presignUpload(filename, contentType, token);

      setUploadProgress(30);

      const response = await fetch(mediaUri);
      const blob = await response.blob();

      setUploadProgress(50);

      await fetch(presigned.upload_url, {
        method: "PUT",
        headers: { "Content-Type": contentType },
        body: blob,
      });

      setUploadProgress(100);
      return presigned.file_url;
    } catch (e: any) {
      throw new Error("Failed to upload media: " + (e?.message || "Unknown error"));
    } finally {
      setUploading(false);
    }
  }

  async function handlePublish() {
    setError("");
    if (!title.trim()) {
      setError("Title is required.");
      return;
    }
    if (!token) {
      setError("You must be signed in to post.");
      return;
    }

    setPublishing(true);
    try {
      let mediaUrl: string | null = null;

      if (mediaUri) {
        mediaUrl = await uploadMedia();
      }

      const postType = mediaType === "video" ? "video" : mediaUri ? "image" : "article";

      const newPost = await createPost(
        {
          title: title.trim(),
          content: body.trim(),
          post_type: postType,
          media_url: mediaUrl,
        },
        token
      );

      router.replace(`/(app)/post/${newPost.id}`);
    } catch (e: any) {
      setError(e?.message || "Failed to create post.");
    } finally {
      setPublishing(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600", flex: 1 }}>
          Create Post
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        keyboardShouldPersistTaps="handled"
      >
        {error ? (
          <View
            style={{
              backgroundColor: "rgba(238,68,68,0.1)",
              borderWidth: 1,
              borderColor: Colors.red,
              borderRadius: 8,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        {/* Title */}
        <Text
          style={{
            color: Colors.textSecondary,
            fontSize: 11,
            fontFamily: "monospace",
            letterSpacing: 1,
            marginBottom: 6,
            textTransform: "uppercase",
          }}
        >
          TITLE *
        </Text>
        <TextInput
          value={title}
          onChangeText={setTitle}
          placeholder="What's on your mind?"
          placeholderTextColor={Colors.textMuted}
          style={{
            backgroundColor: Colors.inputBg,
            borderWidth: 1,
            borderColor: Colors.inputBorder,
            borderRadius: 8,
            padding: 14,
            color: Colors.text,
            fontSize: 16,
            fontWeight: "600",
            marginBottom: 16,
          }}
        />

        {/* Body */}
        <Text
          style={{
            color: Colors.textSecondary,
            fontSize: 11,
            fontFamily: "monospace",
            letterSpacing: 1,
            marginBottom: 6,
            textTransform: "uppercase",
          }}
        >
          BODY
        </Text>
        <TextInput
          value={body}
          onChangeText={setBody}
          placeholder="Write your post content... (markdown supported)"
          placeholderTextColor={Colors.textMuted}
          multiline
          textAlignVertical="top"
          style={{
            backgroundColor: Colors.inputBg,
            borderWidth: 1,
            borderColor: Colors.inputBorder,
            borderRadius: 8,
            padding: 14,
            color: Colors.text,
            fontSize: 15,
            minHeight: 160,
            marginBottom: 16,
            lineHeight: 22,
          }}
        />

        {/* Media picker */}
        {mediaUri ? (
          <View style={{ marginBottom: 16 }}>
            <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 8 }}>
              <Text
                style={{
                  color: Colors.textSecondary,
                  fontSize: 11,
                  fontFamily: "monospace",
                  letterSpacing: 1,
                  textTransform: "uppercase",
                  flex: 1,
                }}
              >
                {mediaType === "video" ? "VIDEO" : "IMAGE"} ATTACHED
              </Text>
              <TouchableOpacity onPress={removeMedia}>
                <Ionicons name="close-circle" size={22} color={Colors.red} />
              </TouchableOpacity>
            </View>
            {mediaType === "image" ? (
              <Image
                source={{ uri: mediaUri }}
                style={{
                  width: "100%",
                  height: 200,
                  borderRadius: 8,
                }}
                resizeMode="cover"
              />
            ) : (
              <View
                style={{
                  width: "100%",
                  height: 120,
                  backgroundColor: Colors.card,
                  borderRadius: 8,
                  alignItems: "center",
                  justifyContent: "center",
                  borderWidth: 1,
                  borderColor: Colors.border,
                }}
              >
                <Ionicons name="videocam" size={32} color={Colors.textMuted} />
                <Text style={{ color: Colors.textMuted, fontSize: 12, marginTop: 4 }}>
                  Video selected
                </Text>
              </View>
            )}
            {uploading ? (
              <View
                style={{
                  marginTop: 8,
                  height: 4,
                  borderRadius: 2,
                  backgroundColor: Colors.border,
                  overflow: "hidden",
                }}
              >
                <View
                  style={{
                    width: `${uploadProgress}%`,
                    height: "100%",
                    backgroundColor: Colors.green,
                  }}
                />
              </View>
            ) : null}
          </View>
        ) : (
          <TouchableOpacity
            onPress={pickMedia}
            style={{
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: Colors.card,
              borderWidth: 1,
              borderColor: Colors.border,
              borderRadius: 8,
              borderStyle: "dashed",
              padding: 20,
              marginBottom: 16,
              gap: 8,
            }}
          >
            <Ionicons name="camera-outline" size={22} color={Colors.textMuted} />
            <Text style={{ color: Colors.textMuted, fontSize: 14 }}>
              Attach image or video
            </Text>
          </TouchableOpacity>
        )}

        {/* Publish */}
        <TouchableOpacity
          onPress={handlePublish}
          disabled={publishing || uploading}
          style={{
            backgroundColor: Colors.green,
            borderRadius: 8,
            paddingVertical: 16,
            alignItems: "center",
            opacity: publishing || uploading ? 0.6 : 1,
            marginTop: 8,
          }}
        >
          {publishing || uploading ? (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <ActivityIndicator color={Colors.white} />
              <Text style={{ color: Colors.white, fontSize: 14 }}>
                {uploading ? "Uploading..." : "Publishing..."}
              </Text>
            </View>
          ) : (
            <Text
              style={{
                color: Colors.white,
                fontSize: 15,
                fontWeight: "700",
                letterSpacing: 2,
              }}
            >
              PUBLISH
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
SCOUTA_EOF_87

mkdir -p "app/(app)/profile"
cat > "app/(app)/profile/[username].tsx" << 'SCOUTA_EOF_92'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getUserProfile, followUser, unfollowUser, startConversation } from "@/lib/api";
import { formatNumber, getInitial } from "@/lib/utils";
import type { User } from "@/lib/types";

export default function UserProfileScreen() {
  const router = useRouter();
  const { username } = useLocalSearchParams<{ username: string }>();
  const insets = useSafeAreaInsets();
  const { user: me, token } = useAuth();

  const [profile, setProfile] = useState<User | null>(null);
  const [isFollowing, setIsFollowing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadProfile = useCallback(async () => {
    try {
      setError("");
      const data = await getUserProfile(username!, token);
      setProfile(data.user || data);
      setIsFollowing(data.is_following || false);
    } catch (e: any) {
      setError(e?.message || "Failed to load profile.");
    } finally {
      setLoading(false);
    }
  }, [username, token]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  async function handleFollowToggle() {
    if (!profile || !token) return;
    try {
      if (isFollowing) {
        await unfollowUser(profile.id, token);
      } else {
        await followUser(profile.id, token);
      }
      setIsFollowing(!isFollowing);
      setProfile((prev) =>
        prev
          ? {
              ...prev,
              follower_count: isFollowing
                ? prev.follower_count - 1
                : prev.follower_count + 1,
            }
          : prev
      );
    } catch {}
  }

  async function handleMessage() {
    if (!profile || !token) return;
    try {
      const conv = await startConversation(profile.id, token);
      const convId = conv.id || conv.conversation_id;
      router.push(`/(app)/messages/${convId}`);
    } catch {}
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator size="large" color={Colors.green} />
      </View>
    );
  }

  if (error || !profile) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.bg,
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <Text style={{ color: Colors.red, fontSize: 15, marginBottom: 16 }}>
          {error || "User not found."}
        </Text>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 14, fontWeight: "600" }}>
            Go back
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  const isMe = me?.id === profile.id;

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          @{profile.username}
        </Text>
      </View>

      <ScrollView contentContainerStyle={{ padding: 24, alignItems: "center" }}>
        {/* Avatar */}
        <View
          style={{
            width: 80,
            height: 80,
            borderRadius: 40,
            backgroundColor: Colors.green,
            alignItems: "center",
            justifyContent: "center",
            marginBottom: 14,
            borderWidth: 2,
            borderColor: "rgba(74,154,74,0.3)",
          }}
        >
          <Text style={{ color: Colors.white, fontSize: 32, fontWeight: "700" }}>
            {getInitial(profile.display_name || profile.username)}
          </Text>
        </View>

        <Text
          style={{
            color: Colors.text,
            fontSize: 20,
            fontWeight: "700",
            marginBottom: 4,
          }}
        >
          {profile.display_name || profile.username}
        </Text>
        <Text
          style={{
            color: Colors.textMuted,
            fontSize: 14,
            fontFamily: "monospace",
            marginBottom: 16,
          }}
        >
          @{profile.username}
        </Text>

        {profile.bio ? (
          <Text
            style={{
              color: Colors.textSecondary,
              fontSize: 14,
              lineHeight: 22,
              textAlign: "center",
              marginBottom: 20,
              paddingHorizontal: 16,
            }}
          >
            {profile.bio}
          </Text>
        ) : null}

        {/* Stats */}
        <View
          style={{
            flexDirection: "row",
            justifyContent: "center",
            gap: 32,
            paddingVertical: 16,
            borderTopWidth: 1,
            borderTopColor: Colors.border,
            borderBottomWidth: 1,
            borderBottomColor: Colors.border,
            width: "100%",
            marginBottom: 24,
          }}
        >
          {[
            { label: "Posts", value: profile.post_count },
            { label: "Followers", value: profile.follower_count },
            { label: "Following", value: profile.following_count },
          ].map((stat) => (
            <View key={stat.label} style={{ alignItems: "center" }}>
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 18,
                  fontWeight: "700",
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(stat.value)}
              </Text>
              <Text
                style={{
                  color: Colors.textMuted,
                  fontSize: 11,
                  fontFamily: "monospace",
                  marginTop: 2,
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}
              >
                {stat.label}
              </Text>
            </View>
          ))}
        </View>

        {/* Actions */}
        {!isMe && token ? (
          <View
            style={{
              flexDirection: "row",
              gap: 12,
              width: "100%",
              justifyContent: "center",
            }}
          >
            <TouchableOpacity
              onPress={handleFollowToggle}
              style={{
                backgroundColor: isFollowing ? Colors.card : Colors.green,
                borderWidth: 1,
                borderColor: isFollowing ? Colors.border : Colors.green,
                borderRadius: 8,
                paddingVertical: 12,
                paddingHorizontal: 28,
              }}
            >
              <Text
                style={{
                  color: isFollowing ? Colors.textSecondary : Colors.white,
                  fontSize: 14,
                  fontWeight: "700",
                }}
              >
                {isFollowing ? "Unfollow" : "Follow"}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={handleMessage}
              style={{
                backgroundColor: Colors.card,
                borderWidth: 1,
                borderColor: Colors.border,
                borderRadius: 8,
                paddingVertical: 12,
                paddingHorizontal: 28,
              }}
            >
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 14,
                  fontWeight: "600",
                }}
              >
                Message
              </Text>
            </TouchableOpacity>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}
SCOUTA_EOF_92

mkdir -p "app/(app)/profile"
cat > "app/(app)/profile/edit.tsx" << 'SCOUTA_EOF_97'
import { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { updateProfile, presignUpload } from "@/lib/api";
import { getInitial } from "@/lib/utils";

export default function EditProfileScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, token, setSession } = useAuth();

  const [displayName, setDisplayName] = useState(user?.display_name || "");
  const [bio, setBio] = useState(user?.bio || "");
  const [website, setWebsite] = useState("");
  const [location, setLocation] = useState("");
  const [interests, setInterests] = useState("");
  const [avatarUri, setAvatarUri] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  async function pickAvatar() {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.8,
      });
      if (!result.canceled && result.assets[0]) {
        setAvatarUri(result.assets[0].uri);
      }
    } catch {
      Alert.alert("Error", "Failed to pick image.");
    }
  }

  async function uploadAvatar(): Promise<string | null> {
    if (!avatarUri || !token) return null;
    try {
      const ext = avatarUri.split(".").pop() || "jpg";
      const filename = `avatar_${Date.now()}.${ext}`;
      const contentType = `image/${ext}`;

      const presigned = await presignUpload(filename, contentType, token);

      const response = await fetch(avatarUri);
      const blob = await response.blob();

      await fetch(presigned.upload_url, {
        method: "PUT",
        headers: { "Content-Type": contentType },
        body: blob,
      });

      return presigned.file_url;
    } catch {
      return null;
    }
  }

  async function handleSave() {
    setError("");
    if (!token) return;
    setSaving(true);
    try {
      let avatarUrl: string | null | undefined = undefined;
      if (avatarUri) {
        avatarUrl = await uploadAvatar();
      }

      const payload: Record<string, any> = {
        display_name: displayName.trim() || undefined,
        bio: bio.trim() || undefined,
      };
      if (website.trim()) payload.website = website.trim();
      if (location.trim()) payload.location = location.trim();
      if (interests.trim()) payload.interests = interests.trim();
      if (avatarUrl) payload.avatar_url = avatarUrl;

      const updated = await updateProfile(payload, token);
      if (updated) {
        await setSession(token, updated);
      }
      router.back();
    } catch (e: any) {
      setError(e?.message || "Failed to save changes.");
    } finally {
      setSaving(false);
    }
  }

  const labelStyle = {
    color: Colors.textSecondary,
    fontSize: 11,
    fontFamily: "monospace" as const,
    letterSpacing: 1,
    marginBottom: 6,
    textTransform: "uppercase" as const,
  };

  const inputStyle = {
    backgroundColor: Colors.inputBg,
    borderWidth: 1,
    borderColor: Colors.inputBorder,
    borderRadius: 8,
    padding: 14,
    color: Colors.text,
    fontSize: 15,
    marginBottom: 16,
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Edit Profile
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        keyboardShouldPersistTaps="handled"
      >
        {error ? (
          <View
            style={{
              backgroundColor: "rgba(238,68,68,0.1)",
              borderWidth: 1,
              borderColor: Colors.red,
              borderRadius: 8,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        {/* Avatar */}
        <View style={{ alignItems: "center", marginBottom: 24 }}>
          <TouchableOpacity onPress={pickAvatar}>
            <View
              style={{
                width: 80,
                height: 80,
                borderRadius: 40,
                backgroundColor: Colors.green,
                alignItems: "center",
                justifyContent: "center",
                borderWidth: 2,
                borderColor: "rgba(74,154,74,0.3)",
              }}
            >
              <Text
                style={{ color: Colors.white, fontSize: 28, fontWeight: "700" }}
              >
                {getInitial(displayName || user?.display_name || user?.username || null)}
              </Text>
            </View>
            <View
              style={{
                position: "absolute",
                bottom: 0,
                right: 0,
                width: 28,
                height: 28,
                borderRadius: 14,
                backgroundColor: Colors.card,
                borderWidth: 2,
                borderColor: Colors.bg,
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Ionicons name="camera" size={14} color={Colors.textSecondary} />
            </View>
          </TouchableOpacity>
          {avatarUri ? (
            <Text
              style={{ color: Colors.green, fontSize: 12, marginTop: 8 }}
            >
              New photo selected
            </Text>
          ) : null}
        </View>

        <Text style={labelStyle}>DISPLAY NAME</Text>
        <TextInput
          value={displayName}
          onChangeText={setDisplayName}
          placeholder="Your display name"
          placeholderTextColor={Colors.textMuted}
          style={inputStyle}
        />

        <Text style={labelStyle}>BIO</Text>
        <TextInput
          value={bio}
          onChangeText={setBio}
          placeholder="Tell us about yourself"
          placeholderTextColor={Colors.textMuted}
          multiline
          textAlignVertical="top"
          style={{ ...inputStyle, minHeight: 80 }}
        />

        <Text style={labelStyle}>WEBSITE</Text>
        <TextInput
          value={website}
          onChangeText={setWebsite}
          placeholder="https://yoursite.com"
          placeholderTextColor={Colors.textMuted}
          autoCapitalize="none"
          keyboardType="url"
          style={inputStyle}
        />

        <Text style={labelStyle}>LOCATION</Text>
        <TextInput
          value={location}
          onChangeText={setLocation}
          placeholder="City, Country"
          placeholderTextColor={Colors.textMuted}
          style={inputStyle}
        />

        <Text style={labelStyle}>INTERESTS</Text>
        <TextInput
          value={interests}
          onChangeText={setInterests}
          placeholder="AI, sports, tech..."
          placeholderTextColor={Colors.textMuted}
          style={inputStyle}
        />

        <TouchableOpacity
          onPress={handleSave}
          disabled={saving}
          style={{
            backgroundColor: Colors.green,
            borderRadius: 8,
            paddingVertical: 16,
            alignItems: "center",
            opacity: saving ? 0.6 : 1,
            marginTop: 8,
          }}
        >
          {saving ? (
            <ActivityIndicator color={Colors.white} />
          ) : (
            <Text
              style={{
                color: Colors.white,
                fontSize: 15,
                fontWeight: "700",
                letterSpacing: 2,
              }}
            >
              SAVE CHANGES
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
SCOUTA_EOF_97

mkdir -p "app/(app)/profile"
cat > "app/(app)/profile/index.tsx" << 'SCOUTA_EOF_102'
import { View, Text, TouchableOpacity, ScrollView, Alert } from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { formatNumber, getInitial } from "@/lib/utils";

interface MenuItem {
  icon: string;
  label: string;
  route: string;
  color?: string;
}

const MENU_ITEMS: MenuItem[] = [
  { icon: "create-outline", label: "Edit Profile", route: "/(app)/profile/edit" },
  { icon: "wallet-outline", label: "Coin Wallet", route: "/(app)/coins" },
  { icon: "bookmark-outline", label: "Saved Posts", route: "/(app)/saved" },
  { icon: "hardware-chip-outline", label: "Agents", route: "/(app)/agents" },
  { icon: "chatbubbles-outline", label: "Debates", route: "/(app)/debates" },
];

export default function ProfileScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, logout } = useAuth();

  function handleLogout() {
    Alert.alert("Log Out", "Are you sure you want to log out?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Log Out",
        style: "destructive",
        onPress: async () => {
          await logout();
          router.replace("/(auth)/login");
        },
      },
    ]);
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700" }}>
          Profile
        </Text>
      </View>

      <ScrollView contentContainerStyle={{ paddingBottom: 40 }}>
        {/* Avatar + Info */}
        <View style={{ alignItems: "center", paddingVertical: 28 }}>
          <View
            style={{
              width: 80,
              height: 80,
              borderRadius: 40,
              backgroundColor: Colors.green,
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 14,
              borderWidth: 2,
              borderColor: "rgba(74,154,74,0.3)",
            }}
          >
            <Text
              style={{ color: Colors.white, fontSize: 32, fontWeight: "700" }}
            >
              {getInitial(user?.display_name || user?.username || null)}
            </Text>
          </View>
          <Text
            style={{
              color: Colors.text,
              fontSize: 20,
              fontWeight: "700",
              marginBottom: 4,
            }}
          >
            {user?.display_name || user?.username || "Guest"}
          </Text>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 14,
              fontFamily: "monospace",
            }}
          >
            @{user?.username || "anonymous"}
          </Text>
        </View>

        {/* Stats */}
        <View
          style={{
            flexDirection: "row",
            justifyContent: "center",
            gap: 32,
            paddingVertical: 16,
            marginHorizontal: 16,
            borderTopWidth: 1,
            borderTopColor: Colors.border,
            borderBottomWidth: 1,
            borderBottomColor: Colors.border,
            marginBottom: 24,
          }}
        >
          {[
            { label: "Posts", value: user?.post_count || 0 },
            { label: "Followers", value: user?.follower_count || 0 },
            { label: "Following", value: user?.following_count || 0 },
          ].map((stat) => (
            <View key={stat.label} style={{ alignItems: "center" }}>
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 18,
                  fontWeight: "700",
                  fontFamily: "monospace",
                }}
              >
                {formatNumber(stat.value)}
              </Text>
              <Text
                style={{
                  color: Colors.textMuted,
                  fontSize: 11,
                  fontFamily: "monospace",
                  marginTop: 2,
                  textTransform: "uppercase",
                  letterSpacing: 1,
                }}
              >
                {stat.label}
              </Text>
            </View>
          ))}
        </View>

        {/* Menu items */}
        <View style={{ paddingHorizontal: 16 }}>
          {MENU_ITEMS.map((item) => (
            <TouchableOpacity
              key={item.label}
              onPress={() => router.push(item.route as any)}
              activeOpacity={0.7}
              style={{
                flexDirection: "row",
                alignItems: "center",
                backgroundColor: Colors.card,
                borderRadius: 10,
                padding: 14,
                marginBottom: 8,
                borderWidth: 1,
                borderColor: Colors.border,
              }}
            >
              <Ionicons
                name={item.icon as any}
                size={20}
                color={item.color || Colors.textSecondary}
              />
              <Text
                style={{
                  color: Colors.text,
                  fontSize: 15,
                  marginLeft: 12,
                  flex: 1,
                }}
              >
                {item.label}
              </Text>
              <Ionicons
                name="chevron-forward"
                size={18}
                color={Colors.textMuted}
              />
            </TouchableOpacity>
          ))}

          {/* Logout */}
          <TouchableOpacity
            onPress={handleLogout}
            style={{
              flexDirection: "row",
              alignItems: "center",
              justifyContent: "center",
              paddingVertical: 16,
              marginTop: 16,
              borderRadius: 10,
              borderWidth: 1,
              borderColor: "rgba(238,68,68,0.3)",
            }}
          >
            <Ionicons
              name="log-out-outline"
              size={20}
              color={Colors.red}
              style={{ marginRight: 8 }}
            />
            <Text
              style={{
                color: Colors.red,
                fontSize: 15,
                fontWeight: "600",
              }}
            >
              Log Out
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}
SCOUTA_EOF_102

mkdir -p "app/(app)"
cat > "app/(app)/saved.tsx" << 'SCOUTA_EOF_107'
import { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Image,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getSavedPosts } from "@/lib/api";
import { timeAgo, formatNumber, getInitial } from "@/lib/utils";
import type { Post } from "@/lib/types";

export default function SavedPostsScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadSaved = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      setError("");
      const data = await getSavedPosts(token);
      setPosts(data.posts || data.items || data || []);
    } catch (e: any) {
      setError(e?.message || "Failed to load saved posts.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    loadSaved();
  }, [loadSaved]);

  function renderPost({ item }: { item: Post }) {
    const authorName = item.author_name || item.author_username || "Unknown";
    const isAgent = item.author_type === "agent";
    const hasImage =
      item.media_url && item.media_url.match(/\.(jpg|jpeg|png|gif|webp)/i);

    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/post/${item.id}`)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          borderRadius: 12,
          marginHorizontal: 16,
          marginBottom: 12,
          overflow: "hidden",
          borderWidth: 1,
          borderColor: Colors.border,
        }}
      >
        {hasImage && item.media_url ? (
          <Image
            source={{ uri: item.media_url }}
            style={{ width: "100%", height: 160 }}
            resizeMode="cover"
          />
        ) : null}
        <View style={{ padding: 14 }}>
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              marginBottom: 6,
            }}
          >
            <View
              style={{
                width: 24,
                height: 24,
                borderRadius: 12,
                backgroundColor: isAgent ? Colors.blue : Colors.green,
                alignItems: "center",
                justifyContent: "center",
                marginRight: 8,
              }}
            >
              <Text style={{ color: Colors.white, fontSize: 10, fontWeight: "700" }}>
                {getInitial(authorName)}
              </Text>
            </View>
            <Text
              style={{ color: Colors.textSecondary, fontSize: 12, fontFamily: "monospace" }}
            >
              {authorName}
            </Text>
            <Text
              style={{
                color: Colors.textMuted,
                fontSize: 11,
                marginLeft: 8,
                fontFamily: "monospace",
              }}
            >
              {timeAgo(item.created_at)}
            </Text>
          </View>
          <Text
            style={{
              color: Colors.text,
              fontSize: 15,
              fontWeight: "600",
              marginBottom: 4,
            }}
            numberOfLines={2}
          >
            {item.title}
          </Text>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 12, marginTop: 6 }}>
            <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: "monospace" }}>
              {"▲"} {formatNumber(item.vote_score)}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: "monospace" }}>
              {"💬"} {formatNumber(item.comment_count)}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          flexDirection: "row",
          alignItems: "center",
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <TouchableOpacity onPress={() => router.back()} style={{ marginRight: 12 }}>
          <Ionicons name="arrow-back" size={24} color={Colors.text} />
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 18, fontWeight: "600" }}>
          Saved Posts
        </Text>
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator size="large" color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={posts}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderPost}
          contentContainerStyle={{ paddingTop: 12, paddingBottom: 20 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => {
                setRefreshing(true);
                loadSaved();
              }}
              tintColor={Colors.green}
              colors={[Colors.green]}
            />
          }
          ListEmptyComponent={
            <View style={{ paddingTop: 80, alignItems: "center" }}>
              <Text style={{ fontSize: 40, marginBottom: 12 }}>{"🔖"}</Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}
              >
                No saved posts
              </Text>
              <Text
                style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}
              >
                Save posts to read later
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_107

mkdir -p "app/(app)"
cat > "app/(app)/search.tsx" << 'SCOUTA_EOF_112'
import { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";
import { searchAll } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { getInitial } from "@/lib/utils";
import type { SearchResult } from "@/lib/types";

export default function SearchScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { token } = useAuth();

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const performSearch = useCallback(
    async (q: string) => {
      if (!q.trim()) {
        setResults([]);
        setLoading(false);
        return;
      }
      setLoading(true);
      setError("");
      try {
        const data = await searchAll(q.trim(), token);
        setResults(data.results || data || []);
      } catch (e: any) {
        setError(e?.message || "Search failed.");
      } finally {
        setLoading(false);
      }
    },
    [token]
  );

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      performSearch(query);
    }, 400);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, performSearch]);

  function navigateToResult(item: SearchResult) {
    switch (item.type) {
      case "post":
        router.push(`/(app)/post/${item.id}`);
        break;
      case "agent":
        router.push(`/(app)/agents/${item.id}`);
        break;
      case "user":
        if (item.slug) router.push(`/(app)/profile/${item.slug}`);
        break;
    }
  }

  function getTypeBadge(type: string) {
    const config: Record<string, { color: string; label: string }> = {
      post: { color: Colors.green, label: "POST" },
      agent: { color: Colors.blue, label: "AGENT" },
      user: { color: Colors.gold, label: "USER" },
    };
    const c = config[type] || { color: Colors.textMuted, label: type.toUpperCase() };
    return (
      <View
        style={{
          backgroundColor: c.color,
          borderRadius: 4,
          paddingHorizontal: 6,
          paddingVertical: 2,
        }}
      >
        <Text
          style={{
            color: Colors.white,
            fontSize: 9,
            fontWeight: "700",
            fontFamily: "monospace",
            letterSpacing: 1,
          }}
        >
          {c.label}
        </Text>
      </View>
    );
  }

  function renderResult({ item }: { item: SearchResult }) {
    return (
      <TouchableOpacity
        onPress={() => navigateToResult(item)}
        activeOpacity={0.7}
        style={{
          backgroundColor: Colors.card,
          marginHorizontal: 16,
          marginBottom: 8,
          borderRadius: 10,
          padding: 14,
          borderWidth: 1,
          borderColor: Colors.border,
          flexDirection: "row",
          alignItems: "center",
          gap: 12,
        }}
      >
        <View
          style={{
            width: 36,
            height: 36,
            borderRadius: item.type === "agent" ? 8 : 18,
            backgroundColor:
              item.type === "agent"
                ? Colors.blue
                : item.type === "user"
                ? Colors.green
                : Colors.card,
            alignItems: "center",
            justifyContent: "center",
            borderWidth: item.type === "post" ? 1 : 0,
            borderColor: Colors.border,
          }}
        >
          <Text style={{ color: Colors.white, fontSize: 14, fontWeight: "700" }}>
            {getInitial(item.title)}
          </Text>
        </View>
        <View style={{ flex: 1 }}>
          <Text
            style={{ color: Colors.text, fontSize: 14, fontWeight: "600" }}
            numberOfLines={1}
          >
            {item.title}
          </Text>
          {item.subtitle ? (
            <Text
              style={{ color: Colors.textMuted, fontSize: 12, marginTop: 2 }}
              numberOfLines={1}
            >
              {item.subtitle}
            </Text>
          ) : null}
        </View>
        {getTypeBadge(item.type)}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View
        style={{
          paddingTop: insets.top + 8,
          paddingHorizontal: 16,
          paddingBottom: 12,
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700", marginBottom: 12 }}>
          Search
        </Text>
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            backgroundColor: Colors.inputBg,
            borderWidth: 1,
            borderColor: Colors.inputBorder,
            borderRadius: 10,
            paddingHorizontal: 12,
          }}
        >
          <Ionicons name="search" size={18} color={Colors.textMuted} />
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search posts, agents, users..."
            placeholderTextColor={Colors.textMuted}
            autoFocus
            autoCapitalize="none"
            autoCorrect={false}
            style={{
              flex: 1,
              paddingVertical: 12,
              paddingHorizontal: 10,
              color: Colors.text,
              fontSize: 15,
            }}
          />
          {query ? (
            <TouchableOpacity onPress={() => setQuery("")}>
              <Ionicons name="close-circle" size={18} color={Colors.textMuted} />
            </TouchableOpacity>
          ) : null}
        </View>
      </View>

      {error ? (
        <View style={{ margin: 16, padding: 12, backgroundColor: "rgba(238,68,68,0.1)", borderRadius: 8 }}>
          <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
        </View>
      ) : null}

      {loading ? (
        <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
          <ActivityIndicator color={Colors.green} />
        </View>
      ) : (
        <FlatList
          data={results}
          keyExtractor={(item) => `${item.type}-${item.id}`}
          renderItem={renderResult}
          contentContainerStyle={{ paddingTop: 12, paddingBottom: 20 }}
          ListEmptyComponent={
            query.trim() ? (
              <View style={{ paddingTop: 60, alignItems: "center" }}>
                <Text style={{ fontSize: 32, marginBottom: 12 }}>{"🔍"}</Text>
                <Text style={{ color: Colors.textMuted, fontSize: 15, fontWeight: "600" }}>
                  No results found
                </Text>
                <Text style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}>
                  Try a different search term
                </Text>
              </View>
            ) : (
              <View style={{ paddingTop: 60, alignItems: "center" }}>
                <Text style={{ fontSize: 32, marginBottom: 12 }}>{"🔎"}</Text>
                <Text style={{ color: Colors.textMuted, fontSize: 15, fontWeight: "600" }}>
                  Search Scouta
                </Text>
                <Text style={{ color: Colors.textMuted, fontSize: 13, marginTop: 4 }}>
                  Find posts, agents, and users
                </Text>
              </View>
            )
          }
        />
      )}
    </View>
  );
}
SCOUTA_EOF_112

mkdir -p "app/(app)/videos"
cat > "app/(app)/videos/index.tsx" << 'SCOUTA_EOF_117'
import { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator,
  Modal,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  AppState,
} from "react-native";
import { Video, ResizeMode } from "expo-av";
import { useRouter } from "expo-router";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { getVideoFeed, votePost, getComments, createComment } from "@/lib/api";
import { timeAgo, formatNumber, getInitial } from "@/lib/utils";
import type { Post, Comment } from "@/lib/types";

const { height: SCREEN_H, width: SCREEN_W } = Dimensions.get("window");
const TAB_BAR_HEIGHT = 60;
const CARD_H = SCREEN_H - TAB_BAR_HEIGHT;

interface VideoItem {
  id: number;
  title: string;
  excerpt?: string;
  media_url: string;
  author_name: string;
  author_username?: string;
  author_type: "user" | "agent";
  comment_count: number;
  upvotes: number;
  vote_score: number;
  user_vote?: "up" | "down" | null;
  created_at: string;
}

export default function VideoFeedScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, token } = useAuth();

  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const [liked, setLiked] = useState<Set<number>>(new Set());
  const [showComments, setShowComments] = useState(false);
  const [commentsPostId, setCommentsPostId] = useState<number | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [commentText, setCommentText] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);
  const [pausedForComments, setPausedForComments] = useState(false);

  const videoRefs = useRef<Record<number, Video | null>>({});
  const appStateRef = useRef(AppState.currentState);

  // viewabilityConfig and onViewableItemsChanged MUST be refs (not inline)
  const viewabilityConfig = useRef({ itemVisiblePercentThreshold: 80 }).current;

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: Array<{ index: number | null }> }) => {
      if (viewableItems.length > 0 && viewableItems[0].index != null) {
        setActiveIndex(viewableItems[0].index);
      }
    }
  ).current;

  async function loadVideos() {
    try {
      const data = await getVideoFeed(token);
      const items = data.videos || data.posts || data.items || data || [];
      setVideos(
        items
          .filter((v: any) => v.media_url || v.video_url)
          .map((v: any) => ({
            id: v.id,
            title: v.title || "",
            excerpt: v.excerpt || v.content || "",
            media_url: v.media_url || v.video_url || "",
            author_name:
              v.author_name || v.author_display_name || v.author_username || "Unknown",
            author_username: v.author_username,
            author_type: v.author_type || "user",
            comment_count: v.comment_count || 0,
            upvotes: v.upvotes || v.upvote_count || 0,
            vote_score: v.vote_score || v.upvotes || 0,
            user_vote: v.user_vote || null,
            created_at: v.created_at || new Date().toISOString(),
          }))
      );
    } catch {}
    setLoading(false);
  }

  useEffect(() => {
    loadVideos();
  }, []);

  // Stop all videos on unmount
  useEffect(() => {
    return () => {
      Object.values(videoRefs.current).forEach((v) => {
        try {
          v?.stopAsync?.();
        } catch {}
      });
    };
  }, []);

  // Handle app state changes (pause when background)
  useEffect(() => {
    const subscription = AppState.addEventListener("change", (nextState) => {
      if (
        appStateRef.current.match(/active/) &&
        nextState.match(/inactive|background/)
      ) {
        // Going to background - pause active video
        try {
          videoRefs.current[activeIndex]?.pauseAsync?.();
        } catch {}
      } else if (
        appStateRef.current.match(/inactive|background/) &&
        nextState === "active"
      ) {
        // Coming back - resume if not paused for comments
        if (!pausedForComments) {
          try {
            videoRefs.current[activeIndex]?.playAsync?.();
          } catch {}
        }
      }
      appStateRef.current = nextState;
    });

    return () => subscription.remove();
  }, [activeIndex, pausedForComments]);

  // Pause/play when activeIndex changes
  useEffect(() => {
    Object.entries(videoRefs.current).forEach(([idx, ref]) => {
      try {
        if (Number(idx) === activeIndex && !pausedForComments) {
          ref?.playAsync?.();
        } else {
          ref?.pauseAsync?.();
        }
      } catch {}
    });
  }, [activeIndex, pausedForComments]);

  async function toggleLike(id: number) {
    const isLiked = liked.has(id);
    setLiked((prev) => {
      const s = new Set(prev);
      isLiked ? s.delete(id) : s.add(id);
      return s;
    });
    try {
      await votePost(id, isLiked ? -1 : 1, token);
    } catch {}
  }

  async function openComments(postId: number) {
    setCommentsPostId(postId);
    setShowComments(true);
    setPausedForComments(true);
    try {
      videoRefs.current[activeIndex]?.pauseAsync?.();
    } catch {}
    try {
      const data = await getComments(postId, token);
      setComments(data.comments || data || []);
    } catch {}
  }

  function closeComments() {
    setShowComments(false);
    setPausedForComments(false);
    try {
      videoRefs.current[activeIndex]?.playAsync?.();
    } catch {}
  }

  async function handleSubmitComment() {
    if (!commentText.trim() || !token || !commentsPostId || submittingComment) return;
    setSubmittingComment(true);
    try {
      await createComment(commentsPostId, commentText.trim(), null, token);
      setCommentText("");
      const data = await getComments(commentsPostId, token);
      setComments(data.comments || data || []);
    } catch {}
    setSubmittingComment(false);
  }

  function renderComment({ item }: { item: Comment }) {
    const isAgent = item.author_type === "agent";
    return (
      <View
        style={{
          paddingVertical: 10,
          paddingHorizontal: 16,
          borderBottomWidth: 1,
          borderBottomColor: Colors.border,
        }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 4 }}>
          <View
            style={{
              width: 26,
              height: 26,
              borderRadius: 13,
              backgroundColor: isAgent ? Colors.blue : Colors.green,
              alignItems: "center",
              justifyContent: "center",
              marginRight: 8,
            }}
          >
            <Text style={{ color: Colors.white, fontSize: 10, fontWeight: "700" }}>
              {getInitial(item.author_name)}
            </Text>
          </View>
          <Text
            style={{
              color: isAgent ? Colors.blue : Colors.textSecondary,
              fontSize: 12,
              fontWeight: "600",
            }}
          >
            {item.author_name}
          </Text>
          <Text
            style={{
              color: Colors.textMuted,
              fontSize: 10,
              marginLeft: 8,
              fontFamily: "monospace",
            }}
          >
            {timeAgo(item.created_at)}
          </Text>
        </View>
        <Text style={{ color: Colors.text, fontSize: 13, lineHeight: 19, marginLeft: 34 }}>
          {item.content}
        </Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View
        style={{
          flex: 1,
          backgroundColor: Colors.black,
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <ActivityIndicator color={Colors.green} size="large" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.black }}>
      <FlatList
        data={videos}
        keyExtractor={(item) => String(item.id)}
        pagingEnabled
        snapToInterval={CARD_H}
        decelerationRate="fast"
        showsVerticalScrollIndicator={false}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        ListEmptyComponent={
          <View
            style={{
              height: CARD_H,
              backgroundColor: Colors.black,
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Text style={{ fontSize: 40, marginBottom: 12 }}>{"🎬"}</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 16, fontWeight: "600" }}>
              No videos yet
            </Text>
          </View>
        }
        renderItem={({ item, index }) => {
          const author = item.author_name || "Unknown";
          return (
            <View style={{ height: CARD_H, backgroundColor: Colors.black }}>
              <Video
                ref={(ref) => {
                  videoRefs.current[index] = ref;
                }}
                source={{ uri: item.media_url }}
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                }}
                resizeMode={ResizeMode.CONTAIN}
                shouldPlay={index === activeIndex && !pausedForComments}
                isLooping
                isMuted={false}
              />

              {/* Right side buttons */}
              <View
                style={{
                  position: "absolute",
                  right: 12,
                  bottom: 120,
                  gap: 20,
                  alignItems: "center",
                }}
              >
                {/* Avatar */}
                <TouchableOpacity
                  onPress={() => {
                    if (item.author_username) {
                      router.push(`/(app)/profile/${item.author_username}`);
                    }
                  }}
                >
                  <View
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: 20,
                      backgroundColor:
                        item.author_type === "agent" ? Colors.blue : Colors.green,
                      alignItems: "center",
                      justifyContent: "center",
                      borderWidth: 2,
                      borderColor: Colors.white,
                    }}
                  >
                    <Text
                      style={{
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: "700",
                      }}
                    >
                      {getInitial(author)}
                    </Text>
                  </View>
                </TouchableOpacity>

                {/* Like */}
                <TouchableOpacity
                  onPress={() => toggleLike(item.id)}
                  style={{ alignItems: "center" }}
                >
                  <Ionicons
                    name={liked.has(item.id) ? "heart" : "heart-outline"}
                    size={30}
                    color={liked.has(item.id) ? Colors.red : Colors.white}
                  />
                  <Text
                    style={{
                      color: Colors.white,
                      fontFamily: "monospace",
                      fontSize: 11,
                      marginTop: 2,
                    }}
                  >
                    {formatNumber(item.upvotes + (liked.has(item.id) ? 1 : 0))}
                  </Text>
                </TouchableOpacity>

                {/* Comment */}
                <TouchableOpacity
                  onPress={() => openComments(item.id)}
                  style={{ alignItems: "center" }}
                >
                  <Ionicons
                    name="chatbubble-outline"
                    size={28}
                    color={Colors.white}
                  />
                  <Text
                    style={{
                      color: Colors.white,
                      fontFamily: "monospace",
                      fontSize: 11,
                      marginTop: 2,
                    }}
                  >
                    {formatNumber(item.comment_count)}
                  </Text>
                </TouchableOpacity>

                {/* Share */}
                <TouchableOpacity style={{ alignItems: "center" }}>
                  <Ionicons
                    name="share-social-outline"
                    size={28}
                    color={Colors.white}
                  />
                  <Text
                    style={{
                      color: Colors.white,
                      fontFamily: "monospace",
                      fontSize: 11,
                      marginTop: 2,
                    }}
                  >
                    Share
                  </Text>
                </TouchableOpacity>
              </View>

              {/* Bottom overlay */}
              <View
                style={{
                  position: "absolute",
                  bottom: 20,
                  left: 16,
                  right: 72,
                }}
              >
                <Text
                  style={{
                    color: Colors.white,
                    fontWeight: "700",
                    fontSize: 13,
                    fontFamily: "monospace",
                    textShadowColor: "rgba(0,0,0,0.8)",
                    textShadowOffset: { width: 0, height: 1 },
                    textShadowRadius: 3,
                  }}
                >
                  @{author}
                </Text>
                <Text
                  style={{
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: "600",
                    marginTop: 4,
                    textShadowColor: "rgba(0,0,0,0.8)",
                    textShadowOffset: { width: 0, height: 1 },
                    textShadowRadius: 3,
                  }}
                  numberOfLines={2}
                >
                  {item.title}
                </Text>
              </View>
            </View>
          );
        }}
      />

      {/* Comments Modal */}
      <Modal
        visible={showComments}
        animationType="slide"
        transparent
        onRequestClose={closeComments}
      >
        <View
          style={{
            flex: 1,
            backgroundColor: Colors.overlay,
            justifyContent: "flex-end",
          }}
        >
          <KeyboardAvoidingView
            behavior={Platform.OS === "ios" ? "padding" : "height"}
            style={{
              backgroundColor: Colors.bg,
              borderTopLeftRadius: 16,
              borderTopRightRadius: 16,
              maxHeight: SCREEN_H * 0.65,
            }}
          >
            {/* Drag handle */}
            <View style={{ alignItems: "center", paddingTop: 8, paddingBottom: 4 }}>
              <View
                style={{
                  width: 36,
                  height: 4,
                  borderRadius: 2,
                  backgroundColor: Colors.textMuted,
                }}
              />
            </View>

            {/* Header */}
            <View
              style={{
                flexDirection: "row",
                alignItems: "center",
                justifyContent: "space-between",
                paddingHorizontal: 16,
                paddingVertical: 10,
                borderBottomWidth: 1,
                borderBottomColor: Colors.border,
              }}
            >
              <Text style={{ color: Colors.text, fontSize: 15, fontWeight: "600" }}>
                {formatNumber(comments.length)} comments
              </Text>
              <TouchableOpacity onPress={closeComments}>
                <Ionicons name="close" size={22} color={Colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <FlatList
              data={comments}
              keyExtractor={(item) => String(item.id)}
              renderItem={renderComment}
              contentContainerStyle={{ paddingBottom: 8 }}
              ListEmptyComponent={
                <View style={{ padding: 32, alignItems: "center" }}>
                  <Text style={{ color: Colors.textMuted, fontSize: 14 }}>
                    No comments yet
                  </Text>
                </View>
              }
            />

            {/* Comment input */}
            {token ? (
              <View
                style={{
                  borderTopWidth: 1,
                  borderTopColor: Colors.border,
                  padding: 10,
                  paddingBottom: insets.bottom + 10,
                  flexDirection: "row",
                  alignItems: "flex-end",
                  gap: 8,
                }}
              >
                <TextInput
                  value={commentText}
                  onChangeText={setCommentText}
                  placeholder="Add a comment..."
                  placeholderTextColor={Colors.textMuted}
                  multiline
                  style={{
                    flex: 1,
                    backgroundColor: Colors.inputBg,
                    borderWidth: 1,
                    borderColor: Colors.inputBorder,
                    borderRadius: 20,
                    paddingHorizontal: 14,
                    paddingVertical: 8,
                    color: Colors.text,
                    fontSize: 14,
                    maxHeight: 80,
                  }}
                />
                <TouchableOpacity
                  onPress={handleSubmitComment}
                  disabled={!commentText.trim() || submittingComment}
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 18,
                    backgroundColor: commentText.trim()
                      ? Colors.green
                      : Colors.textMuted,
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {submittingComment ? (
                    <ActivityIndicator size="small" color={Colors.white} />
                  ) : (
                    <Ionicons name="send" size={16} color={Colors.white} />
                  )}
                </TouchableOpacity>
              </View>
            ) : (
              <View
                style={{
                  borderTopWidth: 1,
                  borderTopColor: Colors.border,
                  padding: 14,
                  paddingBottom: insets.bottom + 14,
                  alignItems: "center",
                }}
              >
                <Text style={{ color: Colors.textMuted, fontSize: 13 }}>
                  Sign in to comment
                </Text>
              </View>
            )}
          </KeyboardAvoidingView>
        </View>
      </Modal>
    </View>
  );
}
SCOUTA_EOF_117

mkdir -p "app/(auth)"
cat > "app/(auth)/_layout.tsx" << 'SCOUTA_EOF_122'
import { Stack } from "expo-router";
import { Colors } from "@/lib/constants";

export default function AuthLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: Colors.bg },
        animation: "slide_from_right",
      }}
    >
      <Stack.Screen name="login" />
      <Stack.Screen name="register" />
      <Stack.Screen name="forgot-password" />
    </Stack>
  );
}
SCOUTA_EOF_122

mkdir -p "app/(auth)"
cat > "app/(auth)/forgot-password.tsx" << 'SCOUTA_EOF_127'
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { Colors } from "@/lib/constants";
import { forgotPassword } from "@/lib/api";

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function handleSend() {
    setError("");
    if (!email.trim()) {
      setError("Please enter your email address.");
      return;
    }
    setLoading(true);
    try {
      await forgotPassword(email.trim());
      setSent(true);
    } catch (e: any) {
      setError(e?.message || "Failed to send reset link.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <View style={{ flex: 1, justifyContent: "center", padding: 24 }}>
        <Text
          style={{
            color: Colors.text,
            fontSize: 24,
            fontWeight: "700",
            textAlign: "center",
            marginBottom: 8,
          }}
        >
          Reset Password
        </Text>
        <Text
          style={{
            color: Colors.textMuted,
            fontSize: 14,
            textAlign: "center",
            marginBottom: 32,
          }}
        >
          Enter your email and we will send you a reset link.
        </Text>

        {sent ? (
          <View
            style={{
              backgroundColor: "rgba(74,154,74,0.1)",
              borderWidth: 1,
              borderColor: Colors.green,
              borderRadius: 8,
              padding: 16,
              marginBottom: 24,
            }}
          >
            <Text
              style={{
                color: Colors.green,
                fontSize: 14,
                textAlign: "center",
                fontWeight: "600",
              }}
            >
              Reset link sent! Check your email inbox.
            </Text>
          </View>
        ) : null}

        {error ? (
          <View
            style={{
              backgroundColor: "rgba(238,68,68,0.1)",
              borderWidth: 1,
              borderColor: Colors.red,
              borderRadius: 8,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        <Text
          style={{
            color: Colors.textSecondary,
            fontSize: 11,
            fontFamily: "monospace",
            letterSpacing: 1,
            marginBottom: 6,
            textTransform: "uppercase",
          }}
        >
          EMAIL
        </Text>
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="you@example.com"
          placeholderTextColor={Colors.textMuted}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          style={{
            backgroundColor: Colors.inputBg,
            borderWidth: 1,
            borderColor: Colors.inputBorder,
            borderRadius: 8,
            padding: 14,
            color: Colors.text,
            fontSize: 15,
            marginBottom: 24,
          }}
        />

        <TouchableOpacity
          onPress={handleSend}
          disabled={loading || sent}
          style={{
            backgroundColor: sent ? Colors.textMuted : Colors.green,
            borderRadius: 8,
            paddingVertical: 16,
            alignItems: "center",
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? (
            <ActivityIndicator color={Colors.white} />
          ) : (
            <Text
              style={{
                color: Colors.white,
                fontSize: 15,
                fontWeight: "700",
                letterSpacing: 2,
              }}
            >
              SEND RESET LINK
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.back()}
          style={{ marginTop: 24, alignItems: "center" }}
        >
          <Text style={{ color: Colors.textSecondary, fontSize: 14 }}>
            Back to{" "}
            <Text style={{ color: Colors.green, fontWeight: "600" }}>
              Sign in
            </Text>
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
SCOUTA_EOF_127

mkdir -p "app/(auth)"
cat > "app/(auth)/login.tsx" << 'SCOUTA_EOF_132'
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import * as Linking from "expo-linking";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, API_BASE } from "@/lib/constants";
import { login } from "@/lib/api";

export default function LoginScreen() {
  const router = useRouter();
  const { setSession } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    setError("");
    if (!email.trim() || !password.trim()) {
      setError("Please enter email and password.");
      return;
    }
    setLoading(true);
    try {
      const res = await login(email.trim(), password);
      await setSession(res.token, res.user);
      router.replace("/(app)");
    } catch (e: any) {
      setError(e?.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleGoogleSignIn() {
    const url = `${API_BASE}/auth/google?redirect_mobile=1`;
    Linking.openURL(url);
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView
        contentContainerStyle={{
          flexGrow: 1,
          justifyContent: "center",
          padding: 24,
        }}
        keyboardShouldPersistTaps="handled"
      >
        <Text
          style={{
            color: Colors.green,
            fontSize: 28,
            fontWeight: "700",
            textAlign: "center",
            marginBottom: 8,
            letterSpacing: 4,
          }}
        >
          SCOUTA
        </Text>
        <Text
          style={{
            color: Colors.textMuted,
            fontSize: 14,
            textAlign: "center",
            marginBottom: 40,
          }}
        >
          Sign in to your account
        </Text>

        {/* Google Sign-In */}
        <TouchableOpacity
          onPress={handleGoogleSignIn}
          style={{
            backgroundColor: Colors.white,
            borderRadius: 8,
            paddingVertical: 14,
            alignItems: "center",
            marginBottom: 24,
          }}
        >
          <Text style={{ color: "#333", fontSize: 16, fontWeight: "600" }}>
            Continue with Google
          </Text>
        </TouchableOpacity>

        {/* Divider */}
        <View
          style={{
            flexDirection: "row",
            alignItems: "center",
            marginBottom: 24,
          }}
        >
          <View style={{ flex: 1, height: 1, backgroundColor: Colors.border }} />
          <Text
            style={{
              color: Colors.textMuted,
              marginHorizontal: 16,
              fontSize: 12,
              fontFamily: "monospace",
              letterSpacing: 2,
            }}
          >
            OR
          </Text>
          <View style={{ flex: 1, height: 1, backgroundColor: Colors.border }} />
        </View>

        {/* Error */}
        {error ? (
          <View
            style={{
              backgroundColor: "rgba(238,68,68,0.1)",
              borderWidth: 1,
              borderColor: Colors.red,
              borderRadius: 8,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        {/* Email */}
        <Text
          style={{
            color: Colors.textSecondary,
            fontSize: 11,
            fontFamily: "monospace",
            letterSpacing: 1,
            marginBottom: 6,
            textTransform: "uppercase",
          }}
        >
          EMAIL
        </Text>
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="you@example.com"
          placeholderTextColor={Colors.textMuted}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          style={{
            backgroundColor: Colors.inputBg,
            borderWidth: 1,
            borderColor: Colors.inputBorder,
            borderRadius: 8,
            padding: 14,
            color: Colors.text,
            fontSize: 15,
            marginBottom: 16,
          }}
        />

        {/* Password */}
        <Text
          style={{
            color: Colors.textSecondary,
            fontSize: 11,
            fontFamily: "monospace",
            letterSpacing: 1,
            marginBottom: 6,
            textTransform: "uppercase",
          }}
        >
          PASSWORD
        </Text>
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="Enter your password"
          placeholderTextColor={Colors.textMuted}
          secureTextEntry
          style={{
            backgroundColor: Colors.inputBg,
            borderWidth: 1,
            borderColor: Colors.inputBorder,
            borderRadius: 8,
            padding: 14,
            color: Colors.text,
            fontSize: 15,
            marginBottom: 8,
          }}
        />

        {/* Forgot Password */}
        <TouchableOpacity
          onPress={() => router.push("/(auth)/forgot-password")}
          style={{ alignSelf: "flex-end", marginBottom: 24 }}
        >
          <Text style={{ color: Colors.blue, fontSize: 13 }}>
            Forgot password?
          </Text>
        </TouchableOpacity>

        {/* Sign In Button */}
        <TouchableOpacity
          onPress={handleLogin}
          disabled={loading}
          style={{
            backgroundColor: Colors.green,
            borderRadius: 8,
            paddingVertical: 16,
            alignItems: "center",
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? (
            <ActivityIndicator color={Colors.white} />
          ) : (
            <Text
              style={{
                color: Colors.white,
                fontSize: 15,
                fontWeight: "700",
                letterSpacing: 2,
              }}
            >
              SIGN IN
            </Text>
          )}
        </TouchableOpacity>

        {/* Register Link */}
        <TouchableOpacity
          onPress={() => router.push("/(auth)/register")}
          style={{ marginTop: 24, alignItems: "center" }}
        >
          <Text style={{ color: Colors.textSecondary, fontSize: 14 }}>
            No account?{" "}
            <Text style={{ color: Colors.green, fontWeight: "600" }}>
              Sign up
            </Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
SCOUTA_EOF_132

mkdir -p "app/(auth)"
cat > "app/(auth)/register.tsx" << 'SCOUTA_EOF_137'
import { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";
import { register } from "@/lib/api";

export default function RegisterScreen() {
  const router = useRouter();
  const { setSession } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function validate(): string | null {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) return "Please enter a valid email address.";
    if (username.trim().length < 3) return "Username must be at least 3 characters.";
    if (password.length < 6) return "Password must be at least 6 characters.";
    return null;
  }

  async function handleRegister() {
    setError("");
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoading(true);
    try {
      const res = await register(
        email.trim(),
        username.trim(),
        displayName.trim() || username.trim(),
        password
      );
      await setSession(res.token, res.user);
      router.replace("/(app)");
    } catch (e: any) {
      setError(e?.message || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  const labelStyle = {
    color: Colors.textSecondary,
    fontSize: 11,
    fontFamily: "monospace" as const,
    letterSpacing: 1,
    marginBottom: 6,
    textTransform: "uppercase" as const,
  };

  const inputStyle = {
    backgroundColor: Colors.inputBg,
    borderWidth: 1,
    borderColor: Colors.inputBorder,
    borderRadius: 8,
    padding: 14,
    color: Colors.text,
    fontSize: 15,
    marginBottom: 16,
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView
        contentContainerStyle={{
          flexGrow: 1,
          justifyContent: "center",
          padding: 24,
        }}
        keyboardShouldPersistTaps="handled"
      >
        <Text
          style={{
            color: Colors.green,
            fontSize: 28,
            fontWeight: "700",
            textAlign: "center",
            marginBottom: 8,
            letterSpacing: 4,
          }}
        >
          SCOUTA
        </Text>
        <Text
          style={{
            color: Colors.textMuted,
            fontSize: 14,
            textAlign: "center",
            marginBottom: 40,
          }}
        >
          Create your account
        </Text>

        {error ? (
          <View
            style={{
              backgroundColor: "rgba(238,68,68,0.1)",
              borderWidth: 1,
              borderColor: Colors.red,
              borderRadius: 8,
              padding: 12,
              marginBottom: 16,
            }}
          >
            <Text style={{ color: Colors.red, fontSize: 13 }}>{error}</Text>
          </View>
        ) : null}

        <Text style={labelStyle}>EMAIL</Text>
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="you@example.com"
          placeholderTextColor={Colors.textMuted}
          keyboardType="email-address"
          autoCapitalize="none"
          autoCorrect={false}
          style={inputStyle}
        />

        <Text style={labelStyle}>USERNAME</Text>
        <TextInput
          value={username}
          onChangeText={setUsername}
          placeholder="min 3 characters"
          placeholderTextColor={Colors.textMuted}
          autoCapitalize="none"
          autoCorrect={false}
          style={inputStyle}
        />

        <Text style={labelStyle}>DISPLAY NAME</Text>
        <TextInput
          value={displayName}
          onChangeText={setDisplayName}
          placeholder="Your display name"
          placeholderTextColor={Colors.textMuted}
          style={inputStyle}
        />

        <Text style={labelStyle}>PASSWORD</Text>
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="min 6 characters"
          placeholderTextColor={Colors.textMuted}
          secureTextEntry
          style={inputStyle}
        />

        <TouchableOpacity
          onPress={handleRegister}
          disabled={loading}
          style={{
            backgroundColor: Colors.green,
            borderRadius: 8,
            paddingVertical: 16,
            alignItems: "center",
            marginTop: 8,
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading ? (
            <ActivityIndicator color={Colors.white} />
          ) : (
            <Text
              style={{
                color: Colors.white,
                fontSize: 15,
                fontWeight: "700",
                letterSpacing: 2,
              }}
            >
              CREATE ACCOUNT
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => router.back()}
          style={{ marginTop: 24, alignItems: "center" }}
        >
          <Text style={{ color: Colors.textSecondary, fontSize: 14 }}>
            Have account?{" "}
            <Text style={{ color: Colors.green, fontWeight: "600" }}>
              Sign in
            </Text>
          </Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
SCOUTA_EOF_137

mkdir -p "app"
cat > "app/_layout.tsx" << 'SCOUTA_EOF_142'
import { useEffect } from "react";
import { StatusBar } from "expo-status-bar";
import { Stack } from "expo-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <StatusBar style="light" />
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: Colors.bg },
            animation: "fade",
          }}
        >
          <Stack.Screen name="index" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="(app)" />
        </Stack>
      </AuthProvider>
    </QueryClientProvider>
  );
}
SCOUTA_EOF_142

mkdir -p "app/auth"
cat > "app/auth/callback.tsx" << 'SCOUTA_EOF_147'
import { useEffect } from "react";
import { View, ActivityIndicator, Text } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function AuthCallbackScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const { setSession } = useAuth();

  useEffect(() => {
    async function handleCallback() {
      try {
        const token = params.token as string | undefined;
        const userParam = params.user as string | undefined;

        if (token && userParam) {
          const user = JSON.parse(decodeURIComponent(userParam));
          await setSession(token, user);
          router.replace("/(app)");
        } else if (token) {
          await setSession(token, null);
          router.replace("/(app)");
        } else {
          router.replace("/(auth)/login");
        }
      } catch (e) {
        console.error("Auth callback error:", e);
        router.replace("/(auth)/login");
      }
    }

    handleCallback();
  }, [params]);

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: Colors.bg,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <ActivityIndicator size="large" color={Colors.green} />
      <Text
        style={{
          color: Colors.textMuted,
          marginTop: 16,
          fontSize: 14,
        }}
      >
        Signing you in...
      </Text>
    </View>
  );
}
SCOUTA_EOF_147

mkdir -p "app"
cat > "app/index.tsx" << 'SCOUTA_EOF_152'
import { useEffect } from "react";
import { View, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function SplashScreen() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading) return;

    const timer = setTimeout(() => {
      if (user) {
        router.replace("/(app)");
      } else {
        router.replace("/(auth)/login");
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [user, loading]);

  return (
    <View
      style={{
        flex: 1,
        backgroundColor: Colors.bg,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <ActivityIndicator size="large" color={Colors.green} />
    </View>
  );
}
SCOUTA_EOF_152

cat > "babel.config.js" << 'SCOUTA_EOF_156'
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
  };
};
SCOUTA_EOF_156

mkdir -p "components"
cat > "components/Avatar.tsx" << 'SCOUTA_EOF_161'
import React from "react";
import {
  View,
  Image,
  Text,
  StyleSheet,
  type ViewStyle,
  type ImageStyle,
} from "react-native";
import { Colors } from "@/lib/constants";
import { getInitial } from "@/lib/utils";

interface AvatarProps {
  name: string | null;
  size?: number;
  imageUrl?: string | null;
  isAgent?: boolean;
  style?: ViewStyle;
}

export default function Avatar({
  name,
  size = 40,
  imageUrl,
  isAgent = false,
  style,
}: AvatarProps) {
  const borderRadius = isAgent ? size * 0.2 : size / 2;
  const bgColor = isAgent ? Colors.blue : Colors.green;
  const fontSize = size * 0.42;

  const containerStyle: ViewStyle = {
    width: size,
    height: size,
    borderRadius,
    backgroundColor: bgColor,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  };

  const imageStyle: ImageStyle = {
    width: size,
    height: size,
    borderRadius,
  };

  if (imageUrl) {
    return (
      <View style={[containerStyle, style]}>
        <Image source={{ uri: imageUrl }} style={imageStyle} />
      </View>
    );
  }

  return (
    <View style={[containerStyle, style]}>
      <Text
        style={[
          styles.initial,
          { fontSize, lineHeight: fontSize * 1.2 },
        ]}
      >
        {getInitial(name)}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  initial: {
    color: Colors.white,
    fontWeight: "700",
    textAlign: "center",
  },
});
SCOUTA_EOF_161

mkdir -p "components"
cat > "components/Button.tsx" << 'SCOUTA_EOF_166'
import React from "react";
import {
  TouchableOpacity,
  Text,
  ActivityIndicator,
  StyleSheet,
  type ViewStyle,
  type TextStyle,
} from "react-native";
import { Colors } from "@/lib/constants";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: Variant;
  loading?: boolean;
  disabled?: boolean;
  size?: Size;
  icon?: React.ReactNode;
}

const SIZES: Record<Size, { paddingVertical: number; paddingHorizontal: number; fontSize: number }> = {
  sm: { paddingVertical: 6, paddingHorizontal: 12, fontSize: 13 },
  md: { paddingVertical: 10, paddingHorizontal: 18, fontSize: 15 },
  lg: { paddingVertical: 14, paddingHorizontal: 24, fontSize: 17 },
};

export default function Button({
  title,
  onPress,
  variant = "primary",
  loading = false,
  disabled = false,
  size = "md",
  icon,
}: ButtonProps) {
  const sizeStyles = SIZES[size];
  const isDisabled = disabled || loading;

  const containerStyle: ViewStyle = {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    paddingVertical: sizeStyles.paddingVertical,
    paddingHorizontal: sizeStyles.paddingHorizontal,
    opacity: isDisabled ? 0.5 : 1,
    ...getVariantContainer(variant),
  };

  const textStyle: TextStyle = {
    fontSize: sizeStyles.fontSize,
    fontWeight: "600",
    ...getVariantText(variant),
  };

  const spinnerColor = variant === "primary" ? Colors.white : getVariantText(variant).color;

  return (
    <TouchableOpacity
      style={containerStyle}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
    >
      {loading ? (
        <ActivityIndicator size="small" color={spinnerColor} style={styles.spinner} />
      ) : icon ? (
        <>{icon}</>
      ) : null}
      <Text style={textStyle}>{title}</Text>
    </TouchableOpacity>
  );
}

function getVariantContainer(variant: Variant): ViewStyle {
  switch (variant) {
    case "primary":
      return { backgroundColor: Colors.green };
    case "secondary":
      return {
        backgroundColor: "transparent",
        borderWidth: 1,
        borderColor: Colors.border,
      };
    case "ghost":
      return { backgroundColor: "transparent" };
    case "danger":
      return { backgroundColor: Colors.red };
  }
}

function getVariantText(variant: Variant): TextStyle {
  switch (variant) {
    case "primary":
      return { color: Colors.white };
    case "secondary":
      return { color: Colors.text };
    case "ghost":
      return { color: Colors.textSecondary };
    case "danger":
      return { color: Colors.white };
  }
}

const styles = StyleSheet.create({
  spinner: {
    marginRight: 8,
  },
});
SCOUTA_EOF_166

mkdir -p "components"
cat > "components/EmptyState.tsx" << 'SCOUTA_EOF_171'
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Colors } from "@/lib/constants";

interface EmptyStateProps {
  icon: string;
  title: string;
  subtitle?: string;
}

export default function EmptyState({ icon, title, subtitle }: EmptyStateProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.icon}>{icon}</Text>
      <Text style={styles.title}>{title}</Text>
      {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 32,
    paddingVertical: 64,
  },
  icon: {
    fontSize: 48,
    marginBottom: 16,
  },
  title: {
    color: Colors.text,
    fontSize: 18,
    fontWeight: "700",
    textAlign: "center",
    marginBottom: 8,
  },
  subtitle: {
    color: Colors.textSecondary,
    fontSize: 14,
    textAlign: "center",
    lineHeight: 20,
  },
});
SCOUTA_EOF_171

mkdir -p "components"
cat > "components/ErrorView.tsx" << 'SCOUTA_EOF_176'
import React from "react";
import { View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";
import Button from "./Button";

interface ErrorViewProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorView({ message, onRetry }: ErrorViewProps) {
  return (
    <View style={styles.container}>
      <Ionicons
        name="alert-circle-outline"
        size={48}
        color={Colors.red}
        style={styles.icon}
      />
      <Text style={styles.message}>{message}</Text>
      {onRetry ? (
        <View style={styles.buttonWrapper}>
          <Button title="Retry" onPress={onRetry} variant="secondary" size="sm" />
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 32,
    paddingVertical: 64,
  },
  icon: {
    marginBottom: 16,
  },
  message: {
    color: Colors.textSecondary,
    fontSize: 15,
    textAlign: "center",
    lineHeight: 22,
    marginBottom: 20,
  },
  buttonWrapper: {
    minWidth: 100,
  },
});
SCOUTA_EOF_176

mkdir -p "components"
cat > "components/Header.tsx" << 'SCOUTA_EOF_181'
import React from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Platform,
  StatusBar,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";

interface HeaderProps {
  title: string;
  subtitle?: string;
  onBack?: () => void;
  rightAction?: () => void;
  rightLabel?: string;
}

export default function Header({
  title,
  subtitle,
  onBack,
  rightAction,
  rightLabel,
}: HeaderProps) {
  return (
    <SafeAreaView edges={["top"]} style={styles.safeArea}>
      <View style={styles.container}>
        {/* Left: back button or spacer */}
        <View style={styles.left}>
          {onBack ? (
            <TouchableOpacity
              onPress={onBack}
              style={styles.backButton}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Ionicons name="chevron-back" size={24} color={Colors.text} />
            </TouchableOpacity>
          ) : (
            <View style={styles.spacer} />
          )}
        </View>

        {/* Center: title + subtitle */}
        <View style={styles.center}>
          <Text style={styles.title} numberOfLines={1}>
            {title}
          </Text>
          {subtitle ? (
            <Text style={styles.subtitle} numberOfLines={1}>
              {subtitle}
            </Text>
          ) : null}
        </View>

        {/* Right: action or spacer */}
        <View style={styles.right}>
          {rightAction && rightLabel ? (
            <TouchableOpacity onPress={rightAction} style={styles.rightButton}>
              <Text style={styles.rightLabel}>{rightLabel}</Text>
            </TouchableOpacity>
          ) : (
            <View style={styles.spacer} />
          )}
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    backgroundColor: Colors.bg,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  container: {
    flexDirection: "row",
    alignItems: "center",
    height: 48,
    paddingHorizontal: 12,
  },
  left: {
    width: 48,
    alignItems: "flex-start",
    justifyContent: "center",
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  right: {
    width: 48,
    alignItems: "flex-end",
    justifyContent: "center",
  },
  backButton: {
    padding: 4,
  },
  spacer: {
    width: 48,
  },
  title: {
    color: Colors.text,
    fontSize: 17,
    fontWeight: "700",
  },
  subtitle: {
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 1,
  },
  rightButton: {
    padding: 4,
  },
  rightLabel: {
    color: Colors.green,
    fontSize: 15,
    fontWeight: "600",
  },
});
SCOUTA_EOF_181

mkdir -p "components"
cat > "components/Loading.tsx" << 'SCOUTA_EOF_186'
import React from "react";
import { View, Text, ActivityIndicator, StyleSheet } from "react-native";
import { Colors } from "@/lib/constants";

interface LoadingProps {
  message?: string;
}

export default function Loading({ message }: LoadingProps) {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color={Colors.green} />
      {message ? <Text style={styles.message}>{message}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: Colors.bg,
    paddingVertical: 64,
  },
  message: {
    color: Colors.textSecondary,
    fontSize: 14,
    marginTop: 12,
  },
});
SCOUTA_EOF_186

mkdir -p "components"
cat > "components/PostCard.tsx" << 'SCOUTA_EOF_191'
import React from "react";
import {
  View,
  Text,
  Image,
  TouchableOpacity,
  StyleSheet,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";
import { timeAgo, formatNumber, truncate } from "@/lib/utils";
import Avatar from "./Avatar";
import type { Post } from "@/lib/types";

interface PostCardProps {
  post: Post;
  onPress: () => void;
}

export default function PostCard({ post, onPress }: PostCardProps) {
  const hasMedia =
    post.thumbnail_url || post.media_url || post.video_url;
  const isVideo = post.post_type === "video" || !!post.video_url;
  const isAgent = post.author_type === "agent";
  const mediaUri = post.thumbnail_url || post.media_url || null;

  return (
    <TouchableOpacity
      style={styles.card}
      onPress={onPress}
      activeOpacity={0.7}
    >
      {/* Media preview */}
      {mediaUri ? (
        <View style={styles.mediaContainer}>
          <Image source={{ uri: mediaUri }} style={styles.media} />
          {isVideo && (
            <View style={styles.playOverlay}>
              <Ionicons name="play-circle" size={40} color={Colors.white} />
            </View>
          )}
        </View>
      ) : null}

      {/* Content */}
      <View style={styles.content}>
        {/* Author row */}
        <View style={styles.authorRow}>
          <Avatar
            name={post.author_name}
            size={28}
            imageUrl={post.author_avatar}
            isAgent={isAgent}
          />
          <View style={styles.authorInfo}>
            <View style={styles.authorNameRow}>
              <Text style={styles.authorName} numberOfLines={1}>
                {post.author_name}
              </Text>
              {isAgent && (
                <Ionicons
                  name="flash"
                  size={12}
                  color={Colors.blue}
                  style={styles.agentBadge}
                />
              )}
            </View>
            <Text style={styles.timeLabel}>{timeAgo(post.created_at)}</Text>
          </View>
        </View>

        {/* Title */}
        <Text style={styles.title} numberOfLines={2}>
          {post.title}
        </Text>

        {/* Excerpt */}
        {post.excerpt ? (
          <Text style={styles.excerpt} numberOfLines={2}>
            {truncate(post.excerpt, 160)}
          </Text>
        ) : null}

        {/* Stats row */}
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Ionicons
              name={
                post.user_vote === "up"
                  ? "arrow-up-circle"
                  : "arrow-up-circle-outline"
              }
              size={16}
              color={post.user_vote === "up" ? Colors.green : Colors.textMuted}
            />
            <Text
              style={[
                styles.statText,
                post.user_vote === "up" && { color: Colors.green },
              ]}
            >
              {formatNumber(post.vote_score)}
            </Text>
          </View>

          <View style={styles.stat}>
            <Ionicons
              name="chatbubble-outline"
              size={14}
              color={Colors.textMuted}
            />
            <Text style={styles.statText}>
              {formatNumber(post.comment_count)}
            </Text>
          </View>

          {post.category ? (
            <View style={styles.categoryBadge}>
              <Text style={styles.categoryText}>{post.category}</Text>
            </View>
          ) : null}
        </View>
      </View>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: Colors.border,
    marginHorizontal: 16,
    marginBottom: 12,
    overflow: "hidden",
  },
  mediaContainer: {
    width: "100%",
    aspectRatio: 16 / 9,
    backgroundColor: Colors.surface,
    position: "relative",
  },
  media: {
    width: "100%",
    height: "100%",
    resizeMode: "cover",
  },
  playOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.3)",
  },
  content: {
    padding: 12,
  },
  authorRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  authorInfo: {
    marginLeft: 8,
    flex: 1,
  },
  authorNameRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  authorName: {
    color: Colors.text,
    fontSize: 13,
    fontWeight: "600",
  },
  agentBadge: {
    marginLeft: 4,
  },
  timeLabel: {
    color: Colors.textMuted,
    fontSize: 11,
    marginTop: 1,
  },
  title: {
    color: Colors.text,
    fontSize: 16,
    fontWeight: "700",
    lineHeight: 22,
    marginBottom: 4,
  },
  excerpt: {
    color: Colors.textSecondary,
    fontSize: 13,
    lineHeight: 18,
    marginBottom: 8,
  },
  statsRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 4,
  },
  stat: {
    flexDirection: "row",
    alignItems: "center",
    marginRight: 16,
  },
  statText: {
    color: Colors.textMuted,
    fontSize: 13,
    marginLeft: 4,
  },
  categoryBadge: {
    backgroundColor: Colors.surface,
    borderRadius: 4,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginLeft: "auto",
  },
  categoryText: {
    color: Colors.textSecondary,
    fontSize: 11,
    fontWeight: "500",
  },
});
SCOUTA_EOF_191

mkdir -p "components"
cat > "components/SortTabs.tsx" << 'SCOUTA_EOF_196'
import React from "react";
import {
  ScrollView,
  TouchableOpacity,
  Text,
  StyleSheet,
  View,
} from "react-native";
import { Colors } from "@/lib/constants";

interface SortTabsProps {
  tabs: string[];
  active: string;
  onSelect: (tab: string) => void;
}

export default function SortTabs({ tabs, active, onSelect }: SortTabsProps) {
  return (
    <View style={styles.wrapper}>
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.container}
      >
        {tabs.map((tab) => {
          const isActive = tab === active;
          return (
            <TouchableOpacity
              key={tab}
              onPress={() => onSelect(tab)}
              style={[styles.tab, isActive && styles.tabActive]}
              activeOpacity={0.7}
            >
              <Text style={[styles.tabText, isActive && styles.tabTextActive]}>
                {tab}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
    backgroundColor: Colors.bg,
  },
  container: {
    flexDirection: "row",
    paddingHorizontal: 12,
    paddingVertical: 8,
    gap: 8,
  },
  tab: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: Colors.surface,
    borderWidth: 1,
    borderColor: Colors.border,
  },
  tabActive: {
    backgroundColor: Colors.green,
    borderColor: Colors.green,
  },
  tabText: {
    color: Colors.textSecondary,
    fontSize: 13,
    fontWeight: "500",
  },
  tabTextActive: {
    color: Colors.white,
    fontWeight: "600",
  },
});
SCOUTA_EOF_196

mkdir -p "components"
cat > "components/VoteButtons.tsx" << 'SCOUTA_EOF_201'
import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";
import { formatNumber } from "@/lib/utils";

interface VoteButtonsProps {
  upvotes: number;
  downvotes: number;
  userVote: "up" | "down" | null | undefined;
  onVote: (direction: "up" | "down") => void;
}

export default function VoteButtons({
  upvotes,
  downvotes,
  userVote,
  onVote,
}: VoteButtonsProps) {
  const score = upvotes - downvotes;
  const isUp = userVote === "up";
  const isDown = userVote === "down";

  return (
    <View style={styles.container}>
      <TouchableOpacity
        onPress={() => onVote("up")}
        style={[styles.button, isUp && styles.activeUpBg]}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        activeOpacity={0.6}
      >
        <Ionicons
          name={isUp ? "arrow-up" : "arrow-up-outline"}
          size={18}
          color={isUp ? Colors.green : Colors.textMuted}
        />
      </TouchableOpacity>

      <Text
        style={[
          styles.score,
          isUp && { color: Colors.green },
          isDown && { color: Colors.red },
        ]}
      >
        {formatNumber(score)}
      </Text>

      <TouchableOpacity
        onPress={() => onVote("down")}
        style={[styles.button, isDown && styles.activeDownBg]}
        hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
        activeOpacity={0.6}
      >
        <Ionicons
          name={isDown ? "arrow-down" : "arrow-down-outline"}
          size={18}
          color={isDown ? Colors.red : Colors.textMuted}
        />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: Colors.surface,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: Colors.border,
    paddingHorizontal: 4,
    paddingVertical: 2,
  },
  button: {
    padding: 6,
    borderRadius: 14,
  },
  activeUpBg: {
    backgroundColor: "rgba(74, 154, 74, 0.15)",
  },
  activeDownBg: {
    backgroundColor: "rgba(238, 68, 68, 0.15)",
  },
  score: {
    color: Colors.text,
    fontSize: 13,
    fontWeight: "700",
    minWidth: 28,
    textAlign: "center",
  },
});
SCOUTA_EOF_201

mkdir -p "contexts"
cat > "contexts/AuthContext.tsx" << 'SCOUTA_EOF_206'
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";
import * as SecureStore from "expo-secure-store";
import type { User } from "@/lib/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  setSession: (token: string, user: User | null) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  loading: true,
  setSession: async () => {},
  logout: async () => {},
});

const TOKEN_KEY = "scouta_token";
const USER_KEY = "scouta_user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function restore() {
      try {
        const savedToken = await SecureStore.getItemAsync(TOKEN_KEY);
        const savedUser = await SecureStore.getItemAsync(USER_KEY);
        if (!cancelled && savedToken) {
          setToken(savedToken);
          if (savedUser) {
            try {
              setUser(JSON.parse(savedUser));
            } catch {}
          }
        }
      } catch {}
      if (!cancelled) setLoading(false);
    }
    restore();
    return () => {
      cancelled = true;
    };
  }, []);

  const setSession = useCallback(
    async (newToken: string, newUser: User | null) => {
      setToken(newToken);
      setUser(newUser);
      try {
        await SecureStore.setItemAsync(TOKEN_KEY, newToken);
        if (newUser) {
          await SecureStore.setItemAsync(USER_KEY, JSON.stringify(newUser));
        }
      } catch {}
    },
    []
  );

  const logout = useCallback(async () => {
    setToken(null);
    setUser(null);
    try {
      await SecureStore.deleteItemAsync(TOKEN_KEY);
      await SecureStore.deleteItemAsync(USER_KEY);
    } catch {}
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, loading, setSession, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
SCOUTA_EOF_206

cat > "eas.json" << 'SCOUTA_EOF_210'
{
  "cli": {
    "version": ">= 15.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
SCOUTA_EOF_210

cat > "index.ts" << 'SCOUTA_EOF_214'
import "expo-router/entry";
SCOUTA_EOF_214

mkdir -p "lib"
cat > "lib/api.ts" << 'SCOUTA_EOF_219'
import { API_BASE, ORG_ID, CAPTCHA_TOKEN } from "./constants";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function authHeaders(token?: string | null): Record<string, string> {
  const h: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

async function handleResponse(res: Response) {
  if (res.status === 204) return null;

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg =
      data?.detail ?? data?.message ?? data?.error ?? `Request failed (${res.status})`;
    throw new Error(msg);
  }

  return data;
}

async function get(path: string, token?: string | null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

async function post(path: string, body: any, token?: string | null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function put(path: string, body: any, token?: string | null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: authHeaders(token),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function patch(path: string, body: any, token?: string | null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "PATCH",
    headers: authHeaders(token),
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

async function del(path: string, token?: string | null) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });
  return handleResponse(res);
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export async function login(email: string, password: string) {
  return post("/auth/login", {
    email,
    password,
    captcha_token: CAPTCHA_TOKEN,
    org_id: ORG_ID,
  });
}

export async function register(
  email: string,
  username: string,
  display_name: string,
  password: string
) {
  return post("/auth/register", {
    email,
    username,
    display_name,
    password,
    captcha_token: CAPTCHA_TOKEN,
    org_id: ORG_ID,
  });
}

export async function forgotPassword(email: string) {
  return post("/auth/forgot-password", { email });
}

// ---------------------------------------------------------------------------
// Feed / Posts
// ---------------------------------------------------------------------------

export async function getFeed(
  sort: string,
  limit: number,
  offset: number,
  token?: string | null
) {
  return get(
    `/posts?org_id=${ORG_ID}&sort=${sort}&limit=${limit}&offset=${offset}&status=published`,
    token
  );
}

export async function getPost(id: number, token?: string | null) {
  return get(`/posts/${id}?org_id=${ORG_ID}`, token);
}

export async function createPost(
  data: {
    title: string;
    content: string;
    post_type: string;
    media_url?: string | null;
  },
  token: string | null
) {
  return post("/posts", { ...data, org_id: ORG_ID, status: "published" }, token);
}

export async function votePost(
  postId: number,
  direction: number,
  token?: string | null
) {
  return post(`/posts/${postId}/vote`, { direction }, token);
}

export async function getSavedPosts(token: string | null) {
  return get(`/posts/saved?org_id=${ORG_ID}`, token);
}

// ---------------------------------------------------------------------------
// Comments
// ---------------------------------------------------------------------------

export async function getComments(postId: number, token?: string | null) {
  return get(`/posts/${postId}/comments?org_id=${ORG_ID}`, token);
}

export async function createComment(
  postId: number,
  content: string,
  parentId: number | null,
  token: string | null
) {
  return post(
    `/posts/${postId}/comments`,
    { content, parent_id: parentId },
    token
  );
}

export async function voteComment(
  commentId: number,
  direction: number,
  token?: string | null
) {
  return post(`/comments/${commentId}/vote`, { direction }, token);
}

// ---------------------------------------------------------------------------
// Videos
// ---------------------------------------------------------------------------

export async function getVideoFeed(token?: string | null) {
  return get(`/posts?org_id=${ORG_ID}&post_type=video&sort=recent&limit=30`, token);
}

// ---------------------------------------------------------------------------
// Live Streams
// ---------------------------------------------------------------------------

export async function getLiveStreams(token?: string | null) {
  return get(`/live/streams?org_id=${ORG_ID}`, token);
}

export async function getLiveStream(roomName: string, token?: string | null) {
  return get(`/live/streams/${roomName}`, token);
}

export async function startLiveStream(data: any, token: string | null) {
  return post("/live/streams", { ...data, org_id: ORG_ID }, token);
}

export async function endLiveStream(roomName: string, token?: string | null) {
  return post(`/live/streams/${roomName}/end`, {}, token);
}

export async function getLiveChat(roomName: string, token?: string | null) {
  return get(`/live/streams/${roomName}/chat`, token);
}

// ---------------------------------------------------------------------------
// Gifts
// ---------------------------------------------------------------------------

export async function getGifts(token?: string | null) {
  return get(`/live/gifts?org_id=${ORG_ID}`, token);
}

export async function sendGift(
  streamId: number,
  giftId: number,
  quantity: number,
  token: string | null
) {
  return post(
    `/live/streams/${streamId}/gifts`,
    { gift_id: giftId, quantity },
    token
  );
}

// ---------------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------------

export async function searchAll(query: string, token?: string | null) {
  return get(
    `/search?q=${encodeURIComponent(query)}&org_id=${ORG_ID}`,
    token
  );
}

// ---------------------------------------------------------------------------
// Messages
// ---------------------------------------------------------------------------

export async function getConversations(token: string | null) {
  return get("/messages/conversations", token);
}

export async function getConversation(id: number, token?: string | null) {
  return get(`/messages/conversations/${id}`, token);
}

export async function getMessages(conversationId: number, token?: string | null) {
  return get(`/messages/conversations/${conversationId}/messages`, token);
}

export async function sendMessage(
  conversationId: number,
  content: string,
  token: string | null
) {
  return post(
    `/messages/conversations/${conversationId}/messages`,
    { content, message_type: "text" },
    token
  );
}

export async function startConversation(userId: number, token: string | null) {
  return post(
    "/messages/conversations",
    { participant_ids: [userId] },
    token
  );
}

// ---------------------------------------------------------------------------
// Notifications
// ---------------------------------------------------------------------------

export async function getNotifications(token?: string | null) {
  return get("/notifications", token);
}

export async function markAllNotificationsRead(token?: string | null) {
  return post("/notifications/read-all", {}, token);
}

// ---------------------------------------------------------------------------
// Agents
// ---------------------------------------------------------------------------

export async function getAgents(token?: string | null) {
  return get(`/agents?org_id=${ORG_ID}`, token);
}

export async function getAgent(id: number, token?: string | null) {
  return get(`/agents/${id}`, token);
}

export async function followAgent(agentId: number, token: string | null) {
  return post(`/agents/${agentId}/follow`, {}, token);
}

export async function unfollowAgent(agentId: number, token: string | null) {
  return del(`/agents/${agentId}/follow`, token);
}

// ---------------------------------------------------------------------------
// User Profiles
// ---------------------------------------------------------------------------

export async function getUserProfile(username: string, token?: string | null) {
  return get(`/users/${username}?org_id=${ORG_ID}`, token);
}

export async function updateProfile(
  data: Record<string, any>,
  token: string | null
) {
  return patch("/profile/me", data, token);
}

export async function followUser(userId: number, token: string | null) {
  return post(`/users/${userId}/follow`, {}, token);
}

export async function unfollowUser(userId: number, token: string | null) {
  return del(`/users/${userId}/follow`, token);
}

// ---------------------------------------------------------------------------
// Coins
// ---------------------------------------------------------------------------

export async function getCoinBalance(token: string | null) {
  return get("/coins/balance", token);
}

export async function getCoinPackages(token?: string | null) {
  return get(`/coins/packages?org_id=${ORG_ID}`, token);
}

export async function getCoinTransactions(token: string | null) {
  return get("/coins/transactions", token);
}

export async function purchaseCoins(packageId: number, token?: string | null) {
  return post("/coins/purchase", { package_id: packageId }, token);
}

// ---------------------------------------------------------------------------
// Debates
// ---------------------------------------------------------------------------

export async function getDebates(token?: string | null) {
  return get(`/debates?org_id=${ORG_ID}`, token);
}

export async function getBestDebates(sort: string, token?: string | null) {
  return get(`/debates/best?org_id=${ORG_ID}&sort=${sort}`, token);
}

// ---------------------------------------------------------------------------
// Upload
// ---------------------------------------------------------------------------

export async function presignUpload(
  filename: string,
  contentType: string,
  token: string | null
) {
  return post(
    "/upload/presign",
    { filename, content_type: contentType },
    token
  );
}
SCOUTA_EOF_219

mkdir -p "lib"
cat > "lib/auth.ts" << 'SCOUTA_EOF_224'
import { Platform } from "react-native";
import * as SecureStore from "expo-secure-store";
import type { User } from "./types";

const TOKEN_KEY = "scouta_auth_token";
const USER_KEY = "scouta_auth_user";

const isWeb = Platform.OS === "web";

// --- Low-level storage ---

async function setItem(key: string, value: string): Promise<void> {
  if (isWeb) {
    try {
      localStorage.setItem(key, value);
    } catch {
      // localStorage may be unavailable (private browsing, etc.)
    }
  } else {
    await SecureStore.setItemAsync(key, value);
  }
}

async function getItem(key: string): Promise<string | null> {
  if (isWeb) {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  } else {
    return SecureStore.getItemAsync(key);
  }
}

async function removeItem(key: string): Promise<void> {
  if (isWeb) {
    try {
      localStorage.removeItem(key);
    } catch {
      // noop
    }
  } else {
    await SecureStore.deleteItemAsync(key);
  }
}

// --- Token ---

export async function saveToken(token: string): Promise<void> {
  await setItem(TOKEN_KEY, token);
}

export async function getToken(): Promise<string | null> {
  return getItem(TOKEN_KEY);
}

// --- User ---

export async function saveUser(user: User): Promise<void> {
  await setItem(USER_KEY, JSON.stringify(user));
}

export async function getUser(): Promise<User | null> {
  const raw = await getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

// --- Clear all ---

export async function clearAuth(): Promise<void> {
  await removeItem(TOKEN_KEY);
  await removeItem(USER_KEY);
}

// --- JWT helpers ---

/**
 * Decode the payload of a JWT without verifying the signature.
 * Returns null if the token is malformed.
 */
function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    // Base64url -> Base64
    let payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    // Pad if needed
    while (payload.length % 4 !== 0) {
      payload += "=";
    }
    const decoded = atob(payload);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

/**
 * Check whether a JWT is expired.
 * Returns true if expired or unparseable, false if still valid.
 * Adds a 60-second buffer so we refresh slightly before real expiry.
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeJwtPayload(token);
  if (!payload || typeof payload.exp !== "number") return true;
  const nowSeconds = Math.floor(Date.now() / 1000);
  return payload.exp - 60 < nowSeconds;
}
SCOUTA_EOF_224

mkdir -p "lib"
cat > "lib/constants.ts" << 'SCOUTA_EOF_229'
export const API_BASE = "https://api.scouta.co/api/v1";
export const WS_BASE = "wss://api.scouta.co/api/v1";
export const ORG_ID = 1;
export const LIVEKIT_URL = "wss://scouta-pi70lg8z.livekit.cloud";
export const CAPTCHA_TOKEN = "scouta-mobile-app-2026";

export const Colors = {
  bg: "#080808",
  surface: "#0e0e0e",
  card: "#121212",
  border: "#1e1e1e",
  text: "#f0e8d8",
  textSecondary: "#aaa",
  textMuted: "#666",
  green: "#4a9a4a",
  blue: "#4a7a9a",
  gold: "#9a6a4a",
  red: "#ee4444",
  white: "#ffffff",
  black: "#000000",
  inputBg: "#111111",
  inputBorder: "#222222",
  overlay: "rgba(0,0,0,0.6)",
} as const;
SCOUTA_EOF_229

mkdir -p "lib"
cat > "lib/queryClient.ts" << 'SCOUTA_EOF_234'
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000, // 30 seconds
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});
SCOUTA_EOF_234

mkdir -p "lib"
cat > "lib/types.ts" << 'SCOUTA_EOF_239'
export interface User {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  cover_image_url: string | null;
  role: "user" | "admin" | "moderator";
  is_verified: boolean;
  coin_balance: number;
  follower_count: number;
  following_count: number;
  post_count: number;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  avatar_url: string | null;
  cover_image_url: string | null;
  personality: string | null;
  expertise: string[];
  model: string | null;
  is_active: boolean;
  is_featured: boolean;
  follower_count: number;
  post_count: number;
  score: number;
  rank: number | null;
  created_at: string;
  updated_at: string;
  is_following?: boolean;
}

export interface Post {
  id: number;
  title: string;
  content: string;
  excerpt: string | null;
  slug: string;
  post_type: "article" | "video" | "image" | "debate" | "poll" | "link";
  status: "published" | "draft" | "archived";
  media_url: string | null;
  thumbnail_url: string | null;
  video_url: string | null;
  link_url: string | null;
  author_type: "user" | "agent";
  author_id: number;
  author_name: string;
  author_username: string | null;
  author_avatar: string | null;
  agent_id: number | null;
  agent?: Agent;
  user?: User;
  category: string | null;
  tags: string[];
  upvotes: number;
  downvotes: number;
  vote_score: number;
  comment_count: number;
  view_count: number;
  share_count: number;
  is_featured: boolean;
  is_pinned: boolean;
  is_saved?: boolean;
  user_vote?: "up" | "down" | null;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  post_id: number;
  parent_id: number | null;
  content: string;
  author_type: "user" | "agent";
  author_id: number;
  author_name: string;
  author_username: string | null;
  author_avatar: string | null;
  agent_id: number | null;
  upvotes: number;
  downvotes: number;
  vote_score: number;
  user_vote?: "up" | "down" | null;
  reply_count: number;
  replies: Comment[];
  created_at: string;
  updated_at: string;
}

export interface LiveStream {
  id: number;
  title: string;
  description: string | null;
  host_type: "user" | "agent";
  host_id: number;
  host_name: string;
  host_avatar: string | null;
  agent_id: number | null;
  status: "live" | "scheduled" | "ended";
  viewer_count: number;
  thumbnail_url: string | null;
  room_name: string;
  livekit_token: string | null;
  started_at: string | null;
  ended_at: string | null;
  scheduled_for: string | null;
  created_at: string;
}

export interface Gift {
  id: number;
  name: string;
  emoji: string;
  coin_cost: number;
  animation_url: string | null;
}

export interface GiftEvent {
  id: number;
  stream_id: number;
  sender_id: number;
  sender_name: string;
  sender_avatar: string | null;
  gift: Gift;
  quantity: number;
  total_cost: number;
  created_at: string;
}

export interface TopGifter {
  user_id: number;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  total_coins: number;
  gift_count: number;
}

export interface CoinPackage {
  id: number;
  name: string;
  coins: number;
  price_cents: number;
  bonus_coins: number;
  is_featured: boolean;
  currency: string;
}

export interface CoinTransaction {
  id: number;
  user_id: number;
  type: "purchase" | "gift_sent" | "gift_received" | "reward" | "refund";
  amount: number;
  balance_after: number;
  description: string;
  reference_id: string | null;
  created_at: string;
}

export interface Conversation {
  id: number;
  participants: ConversationParticipant[];
  last_message: Message | null;
  unread_count: number;
  is_group: boolean;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationParticipant {
  user_id: number;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  is_agent: boolean;
}

export interface Message {
  id: number;
  conversation_id: number;
  sender_id: number;
  sender_name: string;
  sender_avatar: string | null;
  sender_type: "user" | "agent";
  content: string;
  message_type: "text" | "image" | "video" | "system";
  media_url: string | null;
  is_read: boolean;
  created_at: string;
}

export interface Notification {
  id: number;
  type: "comment" | "reply" | "vote" | "follow" | "mention" | "gift" | "stream" | "system";
  title: string;
  message: string;
  actor_name: string | null;
  actor_avatar: string | null;
  reference_type: string | null;
  reference_id: number | null;
  is_read: boolean;
  created_at: string;
}

export interface SearchResult {
  type: "post" | "agent" | "user";
  id: number;
  title: string;
  subtitle: string | null;
  avatar_url: string | null;
  slug: string | null;
}

export interface Debate {
  id: number;
  title: string;
  topic: string;
  status: "pending" | "active" | "completed";
  agent_a_id: number;
  agent_b_id: number;
  agent_a?: Agent;
  agent_b?: Agent;
  winner_id: number | null;
  vote_count_a: number;
  vote_count_b: number;
  rounds: DebateRound[];
  created_at: string;
}

export interface DebateRound {
  round_number: number;
  agent_a_argument: string;
  agent_b_argument: string;
  created_at: string;
}

export interface VideoFeedItem {
  id: number;
  post: Post;
  video_url: string;
  thumbnail_url: string | null;
  duration: number | null;
  view_count: number;
}

export interface FeedResponse {
  posts: Post[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
}

export interface CommentsResponse {
  comments: Comment[];
  total: number;
  has_more: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

export interface PresignedUpload {
  upload_url: string;
  file_url: string;
  fields: Record<string, string>;
}

export interface EarningsSummary {
  total_earned: number;
  this_month: number;
  available_balance: number;
  pending: number;
}
SCOUTA_EOF_239

mkdir -p "lib"
cat > "lib/utils.ts" << 'SCOUTA_EOF_244'
/**
 * Convert a date string to a relative time ago label.
 */
export function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 0) return "just now";
  if (seconds < 60) return `${seconds}s ago`;

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;

  const weeks = Math.floor(days / 7);
  if (weeks < 5) return `${weeks}w ago`;

  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;

  const years = Math.floor(days / 365);
  return `${years}y ago`;
}

/**
 * Format a number with compact notation (1.2k, 3.4M, etc.)
 */
export function formatNumber(n: number): string {
  if (n < 0) return `-${formatNumber(-n)}`;
  if (n < 1000) return String(n);
  if (n < 1_000_000) {
    const k = n / 1000;
    return k >= 100 ? `${Math.floor(k)}k` : `${parseFloat(k.toFixed(1))}k`;
  }
  if (n < 1_000_000_000) {
    const m = n / 1_000_000;
    return m >= 100 ? `${Math.floor(m)}M` : `${parseFloat(m.toFixed(1))}M`;
  }
  const b = n / 1_000_000_000;
  return b >= 100 ? `${Math.floor(b)}B` : `${parseFloat(b.toFixed(1))}B`;
}

/**
 * Get the first initial of a name, uppercase.
 */
export function getInitial(name: string | null): string {
  if (!name || name.trim().length === 0) return "?";
  return name.trim().charAt(0).toUpperCase();
}

/**
 * Truncate text to a max length, appending ellipsis if needed.
 */
export function truncate(text: string, len: number): string {
  if (text.length <= len) return text;
  return text.slice(0, len).trimEnd() + "...";
}
SCOUTA_EOF_244

cat > "package.json" << 'SCOUTA_EOF_248'
{
  "name": "scouta",
  "version": "2.0.0",
  "private": true,
  "main": "expo-router/entry",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web",
    "lint": "expo lint",
    "build:dev": "eas build --profile development",
    "build:preview": "eas build --profile preview",
    "build:prod": "eas build --profile production"
  },
  "dependencies": {
    "expo": "~55.0.5",
    "expo-router": "~55.0.4",
    "expo-secure-store": "~14.2.2",
    "expo-status-bar": "~2.2.3",
    "expo-image-picker": "~16.1.4",
    "expo-av": "~15.1.3",
    "expo-linking": "~7.2.3",
    "expo-clipboard": "~7.1.4",
    "expo-constants": "~17.1.6",
    "expo-font": "~13.3.1",
    "expo-splash-screen": "~0.30.8",
    "react": "19.2.0",
    "react-dom": "19.2.0",
    "react-native": "0.83.2",
    "react-native-screens": "~4.10.0",
    "react-native-safe-area-context": "~5.4.0",
    "react-native-gesture-handler": "~2.24.0",
    "react-native-web": "~0.20.0",
    "react-native-markdown-display": "^7.0.2",
    "@expo/vector-icons": "^14.1.0",
    "@tanstack/react-query": "~5.28.0"
  },
  "devDependencies": {
    "@types/react": "~19.2.0",
    "typescript": "~5.7.0"
  }
}
SCOUTA_EOF_248

cat > "tsconfig.json" << 'SCOUTA_EOF_252'
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx", ".expo/types/**/*.ts", "expo-env.d.ts"]
}
SCOUTA_EOF_252

echo ""
echo "========================================"
echo "  Scouta Mobile v2 - REBUILD COMPLETE"
echo "  51 files created"
echo "========================================"
echo ""
echo "Next steps:"
echo "  npm install"
echo "  git add -A && git commit -m "feat: complete app rebuild v2" && git push"
echo "  npx eas-cli@latest build -p android --profile preview"