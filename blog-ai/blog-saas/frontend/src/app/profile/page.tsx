"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Profile {
  id: number;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
  website?: string;
  likes_received?: number;
  followers?: number;
  following?: number;
}

interface MyPost {
  id: number;
  title: string;
  excerpt?: string;
  comment_count: number;
  upvote_count?: number;
  created_at: string;
  debate_status?: string;
  media_url?: string;
  media_type?: string;
}

interface MyComment {
  id: number;
  post_id: number;
  body: string;
  post_title?: string;
  created_at: string;
}

const API = "/api/proxy/api/v1";

function timeAgo(dateStr: string): string {
  try {
    const m = Math.floor((Date.now() - new Date(dateStr).getTime()) / 60000);
    if (m < 1) return "just now";
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h / 24)}d`;
  } catch { return ""; }
}

function initials(name: string): string {
  return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}

export default function ProfilePage() {
  const { token, logout, isLoaded } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<Profile | null>(null);
  const [posts, setPosts] = useState<MyPost[]>([]);
  const [comments, setComments] = useState<MyComment[]>([]);
  const [tab, setTab] = useState<"posts" | "videos" | "comments">("posts");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoaded) return;
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    if (!t) { router.push("/login?next=/profile"); return; }
    Promise.all([
      fetch(`${API}/profile/me`, { headers: { Authorization: `Bearer ${t}` } }).then((r) => r.ok ? r.json() : null),
      fetch(`${API}/profile/my-posts`, { headers: { Authorization: `Bearer ${t}` } }).then((r) => r.ok ? r.json() : []).catch(() => []),
      fetch(`${API}/profile/my-comments`, { headers: { Authorization: `Bearer ${t}` } }).then((r) => r.ok ? r.json() : []).catch(() => []),
    ]).then(([profile, myPosts, myComments]) => {
      setData(profile);
      setPosts(Array.isArray(myPosts) ? myPosts : (myPosts?.posts || []));
      setComments(Array.isArray(myComments) ? myComments : (myComments?.comments || []));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [isLoaded, token]);

  if (loading || !data) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
        </div>
      </main>
    );
  }

  const name = data.display_name || data.username;
  const textPosts = posts.filter((p) => !p.media_url);
  const videos = posts.filter((p) => p.media_type === "video");

  return (
    <main style={pageStyle}>
      <div style={container}>
        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: "1.5rem", marginBottom: "1.5rem" }}>
          {data.avatar_url ? (
            <img
              src={data.avatar_url}
              alt={name}
              style={{ width: 96, height: 96, borderRadius: "50%", objectFit: "cover", flexShrink: 0, border: "1px solid #1a1a1a" }}
            />
          ) : (
            <div
              style={{
                width: 96, height: 96, borderRadius: "50%",
                background: "#1a2a1a", border: "1px solid #2a4a2a",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.75rem", color: "#4a9a4a",
                fontFamily: "monospace", fontWeight: 700, flexShrink: 0,
              }}
            >
              {initials(name)}
            </div>
          )}

          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={eyebrow}>SCOUTA / MY PROFILE</p>
            <h1 style={{
              fontSize: "clamp(1.5rem, 3.5vw, 2rem)", fontWeight: 400,
              fontFamily: "Georgia, serif", color: "#f0e8d8",
              margin: "0.4rem 0 0.25rem",
            }}>
              {name}
            </h1>
            <p style={{ color: "#555", fontSize: "0.78rem", fontFamily: "monospace", margin: 0 }}>
              @{data.username}
            </p>
            {data.bio && (
              <p style={{
                color: "#888", fontSize: "0.9rem", fontFamily: "Georgia, serif",
                margin: "0.85rem 0 0", lineHeight: 1.6, maxWidth: "560px",
              }}>
                {data.bio}
              </p>
            )}
            <div style={{ display: "flex", gap: "1rem", marginTop: "0.85rem", flexWrap: "wrap", alignItems: "center" }}>
              {data.location && <span style={metaText}>{data.location}</span>}
              {data.website && (
                <a href={data.website} target="_blank" rel="noreferrer" style={{ ...metaText, color: "#4a7a9a", textDecoration: "none" }}>
                  {data.website.replace(/^https?:\/\//, "")}
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Action row */}
        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "2rem" }}>
          <Link href="/profile/edit" style={ctaPrimary}>Edit profile</Link>
          <Link href={`/u/${data.username}`} style={ctaSecondary}>View public profile</Link>
          <Link href="/studio" style={ctaSecondary}>Studio</Link>
          <button
            onClick={() => { logout(); router.push("/"); }}
            style={{ ...ctaSecondary, background: "transparent", border: "1px solid #2a1a1a", color: "#9a6a6a", cursor: "pointer", fontFamily: "monospace" }}
          >
            Log out
          </button>
        </div>

        {/* Stats */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
          gap: "0.5rem",
          marginBottom: "2rem",
          paddingBottom: "1.5rem",
          borderBottom: "1px solid #141414",
        }}>
          <Stat label="POSTS" value={textPosts.length + videos.length} />
          <Stat label="COMMENTS" value={comments.length} />
          <Stat label="LIKES" value={data.likes_received ?? 0} />
          <StatLink label="FOLLOWERS" value={data.followers ?? 0} href={`/u/${data.username}/followers`} />
          <StatLink label="FOLLOWING" value={data.following ?? 0} href={`/u/${data.username}/following`} />
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 0, marginBottom: "1.25rem", borderBottom: "1px solid #1a1a1a" }}>
          <Tab label={`Posts (${textPosts.length})`} active={tab === "posts"} onClick={() => setTab("posts")} />
          <Tab label={`Videos (${videos.length})`} active={tab === "videos"} onClick={() => setTab("videos")} />
          <Tab label={`Comments (${comments.length})`} active={tab === "comments"} onClick={() => setTab("comments")} />
        </div>

        {/* Posts */}
        {tab === "posts" && (
          textPosts.length === 0 ? (
            <Empty
              body="No posts yet."
              sub="Share an idea, a hot take, a question."
              cta={{ href: "/posts/new", label: "+ Write your first post" }}
            />
          ) : (
            <div>
              {textPosts.map((p) => (
                <Link key={p.id} href={`/posts/${p.id}`} style={{ textDecoration: "none", display: "block" }}>
                  <article style={postRow}>
                    <h3 style={{
                      margin: "0 0 0.4rem", fontSize: "1rem", fontWeight: 400,
                      color: "#f0e8d8", fontFamily: "Georgia, serif", lineHeight: 1.35,
                    }}>
                      {p.title}
                    </h3>
                    {p.excerpt && (
                      <p style={{ color: "#666", fontSize: "0.8rem", lineHeight: 1.6, fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>
                        {p.excerpt.slice(0, 160)}{p.excerpt.length > 160 ? "..." : ""}
                      </p>
                    )}
                    <div style={{ display: "flex", gap: "1rem", color: "#444", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.05em", alignItems: "center" }}>
                      <span>{timeAgo(p.created_at)}</span>
                      <span>{p.comment_count ?? 0} comments</span>
                      {p.upvote_count !== undefined && <span>↑ {p.upvote_count}</span>}
                      {p.debate_status === "open" && (
                        <span style={{ color: "#4a9a4a", border: "1px solid #2a4a2a", padding: "0.1rem 0.45rem", letterSpacing: "0.15em" }}>
                          DEBATING
                        </span>
                      )}
                    </div>
                  </article>
                </Link>
              ))}
            </div>
          )
        )}

        {/* Videos */}
        {tab === "videos" && (
          videos.length === 0 ? (
            <Empty
              body="No videos yet."
              sub="Post a video clip or go live to record one."
              cta={{ href: "/posts/new", label: "+ Post a video" }}
            />
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 4 }}>
              {videos.map((p) => (
                <Link
                  key={p.id}
                  href={`/posts/${p.id}`}
                  style={{ textDecoration: "none", position: "relative", display: "block", aspectRatio: "9/16", overflow: "hidden", background: "#0d0d0d", border: "1px solid #141414" }}
                >
                  <video
                    src={p.media_url}
                    muted
                    playsInline
                    preload="metadata"
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                  <div style={{
                    position: "absolute", inset: 0,
                    background: "linear-gradient(transparent 60%, rgba(0,0,0,0.75))",
                    display: "flex", alignItems: "flex-end", padding: "0.5rem 0.6rem",
                  }}>
                    <span style={{ fontSize: "0.6rem", color: "#ddd", fontFamily: "monospace", letterSpacing: "0.05em" }}>
                      ▶ {p.comment_count}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )
        )}

        {/* Comments */}
        {tab === "comments" && (
          comments.length === 0 ? (
            <Empty body="No comments yet." sub="Reply to someone's post to start a thread." />
          ) : (
            <div>
              {comments.map((c) => (
                <Link key={c.id} href={`/posts/${c.post_id}#comment-${c.id}`} style={{ textDecoration: "none", display: "block" }}>
                  <div style={postRow}>
                    <p style={{ fontSize: "0.875rem", color: "#888", fontFamily: "Georgia, serif", lineHeight: 1.6, margin: "0 0 0.4rem" }}>
                      {(c.body || "").slice(0, 200)}{c.body && c.body.length > 200 ? "..." : ""}
                    </p>
                    <div style={{ display: "flex", gap: "1rem", color: "#444", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.05em" }}>
                      <span>{timeAgo(c.created_at)}</span>
                      {c.post_title && <span>on: {c.post_title}</span>}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )
        )}
      </div>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div style={statBox}>
      <div style={statValue}>{value.toLocaleString()}</div>
      <div style={statLabel}>{label}</div>
    </div>
  );
}

function StatLink({ label, value, href }: { label: string; value: number; href: string }) {
  return (
    <Link href={href} style={{ ...statBox, textDecoration: "none", cursor: "pointer" }}>
      <div style={{ ...statValue, color: "#4a7a9a" }}>{value.toLocaleString()}</div>
      <div style={statLabel}>{label}</div>
    </Link>
  );
}

function Tab({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: "none", border: "none", padding: "0.65rem 1.1rem",
        fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase",
        color: active ? "#f0e8d8" : "#555", cursor: "pointer",
        borderBottom: active ? "1.5px solid #f0e8d8" : "1.5px solid transparent",
        marginBottom: "-1px", fontFamily: "monospace",
      }}
    >
      {label}
    </button>
  );
}

function Empty({ body, sub, cta }: { body: string; sub: string; cta?: { href: string; label: string } }) {
  return (
    <div style={{ padding: "3rem 1.5rem", textAlign: "center", border: "1px dashed #1a1a1a", background: "#0a0a0a" }}>
      <p style={{ color: "#777", fontSize: "0.95rem", fontFamily: "Georgia, serif", marginBottom: "0.4rem" }}>{body}</p>
      <p style={{ color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.05em", marginBottom: cta ? "1.25rem" : 0 }}>
        {sub}
      </p>
      {cta && (
        <Link href={cta.href} style={ctaPrimary}>
          {cta.label}
        </Link>
      )}
    </div>
  );
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#e8e0d0" };
const container: React.CSSProperties = { maxWidth: "780px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" };
const eyebrow: React.CSSProperties = { fontSize: "0.55rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: 0 };
const metaText: React.CSSProperties = { color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.05em" };
const ctaPrimary: React.CSSProperties = {
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.55rem 1.4rem", textDecoration: "none",
  fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
  display: "inline-block",
};
const ctaSecondary: React.CSSProperties = {
  background: "transparent", border: "1px solid #2a2a2a", color: "#888",
  padding: "0.55rem 1.4rem", textDecoration: "none",
  fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
  display: "inline-block",
};
const statBox: React.CSSProperties = {
  background: "#0d0d0d", border: "1px solid #1a1a1a",
  padding: "0.75rem 0.85rem",
};
const statValue: React.CSSProperties = {
  fontSize: "1.15rem", fontFamily: "monospace", color: "#f0e8d8",
  fontWeight: 600, marginBottom: "0.25rem",
};
const statLabel: React.CSSProperties = {
  fontSize: "0.55rem", letterSpacing: "0.2em",
  color: "#444", fontFamily: "monospace",
};
const postRow: React.CSSProperties = {
  padding: "1rem 0", borderBottom: "1px solid #141414",
};
