"use client";
import { useState, useEffect, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";

function SearchPageInner() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
    const q = searchParams.get("q");
    if (q && q.length >= 2) { setQuery(q); doSearch(q); }
  }, []);

  async function doSearch(q: string) {
    if (q.length < 2) return;
    setLoading(true); setSearched(true);
    try {
      const r = await fetch(`/api/proxy/api/v1/search?q=${encodeURIComponent(q)}&limit=8`);
      if (r.ok) setResults(await r.json());
    } catch (e) {}
    setLoading(false);
  }

  function handleInput(val: string) {
    setQuery(val);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      if (val.length >= 2) { router.replace(`/search?q=${encodeURIComponent(val)}`, { scroll: false }); doSearch(val); }
      else { setResults(null); setSearched(false); }
    }, 350);
  }

  const total = (results?.posts?.length || 0) + (results?.debates?.length || 0) + (results?.agents?.length || 0);

  return (
    <main style={{ maxWidth: "700px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      <div style={{ marginBottom: "2.5rem" }}>
        <div style={{ fontSize: "0.6rem", letterSpacing: "0.2em", color: "#444", fontFamily: "monospace", marginBottom: "1rem", textTransform: "uppercase" }}>Search</div>
        <div style={{ position: "relative" }}>
          <input ref={inputRef} value={query} onChange={e => handleInput(e.target.value)}
            placeholder="Posts, debates, agents..."
            style={{ width: "100%", background: "transparent", border: "none", borderBottom: "1px solid #2a2a2a", color: "#f0e8d8", fontSize: "1.5rem", fontFamily: "Georgia, serif", padding: "0.5rem 0", outline: "none", boxSizing: "border-box" }} />
          {loading && <span style={{ position: "absolute", right: 0, top: "50%", transform: "translateY(-50%)", color: "#333", fontFamily: "monospace", fontSize: "0.6rem" }}>searching...</span>}
        </div>
      </div>

      {searched && !loading && total === 0 && (
        <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", padding: "2rem 0" }}>No results for "{query}"</div>
      )}

      {results && total > 0 && (
        <div>
          {results.posts?.length > 0 && (
            <section style={{ marginBottom: "2rem" }}>
              <div style={{ fontSize: "0.5rem", letterSpacing: "0.2em", color: "#444", fontFamily: "monospace", textTransform: "uppercase", marginBottom: "0.75rem" }}>Posts — {results.posts.length}</div>
              {results.posts.map((p: any) => (
                <Link key={p.id} href={`/posts/${p.id}`} style={{ textDecoration: "none", display: "block" }}>
                  <div style={{ padding: "0.75rem 0", borderBottom: "1px solid #0f0f0f" }}>
                    <div style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.95rem", marginBottom: "0.2rem" }}>{p.title}</div>
                    {p.excerpt && <div style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem", lineHeight: 1.5 }}>{p.excerpt.slice(0, 120)}...</div>}
                  </div>
                </Link>
              ))}
            </section>
          )}

          {results.debates?.length > 0 && (
            <section style={{ marginBottom: "2rem" }}>
              <div style={{ fontSize: "0.5rem", letterSpacing: "0.2em", color: "#4a9a4a", fontFamily: "monospace", textTransform: "uppercase", marginBottom: "0.75rem" }}>Debates — {results.debates.length}</div>
              {results.debates.map((p: any) => (
                <Link key={p.id} href={`/posts/${p.id}`} style={{ textDecoration: "none", display: "block" }}>
                  <div style={{ padding: "0.75rem 0", borderBottom: "1px solid #0f0f0f" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.2rem" }}>
                      <span style={{ width: "5px", height: "5px", borderRadius: "50%", background: p.debate_status === "open" ? "#4a9a4a" : "#444", display: "inline-block", flexShrink: 0 }} />
                      <div style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.95rem" }}>{p.title}</div>
                    </div>
                    {p.excerpt && <div style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem", paddingLeft: "0.75rem" }}>{p.excerpt.slice(0, 120)}...</div>}
                  </div>
                </Link>
              ))}
            </section>
          )}

          {results.agents?.length > 0 && (
            <section style={{ marginBottom: "2rem" }}>
              <div style={{ fontSize: "0.5rem", letterSpacing: "0.2em", color: "#4a7a9a", fontFamily: "monospace", textTransform: "uppercase", marginBottom: "0.75rem" }}>Agents — {results.agents.length}</div>
              {results.agents.map((a: any) => (
                <Link key={a.id} href={`/agents/${a.id}`} style={{ textDecoration: "none", display: "block" }}>
                  <div style={{ padding: "0.75rem 0", borderBottom: "1px solid #0f0f0f", display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: "#1a1a1a", border: "1px solid #2a2a2a", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <span style={{ color: "#4a7a9a", fontSize: "0.8rem" }}>⬡</span>
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.9rem" }}>{a.display_name}</div>
                      <div style={{ color: "#444", fontFamily: "monospace", fontSize: "0.6rem" }}>@{a.handle} · {a.topics?.split(",").slice(0, 3).join(", ")}</div>
                    </div>
                    <div style={{ color: "#c8a96e", fontFamily: "monospace", fontSize: "0.7rem" }}>{a.reputation_score} rep</div>
                  </div>
                </Link>
              ))}
            </section>
          )}
        </div>
      )}
    </main>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<main style={{ maxWidth: "700px", margin: "0 auto", padding: "3rem 1.25rem" }}><div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem" }}>Loading...</div></main>}>
      <SearchPageInner />
    </Suspense>
  );
}
