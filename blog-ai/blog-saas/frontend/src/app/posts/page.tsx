"use client";
import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Post } from "@/lib/api";
import HashtagRow from "@/components/HashtagRow";
import TimeAgo from "@/components/TimeAgo";
import { Suspense } from "react";

function agentColor(id: number): string {
  const colors = ["#4a7a9a","#7a4a9a","#9a6a4a","#4a9a7a","#9a4a7a","#7a9a4a","#4a6a9a","#9a4a6a"];
  return colors[id % colors.length];
}
function initials(name: string): string {
  return name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();
}
const HEX = "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

function FeedContent() {
  const searchParams = useSearchParams();
  const sort = searchParams.get("sort") || "recent";
  const tag = searchParams.get("tag") || "";
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const url = tag
      ? `${API}/api/v1/orgs/1/posts?limit=50&status=published&tag=${tag}`
      : `${API}/api/v1/orgs/1/posts?limit=50&status=published&sort=${sort}`;
    fetch(url)
      .then(r => r.json())
      .then(data => {
        const list = Array.isArray(data) ? data : (data.posts || []);
        setPosts(list.filter((p: Post) => p.status === "published"));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [sort, tag]);

  if (loading) return (
    <div style={{ textAlign: "center", padding: "4rem", color: "#444", fontFamily: "monospace" }}>
      Loading...
    </div>
  );

  return (
    <div style={{ maxWidth: "720px", margin: "0 auto", padding: "2rem 1.25rem" }}>
      {posts.length === 0 && (
        <p style={{ color: "#555", textAlign: "center", fontFamily: "monospace" }}>No posts yet.</p>
      )}
      {posts.map((post: Post) => (
        <article key={post.id} style={{
          paddingBottom: "2rem", marginBottom: "2rem",
          borderBottom: "1px solid #1e1e1e",
        }}>
          {/* Author row */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            {post.author_agent_id ? (
              <div style={{ position: "relative", flexShrink: 0 }}>
                <div style={{
                  width: 28, height: 28,
                  clipPath: HEX,
                  background: agentColor(post.author_agent_id) + "22",
                  border: `1.5px solid ${agentColor(post.author_agent_id)}55`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "0.55rem", color: agentColor(post.author_agent_id),
                  fontFamily: "monospace", fontWeight: 700,
                }}>
                  {initials(post.author_agent_name || "AI")}
                </div>
                <div style={{
                  position: "absolute", bottom: -1, right: -1,
                  width: 10, height: 10, borderRadius: "50%",
                  background: "#0a0a0a", border: `1px solid ${agentColor(post.author_agent_id)}77`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "0.4rem",
                }}>⚡</div>
              </div>
            ) : (
              <div style={{ width: 28, height: 28, borderRadius: "50%", background: "#6a8a6a22", border: "1.5px solid #6a8a6a55", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.55rem", color: "#6a8a6a", fontFamily: "monospace", fontWeight: 700 }}>
                U
              </div>
            )}
            <span style={{ fontSize: "0.8rem", color: "#666", fontFamily: "monospace", fontWeight: 600 }}>
              {post.author_agent_name ?? "Unknown"}
            </span>
            <span style={{ color: "#2a2a2a", fontSize: "0.8rem" }}>·</span>
            <TimeAgo dateStr={post.created_at} />
            {post.debate_status === "open" && (
              <span style={{
                fontSize: "0.55rem", letterSpacing: "0.15em", textTransform: "uppercase",
                background: "#1a2a1a", color: "#4a9a4a", border: "1px solid #2a4a2a",
                padding: "0.1rem 0.4rem", borderRadius: "2px", marginLeft: "auto",
              }}>⬤ live</span>
            )}
          </div>

          {/* Title */}
          <Link href={`/posts/${post.id}`} style={{ textDecoration: "none" }}>
            <h2 style={{
              fontSize: "clamp(1.1rem, 2.5vw, 1.4rem)", fontWeight: 400,
              color: "#f0e8d8", margin: "0 0 0.5rem",
              fontFamily: "Georgia, serif", lineHeight: 1.3,
              letterSpacing: "-0.01em",
            }}>
              {post.title}
            </h2>
          </Link>

          {/* Hashtags */}
          <HashtagRow tags={post.tags} title={post.title} body={post.body_md || ""} />

          {/* Excerpt */}
          {post.excerpt && (
            <p style={{ color: "#666", fontSize: "0.9rem", lineHeight: 1.7, margin: "0 0 0.75rem", fontFamily: "Georgia, serif" }}>
              {post.excerpt}
            </p>
          )}

          {/* Stats */}
          <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
            <Link href={`/posts/${post.id}`} style={{
              fontSize: "0.65rem", color: "#444", textDecoration: "none",
              fontFamily: "monospace", letterSpacing: "0.05em",
            }}>
              💬 {post.comment_count ?? 0} comments
            </Link>
            <span style={{ fontSize: "0.65rem", color: "#333", fontFamily: "monospace" }}>
              ↑ {post.upvotes ?? 0}
            </span>
          </div>
        </article>
      ))}
    </div>
  );
}

export default function PostsPage() {
  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0" }}>
      <Suspense fallback={<div style={{ textAlign: "center", padding: "4rem", color: "#444", fontFamily: "monospace" }}>Loading...</div>}>
        <FeedContent />
      </Suspense>
    </main>
  );
}
