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
        <Text style={{ color: Colors.text, fontSize: 22, fontFamily: Fonts.serif, marginTop: 8 }}>New Post</Text>
      </View>

      <ScrollView style={{ flex: 1, paddingHorizontal: 16 }} keyboardShouldPersistTaps="handled">
        <Text style={{ color: Colors.textSecondary, fontSize: 11, fontFamily: Fonts.mono, marginBottom: 6 }}>TITLE</Text>
        <TextInput
          value={title}
          onChangeText={setTitle}
          placeholder="Post title..."
          placeholderTextColor={Colors.textMuted}
          style={{
            color: Colors.text, fontSize: 16, fontFamily: Fonts.serif,
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
