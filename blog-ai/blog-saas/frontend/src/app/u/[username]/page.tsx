"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

interface Profile {
  id: number;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  website?: string;
  location?: string;
  created_at: string;
  comment_count: number;
  likes_received: number;
  followers: number;
  following: number;
  recent_comments?: Array<{ id: number; post_id: number; body: string; created_at: string }>;
}

interface Post {
  id: number;
  title: string;
  excerpt?: string;
  body_md?: string;
  author_username?: string;
  author_display_name?: string;
  comment_count: number;
  upvote_count: number;
  media_url?: string;
  media_type?: string;
  created_at: string;
}

const API = "/api/proxy/api/v1";

function timeAgo(s: string): string {
  try {
    const m = Math.floor((Date.now() - new Date(s).getTime()) / 60000);
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

export default function PublicProfilePage() {
  const params = useParams<{ username: string }>();
  const username = params.username;
  const { token } = useAuth();
  const [data, setData] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);
  const [followers, setFollowers] = useState(0);
  const [followLoading, setFollowLoading] = useState(false);
  const [tab, setTab] = useState<"posts" | "videos" | "comments">("posts");
  const [posts, setPosts] = useState<Post[]>([]);
  const [postsLoading, setPostsLoading] = useState(false);

  useEffect(() => {
    fetch(`${API}/u/${username}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        setData(d);
        setFollowers(d?.followers ?? 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [username]);

  useEffect(() => {
    if (!data) return;
    setPostsLoading(true);
    fetch(`${API}/orgs/1/posts?limit=50&sort=recent`)
      .then((r) => r.json())
      .then((d) => {
        const all: Post[] = d.posts || d || [];
        const userPosts = all.filter(
          (p) => p.author_username === username || p.author_display_name === data.display_name
        );
        setPosts(userPosts);
        setPostsLoading(false);
      })
      .catch(() => setPostsLoading(false));
  }, [data, username]);

  async function handleFollow() {
    if (!token) {
      window.location.href = `/login?next=/u/${username}`;
      return;
    }
    setFollowLoading(true);
    const res = await fetch(`${API}/u/${username}/follow`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    const d = await res.json();
    setFollowing(d.action === "followed");
    setFollowers(d.followers);
    setFollowLoading(false);
  }

  if (loading) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
        </div>
      </main>
    );
  }

  if (!data || (data as any).detail) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <p style={{ fontSize: "3rem", color: "#1a1a1a", margin: "0 0 1rem", lineHeight: 1, fontFamily: "monospace" }}>⬡</p>
          <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.95rem", marginBottom: "0.4rem" }}>User not found.</p>
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", marginBottom: "1.5rem" }}>
            @{username} doesn't exist or has been removed.
          </p>
          <Link href="/posts" style={ctaSecondary}>← Back to feed</Link>
        </div>
      </main>
    );
  }

  const displayName = data.display_name || data.username;
  const textPosts = posts.filter((p) => !p.media_url);
  const videos = posts.filter((p) => p.media_type === "video");

  return (
    <main style={pageStyle}>
      <div style={container}>
        {/* Profile header */}
        <div style={{ display: "flex", alignItems: "flex-start", gap: "1.5rem", marginBottom: "1.5rem" }}>
          {/* Avatar */}
          {data.avatar_url ? (
            <img
              src={data.avatar_url}
              alt={displayName}
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
              {initials(displayName)}
            </div>
          )}

          {/* Identity */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={eyebrow}>SCOUTA / @{data.username.toUpperCase()}</p>
            <h1 style={{
              fontSize: "clamp(1.5rem, 3.5vw, 2rem)", fontWeight: 400,
              fontFamily: "Georgia, serif", color: "#f0e8d8",
              margin: "0.4rem 0 0.25rem",
            }}>
              {displayName}
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
              <span style={metaText}>
                Joined {new Date(data.created_at).toLocaleDateString("en-US", { month: "long", year: "numeric" })}
              </span>
              {data.location && <span style={metaText}>· {data.location}</span>}
              {data.website && (
                <a href={data.website} target="_blank" rel="noreferrer" style={{ ...metaText, color: "#4a7a9a", textDecoration: "none" }}>
                  · {data.website.replace(/^https?:\/\//, "")}
                </a>
              )}
            </div>
          </div>
        </div>

        {/* Action row */}
        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap", marginBottom: "2rem" }}>
          <button
            onClick={handleFollow}
            disabled={followLoading}
            style={following ? followingBtn : followBtn}
          >
            {followLoading ? "..." : following ? "Following" : "+ Follow"}
          </button>
          {token && (
            <Link href={`/messages/new?to=${data.username}`} style={ctaSecondary}>
              Message
            </Link>
          )}
        </div>

        {/* Stats grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
          gap: "0.5rem",
          marginBottom: "2rem",
          paddingBottom: "1.5rem",
          borderBottom: "1px solid #141414",
        }}>
          <Stat label="POSTS" value={textPosts.length + videos.length} />
          <Stat label="COMMENTS" value={data.comment_count} />
          <Stat label="LIKES" value={data.likes_received} />
          <StatLink label="FOLLOWERS" value={followers} href={`/u/${username}/followers`} />
          <StatLink label="FOLLOWING" value={data.following} href={`/u/${username}/following`} />
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 0, marginBottom: "1.25rem", borderBottom: "1px solid #1a1a1a" }}>
          <Tab label={`Posts (${textPosts.length})`} active={tab === "posts"} onClick={() => setTab("posts")} />
          <Tab label={`Videos (${videos.length})`} active={tab === "videos"} onClick={() => setTab("videos")} />
          <Tab label={`Comments (${data.comment_count})`} active={tab === "comments"} onClick={() => setTab("comments")} />
        </div>

        {/* Tab content */}
        {tab === "posts" && (
          <div>
            {postsLoading && <p style={mutedText}>Loading...</p>}
            {!postsLoading && textPosts.length === 0 && (
              <Empty body="No posts yet." sub={`@${data.username} hasn't written anything.`} />
            )}
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
                  <div style={{ display: "flex", gap: "1rem", color: "#444", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.05em" }}>
                    <span>{timeAgo(p.created_at)}</span>
                    <span>{p.comment_count} comments</span>
                    <span>↑ {p.upvote_count}</span>
                  </div>
                </article>
              </Link>
            ))}
          </div>
        )}

        {tab === "videos" && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 4 }}>
            {postsLoading && <p style={{ ...mutedText, gridColumn: "1/-1" }}>Loading...</p>}
            {!postsLoading && videos.length === 0 && (
              <div style={{ gridColumn: "1/-1" }}>
                <Empty body="No videos yet." sub={`@${data.username} hasn't posted any video.`} />
              </div>
            )}
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
        )}

        {tab === "comments" && (
          <div>
            {(!data.recent_comments || data.recent_comments.length === 0) && (
              <Empty body="No comments yet." sub={`@${data.username} hasn't replied to anything.`} />
            )}
            {data.recent_comments?.map((c) => (
              <Link key={c.id} href={`/posts/${c.post_id}#comment-${c.id}`} style={{ textDecoration: "none", display: "block" }}>
                <div style={postRow}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.4rem", alignItems: "center" }}>
                    <span style={{ fontSize: "0.55rem", color: "#555", letterSpacing: "0.2em", textTransform: "uppercase", fontFamily: "monospace" }}>
                      Comment
                    </span>
                    <span style={{ fontSize: "0.65rem", color: "#333", fontFamily: "monospace" }}>{timeAgo(c.created_at)}</span>
                  </div>
                  <p style={{ fontSize: "0.875rem", color: "#888", margin: 0, lineHeight: 1.6, fontFamily: "Georgia, serif" }}>
                    {c.body}
                  </p>
                </div>
              </Link>
            ))}
          </div>
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
        color: active ? "#f0e8d8" : "#555",
        cursor: "pointer",
        borderBottom: active ? "1.5px solid #f0e8d8" : "1.5px solid transparent",
        marginBottom: "-1px", fontFamily: "monospace",
      }}
    >
      {label}
    </button>
  );
}

function Empty({ body, sub }: { body: string; sub: string }) {
  return (
    <div style={{ padding: "3rem 1.5rem", textAlign: "center", border: "1px dashed #1a1a1a", background: "#0a0a0a" }}>
      <p style={{ color: "#666", fontSize: "0.9rem", fontFamily: "Georgia, serif", marginBottom: "0.4rem" }}>{body}</p>
      <p style={{ color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.05em" }}>{sub}</p>
    </div>
  );
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#e8e0d0" };
const container: React.CSSProperties = { maxWidth: "780px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" };
const eyebrow: React.CSSProperties = { fontSize: "0.55rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: 0 };
const metaText: React.CSSProperties = { color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.05em" };
const mutedText: React.CSSProperties = { color: "#444", fontSize: "0.75rem", fontFamily: "monospace" };
const followBtn: React.CSSProperties = {
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.55rem 1.5rem", cursor: "pointer",
  fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
};
const followingBtn: React.CSSProperties = {
  background: "transparent", border: "1px solid #2a2a2a", color: "#666",
  padding: "0.55rem 1.5rem", cursor: "pointer",
  fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
};
const ctaSecondary: React.CSSProperties = {
  background: "transparent", border: "1px solid #2a2a2a", color: "#888",
  padding: "0.55rem 1.5rem", textDecoration: "none",
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
