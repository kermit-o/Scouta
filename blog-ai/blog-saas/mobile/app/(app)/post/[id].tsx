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
            <Text style={{ color: Colors.text, fontSize: 22, fontFamily: Fonts.serif, lineHeight: 30, marginBottom: 8 }}>
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
