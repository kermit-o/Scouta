import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator, Switch } from "react-native";
import { useRouter } from "expo-router";
import { Colors, Fonts, API_BASE } from "@/lib/constants";
import { getToken } from "@/lib/auth";

export default function GoLiveScreen() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const [accessType, setAccessType] = useState("password");
  const [password, setPassword] = useState("");
  const [entryCost, setEntryCost] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleStart() {
    if (!title.trim()) return;
    setLoading(true); setError("");
    try {
      const token = await getToken();
      const body: any = { title: title.trim(), description: description.trim() };
      if (isPrivate) {
        body.is_private = true; body.access_type = accessType;
        if (accessType === "password") body.password = password;
        if (accessType === "paid") body.entry_coin_cost = parseInt(entryCost) || 0;
      }
      const res = await fetch(`${API_BASE}/live/start`, {
        method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (data.room_name) { router.replace(`/(app)/live/${data.room_name}`); }
      else { setError(data.detail || "Failed to start"); }
    } catch { setError("Network error"); }
    setLoading(false);
  }

  const inp = { backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder, color: Colors.text, padding: 12, fontFamily: "monospace" as const, fontSize: 14, marginBottom: 12 };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: Colors.bg }} contentContainerStyle={{ padding: 20, paddingTop: 56 }}>
      <TouchableOpacity onPress={() => router.back()}>
        <Text style={{ color: Colors.blue, fontFamily: Fonts.mono, fontSize: 12, marginBottom: 16 }}>{"< Back"}</Text>
      </TouchableOpacity>
      <Text style={{ color: Colors.red, fontSize: 10, fontFamily: Fonts.mono, letterSpacing: 2, marginBottom: 4 }}>GO LIVE</Text>
      <Text style={{ color: Colors.text, fontSize: 22, fontWeight: "700", marginBottom: 24 }}>Start a Live Stream</Text>
      {error ? <Text style={{ color: Colors.red, fontFamily: Fonts.mono, fontSize: 12, marginBottom: 12 }}>{error}</Text> : null}
      <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>TITLE *</Text>
      <TextInput value={title} onChangeText={setTitle} placeholder="What are you debating?" placeholderTextColor={Colors.textMuted} style={inp} />
      <Text style={{ color: Colors.textMuted, fontFamily: Fonts.mono, fontSize: 10, letterSpacing: 1, marginBottom: 4 }}>DESCRIPTION</Text>
      <TextInput value={description} onChangeText={setDescription} placeholder="Optional" placeholderTextColor={Colors.textMuted} multiline numberOfLines={3} style={{ ...inp, textAlignVertical: "top", minHeight: 70 }} />
      <View style={{ flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 16, padding: 12, backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border }}>
        <Switch value={isPrivate} onValueChange={setIsPrivate} trackColor={{ true: Colors.gold }} />
        <Text style={{ color: Colors.text, fontFamily: Fonts.mono, fontSize: 13 }}>Private Room</Text>
      </View>
      {isPrivate && (
        <View style={{ marginBottom: 16 }}>
          <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: 12 }}>
            {[{v:"password",l:"Password"},{v:"invite_only",l:"Invite Only"},{v:"paid",l:"Paid"},{v:"followers",l:"Followers"},{v:"subscribers",l:"Subscribers"},{v:"vip",l:"VIP"}].map(at => (
              <TouchableOpacity key={at.v} onPress={() => setAccessType(at.v)}
                style={{ paddingVertical: 6, paddingHorizontal: 10, backgroundColor: accessType === at.v ? Colors.green + "22" : Colors.card, borderWidth: 1, borderColor: accessType === at.v ? Colors.green : Colors.border }}>
                <Text style={{ color: accessType === at.v ? Colors.green : Colors.textMuted, fontFamily: Fonts.mono, fontSize: 11 }}>{at.l}</Text>
              </TouchableOpacity>
            ))}
          </View>
          {accessType === "password" && <TextInput value={password} onChangeText={setPassword} placeholder="Room password" placeholderTextColor={Colors.textMuted} secureTextEntry style={inp} />}
          {accessType === "paid" && <TextInput value={entryCost} onChangeText={t => setEntryCost(t.replace(/\D/g, ""))} placeholder="Coin cost" placeholderTextColor={Colors.textMuted} keyboardType="numeric" style={inp} />}
        </View>
      )}
      <TouchableOpacity onPress={handleStart} disabled={loading || !title.trim()}
        style={{ backgroundColor: Colors.red, padding: 16, alignItems: "center", opacity: loading || !title.trim() ? 0.5 : 1 }}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={{ color: "#fff", fontFamily: Fonts.mono, fontSize: 13, letterSpacing: 1 }}>START LIVE</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}
