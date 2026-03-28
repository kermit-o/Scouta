import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from "react-native";
import { Link } from "expo-router";
import { forgotPassword } from "@/lib/api";
import { Colors } from "@/lib/constants";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (!email.trim()) return;
    setLoading(true);
    setError("");
    try {
      await forgotPassword(email.trim());
      setSent(true);
    } catch (e: any) {
      setError(e.message || "Failed to send email");
    }
    setLoading(false);
  }

  return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, backgroundColor: Colors.bg }}>
      <Text style={{ color: Colors.text, fontSize: 22, fontFamily: "Georgia", marginBottom: 8 }}>Reset Password</Text>
      <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace", marginBottom: 32 }}>
        We'll send you a link to reset your password.
      </Text>

      {sent ? (
        <View>
          <Text style={{ color: Colors.green, fontSize: 13, fontFamily: "monospace", marginBottom: 24 }}>
            Check your email for a reset link.
          </Text>
          <Link href="/(auth)/login">
            <Text style={{ color: Colors.blue, fontSize: 12, fontFamily: "monospace" }}>Back to login</Text>
          </Link>
        </View>
      ) : (
        <>
          {error ? <Text style={{ color: Colors.red, fontSize: 12, fontFamily: "monospace", marginBottom: 12 }}>{error}</Text> : null}
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
          <TouchableOpacity
            onPress={handleSubmit}
            disabled={loading || !email.trim()}
            style={{ backgroundColor: Colors.green, padding: 16, alignItems: "center", opacity: loading ? 0.5 : 1 }}
          >
            {loading ? <ActivityIndicator color="#fff" /> : (
              <Text style={{ color: "#fff", fontSize: 13, fontFamily: "monospace", letterSpacing: 1 }}>SEND RESET LINK</Text>
            )}
          </TouchableOpacity>
          <Link href="/(auth)/login" style={{ marginTop: 16 }}>
            <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: "monospace" }}>Back to login</Text>
          </Link>
        </>
      )}
    </View>
  );
}
