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
