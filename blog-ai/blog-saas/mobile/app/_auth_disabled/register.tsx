import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useRouter, Link } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function RegisterScreen() {
  const { register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRegister() {
    if (!email.trim() || !password.trim() || !username.trim()) return;
    setLoading(true);
    setError("");
    const result = await register(email.trim(), password, username.trim(), displayName.trim() || undefined);
    setLoading(false);
    if (result.ok) {
      router.replace("/(app)");
    } else {
      setError(result.error || "Registration failed");
    }
  }

  const inputStyle = {
    backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
    color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 16,
  };
  const labelStyle = { color: Colors.textMuted, fontSize: 10, fontFamily: "monospace" as const, letterSpacing: 1, marginBottom: 6 };

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={{ flex: 1, justifyContent: "center", padding: 24 }}>
        <View style={{ alignItems: "center", marginBottom: 32 }}>
          <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "700" }}>Create Account</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 2, marginTop: 8 }}>JOIN THE DEBATE</Text>
        </View>

        {error ? (
          <Text style={{ color: Colors.red, fontSize: 12, fontFamily: "monospace", textAlign: "center", marginBottom: 16 }}>{error}</Text>
        ) : null}

        <Text style={labelStyle}>EMAIL</Text>
        <TextInput value={email} onChangeText={setEmail} placeholder="you@email.com" placeholderTextColor={Colors.textMuted} autoCapitalize="none" keyboardType="email-address" style={inputStyle} />

        <Text style={labelStyle}>USERNAME</Text>
        <TextInput value={username} onChangeText={setUsername} placeholder="your_handle" placeholderTextColor={Colors.textMuted} autoCapitalize="none" style={inputStyle} />

        <Text style={labelStyle}>DISPLAY NAME</Text>
        <TextInput value={displayName} onChangeText={setDisplayName} placeholder="Your Name (optional)" placeholderTextColor={Colors.textMuted} style={inputStyle} />

        <Text style={labelStyle}>PASSWORD</Text>
        <TextInput value={password} onChangeText={setPassword} placeholder="Min 6 characters" placeholderTextColor={Colors.textMuted} secureTextEntry style={inputStyle} />

        <TouchableOpacity
          onPress={handleRegister}
          disabled={loading || !email.trim() || !password.trim() || !username.trim()}
          style={{
            backgroundColor: Colors.green, padding: 16, alignItems: "center",
            opacity: loading || !email.trim() || !password.trim() || !username.trim() ? 0.5 : 1,
          }}
        >
          {loading ? <ActivityIndicator color="#fff" /> : (
            <Text style={{ color: "#fff", fontSize: 13, fontFamily: "monospace", letterSpacing: 1 }}>CREATE ACCOUNT</Text>
          )}
        </TouchableOpacity>

        <View style={{ flexDirection: "row", justifyContent: "center", marginTop: 24, gap: 4 }}>
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace" }}>Have an account?</Text>
          <Link href="/(auth)/login">
            <Text style={{ color: Colors.green, fontSize: 12, fontFamily: "monospace" }}>Sign in</Text>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
