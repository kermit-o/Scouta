"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
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

export default function PublicProfilePage() {
  const { username } = useParams();
  const { token } = useAuth();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);
  const [followers, setFollowers] = useState(0);
  const [followLoading, setFollowLoading] = useState(false);

  const API = "/api/proxy";

  useEffect(() => {
    fetch(`${API}/api/v1/u/${username}`)
      .then(r => r.json())
      .then(d => {
        setData(d);
        setFollowers(d.followers);
        setLoading(false);
      });
  }, [username]);

  async function handleFollow() {
    if (!token) { window.location.href = `/login?next=/u/${username}`; return; }
    setFollowLoading(true);
    const res = await fetch(`${API}/api/v1/u/${username}/follow`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${token}` },
    });
    const d = await res.json();
    setFollowing(d.action === "followed");
    setFollowers(d.followers);
    setFollowLoading(false);
  }

  if (loading) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
    </main>
  );

  if (!data || data.detail) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#555", fontFamily: "monospace" }}>User not found.</p>
    </main>
  );

  const initials = (name: string) => name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace" }}>
      <nav style={{ padding: "1.25rem 2rem", borderBottom: "1px solid #141414" }}>
        <Link href="/posts" style={{ fontSize: "0.7rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#555", textDecoration: "none" }}>← The Feed</Link>
      </nav>

      <div style={{ maxWidth: "640px", margin: "0 auto", padding: "2.5rem 1.5rem" }}>
        {/* Profile header */}
        <div style={{ marginBottom: "2rem", paddingBottom: "2rem", borderBottom: "1px solid #141414" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "1.25rem" }}>
            <div style={{ width: 72, height: 72, borderRadius: "50%", background: "#6a8a6a22", border: "2px solid #6a8a6a55", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.5rem", color: "#6a8a6a", fontWeight: 700, flexShrink: 0 }}>
              {initials(data.display_name || data.username || "U")}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
                <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#f0e8d8", margin: 0 }}>
                  {data.display_name || data.username}
                </h1>
                <button onClick={handleFollow} disabled={followLoading} style={{
                  background: following ? "none" : "#1a2a1a",
                  border: `1px solid ${following ? "#2a2a2a" : "#2a4a2a"}`,
                  color: following ? "#555" : "#4a9a4a",
                  padding: "0.3rem 0.875rem", cursor: "pointer",
                  fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.1em",
                }}>
                  {followLoading ? "..." : following ? "Following" : "+ Follow"}
                </button>
              </div>
              <p style={{ fontSize: "0.8rem", color: "#444", margin: "0.25rem 0 0.5rem" }}>@{data.username}</p>
              {data.bio && <p style={{ fontSize: "0.875rem", color: "#666", margin: "0 0 0.5rem", lineHeight: 1.6, fontFamily: "Georgia, serif" }}>{data.bio}</p>}
              <p style={{ fontSize: "0.65rem", color: "#333", margin: 0 }}>Joined {new Date(data.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}</p>
            </div>
          </div>

          {/* Stats */}
          <div style={{ display: "flex", gap: "2rem", marginTop: "1.5rem" }}>
            {[
              { label: "Comments", value: data.comment_count },
              { label: "Likes", value: data.likes_received },
              { label: "Followers", value: followers, href: `/u/${username}/followers` },
              { label: "Following", value: data.following, href: `/u/${username}/following` },
            ].map((s: any) => (
              s.href ? (
                <Link key={s.label} href={s.href} style={{ textDecoration: "none" }}>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f0e8d8" }}>{s.value}</div>
                  <div style={{ fontSize: "0.6rem", color: "#4a7a9a", letterSpacing: "0.1em", textTransform: "uppercase" }}>{s.label}</div>
                </Link>
              ) : (
                <div key={s.label}>
                  <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f0e8d8" }}>{s.value}</div>
                  <div style={{ fontSize: "0.6rem", color: "#444", letterSpacing: "0.1em", textTransform: "uppercase" }}>{s.label}</div>
                </div>
              )
            ))}
          </div>
        </div>

        {/* Recent comments */}
        <div>
          <h2 style={{ fontSize: "0.65rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#555", marginBottom: "1.25rem" }}>
            Recent Comments
          </h2>
          {data.recent_comments?.length === 0 ? (
            <p style={{ fontSize: "0.8rem", color: "#333" }}>No comments yet.</p>
          ) : (
            data.recent_comments?.map((c: any) => (
              <Link key={c.id} href={`/posts/${c.post_id}#comment-${c.id}`} style={{ textDecoration: "none", display: "block" }}>
                <div style={{ padding: "0.875rem 0", borderBottom: "1px solid #0f0f0f" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem" }}>
                    <span style={{ fontSize: "0.6rem", color: "#4a9a4a", letterSpacing: "0.1em", textTransform: "uppercase" }}>comment</span>
                    <span style={{ fontSize: "0.65rem", color: "#333" }}>{timeAgo(c.created_at)}</span>
                  </div>
                  <p style={{ fontSize: "0.875rem", color: "#888", margin: 0, lineHeight: 1.6, fontFamily: "Georgia, serif" }}>
                    {c.body}...
                  </p>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </main>
  );
}
