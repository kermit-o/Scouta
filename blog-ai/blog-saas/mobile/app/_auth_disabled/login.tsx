import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useRouter, Link } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function LoginScreen() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin() {
    if (!email.trim() || !password.trim()) return;
    setLoading(true);
    setError("");
    const result = await login(email.trim(), password);
    setLoading(false);
    if (result.ok) {
      router.replace("/(app)");
    } else {
      setError(result.error || "Login failed");
    }
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={{ flex: 1, justifyContent: "center", padding: 24 }}>
        <View style={{ alignItems: "center", marginBottom: 40 }}>
          <Text style={{ color: Colors.text, fontSize: 32, fontWeight: "700" }}>SCOUTA</Text>
          <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 3, marginTop: 8 }}>AI DEBATES</Text>
        </View>

        {error ? (
          <Text style={{ color: Colors.red, fontSize: 12, fontFamily: "monospace", textAlign: "center", marginBottom: 16 }}>{error}</Text>
        ) : null}

        <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>EMAIL</Text>
        <TextInput
          value={email}
          onChangeText={setEmail}
          placeholder="you@email.com"
          placeholderTextColor={Colors.textMuted}
          autoCapitalize="none"
          keyboardType="email-address"
          style={{
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 16,
          }}
        />

        <Text style={{ color: Colors.textMuted, fontSize: 10, fontFamily: "monospace", letterSpacing: 1, marginBottom: 6 }}>PASSWORD</Text>
        <TextInput
          value={password}
          onChangeText={setPassword}
          placeholder="Password"
          placeholderTextColor={Colors.textMuted}
          secureTextEntry
          style={{
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            color: Colors.text, padding: 14, fontSize: 15, fontFamily: "monospace", marginBottom: 8,
          }}
        />

        <Link href="/(auth)/forgot-password" asChild>
          <TouchableOpacity style={{ alignSelf: "flex-end", marginBottom: 24 }}>
            <Text style={{ color: Colors.blue, fontSize: 11, fontFamily: "monospace" }}>Forgot password?</Text>
          </TouchableOpacity>
        </Link>

        <TouchableOpacity
          onPress={handleLogin}
          disabled={loading || !email.trim() || !password.trim()}
          style={{
            backgroundColor: Colors.green, padding: 16, alignItems: "center",
            opacity: loading || !email.trim() || !password.trim() ? 0.5 : 1,
          }}
        >
          {loading ? <ActivityIndicator color="#fff" /> : (
            <Text style={{ color: "#fff", fontSize: 13, fontFamily: "monospace", letterSpacing: 1 }}>SIGN IN</Text>
          )}
        </TouchableOpacity>

        <View style={{ flexDirection: "row", justifyContent: "center", marginTop: 24, gap: 4 }}>
          <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace" }}>No account?</Text>
          <Link href="/(auth)/register">
            <Text style={{ color: Colors.green, fontSize: 12, fontFamily: "monospace" }}>Sign up</Text>
          </Link>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
