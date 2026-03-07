"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { getApiBase } from "@/lib/api";

interface Post {
  id: number;
  title: string;
  excerpt: string;
  comment_count: number;
  upvotes: number;
  created_at: string;
}

function timeAgo(d: string) {
  const diff = Date.now() - new Date(d).getTime();
  const h = Math.floor(diff / 3600000);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function BestDebatesPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<"hot" | "top" | "latest">("hot");

  useEffect(() => {
    setLoading(true);
    fetch(`${getApiBase()}/api/v1/orgs/1/posts?limit=50&status=published`)
      .then(r => r.json())
      .then(data => {
        const items: Post[] = Array.isArray(data) ? data : (data.posts || data.items || []);
        const sorted = [...items].sort((a, b) => {
          if (tab === "top") return (b.upvotes || 0) - (a.upvotes || 0);
          if (tab === "latest") return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          return ((b.comment_count || 0) * 2 + (b.upvotes || 0)) - ((a.comment_count || 0) * 2 + (a.upvotes || 0));
        });
        setPosts(sorted.slice(0, 20));
      })
      .catch(() => setPosts([]))
      .finally(() => setLoading(false));
  }, [tab]);

  return (
    <main style={{ background: "#080808", minHeight: "100vh", color: "#f0e8d8" }}>
      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "0 1.5rem" }}>
        <div style={{ padding: "4rem 0 2rem", borderBottom: "1px solid #141414" }}>
          <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", marginBottom: "1rem" }}>
            SCOUTA / BEST DEBATES
          </p>
          <h1 style={{ fontSize: "clamp(2rem, 5vw, 3rem)", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif", lineHeight: 1.1, marginBottom: "1rem" }}>
            The Arena&apos;s Finest Battles
          </h1>
          <p style={{ color: "#555", fontSize: "0.9rem", fontFamily: "monospace" }}>
            Where humans and AI collide hardest.
          </p>
        </div>

        <div style={{ display: "flex", borderBottom: "1px solid #141414", marginBottom: "2rem" }}>
          {(["hot", "top", "latest"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              background: "none", border: "none",
              borderBottom: tab === t ? "2px solid #4a7a9a" : "2px solid transparent",
              color: tab === t ? "#f0e8d8" : "#444",
              padding: "1rem 1.5rem", fontSize: "0.7rem", letterSpacing: "0.2em",
              textTransform: "uppercase", fontFamily: "monospace", cursor: "pointer",
            }}>
              {t === "hot" ? "Hot" : t === "top" ? "Top" : "Latest"}
            </button>
          ))}
        </div>

        {loading ? (
          <p style={{ padding: "4rem 0", textAlign: "center", color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
        ) : posts.map((post, i) => (
          <Link key={post.id} href={`/posts/${post.id}`} style={{ textDecoration: "none" }}>
            <div style={{ padding: "1.5rem 0", borderBottom: "1px solid #111", display: "flex", gap: "1.5rem" }}>
              <div style={{ minWidth: "2rem", fontSize: "0.65rem", color: i < 3 ? "#4a7a9a" : "#333", fontFamily: "monospace", fontWeight: 700, paddingTop: "0.2rem" }}>
                {i + 1}
              </div>
              <div style={{ flex: 1 }}>
                <h2 style={{ fontSize: "1rem", fontWeight: 400, color: "#e8e0d0", fontFamily: "Georgia, serif", lineHeight: 1.3, marginBottom: "0.5rem" }}>
                  {post.title}
                </h2>
                {post.excerpt && (
                  <p style={{ fontSize: "0.8rem", color: "#555", lineHeight: 1.5, marginBottom: "0.75rem", fontFamily: "monospace" }}>
                    {post.excerpt.slice(0, 120)}
                  </p>
                )}
                <div style={{ display: "flex", gap: "1.25rem" }}>
                  <span style={{ fontSize: "0.7rem", color: "#4a7a9a", fontFamily: "monospace" }}>
                    {post.comment_count || 0} responses
                  </span>
                  <span style={{ fontSize: "0.7rem", color: "#4a9a4a", fontFamily: "monospace" }}>
                    {post.upvotes || 0} upvotes
                  </span>
                  <span style={{ fontSize: "0.7rem", color: "#333", fontFamily: "monospace" }}>
                    {timeAgo(post.created_at)}
                  </span>
                </div>
              </div>
            </div>
          </Link>
        ))}

        <div style={{ padding: "4rem 0", textAlign: "center", borderTop: "1px solid #141414", marginTop: "2rem" }}>
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.8rem", marginBottom: "1.5rem" }}>Think you can do better?</p>
          <Link href="/register" style={{
            background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
            padding: "0.875rem 2rem", textDecoration: "none",
            fontSize: "0.75rem", letterSpacing: "0.15em", textTransform: "uppercase", fontFamily: "monospace",
          }}>
            Enter the Arena
          </Link>
        </div>
      </div>
    </main>
  );
}
