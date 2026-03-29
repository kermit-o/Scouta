import { useState, useEffect, useRef } from "react";
import { View, Text, TextInput, FlatList, TouchableOpacity, ActivityIndicator } from "react-native";
import { useRouter } from "expo-router";
import { globalSearch } from "@/lib/api";
import { Colors, Fonts } from "@/lib/constants";

interface SearchResult {
  id: number;
  type: string;
  title?: string;
  username?: string;
  display_name?: string;
  excerpt?: string;
}

export default function SearchScreen() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    if (!query.trim()) {
      setResults([]);
      setSearched(false);
      return;
    }
    timerRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await globalSearch(query.trim());
        const items = Array.isArray(data) ? data : data.results || [];
        setResults(items);
      } catch {
        setResults([]);
      }
      setLoading(false);
      setSearched(true);
    }, 400);

    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [query]);

  function handlePress(item: SearchResult) {
    if (item.type === "post") {
      router.push(`/(app)/post/${item.id}`);
    } else if (item.type === "user" && item.username) {
      router.push(`/(app)/profile/${item.username}`);
    } else if (item.type === "agent") {
      router.push(`/(app)/agents/${item.id}`);
    }
  }

  function renderResult({ item }: { item: SearchResult }) {
    const label = item.type === "post" ? "POST" : item.type === "agent" ? "AGENT" : "USER";
    const color = item.type === "post" ? Colors.green : item.type === "agent" ? Colors.blue : Colors.gold;
    const title = item.title || item.display_name || item.username || `#${item.id}`;

    return (
      <TouchableOpacity
        onPress={() => handlePress(item)}
        style={{ backgroundColor: Colors.card, borderWidth: 1, borderColor: Colors.border, padding: 14, marginBottom: 6 }}
      >
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <View style={{ backgroundColor: color + "22", paddingHorizontal: 6, paddingVertical: 2 }}>
            <Text style={{ color, fontSize: 9, fontFamily: Fonts.mono, fontWeight: "700" }}>{label}</Text>
          </View>
          <Text style={{ color: Colors.text, fontSize: 14, fontWeight: "600", flex: 1 }} numberOfLines={1}>
            {title}
          </Text>
        </View>
        {item.excerpt ? (
          <Text style={{ color: Colors.textMuted, fontSize: 12, lineHeight: 16 }} numberOfLines={2}>
            {item.excerpt}
          </Text>
        ) : null}
      </TouchableOpacity>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: Colors.bg }}>
      <View style={{ paddingTop: 56, paddingHorizontal: 16, paddingBottom: 12 }}>
        <Text style={{ color: Colors.blue, fontSize: 9, fontFamily: Fonts.mono, letterSpacing: 3 }}>SCOUTA</Text>
        <Text style={{ color: Colors.text, fontSize: 24, fontWeight: "600", marginTop: 4, marginBottom: 12 }}>Search</Text>
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search posts, users, agents..."
          placeholderTextColor={Colors.textMuted}
          autoFocus
          style={{
            color: Colors.text, fontSize: 14,
            backgroundColor: Colors.inputBg, borderWidth: 1, borderColor: Colors.inputBorder,
            paddingHorizontal: 12, paddingVertical: 10,
          }}
        />
      </View>

      {loading ? (
        <ActivityIndicator color={Colors.green} style={{ marginTop: 30 }} />
      ) : (
        <FlatList
          data={results}
          keyExtractor={(item, i) => `${item.type}-${item.id}-${i}`}
          renderItem={renderResult}
          contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 40 }}
          ListEmptyComponent={
            searched ? (
              <Text style={{ color: Colors.textMuted, fontSize: 12, fontFamily: Fonts.mono, textAlign: "center", marginTop: 40 }}>
                No results found.
              </Text>
            ) : null
          }
        />
      )}
    </View>
  );
}
