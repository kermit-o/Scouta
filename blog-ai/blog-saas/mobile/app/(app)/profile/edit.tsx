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
        <Text style={{ color: Colors.text, fontSize: 22, fontFamily: Fonts.serif, marginTop: 8 }}>Edit Profile</Text>
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
