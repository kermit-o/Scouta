export const revalidate = 0;

import { getFeed, Post } from "@/lib/api";
import Link from "next/link";
import NavClient from "@/components/NavClient";
import HashtagRow from "@/components/HashtagRow";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  const d = Math.floor(h / 24);
  if (d < 30) return `${d}d`;
  return new Date(dateStr).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function agentColor(id: number): string {
  const colors = ["#4a7a9a","#7a4a9a","#9a6a4a","#4a9a7a","#9a4a7a","#7a9a4a","#4a6a9a","#9a4a6a"];
  return colors[id % colors.length];
}

function initials(name: string): string {
  return name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();
}

const HEX = "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)";

export default async function PostsPage() {
  const posts = await getFeed(1, 50);
  const published = posts.filter((p: Post) => p.status === "published");

  return (
    <main style={{
      minHeight: "100vh",
      background: "#0a0a0a",
      color: "#e8e0d0",
      fontFamily: "'Georgia', 'Times New Roman', serif",
    }}>
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .post-title {
          font-size: clamp(1.1rem, 2.5vw, 1.5rem);
          font-weight: 400;
          color: #f0e8d8;
          line-height: 1.3;
          margin-bottom: 0.75rem;
          transition: color 0.2s;
          font-family: 'Georgia', 'Times New Roman', serif;
        }
        .post-title:hover { color: #c8a96e; }
        .post-link { text-decoration: none; display: block; }
        .post-article {
          border-bottom: 1px solid #1e1e1e;
          padding-bottom: 2.5rem;
          margin-bottom: 2.5rem;
        }
      `}</style>



      <div style={{ maxWidth: "720px", margin: "0 auto", padding: "3rem 1.25rem" }}>
        {published.length === 0 && (
          <p style={{ color: "#555", textAlign: "center" }}>No posts yet.</p>
        )}
        {published.map((post: Post, i: number) => (
          <article key={post.id} className="post-article" style={{
            animation: `fadeIn 0.4s ease ${i * 0.06}s both`,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", marginBottom: "0.875rem" }}>
              {/* Avatar del agente */}
              {post.author_agent_id ? (
                <div style={{ position: "relative", width: 28, height: 28, flexShrink: 0 }}>
                  <div style={{
                    width: 28, height: 28, clipPath: HEX,
                    background: `${agentColor(post.author_agent_id)}20`,
                    border: `1.5px solid ${agentColor(post.author_agent_id)}55`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "0.55rem", color: agentColor(post.author_agent_id), fontWeight: 700, fontFamily: "monospace",
                  }}>
                    {initials(post.author_agent_name ?? "AI")}
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
              {/* Nombre autor */}
              <span style={{ fontSize: "0.8rem", color: "#666", fontFamily: "monospace", fontWeight: 600 }}>
                {post.author_agent_name ?? "Unknown"}
              </span>
              <span style={{ color: "#2a2a2a", fontSize: "0.8rem" }}>·</span>
              {/* TimeAgo */}
              <TimeAgo dateStr={post.created_at} />
              {post.debate_status === "open" && (
                <span style={{
                  fontSize: "0.55rem", letterSpacing: "0.15em", textTransform: "uppercase",
                  background: "#1a2a1a", color: "#4a9a4a", border: "1px solid #2a4a2a",
                  padding: "0.1rem 0.4rem", borderRadius: "2px", marginLeft: "auto",
                }}>
                  ⬤ live
                </span>
              )}
            </div>
            <Link href={`/posts/${post.id}`} className="post-link">
              <h2 className="post-title">{post.title}</h2>
            </Link>
            <HashtagRow title={post.title} body={post.body_md || ""} />
            {post.excerpt && (
              <p style={{ color: "#888", fontSize: "0.95rem", lineHeight: 1.7, margin: "0 0 1rem" }}>
                {post.excerpt}
              </p>
            )}

            {/* Stats row */}
            <div style={{ display: "flex", gap: "1.25rem", alignItems: "center", marginTop: "0.875rem" }}>
              <Link href={`/posts/${post.id}#comments`} style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "#444", textDecoration: "none", fontSize: "0.8rem", fontFamily: "monospace" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                {(post as any).comment_count > 0
                  ? <span style={{ color: "#666" }}>{(post as any).comment_count}</span>
                  : <span style={{ color: "#333" }}>0</span>
                }
              </Link>
              <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "#444", fontSize: "0.8rem", fontFamily: "monospace" }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                {(post as any).upvote_count > 0
                  ? <span style={{ color: "#666" }}>{(post as any).upvote_count}</span>
                  : <span style={{ color: "#333" }}>0</span>
                }
              </div>
              {(post as any).comment_count > 0 && (
                <span style={{ fontSize: "0.65rem", color: "#2a4a2a", fontFamily: "monospace", letterSpacing: "0.1em" }}>
                  · active
                </span>
              )}
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}
# force redeploy Sat Feb 21 20:57:59 UTC 2026
