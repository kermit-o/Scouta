#!/bin/bash
set -e
echo "=== Scouta Mobile - Complete Fix Script ==="
echo ""

# Ensure we're in the right directory
if [ ! -f "package.json" ]; then
  echo "ERROR: Run this from /workspaces/scouta-mobile"
  exit 1
fi

echo "[1/7] Fixing Feed - show media + add create button..."

cat > "app/(app)/index.tsx" << 'EOF'
import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, RefreshControl, ActivityIndicator, Image } from "react-native";
import { useRouter } from "expo-router";
import { getFeed } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";
import type { Post } from "@/lib/types";

const SORTS = ["recent", "hot", "top", "commented"] as const;

export default function FeedScreen() {
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [sort, setSort] = useState<string>("recent");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [offset, setOffset] = useState(0);

  async function loadPosts(reset = false) {
    const o = reset ? 0 : offset;
    try {
      const data = await getFeed(sort, 20, o);
      const items = Array.isArray(data) ? data : data.posts || [];
      setPosts(prev => reset ? items : [...prev, ...items]);
      setOffset(o + items.length);
    } catch {}
    setLoading(false);
    setRefreshing(false);
  }

  useEffect(() => { setLoading(true); setOffset(0); loadPosts(true); }, [sort]);
  const onRefresh = useCallback(() => { setRefreshing(true); setOffset(0); loadPosts(true); }, [sort]);

  function timeAgo(d: string) {
    const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000);
    if (m < 1) return "now"; if (m < 60) return m + "m";
    const h = Math.floor(m / 60); if (h < 24) return h + "h"; return Math.floor(h / 24) + "d";
  }

  function renderPost({ item }: { item: Post }) {
    const author = item.author_display_name || item.author_agent_name || item.author_username || "Unknown";
    const isAgent = item.author_type === "agent";
    return (
      <TouchableOpacity onPress={() => router.push(`/(app)/post/${item.id}`)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, marginBottom: 8, overflow: "hidden" }}>
        {/* Media */}
        {item.media_url && item.media_type === "image" && (
          <Image source={{ uri: item.media_url }} style={{ width: "100%", height: 200, backgroundColor: "#111" }} resizeMode="cover" />
        )}
        {item.media_url && item.media_type === "video" && (
          <View style={{ width: "100%", height: 200, backgroundColor: "#111", alignItems: "center", justifyContent: "center" }}>
            <Text style={{ fontSize: 40, opacity: 0.5 }}>▶</Text>
          </View>
        )}
        <View style={{ padding: 14 }}>
          <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 8, gap: 6 }}>
            <View style={{ width: 24, height: 24, borderRadius: isAgent ? 4 : 12, backgroundColor: isAgent ? Colors.blue + "33" : Colors.green + "33", alignItems: "center", justifyContent: "center" }}>
              <Text style={{ color: isAgent ? Colors.blue : Colors.green, fontSize: 10, fontWeight: "700" }}>{(author || "?").charAt(0).toUpperCase()}</Text>
            </View>
            <Text style={{ color: isAgent ? Colors.blue : Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>{author}{isAgent ? " ⚡" : ""}</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono, marginLeft: "auto" }}>{timeAgo(item.created_at)}</Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600", lineHeight: 22, marginBottom: 4 }}>{item.title}</Text>
          {item.excerpt ? <Text style={{ color: Colors.textSecondary, fontSize: 13, lineHeight: 18, marginBottom: 8 }} numberOfLines={2}>{item.excerpt}</Text> : null}
          <View style={{ flexDirection: "row", gap: 16 }}>
            <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>▲ {item.upvote_count || 0}</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>💬 {item.comment_count || 0}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 52, paddingHorizontal: 16, paddingBottom: 8, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" }}>
        <View>
          <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>SCOUTA</Text>
          <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "700", marginTop: 4 }}>Feed</Text>
        </View>
        <TouchableOpacity onPress={() => router.push("/(app)/post/create")}
          style={{ backgroundColor: Colors.green, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 4 }}>
          <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 12, fontWeight: "700" }}>+ Write</Text>
        </TouchableOpacity>
      </View>
      <View style={{ flexDirection: "row", paddingHorizontal: 16, marginBottom: 8, gap: 8 }}>
        {SORTS.map(s => (
          <TouchableOpacity key={s} onPress={() => setSort(s)}
            style={{ paddingVertical: 6, paddingHorizontal: 12, backgroundColor: sort === s ? Colors.green + "22" : "transparent", borderWidth: 1, borderColor: sort === s ? Colors.green : Colors.border }}>
            <Text style={{ color: sort === s ? Colors.green : Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono, textTransform: "capitalize" }}>{s}</Text>
          </TouchableOpacity>
        ))}
      </View>
      {loading ? <ActivityIndicator color={Colors.green} style={{ marginTop: 40 }} /> : (
        <FlatList data={posts} keyExtractor={item => String(item.id)} renderItem={renderPost}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={Colors.green} />}
          onEndReached={() => { if (!loading) loadPosts(); }} onEndReachedThreshold={0.5}
          ListEmptyComponent={<Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 60 }}>No posts yet.</Text>} />
      )}
    </View>
  );
}
EOF

echo "[2/7] Fixing Live - add Go Live button..."

cat > "app/(app)/live/index.tsx" << 'EOF'
import { useEffect, useState } from "react";
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator, RefreshControl } from "react-native";
import { useRouter } from "expo-router";
import { getActiveStreams } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";
import type { LiveStream } from "@/lib/types";

export default function LiveScreen() {
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

  function timeAgo(d: string) { const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000); if (m < 1) return "just started"; if (m < 60) return m + "m"; return Math.floor(m / 60) + "h"; }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 52, paddingHorizontal: 16, paddingBottom: 12, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" }}>
        <View>
          <Text style={{ color: Colors.red, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>LIVE</Text>
          <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "700", marginTop: 4 }}>Streams</Text>
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
              style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: item.is_private ? Colors.gold + "44" : Colors.border, padding: 16, marginBottom: 8 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 8 }}>
                <View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: Colors.red }} />
                <Text style={{ color: Colors.red, fontFamily: Fonts.mono, fontSize: 10, letterSpacing: 1 }}>LIVE</Text>
                {item.is_private && <Text style={{ color: Colors.gold, fontFamily: Fonts.mono, fontSize: 9, borderWidth: 1, borderColor: Colors.gold + "44", paddingHorizontal: 6, paddingVertical: 1 }}>🔒 {item.access_type === "paid" ? "🪙 " + item.entry_coin_cost : "PRIVATE"}</Text>}
                <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 10, marginLeft: "auto" }}>{item.viewer_count} viewers</Text>
              </View>
              <Text style={{ color: Colors.text, fontSize: 16, fontWeight: "600", marginBottom: 4 }}>{item.title}</Text>
              <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 11 }}>@{item.host_display_name || item.host_username} · {timeAgo(item.started_at)}</Text>
            </TouchableOpacity>
          )} />
      )}
    </View>
  );
}
EOF

echo "[3/7] Fixing Chat keyboard issue..."

cat > "app/(app)/messages/[convId].tsx" << 'EOF'
import { useEffect, useState, useRef } from "react";
import { View, Text, TextInput, FlatList, TouchableOpacity, KeyboardAvoidingView, Platform } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { getMessages } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts, WS_BASE } from "@/lib/constants";

interface Msg { id: number; sender_id: number; body: string; created_at: string; }

export default function ChatScreen() {
  const { convId } = useLocalSearchParams<{ convId: string }>();
  const { user } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(true);
  const wsRef = useRef<WebSocket | null>(null);
  const listRef = useRef<FlatList>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    (async () => {
      const data = await getMessages(Number(convId));
      setMessages(Array.isArray(data) ? data : []);
      setLoading(false);
      const token = await getToken();
      if (token) {
        const wsUrl = WS_BASE.replace("https://", "wss://") + `/messages/ws/${convId}?token=${token}`;
        ws = new WebSocket(wsUrl);
        wsRef.current = ws;
        ws.onmessage = (e) => {
          const msg = JSON.parse(e.data);
          if (msg.type === "message" || msg.type === "new_message") {
            setMessages(prev => [...prev, { id: msg.id, sender_id: msg.sender_id, body: msg.body, created_at: msg.created_at }]);
          }
        };
      }
    })();
    return () => { ws?.close(); };
  }, [convId]);

  function sendMsg() {
    if (!body.trim() || !wsRef.current) return;
    wsRef.current.send(body.trim());
    setBody("");
  }

  function timeAgo(d: string) { const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000); if (m < 1) return "now"; if (m < 60) return m + "m"; return Math.floor(m / 60) + "h"; }

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 20}>
      <View style={{ paddingTop: 50, paddingHorizontal: 16, paddingBottom: 10, borderBottomWidth: 1, borderBottomColor: Colors.border }}>
        <TouchableOpacity onPress={() => router.back()}>
          <Text style={{ color: Colors.blue, fontFamily: Fonts.mono, fontSize: 12 }}>{"< Back"}</Text>
        </TouchableOpacity>
      </View>
      <FlatList ref={listRef} data={messages} keyExtractor={item => String(item.id)}
        onContentSizeChange={() => listRef.current?.scrollToEnd({ animated: false })}
        contentContainerStyle={{ padding: 12, gap: 6, flexGrow: 1 }}
        renderItem={({ item }) => {
          const isMe = item.sender_id === user?.id;
          return (
            <View style={{ alignItems: isMe ? "flex-end" : "flex-start" }}>
              <View style={{ backgroundColor: isMe ? Colors.green + "33" : Colors.card, borderWidth: 1, borderColor: isMe ? Colors.green + "44" : Colors.border, padding: 10, borderRadius: 12, maxWidth: "75%" }}>
                <Text style={{ color: Colors.text, fontSize: 14 }}>{item.body}</Text>
                <Text style={{ color: Colors.textMuted, fontSize: 9, fontFamily: Fonts.mono, marginTop: 4 }}>{timeAgo(item.created_at)}</Text>
              </View>
            </View>
          );
        }} />
      <View style={{ flexDirection: "row", padding: 8, gap: 8, borderTopWidth: 1, borderTopColor: Colors.border, backgroundColor: Colors.bg }}>
        <TextInput value={body} onChangeText={setBody} onSubmitEditing={sendMsg} placeholder="Type a message..." placeholderTextColor={Colors.textMuted}
          style={{ flex: 1, backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder, color: Colors.text, paddingHorizontal: 12, paddingVertical: 10, borderRadius: 20, fontSize: 14 }} />
        <TouchableOpacity onPress={sendMsg} disabled={!body.trim()}
          style={{ backgroundColor: body.trim() ? Colors.green : Colors.border, borderRadius: 20, width: 40, height: 40, alignItems: "center", justifyContent: "center" }}>
          <Text style={{ color: "#fff", fontSize: 16 }}>↑</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
EOF

echo "[4/7] Fixing Videos - real video playback..."

mkdir -p "app/(app)/videos"
cat > "app/(app)/videos/index.tsx" << 'EOF'
import { useEffect, useState, useRef, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, Dimensions, ActivityIndicator, RefreshControl } from "react-native";
import { Video, ResizeMode } from "expo-av";
import { useRouter } from "expo-router";
import { getVideoFeed, votePost } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Colors, Fonts } from "@/lib/constants";

const { height: SCREEN_H } = Dimensions.get("window");
const CARD_H = SCREEN_H - 80;

interface VideoPost {
  id: number; title: string; excerpt?: string; media_url: string;
  author_display_name?: string; author_agent_name?: string; author_username?: string;
  comment_count: number; upvote_count: number; created_at: string;
}

export default function VideoFeedScreen() {
  const { user } = useAuth();
  const router = useRouter();
  const [videos, setVideos] = useState<VideoPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [liked, setLiked] = useState<Set<number>>(new Set());

  async function load() {
    try {
      const data = await getVideoFeed(user?.id);
      const items = data.videos || data || [];
      setVideos(items.filter((v: any) => v.media_url));
    } catch {}
    setLoading(false); setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  const onViewableItemsChanged = useCallback(({ viewableItems }: any) => {
    if (viewableItems.length > 0) setActiveIndex(viewableItems[0].index || 0);
  }, []);

  async function toggleLike(id: number) {
    const isLiked = liked.has(id);
    setLiked(prev => { const s = new Set(prev); isLiked ? s.delete(id) : s.add(id); return s; });
    await votePost(id, isLiked ? -1 : 1);
  }

  if (loading) return <View style={{ flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center" }}><ActivityIndicator color={Colors.green} size="large" /></View>;

  return (
    <FlatList
      data={videos}
      keyExtractor={item => String(item.id)}
      pagingEnabled
      snapToInterval={CARD_H}
      decelerationRate="fast"
      showsVerticalScrollIndicator={false}
      onViewableItemsChanged={onViewableItemsChanged}
      viewabilityConfig={{ itemVisiblePercentThreshold: 80 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={Colors.green} />}
      ListEmptyComponent={<View style={{ height: CARD_H, backgroundColor: "#000", alignItems: "center", justifyContent: "center" }}><Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono }}>No videos yet</Text></View>}
      renderItem={({ item, index }) => {
        const author = item.author_display_name || item.author_agent_name || item.author_username || "Unknown";
        return (
          <View style={{ height: CARD_H, backgroundColor: "#000" }}>
            {/* Video */}
            <Video
              source={{ uri: item.media_url }}
              style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}
              resizeMode={ResizeMode.CONTAIN}
              shouldPlay={index === activeIndex}
              isLooping
              isMuted={false}
            />
            {/* Right buttons */}
            <View style={{ position: "absolute", right: 12, bottom: 100, gap: 20, alignItems: "center" }}>
              <TouchableOpacity onPress={() => toggleLike(item.id)} style={{ alignItems: "center" }}>
                <Text style={{ fontSize: 28, color: liked.has(item.id) ? Colors.red : "#fff" }}>♥</Text>
                <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 11 }}>{item.upvote_count || 0}</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => router.push(`/(app)/post/${item.id}`)} style={{ alignItems: "center" }}>
                <Text style={{ fontSize: 24, color: "#fff" }}>💬</Text>
                <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 11 }}>{item.comment_count || 0}</Text>
              </TouchableOpacity>
              <TouchableOpacity style={{ alignItems: "center" }}>
                <Text style={{ fontSize: 24, color: "#fff" }}>↗</Text>
              </TouchableOpacity>
            </View>
            {/* Bottom info */}
            <View style={{ position: "absolute", bottom: 20, left: 16, right: 60 }}>
              <Text style={{ color: "#fff", fontWeight: "700", fontSize: 13, fontFamily: Fonts.mono }}>@{author}</Text>
              <Text style={{ color: "#fff", fontSize: 15, fontWeight: "600", marginTop: 4 }}>{item.title}</Text>
            </View>
          </View>
        );
      }}
    />
  );
}
EOF

echo "[5/7] Adding expo-av dependency..."
# Check if expo-av is in package.json, add if not
if ! grep -q "expo-av" package.json; then
  sed -i '/"@expo\/vector-icons"/i\    "expo-av": "~55.0.9",' package.json
fi

echo "[6/7] Adding getVideoFeed + startStream to api.ts..."
if ! grep -q "getVideoFeed" lib/api.ts; then
cat >> lib/api.ts << 'APIEOF'

export async function getVideoFeed(userId?: number, limit = 50, offset = 0) {
  let url = `/videos/feed?limit=${limit}&offset=${offset}&language=en`;
  if (userId) url += `&user_id=${userId}`;
  const res = await apiFetch(url);
  return res.json();
}

export async function startStream(title: string, description: string, opts: any = {}) {
  const res = await apiFetch("/live/start", {
    method: "POST",
    body: JSON.stringify({ title, description, ...opts }),
  });
  return res.json();
}

export async function presignUpload(filename: string, contentType: string, sizeBytes: number) {
  const res = await apiFetch("/upload/presign", {
    method: "POST",
    body: JSON.stringify({ filename, content_type: contentType, size_bytes: sizeBytes }),
  });
  return res.json();
}
APIEOF
fi

echo "[7/7] Fixing CAPTCHA token in api.ts..."
sed -i 's/cf_turnstile_token: ""/cf_turnstile_token: "scouta-mobile-app-2026"/g' lib/api.ts

echo ""
echo "========================================"
echo "  ALL FIXES APPLIED!"
echo "========================================"
echo ""
echo "Changes:"
echo "  1. Feed: shows images/videos + '+ Write' button"
echo "  2. Live: 'Go Live' button for authenticated users"
echo "  3. Chat: keyboard no longer covers input"
echo "  4. Videos: real video playback with expo-av"
echo "  5. expo-av added to dependencies"
echo "  6. New API functions (getVideoFeed, startStream, presignUpload)"
echo "  7. CAPTCHA bypass token fixed"
echo ""
echo "Next steps:"
echo "  rm -rf node_modules package-lock.json"
echo "  npm install"
echo "  git add -A && git commit -m 'fix: all mobile issues' && git push"
echo "  npx eas-cli@latest build -p android --profile preview"
