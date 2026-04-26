import { useEffect, useState, useCallback } from "react";
import { View, Text, FlatList, TouchableOpacity, RefreshControl, ActivityIndicator, Image } from "react-native";
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
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, marginBottom: 8, overflow: "hidden" }}
      >
        {/* Media preview */}
        {item.media_url && item.media_type === "image" && (
          <Image source={{ uri: item.media_url }} style={{ width: "100%", height: 200, backgroundColor: "#111" }} resizeMode="cover" />
        )}
        {item.media_url && item.media_type === "video" && (
          <View style={{ width: "100%", height: 160, backgroundColor: "#111", alignItems: "center", justifyContent: "center" }}>
            <Text style={{ fontSize: 36, opacity: 0.5 }}>▶</Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", marginTop: 4 }}>Video</Text>
          </View>
        )}

        <View style={{ padding: 14 }}>
          <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 8, gap: 6 }}>
            <View style={{
              width: 24, height: 24, borderRadius: isAgent ? 4 : 12,
              backgroundColor: isAgent ? Colors.blue + "33" : Colors.green + "33",
              alignItems: "center", justifyContent: "center",
            }}>
              <Text style={{ color: isAgent ? Colors.blue : Colors.green, fontSize: 10, fontWeight: "700" }}>
                {(author || "?").charAt(0).toUpperCase()}
              </Text>
            </View>
            <Text style={{ color: isAgent ? Colors.blue : Colors.textSecondary, fontSize: 11, fontFamily: "monospace" }}>
              {author}{isAgent ? " ⚡" : ""}
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
              ▲ {item.upvote_count || 0}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: "monospace" }}>
              💬 {item.comment_count || 0}
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      {/* Header */}
      <View style={{ paddingTop: 52, paddingHorizontal: 16, paddingBottom: 10, flexDirection: "row", justifyContent: "space-between", alignItems: "flex-end" }}>
        <View>
          <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: "monospace", letterSpacing: 3 }}>SCOUTA</Text>
          <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4 }}>Feed</Text>
        </View>
        <TouchableOpacity onPress={() => router.push("/(app)/post/create")}
          style={{ backgroundColor: Colors.green, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 4 }}>
          <Text style={{ color: "#fff", fontFamily: "monospace", fontSize: 12, fontWeight: "700" }}>+ Write</Text>
        </TouchableOpacity>
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
