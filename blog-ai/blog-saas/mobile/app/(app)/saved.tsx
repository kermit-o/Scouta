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
        <Text style={{ color: Colors.text, fontSize: 16, fontFamily: Fonts.serif, lineHeight: 22, marginBottom: 6 }}>
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
        <Text style={{ color: Colors.text, fontSize: 22, fontFamily: Fonts.serif, marginTop: 8 }}>Saved Posts</Text>
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
