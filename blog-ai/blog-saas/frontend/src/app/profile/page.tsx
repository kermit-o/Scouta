"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

export default function ProfilePage() {
  const { token, user, logout } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [posts, setPosts] = useState<any[]>([]);
  const [comments, setComments] = useState<any[]>([]);
  const [tab, setTab] = useState<"posts" | "comments">("posts");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const t = token || localStorage.getItem("token");
    if (!t) { router.push("/login?next=/profile"); return; }
    const API = "/api/proxy";
    Promise.all([
      fetch(`${API}/api/v1/profile/me`, { headers: { Authorization: `Bearer ${t}` } }).then(r => r.json()),
      fetch(`${API}/api/v1/profile/my-posts`, { headers: { Authorization: `Bearer ${t}` } }).then(r => r.ok ? r.json() : []),
      fetch(`${API}/api/v1/profile/my-comments`, { headers: { Authorization: `Bearer ${t}` } }).then(r => r.ok ? r.json() : []),
    ]).then(([profile, myPosts, myComments]) => {
      setData(profile);
      setPosts(Array.isArray(myPosts) ? myPosts : myPosts.posts || []);
      setComments(Array.isArray(myComments) ? myComments : myComments.comments || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  if (loading) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
    </main>
  );

  const name = data?.display_name || data?.username || "User";
  const initials = name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();

  const tabStyle = (active: boolean) => ({
    background: "none", border: "none", borderBottom: active ? "1px solid #f0e8d8" : "1px solid transparent",
    color: active ? "#f0e8d8" : "#444", padding: "0.5rem 0", cursor: "pointer",
    fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.15em",
    textTransform: "uppercase" as const, marginRight: "2rem",
  });

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace" }}>
      <div style={{ maxWidth: "720px", margin: "0 auto", padding: "2rem 1.5rem" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: "1.5rem", marginBottom: "2.5rem", paddingBottom: "2rem", borderBottom: "1px solid #1a1a1a" }}>
          {/* Avatar */}
          {data?.avatar_url ? (
            <img src={data.avatar_url} alt={name} style={{ width: 72, height: 72, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
          ) : (
            <div style={{ width: 72, height: 72, borderRadius: "50%", background: "#1a2a3a", border: "1px solid #2a3a4a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem", color: "#4a7a9a", flexShrink: 0 }}>
              {initials}
            </div>
          )}

          {/* Info */}
          <div style={{ flex: 1 }}>
            <h1 style={{ fontSize: "1.3rem", fontWeight: 400, fontFamily: "Georgia, serif", color: "#f0e8d8", margin: "0 0 0.25rem" }}>
              {name}
            </h1>
            <p style={{ fontSize: "0.7rem", color: "#555", margin: "0 0 0.5rem" }}>@{data?.username}</p>
            {data?.bio && <p style={{ fontSize: "0.85rem", color: "#888", lineHeight: 1.6, margin: "0 0 0.5rem", fontFamily: "Georgia, serif" }}>{data.bio}</p>}
            <div style={{ display: "flex", gap: "1.5rem", marginTop: "0.5rem" }}>
              {data?.location && <span style={{ fontSize: "0.65rem", color: "#555" }}>📍 {data.location}</span>}
              {data?.website && <a href={data.website} target="_blank" style={{ fontSize: "0.65rem", color: "#4a7a9a", textDecoration: "none" }}>{data.website}</a>}
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", flexShrink: 0 }}>
            <Link href="/profile/edit" style={{ border: "1px solid #2a2a2a", color: "#888", padding: "0.3rem 0.75rem", fontSize: "0.6rem", fontFamily: "monospace", letterSpacing: "0.1em", textDecoration: "none", textAlign: "center" }}>
              Edit Profile
            </Link>
            <button onClick={() => { logout(); router.push("/"); }} style={{ background: "none", border: "1px solid #2a1a1a", color: "#555", padding: "0.3rem 0.75rem", cursor: "pointer", fontSize: "0.6rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>
              Logout
            </button>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: "2rem", marginBottom: "2rem" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "1.2rem", color: "#f0e8d8", fontFamily: "Georgia, serif" }}>{posts.length}</div>
            <div style={{ fontSize: "0.55rem", color: "#444", letterSpacing: "0.15em", textTransform: "uppercase" }}>Posts</div>
          </div>
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "1.2rem", color: "#f0e8d8", fontFamily: "Georgia, serif" }}>{comments.length}</div>
            <div style={{ fontSize: "0.55rem", color: "#444", letterSpacing: "0.15em", textTransform: "uppercase" }}>Comments</div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ borderBottom: "1px solid #1a1a1a", marginBottom: "1.5rem" }}>
          <button style={tabStyle(tab === "posts")} onClick={() => setTab("posts")}>Posts</button>
          <button style={tabStyle(tab === "comments")} onClick={() => setTab("comments")}>Comments</button>
        </div>

        {/* Posts tab */}
        {tab === "posts" && (
          <div>
            {posts.length === 0 ? (
              <div style={{ textAlign: "center", padding: "3rem", color: "#333" }}>
                <p style={{ marginBottom: "1rem" }}>No posts yet.</p>
                <Link href="/posts/new" style={{ fontSize: "0.65rem", color: "#c8a96e", border: "1px solid #3a2a10", padding: "0.4rem 1rem", textDecoration: "none", letterSpacing: "0.1em" }}>
                  + Write your first post
                </Link>
              </div>
            ) : (
              posts.map((post: any) => (
                <Link key={post.id} href={`/posts/${post.id}`} style={{ textDecoration: "none", display: "block", paddingBottom: "1.5rem", marginBottom: "1.5rem", borderBottom: "1px solid #141414" }}>
                  <h3 style={{ fontSize: "1rem", fontWeight: 400, fontFamily: "Georgia, serif", color: "#f0e8d8", margin: "0 0 0.35rem", lineHeight: 1.4 }}>
                    {post.title}
                  </h3>
                  <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                    <span style={{ fontSize: "0.6rem", color: "#444" }}>{timeAgo(post.created_at)}</span>
                    <span style={{ fontSize: "0.6rem", color: "#444" }}>💬 {post.comment_count ?? 0}</span>
                    {post.debate_status === "open" && (
                      <span style={{ fontSize: "0.55rem", color: "#4a9a4a", border: "1px solid #2a4a2a", padding: "0.1rem 0.4rem" }}>⬤ live</span>
                    )}
                  </div>
                </Link>
              ))
            )}
          </div>
        )}

        {/* Comments tab */}
        {tab === "comments" && (
          <div>
            {comments.length === 0 ? (
              <p style={{ color: "#333", textAlign: "center", padding: "3rem" }}>No comments yet.</p>
            ) : (
              comments.map((c: any) => (
                <Link key={c.id} href={`/posts/${c.post_id}#comment-${c.id}`} style={{ textDecoration: "none", display: "block", paddingBottom: "1.25rem", marginBottom: "1.25rem", borderBottom: "1px solid #141414" }}>
                  <p style={{ fontSize: "0.85rem", color: "#888", fontFamily: "Georgia, serif", lineHeight: 1.6, margin: "0 0 0.35rem" }}>
                    {(c.body || "").slice(0, 200)}{c.body?.length > 200 ? "..." : ""}
                  </p>
                  <div style={{ display: "flex", gap: "1rem" }}>
                    <span style={{ fontSize: "0.6rem", color: "#333" }}>{timeAgo(c.created_at)}</span>
                    <span style={{ fontSize: "0.6rem", color: "#333" }}>on: {c.post_title || `post #${c.post_id}`}</span>
                  </div>
                </Link>
              ))
            )}
          </div>
        )}

      </div>
    </main>
  );
}
