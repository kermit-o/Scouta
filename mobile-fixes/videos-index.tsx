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
  const videoRefs = useRef<Record<number, Video | null>>({});

  async function load() {
    try {
      const data = await getVideoFeed(user?.id);
      const items = data.videos || data || [];
      setVideos(items.filter((v: any) => v.media_url));
    } catch {}
    setLoading(false); setRefreshing(false);
  }

  useEffect(() => { load(); }, []);

  useEffect(() => {
    return () => { Object.values(videoRefs.current).forEach(v => v?.stopAsync?.()); };
  }, []);

  const onViewableItemsChanged = useCallback(({ viewableItems }: any) => {
    if (viewableItems.length > 0) {
      const newIndex = viewableItems[0].index || 0;
      if (newIndex !== activeIndex) videoRefs.current[activeIndex]?.pauseAsync?.();
      setActiveIndex(newIndex);
    }
  }, [activeIndex]);

  async function toggleLike(id: number) {
    const isLiked = liked.has(id);
    setLiked(prev => { const s = new Set(prev); isLiked ? s.delete(id) : s.add(id); return s; });
    await votePost(id, isLiked ? -1 : 1);
  }

  if (loading) return <View style={{ flex: 1, backgroundColor: "#000", alignItems: "center", justifyContent: "center" }}><ActivityIndicator color={Colors.green} size="large" /></View>;

  return (
    <FlatList data={videos} keyExtractor={item => String(item.id)} pagingEnabled snapToInterval={CARD_H}
      decelerationRate="fast" showsVerticalScrollIndicator={false}
      onViewableItemsChanged={onViewableItemsChanged} viewabilityConfig={{ itemVisiblePercentThreshold: 80 }}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} tintColor={Colors.green} />}
      ListEmptyComponent={<View style={{ height: CARD_H, backgroundColor: "#000", alignItems: "center", justifyContent: "center" }}><Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono }}>No videos yet</Text></View>}
      renderItem={({ item, index }) => {
        const author = item.author_display_name || item.author_agent_name || item.author_username || "Unknown";
        return (
          <View style={{ height: CARD_H, backgroundColor: "#000" }}>
            <Video ref={(ref) => { videoRefs.current[index] = ref; }} source={{ uri: item.media_url }}
              style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}
              resizeMode={ResizeMode.CONTAIN} shouldPlay={index === activeIndex} isLooping isMuted={false} />
            <View style={{ position: "absolute", right: 12, bottom: 100, gap: 20, alignItems: "center" }}>
              <TouchableOpacity onPress={() => toggleLike(item.id)} style={{ alignItems: "center" }}>
                <Text style={{ fontSize: 28, color: liked.has(item.id) ? Colors.red : "#fff" }}>{"\u2665"}</Text>
                <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 11 }}>{item.upvote_count || 0}</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={() => router.push(`/(app)/post/${item.id}`)} style={{ alignItems: "center" }}>
                <Text style={{ fontSize: 24, color: "#fff" }}>{"\ud83d\udcac"}</Text>
                <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 11 }}>{item.comment_count || 0}</Text>
              </TouchableOpacity>
            </View>
            <View style={{ position: "absolute", bottom: 20, left: 16, right: 60 }}>
              <Text style={{ color: "#fff", fontWeight: "700", fontSize: 13, fontFamily: Fonts.mono, textShadowColor: "rgba(0,0,0,0.8)", textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 3 }}>@{author}</Text>
              <Text style={{ color: "#fff", fontSize: 15, fontWeight: "600", marginTop: 4, textShadowColor: "rgba(0,0,0,0.8)", textShadowOffset: { width: 0, height: 1 }, textShadowRadius: 3 }}>{item.title}</Text>
            </View>
          </View>
        );
      }}
    />
  );
}
