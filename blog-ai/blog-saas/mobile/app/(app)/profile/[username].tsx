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
              {displayName.charAt(0).toUpperCase()}
            </Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 22, fontFamily: Fonts.serif }}>{displayName}</Text>
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
