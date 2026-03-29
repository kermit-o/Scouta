import { View, Text } from "react-native";

export default function HomeScreen() {
  return (
    <View style={{ flex: 1, backgroundColor: "#080808", alignItems: "center", justifyContent: "center" }}>
      <Text style={{ color: "#4a9a4a", fontSize: 32, fontWeight: "700" }}>SCOUTA</Text>
      <Text style={{ color: "#888", fontSize: 14, marginTop: 8 }}>App is working</Text>
    </View>
  );
}
