import { useEffect } from "react";
import { useRouter } from "expo-router";
import { View, Text, ActivityIndicator } from "react-native";
import { useAuth } from "@/contexts/AuthContext";
import { Colors } from "@/lib/constants";

export default function SplashScreen() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      // Small delay to ensure navigation is ready
      const timer = setTimeout(() => {
        if (isAuthenticated) {
          router.replace("/(app)");
        } else {
          router.replace("/(auth)/login");
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [loading, isAuthenticated]);

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg, alignItems: "center", justifyContent: "center" }}>
      <Text style={{ color: Colors.text, fontSize: 28, fontWeight: "700", marginBottom: 16 }}>SCOUTA</Text>
      <Text style={{ color: Colors.textMuted, fontSize: 11, letterSpacing: 2, marginBottom: 24 }}>AI DEBATES</Text>
      <ActivityIndicator color={Colors.green} />
    </View>
  );
}
