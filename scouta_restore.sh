#!/bin/bash
set -e
echo "=== Restoring Scouta Mobile (pre-rebuild + fixes) ==="

# Clean current app code
rm -rf app lib contexts components hooks

cat > ".easignore" << 'RESTORE_EOF_74961'
node_modules
.expo
dist
.git
*.log
android
ios

# Exclude everything outside mobile (monorepo siblings)
../api
../frontend
../web
../templates
../../backend
../../core
../../diet_ai
../../forge_saas
../../solva
../../FO
../../app
RESTORE_EOF_74961

cat > ".gitignore" << 'RESTORE_EOF_95855'
node_modules/
.expo/
dist/
android/
ios/
*.log
RESTORE_EOF_95855

cat > "app.json" << 'RESTORE_EOF_2945'
{
  "expo": {
    "name": "Scouta",
    "slug": "scouta",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "dark",
    "scheme": "scouta",
    "splash": {
      "image": "./assets/splash-icon.png",
      "resizeMode": "contain",
      "backgroundColor": "#080808"
    },
    "ios": {
      "newArchEnabled": false,
      "supportsTablet": true,
      "bundleIdentifier": "co.scouta.app"
    },
    "android": {
      "newArchEnabled": false,
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#080808"
      },
      "package": "co.scouta.app"
    },
    "web": {
      "bundler": "metro",
      "favicon": "./assets/favicon.png"
    },
    "plugins": [
      "expo-router",
      "expo-secure-store",
      "expo-font",
      "expo-image-picker"
    ]
  }
}
RESTORE_EOF_2945

mkdir -p "app/(app)"
cat > "app/(app)/_layout.tsx" << 'RESTORE_EOF_63037'
import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { Colors } from "@/lib/constants";

export default function AppLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: { backgroundColor: Colors.bg, borderTopColor: Colors.border, borderTopWidth: 1 },
        tabBarActiveTintColor: Colors.green,
        tabBarInactiveTintColor: Colors.textMuted,
        tabBarLabelStyle: { fontSize: 10, fontFamily: "monospace" },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{ title: "Feed", tabBarIcon: ({ color, size }) => <Ionicons name="home-outline" size={size} color={color} /> }}
      />
      <Tabs.Screen
        name="live/index"
        options={{ title: "Live", tabBarIcon: ({ color, size }) => <Ionicons name="radio-outline" size={size} color={color} /> }}
      />
      <Tabs.Screen
        name="search"
        options={{ title: "Search", tabBarIcon: ({ color, size }) => <Ionicons name="search-outline" size={size} color={color} /> }}
      />
      <Tabs.Screen
        name="messages/index"
        options={{ title: "Messages", tabBarIcon: ({ color, size }) => <Ionicons name="chatbubble-outline" size={size} color={color} /> }}
      />
      <Tabs.Screen
        name="profile/index"
        options={{ title: "Profile", tabBarIcon: ({ color, size }) => <Ionicons name="person-outline" size={size} color={color} /> }}
      />

      {/* Hidden screens */}
      <Tabs.Screen name="post/[id]" options={{ href: null }} />
      <Tabs.Screen name="post/create" options={{ href: null }} />
      <Tabs.Screen name="live/[roomName]" options={{ href: null }} />
      <Tabs.Screen name="agents/index" options={{ href: null }} />
      <Tabs.Screen name="agents/[id]" options={{ href: null }} />
      <Tabs.Screen name="messages/[convId]" options={{ href: null }} />
      <Tabs.Screen name="notifications" options={{ href: null }} />
      <Tabs.Screen name="profile/edit" options={{ href: null }} />
      <Tabs.Screen name="profile/[username]" options={{ href: null }} />
      <Tabs.Screen name="coins/index" options={{ href: null }} />
      <Tabs.Screen name="saved" options={{ href: null }} />
    </Tabs>
  );
}
RESTORE_EOF_63037

mkdir -p "app/(app)/agents"
cat > "app/(app)/agents/[id].tsx" << 'RESTORE_EOF_81793'
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
RESTORE_EOF_81793

mkdir -p "app/(app)/agents"
cat > "app/(app)/agents/index.tsx" << 'RESTORE_EOF_46058'
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
                {(item.display_name || "?").charAt(0).toUpperCase()}
              </Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ color: Colors.text, fontSize: 15, fontWeight: "600" }} numberOfLines={1}>
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
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Leaderboard</Text>
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
RESTORE_EOF_46058

mkdir -p "app/(app)/coins"
cat > "app/(app)/coins/index.tsx" << 'RESTORE_EOF_9373'
import { useEffect, useState, useCallback } from "react";
import {
  View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl, ScrollView,
} from "react-native";
import { useRouter } from "expo-router";
import { getCoinBalance, getCoinPackages, getCoinTransactions, getEarnings, purchaseCoins } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { CoinPackage } from "@/lib/types";

interface Transaction {
  id: number;
  type: string;
  amount: number;
  description: string;
  created_at: string;
}

export default function CoinWalletScreen() {
  const router = useRouter();
  const [balance, setBalance] = useState(0);
  const [earnings, setEarnings] = useState<any>(null);
  const [packages, setPackages] = useState<CoinPackage[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      const [balData, pkgData, txData, earnData] = await Promise.all([
        getCoinBalance(),
        getCoinPackages(),
        getCoinTransactions(),
        getEarnings(),
      ]);
      setBalance(balData?.balance ?? balData?.coins ?? 0);
      setPackages(Array.isArray(pkgData) ? pkgData : pkgData.packages || []);
      setTransactions(Array.isArray(txData) ? txData : txData.transactions || []);
      setEarnings(earnData);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, []);

  async function handleBuy(pkg: CoinPackage) {
    try {
      await purchaseCoins(pkg.id);
      load();
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

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600", marginTop: 8 }}>Coin Wallet</Text>
      </View>

      <ScrollView
        contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
      >
        {/* Balance card */}
        <View style={{
          backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.gold + "44",
          padding: 20, alignItems: "center", marginBottom: 20,
        }}>
          <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 4 }}>BALANCE</Text>
          <Text style={{ color: Colors.gold, fontSize: 36, fontFamily: Fonts.mono, fontWeight: "700" }}>{balance}</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>coins</Text>
        </View>

        {/* Earnings summary */}
        {earnings ? (
          <View style={{
            backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
            padding: 16, marginBottom: 20,
          }}>
            <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 8 }}>EARNINGS</Text>
            <Text style={{ color: Colors.text, fontSize: 13, fontFamily: Fonts.mono }}>
              Total: {earnings.total_earned ?? 0} coins
            </Text>
          </View>
        ) : null}

        {/* Packages */}
        {packages.length > 0 ? (
          <View style={{ marginBottom: 20 }}>
            <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 8 }}>BUY COINS</Text>
            {packages.map((pkg) => (
              <TouchableOpacity
                key={pkg.id}
                onPress={() => handleBuy(pkg)}
                style={{
                  backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
                  padding: 14, marginBottom: 6,
                  flexDirection: "row", justifyContent: "space-between", alignItems: "center",
                }}
              >
                <View>
                  <Text style={{ color: Colors.text, fontSize: 16, fontFamily: Fonts.mono, fontWeight: "700" }}>
                    {pkg.coins} coins
                  </Text>
                </View>
                <View style={{
                  backgroundColor: Colors.gold + "22", borderWidth: 1, borderColor: Colors.gold,
                  paddingHorizontal: 12, paddingVertical: 6,
                }}>
                  <Text style={{ color: Colors.gold, fontSize: 12, fontFamily: Fonts.mono, fontWeight: "700" }}>
                    ${(pkg.price_cents / 100).toFixed(2)}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        ) : null}

        {/* Transaction history */}
        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 8 }}>HISTORY</Text>
        {transactions.length > 0 ? (
          transactions.map((tx) => (
            <View
              key={tx.id}
              style={{
                backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
                padding: 12, marginBottom: 6,
              }}
            >
              <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <Text style={{
                  color: tx.amount > 0 ? Colors.green : Colors.red,
                  fontSize: 14, fontFamily: Fonts.mono, fontWeight: "700",
                }}>
                  {tx.amount > 0 ? "+" : ""}{tx.amount}
                </Text>
                <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>{timeAgo(tx.created_at)}</Text>
              </View>
              <Text style={{ color: Colors.textSecondary, fontSize: 12 }}>{tx.description}</Text>
            </View>
          ))
        ) : (
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 20 }}>
            No transactions yet.
          </Text>
        )}
      </ScrollView>
    </View>
  );
}
RESTORE_EOF_9373

mkdir -p "app/(app)"
cat > "app/(app)/index.tsx" << 'RESTORE_EOF_36157'
import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, RefreshControl, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { getFeed } from "@/lib/api";
import { Colors } from "@/lib/constants";
import type { Post } from "@/lib/types";

const SORTS = ["recent", "hot", "top", "commented"] as const;

export default function FeedScreen() {
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [sort, setSort] = useState<string>("recent");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  async function loadPosts(reset = false) {
    const newOffset = reset ? 0 : offset;
    try {
      const data = await getFeed(sort, 20, newOffset);
      const items = Array.isArray(data) ? data : data.posts || [];
      if (reset) {
        setPosts(items);
      } else {
        setPosts(prev => [...prev, ...items]);
      }
      setHasMore(items.length >= 20);
      setOffset(newOffset + items.length);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => {
    setLoading(true);
    setOffset(0);
    loadPosts(true);
  }, [sort]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setOffset(0);
    loadPosts(true);
  }, [sort]);

  function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "now";
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h / 24)}d`;
  }

  function renderPost({ item }: { item: Post }) {
    const author = item.author_display_name || item.author_agent_name || item.author_username || "Unknown";
    const isAgent = item.author_type === "agent";

    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/post/${item.id}`)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 16, marginBottom: 8 }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 8, gap: 6 }}>
          <View style={{
            width: 24, height: 24, borderRadius: isAgent ? 4 : 12,
            backgroundColor: isAgent ? Colors.blue + "33" : Colors.green + "33",
            alignItems: "center", justifyContent: "center",
          }}>
            <Text style={{ color: isAgent ? Colors.blue : Colors.green, fontSize: 10, fontWeight: "700" }}>
              {author.charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={{ color: isAgent ? Colors.blue : Colors.textSecondary, fontSize: 11, fontFamily: "monospace" }}>
            {author}{isAgent ? " \u26A1" : ""}
          </Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", marginLeft: "auto" }}>
            {timeAgo(item.created_at)}
          </Text>
        </View>

        <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600", lineHeight: 22, marginBottom: 6 }}>
          {item.title}
        </Text>

        {item.excerpt ? (
          <Text style={{ color: Colors.textSecondary, fontSize: 13, lineHeight: 18, marginBottom: 10 }} numberOfLines={2}>
            {item.excerpt}
          </Text>
        ) : null}

        <View style={{ flexDirection: "row", gap: 16 }}>
          <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: "monospace" }}>
            {item.upvote_count || 0} votes
          </Text>
          <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: "monospace" }}>
            {item.comment_count || 0} comments
          </Text>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: "monospace", letterSpacing: 3 }}>SCOUTA</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Feed</Text>
      </View>

      {/* Sort tabs */}
      <View style={{ flexDirection: "row", paddingHorizontal: 16, marginBottom: 8, gap: 8 }}>
        {SORTS.map(s => (
          <TouchableOpacity
            key={s}
            onPress={() => setSort(s)}
            style={{
              paddingVertical: 6, paddingHorizontal: 12,
              backgroundColor: sort === s ? Colors.green + "22" : "transparent",
              borderWidth: 1, borderColor: sort === s ? Colors.green : Colors.border,
            }}
          >
            <Text style={{
              color: sort === s ? Colors.green : Colors.textMuted,
              fontSize: 11, fontFamily: "monospace", textTransform: "capitalize",
            }}>
              {s}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Posts list */}
      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={posts}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderPost}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          onEndReached={() => { if (hasMore && !loading) loadPosts(); }}
          onEndReachedThreshold={0.5}
          ListEmptyComponent={
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace", textAlign: "center", marginTop: 60 }}>
              No posts yet.
            </Text>
          }
        />
      )}
    </View>
  );
}
RESTORE_EOF_36157

mkdir -p "app/(app)/live"
cat > "app/(app)/live/[roomName].tsx" << 'RESTORE_EOF_83187'
import { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, ActivityIndicator } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { joinStream } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";

export default function LiveRoomScreen() {
  const { roomName } = useLocalSearchParams<{ roomName: string }>();
  const router = useRouter();
  const [status, setStatus] = useState<"connecting" | "connected" | "error">("connecting");
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const result = await joinStream(roomName);
        if (result.status === 200 && result.data?.token) {
          setToken(result.data.token);
          setStatus("connected");
        } else {
          setError(result.data?.detail || "Failed to join stream");
          setStatus("error");
        }
      } catch {
        setError("Network error");
        setStatus("error");
      }
    })();
  }, [roomName]);

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12, flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
          <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: status === "connected" ? Colors.green : Colors.red }} />
          <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>
            {status === "connecting" ? "Connecting..." : status === "connected" ? "Live" : "Disconnected"}
          </Text>
        </View>
      </View>

      {/* Room name */}
      <View style={{ paddingHorizontal: 16, marginBottom: 16 }}>
        <Text style={{ color: Colors.text, fontSize: 20, fontWeight: "600" }}>{roomName}</Text>
      </View>

      {/* Status area */}
      {status === "connecting" ? (
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
          <ActivityIndicator color={Colors.green} size="large" />
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, marginTop: 12 }}>
            Connecting to stream...
          </Text>
        </View>
      ) : status === "error" ? (
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center", paddingHorizontal: 32 }}>
          <Text style={{ color: Colors.red, fontSize: 13, fontFamily: Fonts.mono, textAlign: "center" }}>{error}</Text>
          <TouchableOpacity
            onPress={() => router.back()}
            style={{ marginTop: 16, paddingVertical: 8, paddingHorizontal: 20, borderWidth: 1, borderColor: Colors.border }}
          >
            <Text style={{ color: Colors.textSecondary, fontSize: 12, fontFamily: Fonts.mono }}>Go back</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={{ flex: 1 }}>
          {/* Video placeholder */}
          <View style={{
            marginHorizontal: 16, height: 200, backgroundColor: Colors.card,
            borderWidth: 1, borderColor: Colors.border,
            justifyContent: "center", alignItems: "center", marginBottom: 16,
          }}>
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono }}>
              Video stream area
            </Text>
          </View>

          {/* Chat messages area */}
          <View style={{
            flex: 1, marginHorizontal: 16, backgroundColor: Colors.card,
            borderWidth: 1, borderColor: Colors.border, padding: 12, marginBottom: 12,
          }}>
            <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 8 }}>
              CHAT
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono }}>
              Chat messages will appear here...
            </Text>
          </View>

          {/* Gift button */}
          <View style={{ paddingHorizontal: 16, paddingBottom: 16 }}>
            <TouchableOpacity
              style={{
                backgroundColor: Colors.gold + "22", borderWidth: 1, borderColor: Colors.gold,
                paddingVertical: 12, alignItems: "center",
              }}
            >
              <Text style={{ color: Colors.gold, fontSize: 13, fontFamily: Fonts.mono, fontWeight: "700" }}>
                Send Gift
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}
RESTORE_EOF_83187

mkdir -p "app/(app)/live"
cat > "app/(app)/live/index.tsx" << 'RESTORE_EOF_5990'
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
RESTORE_EOF_5990

mkdir -p "app/(app)/messages"
cat > "app/(app)/messages/[convId].tsx" << 'RESTORE_EOF_18322'
import { useEffect, useState, useRef } from "react";
import {
  View, Text, FlatList, TextInput, TouchableOpacity,
  ActivityIndicator, KeyboardAvoidingView, Platform,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getMessages, sendMessage } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";
import type { Message } from "@/lib/types";

export default function ChatScreen() {
  const { convId } = useLocalSearchParams<{ convId: string }>();
  const router = useRouter();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const listRef = useRef<FlatList>(null);

  const conversationId = Number(convId);

  async function load() {
    try {
      const data = await getMessages(conversationId);
      const items = Array.isArray(data) ? data : data.messages || [];
      setMessages(items);
    } catch {}
    setLoading(false);
  }

  useEffect(() => { load(); }, [convId]);

  async function handleSend() {
    if (!text.trim() || sending) return;
    setSending(true);
    try {
      await sendMessage(conversationId, text.trim());
      setText("");
      await load();
    } catch {}
    setSending(false);
  }

  function timeStr(dateStr: string) {
    const d = new Date(dateStr);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function renderMessage({ item }: { item: Message }) {
    const isMe = user && item.sender_id === user.id;
    return (
      <View style={{
        alignSelf: isMe ? "flex-end" : "flex-start",
        maxWidth: "78%", marginBottom: 8,
      }}>
        <View style={{
          backgroundColor: isMe ? Colors.blue + "33" : Colors.card,
          borderWidth: 1, borderColor: isMe ? Colors.blue + "55" : Colors.border,
          paddingHorizontal: 12, paddingVertical: 8,
        }}>
          <Text style={{ color: Colors.text, fontSize: 14, lineHeight: 19 }}>{item.body}</Text>
        </View>
        <Text style={{
          color: Colors.textMuted, fontSize: 9, fontFamily: Fonts.mono,
          marginTop: 2, alignSelf: isMe ? "flex-end" : "flex-start",
        }}>
          {timeStr(item.created_at)}
        </Text>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: Colors.bg }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 8, borderBottomWidth: 1, borderColor: Colors.border }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Messages"}</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        ref={listRef}
        data={messages}
        keyExtractor={(item) => String(item.id)}
        renderItem={renderMessage}
        contentContainerStyle={{ paddingHorizontal: 16, paddingVertical: 12 }}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: false })}
        ListEmptyComponent={
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 40 }}>
            No messages yet. Say hello!
          </Text>
        }
      />

      <View style={{
        flexDirection: "row", alignItems: "center", gap: 8,
        paddingHorizontal: 16, paddingVertical: 10,
        borderTopWidth: 1, borderColor: Colors.border, backgroundColor: Colors.card,
      }}>
        <TextInput
          value={text}
          onChangeText={setText}
          placeholder="Type a message..."
          placeholderTextColor={Colors.textMuted}
          style={{
            flex: 1, color: Colors.text, fontSize: 14,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 8,
          }}
        />
        <TouchableOpacity
          onPress={handleSend}
          disabled={sending || !text.trim()}
          style={{
            paddingVertical: 8, paddingHorizontal: 16,
            backgroundColor: text.trim() ? Colors.blue : Colors.border,
          }}
        >
          <Text style={{ color: Colors.text, fontSize: 12, fontFamily: Fonts.mono }}>
            {sending ? "..." : "Send"}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
RESTORE_EOF_18322

mkdir -p "app/(app)/messages"
cat > "app/(app)/messages/index.tsx" << 'RESTORE_EOF_34198'
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
            {(other.display_name || other.username || "?").charAt(0).toUpperCase()}
          </Text>
        </View>

        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
            <Text style={{ color: Colors.text, fontSize: 14, fontWeight: "600" }}>
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
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Messages</Text>
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
RESTORE_EOF_34198

mkdir -p "app/(app)"
cat > "app/(app)/notifications.tsx" << 'RESTORE_EOF_78868'
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
RESTORE_EOF_78868

mkdir -p "app/(app)/post"
cat > "app/(app)/post/[id].tsx" << 'RESTORE_EOF_96267'
import { useEffect, useState, useCallback } from "react";
import {
  View, Text, FlatList, TouchableOpacity, TextInput,
  ActivityIndicator, RefreshControl, KeyboardAvoidingView, Platform,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getPost, getComments, votePost, createComment } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";
import type { Post, Comment } from "@/lib/types";

export default function PostDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();

  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [commentText, setCommentText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [userVote, setUserVote] = useState<1 | -1 | 0>(0);

  const postId = Number(id);

  async function load() {
    try {
      const [postData, commentsData] = await Promise.all([
        getPost(postId),
        getComments(postId),
      ]);
      setPost(postData);
      const items = Array.isArray(commentsData) ? commentsData : commentsData.comments || [];
      setComments(items);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, [id]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, [id]);

  async function handleVote(value: 1 | -1) {
    if (!post) return;
    try {
      await votePost(postId, value);
      setUserVote(prev => (prev === value ? 0 : value));
      load();
    } catch {}
  }

  async function handleAddComment() {
    if (!commentText.trim()) return;
    setSubmitting(true);
    try {
      await createComment(postId, commentText.trim());
      setCommentText("");
      load();
    } catch {}
    setSubmitting(false);
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

  function renderComment({ item }: { item: Comment }) {
    const author = item.author_display_name || item.author_username || "Anon";
    return (
      <View style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 12, marginBottom: 6 }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
          <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>{author}</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>{timeAgo(item.created_at)}</Text>
        </View>
        <Text style={{ color: Colors.text, fontSize: 14, lineHeight: 20 }}>{item.body}</Text>
        <View style={{ flexDirection: "row", gap: 12, marginTop: 8 }}>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>{item.upvotes || 0} up</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>{item.downvotes || 0} down</Text>
        </View>
      </View>
    );
  }

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  if (!post) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 12 }}>Post not found</Text>
      </View>
    );
  }

  const author = post.author_display_name || post.author_agent_name || post.author_username || "Unknown";

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: Colors.bg }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 8 }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={comments}
        keyExtractor={(item) => String(item.id)}
        renderItem={renderComment}
        contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 20 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
        ListHeaderComponent={
          <View style={{ marginBottom: 16 }}>
            <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600", lineHeight: 30, marginBottom: 8 }}>
              {post.title}
            </Text>
            <View style={{ flexDirection: "row", gap: 8, marginBottom: 12 }}>
              <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>{author}</Text>
              <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>{timeAgo(post.created_at)}</Text>
            </View>

            <Text style={{ color: Colors.text, fontSize: 15, lineHeight: 22, marginBottom: 16 }}>
              {post.body_md}
            </Text>

            {/* Vote buttons */}
            <View style={{ flexDirection: "row", gap: 12, marginBottom: 16 }}>
              <TouchableOpacity
                onPress={() => handleVote(1)}
                style={{
                  flexDirection: "row", alignItems: "center", gap: 6,
                  paddingVertical: 6, paddingHorizontal: 12,
                  borderWidth: 1, borderColor: userVote === 1 ? Colors.green : Colors.border,
                  backgroundColor: userVote === 1 ? Colors.green + "22" : "transparent",
                }}
              >
                <Text style={{ color: userVote === 1 ? Colors.green : Colors.textMuted, fontSize: 14 }}>▲</Text>
                <Text style={{ color: userVote === 1 ? Colors.green : Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono }}>
                  {post.upvote_count || 0}
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={() => handleVote(-1)}
                style={{
                  flexDirection: "row", alignItems: "center", gap: 6,
                  paddingVertical: 6, paddingHorizontal: 12,
                  borderWidth: 1, borderColor: userVote === -1 ? Colors.red : Colors.border,
                  backgroundColor: userVote === -1 ? Colors.red + "22" : "transparent",
                }}
              >
                <Text style={{ color: userVote === -1 ? Colors.red : Colors.textMuted, fontSize: 14 }}>▼</Text>
                <Text style={{ color: userVote === -1 ? Colors.red : Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono }}>
                  {post.downvote_count || 0}
                </Text>
              </TouchableOpacity>
            </View>

            <Text style={{ color: Colors.textSecondary, fontSize: 13, fontFamily: Fonts.mono, marginBottom: 8 }}>
              Comments ({post.comment_count || 0})
            </Text>
          </View>
        }
        ListEmptyComponent={
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 20 }}>
            No comments yet.
          </Text>
        }
      />

      {/* Add comment input */}
      <View style={{
        flexDirection: "row", alignItems: "center", gap: 8,
        paddingHorizontal: 16, paddingVertical: 10,
        borderTopWidth: 1, borderColor: Colors.border, backgroundColor: Colors.card,
      }}>
        <TextInput
          value={commentText}
          onChangeText={setCommentText}
          placeholder="Add a comment..."
          placeholderTextColor={Colors.textMuted}
          style={{
            flex: 1, color: Colors.text, fontSize: 14,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 8,
          }}
        />
        <TouchableOpacity
          onPress={handleAddComment}
          disabled={submitting || !commentText.trim()}
          style={{
            paddingVertical: 8, paddingHorizontal: 16,
            backgroundColor: commentText.trim() ? Colors.green : Colors.border,
          }}
        >
          <Text style={{ color: Colors.text, fontSize: 12, fontFamily: Fonts.mono }}>
            {submitting ? "..." : "Send"}
          </Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
RESTORE_EOF_96267

mkdir -p "app/(app)/post"
cat > "app/(app)/post/create.tsx" << 'RESTORE_EOF_80216'
import { useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ActivityIndicator,
  KeyboardAvoidingView, Platform, ScrollView,
} from "react-native";
import { useRouter } from "expo-router";
import { createPost } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";

export default function CreatePostScreen() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handlePublish() {
    if (!title.trim()) { setError("Title is required"); return; }
    if (!body.trim()) { setError("Body is required"); return; }
    setError(null);
    setSubmitting(true);
    try {
      const result = await createPost(title.trim(), body.trim());
      if (result?.id) {
        router.replace(`/(app)/post/${result.id}`);
      } else {
        setError(result?.detail || "Failed to create post");
      }
    } catch {
      setError("Network error");
    }
    setSubmitting(false);
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: Colors.bg }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600", marginTop: 8 }}>New Post</Text>
      </View>

      <ScrollView style={{ flex: 1, paddingHorizontal: 16 }} keyboardShouldPersistTaps="handled">
        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>TITLE</Text>
        <TextInput
          value={title}
          onChangeText={setTitle}
          placeholder="Post title..."
          placeholderTextColor={Colors.textMuted}
          style={{
            color: Colors.text, fontSize: 16, fontWeight: "600",
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10, marginBottom: 16,
          }}
        />

        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>BODY</Text>
        <TextInput
          value={body}
          onChangeText={setBody}
          placeholder="Write your post..."
          placeholderTextColor={Colors.textMuted}
          multiline
          textAlignVertical="top"
          style={{
            color: Colors.text, fontSize: 14, lineHeight: 20,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10, marginBottom: 16,
            minHeight: 200,
          }}
        />

        {error ? (
          <Text style={{ color: Colors.red, fontSize: 12, fontFamily: Fonts.mono, marginBottom: 12 }}>{error}</Text>
        ) : null}

        <TouchableOpacity
          onPress={handlePublish}
          disabled={submitting}
          style={{
            backgroundColor: Colors.green, paddingVertical: 14, alignItems: "center",
            opacity: submitting ? 0.6 : 1,
          }}
        >
          {submitting ? (
            <ActivityIndicator color={Colors.text} size="small" />
          ) : (
            <Text style={{ color: Colors.text, fontSize: 14, fontFamily: Fonts.mono, fontWeight: "700" }}>Publish</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
RESTORE_EOF_80216

mkdir -p "app/(app)/profile"
cat > "app/(app)/profile/[username].tsx" << 'RESTORE_EOF_15870'
import { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, ActivityIndicator, ScrollView } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getUserProfile } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";

interface UserProfile {
  id: number;
  username: string;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  website: string | null;
  post_count?: number;
  comment_count?: number;
  follower_count?: number;
  following_count?: number;
  created_at?: string;
}

export default function UserProfileScreen() {
  const { username } = useLocalSearchParams<{ username: string }>();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const data = await getUserProfile(username);
      setProfile(data);
    } catch {}
    setLoading(false);
  }

  useEffect(() => { load(); }, [username]);

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  if (!profile) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 12 }}>User not found</Text>
      </View>
    );
  }

  const displayName = profile.display_name || profile.username;

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
            width: 64, height: 64, borderRadius: 32, backgroundColor: Colors.green + "33",
            alignItems: "center", justifyContent: "center", marginBottom: 12,
          }}>
            <Text style={{ color: Colors.green, fontSize: 26, fontWeight: "700" }}>
              {(displayName || "?").charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600" }}>{displayName}</Text>
          <Text style={{ color: Colors.textSecondary, fontSize: 12, fontFamily: Fonts.mono, marginTop: 4 }}>@{profile.username}</Text>
        </View>

        {profile.bio ? (
          <Text style={{ color: Colors.textSecondary, fontSize: 14, lineHeight: 20, textAlign: "center", marginBottom: 20 }}>
            {profile.bio}
          </Text>
        ) : null}

        {profile.website ? (
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginBottom: 20 }}>
            {profile.website}
          </Text>
        ) : null}

        {/* Stats */}
        <View style={{
          flexDirection: "row", justifyContent: "space-around",
          backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
          paddingVertical: 16, marginBottom: 24,
        }}>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile.post_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Posts</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile.comment_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Comments</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile.follower_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Followers</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile.following_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Following</Text>
          </View>
        </View>

        <TouchableOpacity
          onPress={() => router.push(`/(app)/messages/index` as any)}
          style={{
            backgroundColor: Colors.blue, paddingVertical: 14, alignItems: "center",
          }}
        >
          <Text style={{ color: Colors.text, fontSize: 14, fontFamily: Fonts.mono, fontWeight: "700" }}>Message</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}
RESTORE_EOF_15870

mkdir -p "app/(app)/profile"
cat > "app/(app)/profile/edit.tsx" << 'RESTORE_EOF_44245'
import { useEffect, useState } from "react";
import {
  View, Text, TextInput, TouchableOpacity, ActivityIndicator,
  KeyboardAvoidingView, Platform, ScrollView,
} from "react-native";
import { useRouter } from "expo-router";
import { getMyProfile, updateProfile } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";

export default function EditProfileScreen() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [website, setWebsite] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await getMyProfile();
        setDisplayName(data.display_name || "");
        setBio(data.bio || "");
        setWebsite(data.website || "");
      } catch {}
      setLoading(false);
    })();
  }, []);

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const result = await updateProfile({
        display_name: displayName.trim(),
        bio: bio.trim(),
        website: website.trim(),
      });
      if (result?.detail) {
        setError(result.detail);
      } else {
        setSuccess(true);
        await refreshUser();
      }
    } catch {
      setError("Network error");
    }
    setSaving(false);
  }

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: Colors.bg }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600", marginTop: 8 }}>Edit Profile</Text>
      </View>

      <ScrollView style={{ flex: 1, paddingHorizontal: 16 }} keyboardShouldPersistTaps="handled">
        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>DISPLAY NAME</Text>
        <TextInput
          value={displayName}
          onChangeText={setDisplayName}
          placeholder="Display name"
          placeholderTextColor={Colors.textMuted}
          style={{
            color: Colors.text, fontSize: 15,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10, marginBottom: 16,
          }}
        />

        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>BIO</Text>
        <TextInput
          value={bio}
          onChangeText={setBio}
          placeholder="Tell us about yourself..."
          placeholderTextColor={Colors.textMuted}
          multiline
          textAlignVertical="top"
          style={{
            color: Colors.text, fontSize: 14, lineHeight: 20,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10, marginBottom: 16,
            minHeight: 100,
          }}
        />

        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>WEBSITE</Text>
        <TextInput
          value={website}
          onChangeText={setWebsite}
          placeholder="https://..."
          placeholderTextColor={Colors.textMuted}
          autoCapitalize="none"
          keyboardType="url"
          style={{
            color: Colors.text, fontSize: 14,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10, marginBottom: 20,
          }}
        />

        {error ? (
          <Text style={{ color: Colors.red, fontSize: 12, fontFamily: Fonts.mono, marginBottom: 12 }}>{error}</Text>
        ) : null}
        {success ? (
          <Text style={{ color: Colors.green, fontSize: 12, fontFamily: Fonts.mono, marginBottom: 12 }}>Profile updated!</Text>
        ) : null}

        <TouchableOpacity
          onPress={handleSave}
          disabled={saving}
          style={{
            backgroundColor: Colors.green, paddingVertical: 14, alignItems: "center",
            opacity: saving ? 0.6 : 1,
          }}
        >
          {saving ? (
            <ActivityIndicator color={Colors.text} size="small" />
          ) : (
            <Text style={{ color: Colors.text, fontSize: 14, fontFamily: Fonts.mono, fontWeight: "700" }}>Save</Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
RESTORE_EOF_44245

mkdir -p "app/(app)/profile"
cat > "app/(app)/profile/index.tsx" << 'RESTORE_EOF_45550'
import { useEffect, useState } from "react";
import { View, Text, TouchableOpacity, ActivityIndicator, ScrollView } from "react-native";
import { useRouter } from "expo-router";
import { getMyProfile } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";

interface Profile {
  id: number;
  username: string;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  website: string | null;
  post_count?: number;
  comment_count?: number;
  follower_count?: number;
  following_count?: number;
  coin_balance?: number;
}

export default function MyProfileScreen() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const data = await getMyProfile();
      setProfile(data);
    } catch {}
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.bg, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator color={Colors.green} />
      </View>
    );
  }

  const displayName = profile?.display_name || user?.display_name || user?.username || "User";
  const username = profile?.username || user?.username || "";

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>SCOUTA</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Profile</Text>
      </View>

      <ScrollView contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}>
        {/* Avatar + name */}
        <View style={{ alignItems: "center", marginBottom: 24, marginTop: 8 }}>
          <View style={{
            width: 64, height: 64, borderRadius: 32, backgroundColor: Colors.green + "33",
            alignItems: "center", justifyContent: "center", marginBottom: 12,
          }}>
            <Text style={{ color: Colors.green, fontSize: 26, fontWeight: "700" }}>
              {(displayName || "?").charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600" }}>{displayName}</Text>
          <Text style={{ color: Colors.textSecondary, fontSize: 12, fontFamily: Fonts.mono, marginTop: 4 }}>@{username}</Text>
        </View>

        {profile?.bio ? (
          <Text style={{ color: Colors.textSecondary, fontSize: 14, lineHeight: 20, textAlign: "center", marginBottom: 20 }}>
            {profile.bio}
          </Text>
        ) : null}

        {/* Stats */}
        <View style={{
          flexDirection: "row", justifyContent: "space-around",
          backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
          paddingVertical: 16, marginBottom: 24,
        }}>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile?.post_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Posts</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile?.comment_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Comments</Text>
          </View>
          <View style={{ alignItems: "center" }}>
            <Text style={{ color: Colors.text, fontSize: 18, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {profile?.follower_count ?? 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginTop: 2 }}>Followers</Text>
          </View>
        </View>

        {/* Action links */}
        {[
          { label: "Edit Profile", route: "/(app)/profile/edit" },
          { label: "Coin Wallet", route: "/(app)/coins" },
          { label: "Saved Posts", route: "/(app)/saved" },
        ].map((item) => (
          <TouchableOpacity
            key={item.label}
            onPress={() => router.push(item.route as any)}
            style={{
              backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border,
              padding: 16, marginBottom: 8, flexDirection: "row", justifyContent: "space-between", alignItems: "center",
            }}
          >
            <Text style={{ color: Colors.text, fontSize: 14, fontFamily: Fonts.mono }}>{item.label}</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 14 }}>{">"}</Text>
          </TouchableOpacity>
        ))}

        <TouchableOpacity
          onPress={logout}
          style={{
            marginTop: 24, paddingVertical: 14, alignItems: "center",
            borderWidth: 1, borderColor: Colors.red + "44",
          }}
        >
          <Text style={{ color: Colors.red, fontSize: 14, fontFamily: Fonts.mono }}>Log out</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}
RESTORE_EOF_45550

mkdir -p "app/(app)"
cat > "app/(app)/saved.tsx" << 'RESTORE_EOF_13491'
import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getSavedPosts } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { Post } from "@/lib/types";

export default function SavedPostsScreen() {
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    try {
      const data = await getSavedPosts();
      const items = Array.isArray(data) ? data : data.posts || [];
      setPosts(items);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, []);

  function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "now";
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h / 24)}d`;
  }

  function renderPost({ item }: { item: Post }) {
    const author = item.author_display_name || item.author_agent_name || item.author_username || "Unknown";
    return (
      <TouchableOpacity
        onPress={() => router.push(`/(app)/post/${item.id}`)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 16, marginBottom: 8 }}
      >
        <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600", lineHeight: 22, marginBottom: 6 }}>
          {item.title}
        </Text>
        {item.excerpt ? (
          <Text style={{ color: Colors.textSecondary, fontSize: 13, lineHeight: 18, marginBottom: 8 }} numberOfLines={2}>
            {item.excerpt}
          </Text>
        ) : null}
        <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
          <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>{author}</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>{timeAgo(item.created_at)}</Text>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: Fonts.mono }}>{"< Back"}</Text>
        </TouchableOpacity>
        <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "600", marginTop: 8 }}>Saved Posts</Text>
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={posts}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderPost}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          ListEmptyComponent={
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>
              No saved posts yet.
            </Text>
          }
        />
      )}
    </View>
  );
}
RESTORE_EOF_13491

mkdir -p "app/(app)"
cat > "app/(app)/search.tsx" << 'RESTORE_EOF_84439'
import { useState, useEffect, useRef } from "react";
import { View, Text, TextInput, FlatList, TouchableOpacity, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { globalSearch } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";

interface SearchResult {
  id: number;
  type: string;
  title?: string;
  username?: string;
  display_name?: string;
  excerpt?: string;
}

export default function SearchScreen() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (!query.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await globalSearch(query.trim());
        const items = Array.isArray(data) ? data : data.results || [];
        setResults(items);
      } catch {
        setResults([]);
      }
      setLoading(false);
      setSearched(true);
    }, 400);

    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [query]);

  function handlePress(item: SearchResult) {
    if (item.type === "post") {
      router.push(`/(app)/post/${item.id}`);
    } else if (item.type === "user" && item.username) {
      router.push(`/(app)/profile/${item.username}`);
    } else if (item.type === "agent") {
      router.push(`/(app)/agents/${item.id}`);
    }
  }

  function renderResult({ item }: { item: SearchResult }) {
    const label = item.type === "post" ? "POST" : item.type === "agent" ? "AGENT" : "USER";
    const color = item.type === "post" ? Colors.green : item.type === "agent" ? Colors.blue : Colors.gold;
    const title = item.title || item.display_name || item.username || `#${item.id}`;

    return (
      <TouchableOpacity
        onPress={() => handlePress(item)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 14, marginBottom: 6 }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <View style={{ backgroundColor: color + "22", paddingHorizontal: 6, paddingVertical: 2 }}>
            <Text style={{ color, fontSize: 9, fontFamily: Fonts.mono, fontWeight: "700" }}>{label}</Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 14, fontWeight: "600", flex: 1 }} numberOfLines={1}>
            {title}
          </Text>
        </View>
        {item.excerpt ? (
          <Text style={{ color: Colors.textMuted, fontSize: 12, lineHeight: 16 }} numberOfLines={2}>
            {item.excerpt}
          </Text>
        ) : null}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>SCOUTA</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4, marginBottom: 12 }}>Search</Text>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search posts, users, agents..."
          placeholderTextColor={Colors.textMuted}
          autoFocus
          style={{
            color: Colors.text, fontSize: 14,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10,
          }}
        />
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 30 }} />
      ) : (
        <FlatList
          data={results}
          keyExtractor={(item, i) => `${item.type}-${item.id}-${i}`}
          renderItem={renderResult}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          ListEmptyComponent={
            searched ? (
              <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 40 }}>
                No results found.
              </Text>
            ) : null
          }
        />
      )}
    </View>
  );
}
RESTORE_EOF_84439

mkdir -p "app/(auth)"
cat > "app/(auth)/_layout.tsx" << 'RESTORE_EOF_26358'
import { Stack } from "expo-router";

export default function AuthLayout() {
  return (
    <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: "#080808" } }} />
  );
}
RESTORE_EOF_26358

mkdir -p "app/(auth)"
cat > "app/(auth)/forgot-password.tsx" << 'RESTORE_EOF_56181'
import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from "react-native";
import { Link } from "expo-router";
import { forgotPassword } from "@/lib/api";
import { Colors } from "@/lib/constants";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!email.trim()) return;
    setLoading(true);
    setError("");
    try {
      await forgotPassword(email.trim());
      setSent(true);
    } catch (e: any) {
      setError(e.message || "Failed to send email");
    }
    setLoading(false);
  }

  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, backgroundColor: Colors.bg }}>
      <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700", marginBottom: 8 }}>Reset Password</Text>
      <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace", marginBottom: 32 }}>
        We'll send you a link to reset your password.
      </Text>

      {sent ? (
        <View>
          <Text style={{ color: Colors.green, fontSize: 13, fontFamily: "monospace", marginBottom: 24 }}>
            Check your email for a reset link.
          </Text>
          <Link href="/(auth)/login">
            <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: "monospace" }}>Back to login</Text>
          </Link>
        </View>
      ) : (
        <>
          {error ? <Text style={{ color: Colors.red, fontSize: 12, fontFamily: "monospace", marginBottom: 12 }}>{error}</Text> : null}
          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="you@email.com"
            placeholderTextColor={Colors.textMuted}
            autoCapitalize="none"
            keyboardType="email-address"
            style={{
              backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
              color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 16,
            }}
          />
          <TouchableOpacity
            onPress={handleSubmit}
            disabled={loading || !email.trim()}
            style={{ backgroundColor: Colors.green, padding: 16, alignItems: "center", opacity: loading ? 0.5 : 1 }}
          >
            {loading ? <ActivityIndicator color="#fff" /> : (
              <Text style={{ color: "#fff", fontSize: 13, fontFamily: "monospace", letterSpacing: 1 }}>SEND RESET LINK</Text>
            )}
          </TouchableOpacity>
          <Link href="/(auth)/login" style={{ marginTop: 16 }}>
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace" }}>Back to login</Text>
          </Link>
        </>
      )}
    </View>
  );
}
RESTORE_EOF_56181

mkdir -p "app/(auth)"
cat > "app/(auth)/login.tsx" << 'RESTORE_EOF_67852'
import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, Linking } from "react-native";
import { useRouter, Link } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

const API = "https://api.scouta.co/api/v1";

export default function LoginScreen() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin() {
    if (!email.trim() || !password.trim()) return;
    setLoading(true);
    setError("");
    const result = await login(email.trim(), password);
    setLoading(false);
    if (result.ok) {
      router.replace("/(app)");
    } else {
      setError(result.error || "Login failed");
    }
  }

  function handleGoogleLogin() {
    Linking.openURL(`${API}/auth/google?redirect_mobile=1`);
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={{ flex: 1, justifyContent: "center", padding: 24 }}>
        <View style={{ alignItems: "center", marginBottom: 40 }}>
          <Text style={{ color: Colors.text, fontSize: 32, fontWeight: "700" }}>SCOUTA</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 3, marginTop: 8 }}>AI DEBATES</Text>
        </View>

        {error ? (
          <Text style={{ color: Colors.red, fontSize: 12, fontFamily: "monospace", textAlign: "center", marginBottom: 16 }}>{error}</Text>
        ) : null}

        <TouchableOpacity onPress={handleGoogleLogin}
          style={{ backgroundColor: "#fff", padding: 14, alignItems: "center", borderRadius: 4, flexDirection: "row", justifyContent: "center", gap: 8, marginBottom: 20 }}>
          <Text style={{ fontSize: 18, fontWeight: "700", color: "#4285F4" }}>G</Text>
          <Text style={{ color: "#333", fontSize: 14, fontWeight: "600" }}>Continue with Google</Text>
        </TouchableOpacity>

        <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 20 }}>
          <View style={{ flex: 1, height: 1, backgroundColor: Colors.border }} />
          <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: "monospace", marginHorizontal: 12 }}>OR</Text>
          <View style={{ flex: 1, height: 1, backgroundColor: Colors.border }} />
        </View>

        <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>EMAIL</Text>
        <TextInput value={email} onChangeText={setEmail} placeholder="you@email.com" placeholderTextColor={Colors.textMuted}
          autoCapitalize="none" keyboardType="email-address"
          style={{ backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder, color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 16 }} />

        <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>PASSWORD</Text>
        <TextInput value={password} onChangeText={setPassword} placeholder="Password" placeholderTextColor={Colors.textMuted} secureTextEntry
          style={{ backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder, color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 8 }} />

        <Link href="/(auth)/forgot-password" asChild>
          <TouchableOpacity style={{ alignSelf: "flex-end", marginBottom: 24 }}>
            <Text style={{ color: Colors.blue, fontSize: 11, fontFamily: "monospace" }}>Forgot password?</Text>
          </TouchableOpacity>
        </Link>

        <TouchableOpacity onPress={handleLogin} disabled={loading || !email.trim() || !password.trim()}
          style={{ backgroundColor: Colors.green, padding: 16, alignItems: "center", opacity: loading || !email.trim() || !password.trim() ? 0.5 : 1 }}>
          {loading ? <ActivityIndicator color="#fff" /> : (
            <Text style={{ color: "#fff", fontSize: 13, fontFamily: "monospace", letterSpacing: 1 }}>SIGN IN</Text>
          )}
        </TouchableOpacity>

        <View style={{ flexDirection: "row", justifyContent: "center", marginTop: 24, gap: 4 }}>
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace" }}>No account?</Text>
          <Link href="/(auth)/register"><Text style={{ color: Colors.green, fontSize: 12, fontFamily: "monospace" }}>Sign up</Text></Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
RESTORE_EOF_67852

mkdir -p "app/(auth)"
cat > "app/(auth)/register.tsx" << 'RESTORE_EOF_18474'
import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useRouter, Link } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function RegisterScreen() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRegister() {
    if (!email.trim() || !password.trim() || !username.trim()) return;
    setLoading(true);
    setError("");
    const result = await register(email.trim(), password, username.trim(), displayName.trim() || undefined);
    setLoading(false);
    if (result.ok) {
      router.replace("/(app)");
    } else {
      setError(result.error || "Registration failed");
    }
  }

  const inputStyle = {
    backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
    color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 16,
  };
  const labelStyle = { color: Colors.textMuted, fontSize: 10, fontFamily: "monospace" as const, letterSpacing: 1, marginBottom: 6 };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={{ flex: 1, justifyContent: "center", padding: 24 }}>
        <View style={{ alignItems: "center", marginBottom: 32 }}>
          <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "700" }}>Create Account</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 2, marginTop: 8 }}>JOIN THE DEBATE</Text>
        </View>

        {error ? (
          <Text style={{ color: Colors.red, fontSize: 12, fontFamily: "monospace", textAlign: "center", marginBottom: 16 }}>{error}</Text>
        ) : null}

        <Text style={labelStyle}>EMAIL</Text>
        <TextInput value={email} onChangeText={setEmail} placeholder="you@email.com" placeholderTextColor={Colors.textMuted} autoCapitalize="none" keyboardType="email-address" style={inputStyle} />

        <Text style={labelStyle}>USERNAME</Text>
        <TextInput value={username} onChangeText={setUsername} placeholder="your_handle" placeholderTextColor={Colors.textMuted} autoCapitalize="none" style={inputStyle} />

        <Text style={labelStyle}>DISPLAY NAME</Text>
        <TextInput value={displayName} onChangeText={setDisplayName} placeholder="Your Name (optional)" placeholderTextColor={Colors.textMuted} style={inputStyle} />

        <Text style={labelStyle}>PASSWORD</Text>
        <TextInput value={password} onChangeText={setPassword} placeholder="Min 6 characters" placeholderTextColor={Colors.textMuted} secureTextEntry style={inputStyle} />

        <TouchableOpacity
          onPress={handleRegister}
          disabled={loading || !email.trim() || !password.trim() || !username.trim()}
          style={{
            backgroundColor: Colors.green, padding: 16, alignItems: "center",
            opacity: loading || !email.trim() || !password.trim() || !username.trim() ? 0.5 : 1,
          }}
        >
          {loading ? <ActivityIndicator color="#fff" /> : (
            <Text style={{ color: "#fff", fontSize: 13, fontFamily: "monospace", letterSpacing: 1 }}>CREATE ACCOUNT</Text>
          )}
        </TouchableOpacity>

        <View style={{ flexDirection: "row", justifyContent: "center", marginTop: 24, gap: 4 }}>
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace" }}>Have an account?</Text>
          <Link href="/(auth)/login">
            <Text style={{ color: Colors.green, fontSize: 12, fontFamily: "monospace" }}>Sign in</Text>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
RESTORE_EOF_18474

mkdir -p "app"
cat > "app/_layout.tsx" << 'RESTORE_EOF_12625'
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AuthProvider } from "@/contexts/AuthContext";
import { View } from "react-native";

export default function RootLayout() {
  return (
    <View style={{ flex: 1, backgroundColor: "#080808" }}>
      <AuthProvider>
        <StatusBar style="light" />
        <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: "#080808" } }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="(auth)" />
          <Stack.Screen name="(app)" />
        </Stack>
      </AuthProvider>
    </View>
  );
}
RESTORE_EOF_12625

mkdir -p "app"
cat > "app/index.tsx" << 'RESTORE_EOF_78755'
import { useEffect } from "react";
import { useRouter } from "expo-router";
import { View, Text, ActivityIndicator } from "react-native";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function SplashScreen() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      // Small delay to ensure navigation is ready
      const timer = setTimeout(() => {
        if (isAuthenticated) {
          router.replace("/(app)");
        } else {
          router.replace("/(auth)/login");
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [loading, isAuthenticated]);

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg, alignItems: "center", justifyContent: "center" }}>
      <Text style={{ color: Colors.text, fontSize: 28, fontWeight: "700", marginBottom: 16 }}>SCOUTA</Text>
      <Text style={{ color: Colors.textMuted, fontSize: 11, letterSpacing: 2, marginBottom: 24 }}>AI DEBATES</Text>
      <ActivityIndicator color={Colors.green} />
    </View>
  );
}
RESTORE_EOF_78755

cat > "babel.config.js" << 'RESTORE_EOF_59119'
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
  };
};
RESTORE_EOF_59119

mkdir -p "contexts"
cat > "contexts/AuthContext.tsx" << 'RESTORE_EOF_39768'
import React, { createContext, useContext, useEffect, useState } from "react";
import { saveToken, getToken, saveUser, getUser, clearAuth } from "@/lib/auth";
import * as api from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>;
  register: (email: string, password: string, username: string, displayName?: string) => Promise<{ ok: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  user: null,
  token: null,
  loading: true,
  isAuthenticated: false,
  login: async () => ({ ok: false }),
  register: async () => ({ ok: false }),
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const storedToken = await getToken();
      if (storedToken) {
        setToken(storedToken);
        try {
          const me = await api.getMe();
          if (me?.id) {
            setUser(me);
            await saveUser(me);
          } else {
            await clearAuth();
          }
        } catch {
          await clearAuth();
        }
      }
      setLoading(false);
    })();
  }, []);

  async function login(email: string, password: string) {
    try {
      const data = await api.login(email, password);
      if (data.access_token) {
        await saveToken(data.access_token);
        setToken(data.access_token);
        const me = await api.getMe();
        if (me?.id) {
          setUser(me);
          await saveUser(me);
        }
        return { ok: true };
      }
      return { ok: false, error: data.detail || "Login failed" };
    } catch (e: any) {
      return { ok: false, error: e.message || "Network error" };
    }
  }

  async function register(email: string, password: string, username: string, displayName?: string) {
    try {
      const data = await api.register(email, password, username, displayName);
      if (data.access_token) {
        await saveToken(data.access_token);
        setToken(data.access_token);
        const me = await api.getMe();
        if (me?.id) {
          setUser(me);
          await saveUser(me);
        }
        return { ok: true };
      }
      return { ok: false, error: data.detail || "Registration failed" };
    } catch (e: any) {
      return { ok: false, error: e.message || "Network error" };
    }
  }

  async function logout() {
    await clearAuth();
    setUser(null);
    setToken(null);
  }

  async function refreshUser() {
    try {
      const me = await api.getMe();
      if (me?.id) {
        setUser(me);
        await saveUser(me);
      }
    } catch {}
  }

  return (
    <AuthContext.Provider
      value={{ user, token, loading, isAuthenticated: !!user, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
RESTORE_EOF_39768

cat > "eas.json" << 'RESTORE_EOF_84139'
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
RESTORE_EOF_84139

cat > "index.ts" << 'RESTORE_EOF_76661'
import "expo-router/entry";
RESTORE_EOF_76661

mkdir -p "lib"
cat > "lib/api.ts" << 'RESTORE_EOF_91313'
import { API_BASE, ORG_ID } from "./constants";
import { getToken } from "./auth";

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = await getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return fetch(`${API_BASE}${path}`, { ...options, headers });
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export async function login(email: string, password: string) {
  const res = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password, cf_turnstile_token: "xPMEvUwAp_EFk7EGkEMJUBm-osAyoLFBPCl9xkzqKkU" }),
  });
  return res.json();
}

export async function register(email: string, password: string, username: string, display_name?: string) {
  const res = await apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, username, display_name: display_name || username, cf_turnstile_token: "xPMEvUwAp_EFk7EGkEMJUBm-osAyoLFBPCl9xkzqKkU" }),
  });
  return res.json();
}

export async function forgotPassword(email: string) {
  const res = await apiFetch("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
  return res.json();
}

export async function getMe() {
  const res = await apiFetch("/auth/me");
  return res.json();
}

// ── Posts ──────────────────────────────────────────────────────────────────────
export async function getFeed(sort = "recent", limit = 20, offset = 0, tag?: string) {
  let url = `/orgs/${ORG_ID}/posts?status=published&sort=${sort}&limit=${limit}&offset=${offset}`;
  if (tag) url += `&tag=${encodeURIComponent(tag)}`;
  const res = await apiFetch(url);
  return res.json();
}

export async function getPost(postId: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}`);
  return res.json();
}

export async function votePost(postId: number, value: 1 | -1) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/vote`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
  return res.json();
}

export async function createPost(title: string, body_md: string, tags?: string[]) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts`, {
    method: "POST",
    body: JSON.stringify({ title, body_md, status: "published", tags: tags || [] }),
  });
  return res.json();
}

export async function savePost(postId: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/save`, { method: "POST" });
  return res.json();
}

export async function unsavePost(postId: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/save`, { method: "DELETE" });
  return res.json();
}

export async function getSavedPosts(limit = 20, offset = 0) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/saved?limit=${limit}&offset=${offset}`);
  return res.json();
}

// ── Comments ──────────────────────────────────────────────────────────────────
export async function getComments(postId: number, limit = 50, offset = 0) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/comments?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function createComment(postId: number, body: string, parentCommentId?: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify({ body, parent_comment_id: parentCommentId || null }),
  });
  return res.json();
}

export async function voteComment(postId: number, commentId: number, value: 1 | -1) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/comments/${commentId}/vote`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
  return res.json();
}

// ── Agents ────────────────────────────────────────────────────────────────────
export async function getLeaderboard(limit = 50) {
  const res = await apiFetch(`/agents/leaderboard?limit=${limit}`);
  return res.json();
}

export async function getAgent(agentId: number) {
  const res = await apiFetch(`/agents/${agentId}`);
  return res.json();
}

export async function followAgent(agentId: number) {
  const res = await apiFetch(`/agents/${agentId}/follow`, { method: "POST" });
  return res.json();
}

export async function unfollowAgent(agentId: number) {
  const res = await apiFetch(`/agents/${agentId}/follow`, { method: "DELETE" });
  return res.json();
}

// ── Profile ───────────────────────────────────────────────────────────────────
export async function getMyProfile() {
  const res = await apiFetch("/profile/me");
  return res.json();
}

export async function getUserProfile(username: string) {
  const res = await apiFetch(`/u/${username}`);
  return res.json();
}

export async function updateProfile(data: Record<string, string>) {
  const res = await apiFetch("/auth/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

// ── Search ────────────────────────────────────────────────────────────────────
export async function globalSearch(q: string) {
  const res = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
  return res.json();
}

// ── Notifications ─────────────────────────────────────────────────────────────
export async function getNotifications(limit = 20, offset = 0) {
  const res = await apiFetch(`/notifications?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function markAllRead() {
  const res = await apiFetch("/notifications/read-all", { method: "POST" });
  return res.json();
}

// ── Messages ──────────────────────────────────────────────────────────────────
export async function getConversations() {
  const res = await apiFetch("/messages/conversations");
  return res.json();
}

export async function getMessages(convId: number, limit = 50) {
  const res = await apiFetch(`/messages/conversations/${convId}/messages?limit=${limit}`);
  return res.json();
}

export async function startConversation(username: string) {
  const res = await apiFetch(`/messages/start/${username}`, { method: "POST" });
  return res.json();
}

export async function sendMessage(convId: number, body: string) {
  const res = await apiFetch(`/messages/conversations/${convId}/messages`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
  return res.json();
}

export async function getUnreadCount() {
  const res = await apiFetch("/messages/unread-count");
  return res.json();
}

// ── Live ──────────────────────────────────────────────────────────────────────
export async function getActiveStreams() {
  const res = await apiFetch("/live/active");
  return res.json();
}

export async function joinStream(roomName: string, password?: string) {
  const res = await apiFetch(`/live/${roomName}/join`, {
    method: "POST",
    body: JSON.stringify(password ? { password } : {}),
  });
  return { status: res.status, data: await res.json() };
}

export async function getGiftCatalog() {
  const res = await apiFetch("/live/gifts/catalog");
  return res.json();
}

export async function sendGift(roomName: string, giftId: number) {
  const res = await apiFetch(`/live/${roomName}/gift`, {
    method: "POST",
    body: JSON.stringify({ gift_id: giftId }),
  });
  return res.json();
}

export async function getTopGifters(roomName: string) {
  const res = await apiFetch(`/live/${roomName}/top-gifters`);
  return res.json();
}

// ── Coins ─────────────────────────────────────────────────────────────────────
export async function getCoinBalance() {
  const res = await apiFetch("/coins/balance");
  return res.json();
}

export async function getCoinPackages() {
  const res = await apiFetch("/coins/packages");
  return res.json();
}

export async function purchaseCoins(packageId: string) {
  const res = await apiFetch("/coins/purchase", {
    method: "POST",
    body: JSON.stringify({ package_id: packageId }),
  });
  return res.json();
}

export async function getCoinTransactions(limit = 20, offset = 0) {
  const res = await apiFetch(`/coins/transactions?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function getEarnings() {
  const res = await apiFetch("/coins/earnings");
  return res.json();
}
RESTORE_EOF_91313

mkdir -p "lib"
cat > "lib/auth.ts" << 'RESTORE_EOF_63604'
import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const TOKEN_KEY = "scouta_jwt";
const USER_KEY = "scouta_user";

const isWeb = Platform.OS === "web";

export async function saveToken(token: string): Promise<void> {
  if (isWeb) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  }
}

export async function getToken(): Promise<string | null> {
  if (isWeb) {
    return localStorage.getItem(TOKEN_KEY);
  }
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function saveUser(user: object): Promise<void> {
  const value = JSON.stringify(user);
  if (isWeb) {
    localStorage.setItem(USER_KEY, value);
  } else {
    await SecureStore.setItemAsync(USER_KEY, value);
  }
}

export async function getUser(): Promise<any | null> {
  const raw = isWeb
    ? localStorage.getItem(USER_KEY)
    : await SecureStore.getItemAsync(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function clearAuth(): Promise<void> {
  if (isWeb) {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } else {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(USER_KEY);
  }
}
RESTORE_EOF_63604

mkdir -p "lib"
cat > "lib/constants.ts" << 'RESTORE_EOF_59621'
export const API_BASE = "https://api.scouta.co/api/v1";
export const WS_BASE = "wss://api.scouta.co/api/v1";
export const ORG_ID = 1;
export const LIVEKIT_URL = "wss://scouta-pi70lg8z.livekit.cloud";

export const Colors = {
  bg: "#080808",
  card: "#121212",
  border: "#1e1e1e",
  text: "#f0e8d8",
  textSecondary: "#888",
  textMuted: "#555",
  green: "#4a9a4a",
  blue: "#4a7a9a",
  gold: "#9a6a4a",
  red: "#e44",
  inputBg: "#111",
  inputBorder: "#222",
} as const;

export const Fonts = {
  mono: "monospace",
} as const;
RESTORE_EOF_59621

mkdir -p "lib"
cat > "lib/types.ts" << 'RESTORE_EOF_60126'
export interface User {
  id: number;
  email: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  is_verified: boolean;
  is_superuser: boolean;
}

export interface Post {
  id: number;
  title: string;
  slug: string;
  body_md: string;
  excerpt: string | null;
  status: string;
  media_url: string | null;
  media_type: string | null;
  author_type: string;
  author_user_id: number | null;
  author_agent_id: number | null;
  author_display_name?: string;
  author_username?: string;
  author_agent_name?: string;
  author_avatar_url?: string;
  upvote_count: number;
  downvote_count: number;
  comment_count: number;
  debate_status: string;
  created_at: string;
  published_at: string | null;
  tags?: string[];
}

export interface Comment {
  id: number;
  body: string;
  author_type: string;
  author_display_name: string | null;
  author_username: string | null;
  author_avatar_url: string | null;
  upvotes: number;
  downvotes: number;
  parent_comment_id: number | null;
  source: string;
  created_at: string;
  replies?: Comment[];
}

export interface Agent {
  id: number;
  display_name: string;
  handle: string;
  bio: string | null;
  topics: string | null;
  style: string | null;
  reputation_score: number;
  is_enabled: boolean;
  total_comments?: number;
  total_upvotes?: number;
  follower_count?: number;
  is_following?: boolean;
}

export interface LiveStream {
  room_name: string;
  title: string;
  viewer_count: number;
  host_username: string;
  host_display_name: string;
  description: string;
  started_at: string;
  is_private: boolean;
  access_type: string;
  entry_coin_cost: number;
}

export interface Gift {
  id: number;
  name: string;
  emoji: string;
  coin_cost: number;
  animation_type: string;
}

export interface CoinPackage {
  id: string;
  coins: number;
  price_cents: number;
}

export interface Conversation {
  id: number;
  other_user: {
    id: number;
    username: string;
    display_name: string;
    avatar_url: string | null;
  };
  last_message_preview: string | null;
  last_message_at: string | null;
  unread: number;
}

export interface Message {
  id: number;
  sender_id: number;
  body: string;
  read: boolean;
  created_at: string;
}

export interface Notification {
  id: number;
  type: string;
  message: string;
  read: boolean;
  post_id: number | null;
  comment_id: number | null;
  created_at: string;
}
RESTORE_EOF_60126

cat > "package.json" << 'RESTORE_EOF_29595'
{
  "name": "scouta-mobile",
  "version": "1.0.0",
  "main": "expo-router/entry",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~55.0.5",
    "expo-router": "~55.0.4",
    "expo-secure-store": "~55.0.8",
    "expo-constants": "~55.0.7",
    "expo-font": "~55.0.4",
    "expo-image-picker": "~55.0.11",
    "expo-splash-screen": "~55.0.10",
    "expo-status-bar": "~55.0.4",
    "expo-linking": "~55.0.7",
    "expo-clipboard": "~55.0.8",
    "react": "19.2.0",
    "react-dom": "19.2.0",
    "react-native": "0.83.2",
    "react-native-screens": "~4.23.0",
    "react-native-safe-area-context": "~5.6.2",
    "react-native-gesture-handler": "~2.30.0",
    "react-native-web": "^0.21.0",
    "react-native-markdown-display": "^7.0.2",
    "@expo/vector-icons": "^15.0.2"
  },
  "devDependencies": {
    "@types/react": "~19.2.2",
    "typescript": "~5.9.2"
  },
  "private": true
}
RESTORE_EOF_29595

cat > "tsconfig.json" << 'RESTORE_EOF_13795'
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
RESTORE_EOF_13795

echo ""
echo "=== Restore complete! ==="
echo "Files restored: 36"
echo ""
echo "Next: npm install && git add -A && git commit -m restore && git push && npx eas-cli@latest build -p android --profile preview"