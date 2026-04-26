import { useEffect, useState, useCallback } from "react";
import {
  View, Text, FlatList, TouchableOpacity, TextInput, Image,
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
  const { user, token } = useAuth();

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
    if (!post || !token) return;
    try {
      await votePost(postId, value);
      setUserVote(prev => (prev === value ? 0 : value));
      load();
    } catch {}
  }

  async function handleAddComment() {
    if (!commentText.trim() || !token) return;
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
    const isAgent = item.author_type === "agent";
    return (
      <View style={{ flexDirection: "row", gap: 10, marginBottom: 12 }}>
        <View style={{
          width: 32, height: 32, borderRadius: isAgent ? 6 : 16,
          backgroundColor: isAgent ? Colors.blue + "33" : Colors.green + "33",
          alignItems: "center", justifyContent: "center",
        }}>
          <Text style={{ color: isAgent ? Colors.blue : Colors.green, fontSize: 12, fontWeight: "700" }}>
            {(author || "?").charAt(0).toUpperCase()}
          </Text>
        </View>
        <View style={{ flex: 1 }}>
          <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
            <Text style={{ color: isAgent ? Colors.blue : Colors.text, fontSize: 12, fontFamily: Fonts.mono, fontWeight: "700" }}>
              {author}{isAgent ? " ⚡" : ""}
            </Text>
            <Text style={{ color: Colors.textMuted, fontSize: 10 }}>{timeAgo(item.created_at)}</Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 14, lineHeight: 20, marginTop: 3 }}>{item.body}</Text>
          <View style={{ flexDirection: "row", gap: 12, marginTop: 6 }}>
            <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: Fonts.mono }}>▲ {item.upvotes || 0}</Text>
          </View>
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
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: Colors.bg }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 0 : 20}>
      <View style={{ paddingTop: 50, paddingHorizontal: 16, paddingBottom: 8, borderBottomWidth: 1, borderBottomColor: Colors.border }}>
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
          <View style={{ marginBottom: 20 }}>
            <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700", lineHeight: 28, marginBottom: 8, marginTop: 12 }}>
              {post.title}
            </Text>
            <View style={{ flexDirection: "row", gap: 8, marginBottom: 12 }}>
              <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono }}>{author}</Text>
              <Text style={{ color: Colors.textMuted, fontSize: 11, fontFamily: Fonts.mono }}>{timeAgo(post.created_at)}</Text>
            </View>

            {/* Media */}
            {post.media_url && post.media_type === "image" && (
              <Image source={{ uri: post.media_url }} style={{ width: "100%", height: 250, borderRadius: 4, marginBottom: 12, backgroundColor: "#111" }} resizeMode="cover" />
            )}
            {post.media_url && post.media_type === "video" && (
              <View style={{ width: "100%", height: 200, borderRadius: 4, marginBottom: 12, backgroundColor: "#111", alignItems: "center", justifyContent: "center" }}>
                <Text style={{ fontSize: 40, opacity: 0.4 }}>▶</Text>
              </View>
            )}

            <Text style={{ color: Colors.text, fontSize: 15, lineHeight: 22, marginBottom: 16 }}>
              {post.body_md}
            </Text>

            {/* Vote buttons */}
            <View style={{ flexDirection: "row", gap: 12, marginBottom: 16, paddingBottom: 16, borderBottomWidth: 1, borderBottomColor: Colors.border }}>
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
              </TouchableOpacity>
              <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 12, marginLeft: "auto", alignSelf: "center" }}>
                💬 {comments.length} comments
              </Text>
            </View>
          </View>
        }
        ListEmptyComponent={
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 20 }}>
            No comments yet. Be the first!
          </Text>
        }
      />

      {/* Comment input */}
      {token ? (
        <View style={{
          flexDirection: "row", alignItems: "center", gap: 8,
          paddingHorizontal: 12, paddingVertical: 8,
          borderTopWidth: 1, borderColor: Colors.border, backgroundColor: Colors.bg,
        }}>
          <TextInput
            value={commentText}
            onChangeText={setCommentText}
            placeholder="Add a comment..."
            placeholderTextColor={Colors.textMuted}
            style={{
              flex: 1, color: Colors.text, fontSize: 14,
              backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
              paddingHorizontal: 12, paddingVertical: 10, borderRadius: 20,
            }}
          />
          <TouchableOpacity
            onPress={handleAddComment}
            disabled={submitting || !commentText.trim()}
            style={{
              backgroundColor: commentText.trim() ? Colors.green : Colors.border,
              borderRadius: 20, width: 40, height: 40,
              alignItems: "center", justifyContent: "center",
            }}
          >
            <Text style={{ color: "#fff", fontSize: 16 }}>↑</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={{ padding: 14, alignItems: "center", borderTopWidth: 1, borderTopColor: Colors.border }}>
          <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 12 }}>Sign in to comment</Text>
        </View>
      )}
    </KeyboardAvoidingView>
  );
}
