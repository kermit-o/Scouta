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
  const { token, logout } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) { router.push("/login?next=/profile"); return; }
    const API = "/api/proxy";
    fetch(`${API}/api/v1/profile/me`, {
      headers: { "Authorization": `Bearer ${token}` },
    }).then(r => r.json()).then(d => { setData(d); setLoading(false); });
  }, [token]);

  if (loading) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
    </main>
  );

  const initials = (name: string) => name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace" }}>
      {/* Nav */}
      <nav style={{ padding: "1.25rem 2rem", borderBottom: "1px solid #141414", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <Link href="/posts" style={{ fontSize: "0.7rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#555", textDecoration: "none" }}>← The Feed</Link>
        <Link href="/profile/edit" style={{ background: "none", border: "1px solid #2a2a2a", color: "#4a7a9a", padding: "0.3rem 0.75rem", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.1em", textDecoration: "none", marginRight: "0.5rem" }}>Edit Profile</Link>
        <button onClick={() => { logout(); router.push("/"); }} style={{ background: "none", border: "1px solid #2a2a2a", color: "#555", padding: "0.3rem 0.75rem", cursor: "pointer", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>
          Logout
        </button>
      </nav>

      <div style={{ maxWidth: "640px", margin: "0 auto", padding: "2.5rem 1.5rem" }}>
        {/* Profile header */}
        <div style={{ marginBottom: "2rem", paddingBottom: "2rem", borderBottom: "1px solid #141414" }}>
          <div style={{ display: "flex", alignItems: "flex-start", gap: "1.25rem" }}>
            {/* Avatar */}
            <div style={{ width: 72, height: 72, borderRadius: "50%", background: "#6a8a6a22", border: "2px solid #6a8a6a55", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.5rem", color: "#6a8a6a", fontWeight: 700, flexShrink: 0 }}>
              {initials(data.display_name || data.username || "U")}
            </div>
            <div style={{ flex: 1 }}>
              <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#f0e8d8", margin: "0 0 0.25rem" }}>
                {data.display_name || data.username}
              </h1>
              <p style={{ fontSize: "0.8rem", color: "#444", margin: "0 0 0.5rem" }}>@{data.username}</p>
              {data.bio && <p style={{ fontSize: "0.875rem", color: "#666", margin: "0 0 0.75rem", lineHeight: 1.6, fontFamily: "Georgia, serif" }}>{data.bio}</p>}
              <p style={{ fontSize: "0.65rem", color: "#333", margin: 0 }}>Joined {new Date(data.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}</p>
            </div>
          </div>

          {/* Stats */}
          <div style={{ display: "flex", gap: "2rem", marginTop: "1.5rem" }}>
            {[
              { label: "Comments", value: data.comment_count },
              { label: "Likes received", value: data.likes_received },
              { label: "Followers", value: data.followers },
              { label: "Following", value: data.following },
            ].map(s => (
              <div key={s.label}>
                <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "#f0e8d8" }}>{s.value}</div>
                <div style={{ fontSize: "0.6rem", color: "#444", letterSpacing: "0.1em", textTransform: "uppercase" }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent activity */}
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
                    <span style={{ fontSize: "0.6rem", color: c.source === "human" ? "#4a9a4a" : "#4a6a9a", letterSpacing: "0.1em", textTransform: "uppercase" }}>
                      {c.source === "human" ? "comment" : c.source}
                    </span>
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

        {/* Public profile link */}
        {data.username && (
          <div style={{ marginTop: "2rem", paddingTop: "1.5rem", borderTop: "1px solid #141414" }}>
            <Link href={`/u/${data.username}`} style={{ fontSize: "0.7rem", color: "#4a7a9a", textDecoration: "none", letterSpacing: "0.1em" }}>
              View public profile →
            </Link>
          </div>
        )}
      </div>
    </main>
  );
}
