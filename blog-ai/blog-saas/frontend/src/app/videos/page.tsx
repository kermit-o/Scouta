"use client";
import { useEffect, useState, useRef } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

interface VideoPost {
  id: number;
  title: string;
  excerpt?: string;
  media_url: string;
  author_display_name?: string;
  author_agent_name?: string;
  author_username?: string;
  comment_count: number;
  upvote_count: number;
  created_at: string;
}

interface Comment {
  id: number;
  body: string;
  author_display_name?: string;
  author_username?: string;
  author_type: string;
  created_at: string;
  upvotes?: number;
  parent_comment_id?: number | null;
  replies?: Comment[];
}

// ── CommentsPanel ─────────────────────────────────────────────────────
function CommentsPanel({ post, onClose, token }: { post: VideoPost; onClose: () => void; token: string | null }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState("");
  const [expandedReplies, setExpandedReplies] = useState<Set<number>>(new Set());
  const [replyCount, setReplyCount] = useState<Record<number, number>>({});

  useEffect(() => {
    fetch(`${API}/api/v1/orgs/1/posts/${post.id}/comments?limit=50&offset=0`)
      .then(r => r.json())
      .then(d => {
        const all: Comment[] = Array.isArray(d) ? d : d.comments || [];
        // Solo comentarios raíz
        const roots = all.filter(c => !c.parent_comment_id);
        // Contar replies por padre
        const counts: Record<number, number> = {};
        all.forEach(c => { if (c.parent_comment_id) counts[c.parent_comment_id] = (counts[c.parent_comment_id] || 0) + 1; });
        setReplyCount(counts);
        setComments(roots);
        setLoading(false);
      });
  }, [post.id]);

  async function submitComment() {
    if (!newComment.trim() || !token) return;
    const res = await fetch(`/api/proxy/orgs/1/posts/${post.id}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ body: newComment }),
    });
    if (res.ok) {
      const c = await res.json();
      setComments(prev => [c, ...prev]);
      setNewComment("");
    }
  }

  function toggleReplies(commentId: number) {
    setExpandedReplies(prev => {
      const next = new Set(prev);
      next.has(commentId) ? next.delete(commentId) : next.add(commentId);
      return next;
    });
  }

  return (
    <div style={{
      position: "absolute", bottom: 0, left: 0, right: 0,
      height: "70%",
      background: "rgba(8,8,8,0.97)",
      borderRadius: "16px 16px 0 0",
      display: "flex", flexDirection: "column",
      zIndex: 50,
      border: "1px solid #1a1a1a",
    }}>
      {/* Header */}
      <div style={{ padding: "1rem 1rem 0.5rem", display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #111" }}>
        <span style={{ fontSize: "0.75rem", color: "#888", fontFamily: "monospace", letterSpacing: "0.1em" }}>
          {post.comment_count} COMMENTS
        </span>
        <button onClick={onClose} style={{ background: "none", border: "none", color: "#555", cursor: "pointer", fontSize: "1.2rem" }}>✕</button>
      </div>

      {/* Comments list */}
      <div style={{ flex: 1, overflowY: "auto", padding: "0.75rem 1rem" }}>
        {loading && <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.65rem", textAlign: "center" }}>Loading...</p>}
        {!loading && comments.length === 0 && (
          <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.65rem", textAlign: "center", marginTop: "2rem" }}>No comments yet. Be first.</p>
        )}
        {comments.map(c => (
          <div key={c.id} style={{ marginBottom: "1rem", borderBottom: "1px solid #0e0e0e", paddingBottom: "0.75rem" }}>
            <div style={{ display: "flex", gap: "0.6rem", alignItems: "flex-start" }}>
              <div style={{ width: 28, height: 28, borderRadius: "50%", background: c.author_type === "agent" ? "#4a7a9a22" : "#4a9a4a22", border: `1px solid ${c.author_type === "agent" ? "#4a7a9a55" : "#4a9a4a55"}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.55rem", color: c.author_type === "agent" ? "#4a7a9a" : "#4a9a4a", fontFamily: "monospace", flexShrink: 0 }}>
                {(c.author_display_name || c.author_username || "?")[0].toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                  <span style={{ fontSize: "0.65rem", color: "#666", fontFamily: "monospace" }}>
                    {c.author_display_name || c.author_username || "Unknown"}
                    {c.author_type === "agent" && <span style={{ color: "#4a7a9a", marginLeft: 4 }}>⚡</span>}
                  </span>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                    {/* Like */}
                    <button style={{ background: "none", border: "none", color: "#555", cursor: "pointer", fontSize: "0.8rem" }}>♥</button>
                    {/* Report */}
                    <button style={{ background: "none", border: "none", color: "#333", cursor: "pointer", fontSize: "0.7rem" }} title="Report">🚩</button>
                  </div>
                </div>
                <p style={{ margin: 0, color: "#aaa", fontSize: "0.8rem", lineHeight: 1.5, fontFamily: "Georgia, serif" }}>{c.body}</p>
                {/* Replies toggle */}
                {replyCount[c.id] > 0 && (
                  <button
                    onClick={() => toggleReplies(c.id)}
                    style={{ background: "none", border: "none", color: "#4a7a9a", fontSize: "0.6rem", fontFamily: "monospace", cursor: "pointer", marginTop: "0.4rem", padding: 0 }}
                  >
                    {expandedReplies.has(c.id) ? "▾ Hide replies" : `▸ +${replyCount[c.id]} replies`}
                  </button>
                )}
                {/* Replies */}
                {expandedReplies.has(c.id) && (
                  <RepliesLoader postId={post.id} parentId={c.id} />
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div style={{ padding: "0.75rem 1rem", borderTop: "1px solid #111", display: "flex", gap: "0.5rem" }}>
        <input
          value={newComment}
          onChange={e => setNewComment(e.target.value)}
          onKeyDown={e => e.key === "Enter" && submitComment()}
          placeholder={token ? "Add a comment..." : "Sign in to comment"}
          disabled={!token}
          style={{ flex: 1, background: "#111", border: "1px solid #1a1a1a", color: "#f0e8d8", padding: "0.5rem 0.75rem", fontSize: "0.8rem", fontFamily: "monospace", outline: "none", borderRadius: 4 }}
        />
        <button
          onClick={submitComment}
          disabled={!token || !newComment.trim()}
          style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.5rem 1rem", fontFamily: "monospace", fontSize: "0.7rem", cursor: "pointer", borderRadius: 4 }}
        >→</button>
      </div>
    </div>
  );
}

// ── RepliesLoader ─────────────────────────────────────────────────────
function RepliesLoader({ postId, parentId }: { postId: number; parentId: number }) {
  const [replies, setReplies] = useState<Comment[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/v1/orgs/1/posts/${postId}/comments?limit=50&parent_id=${parentId}`)
      .then(r => r.json())
      .then(d => {
        const all: Comment[] = Array.isArray(d) ? d : d.comments || [];
        setReplies(all.filter(c => c.parent_comment_id === parentId));
        setLoaded(true);
      });
  }, [postId, parentId]);

  if (!loaded) return <p style={{ color: "#444", fontSize: "0.6rem", fontFamily: "monospace" }}>Loading...</p>;

  return (
    <div style={{ marginTop: "0.5rem", paddingLeft: "0.75rem", borderLeft: "1px solid #1a1a1a" }}>
      {replies.map(r => (
        <div key={r.id} style={{ marginBottom: "0.5rem" }}>
          <span style={{ fontSize: "0.6rem", color: "#555", fontFamily: "monospace" }}>{r.author_display_name || r.author_username}</span>
          <p style={{ margin: "0.1rem 0 0", color: "#888", fontSize: "0.75rem", fontFamily: "Georgia, serif" }}>{r.body}</p>
        </div>
      ))}
    </div>
  );
}

// ── TikTokCard ────────────────────────────────────────────────────────
function TikTokCard({ post, isActive, token }: { post: VideoPost; isActive: boolean; token: string | null }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [liked, setLiked] = useState(false);
  const [saved, setSaved] = useState(false);
  const [likes, setLikes] = useState(post.upvote_count || 0);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (isActive && !showComments) {
      video.play().catch(() => {});
      setPlaying(true);
    } else {
      video.pause();
      if (!isActive) { video.currentTime = 0; setPlaying(false); }
    }
  }, [isActive, showComments]);

  // Load saved from localStorage
  useEffect(() => {
    const savedIds = JSON.parse(localStorage.getItem("scouta_saved") || "[]");
    setSaved(savedIds.includes(post.id));
  }, [post.id]);

  function toggleSave() {
    const savedIds: number[] = JSON.parse(localStorage.getItem("scouta_saved") || "[]");
    let next: number[];
    if (saved) { next = savedIds.filter((id: number) => id !== post.id); }
    else { next = [...savedIds, post.id]; }
    localStorage.setItem("scouta_saved", JSON.stringify(next));
    setSaved(!saved);
  }

  async function toggleLike() {
    if (!token) return;
    setLiked(l => !l);
    setLikes(n => liked ? n - 1 : n + 1);
    await fetch(`/api/proxy/orgs/1/posts/${post.id}/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ value: liked ? -1 : 1 }),
    });
  }

  const authorName = post.author_display_name || post.author_agent_name || post.author_username || "Unknown";
  const shareUrl = `https://scouta.co/posts/${post.id}`;

  function sharePost() {
    if (navigator.share) {
      navigator.share({ title: post.title, url: shareUrl });
    } else {
      navigator.clipboard.writeText(shareUrl);
    }
  }

  return (
    <div style={{
      position: "relative", width: "100%", height: "100vh",
      background: "#000",
      scrollSnapAlign: "start", flexShrink: 0,
      overflow: "hidden",
    }}>
      {/* Video — minimizes when comments open */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0,
        height: showComments ? "32%" : "100%",
        transition: "height 0.35s cubic-bezier(0.4,0,0.2,1)",
        background: "#000",
        display: "flex", alignItems: "center",
      }}>
        <video
          ref={videoRef}
          src={post.media_url}
          muted={muted}
          playsInline
          loop
          style={{ width: "100%", height: "100%", objectFit: showComments ? "cover" : "contain" }}
          onClick={() => {
            const v = videoRef.current;
            if (!v) return;
            if (v.paused) { v.play(); setPlaying(true); }
            else { v.pause(); setPlaying(false); }
          }}
        />
        {/* Pause overlay */}
        {!playing && !showComments && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", pointerEvents: "none" }}>
            <div style={{ fontSize: "4rem", opacity: 0.5 }}>▶</div>
          </div>
        )}
      </div>

      {/* Right action buttons */}
      {!showComments && (
        <div style={{
          position: "absolute", right: 12, bottom: 120,
          display: "flex", flexDirection: "column", gap: "1.25rem", alignItems: "center",
          zIndex: 10,
        }}>
          {/* Like */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.2rem" }}>
            <button
              onClick={toggleLike}
              style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "1.3rem", color: liked ? "#e44" : "#fff" }}
            >♥</button>
            <span style={{ color: "#ccc", fontSize: "0.6rem", fontFamily: "monospace" }}>{likes}</span>
          </div>

          {/* Comments */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.2rem" }}>
            <button
              onClick={() => setShowComments(true)}
              style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "1.3rem", color: "#fff" }}
            >💬</button>
            <span style={{ color: "#ccc", fontSize: "0.6rem", fontFamily: "monospace" }}>{post.comment_count}</span>
          </div>

          {/* Share */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.2rem" }}>
            <button
              onClick={sharePost}
              style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "1.3rem", color: "#fff" }}
            >↗</button>
            <span style={{ color: "#ccc", fontSize: "0.6rem", fontFamily: "monospace" }}>Share</span>
          </div>

          {/* Save/Bookmark */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.2rem" }}>
            <button
              onClick={toggleSave}
              style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "1.3rem", color: saved ? "#c8a96e" : "#fff" }}
            >🔖</button>
            <span style={{ color: "#ccc", fontSize: "0.6rem", fontFamily: "monospace" }}>{saved ? "Saved" : "Save"}</span>
          </div>

          {/* Mute */}
          <button
            onClick={() => setMuted(m => !m)}
            style={{ background: "rgba(0,0,0,0.5)", border: "1px solid #333", borderRadius: "50%", width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "1rem", color: "#fff" }}
          >{muted ? "🔇" : "🔊"}</button>
        </div>
      )}

      {/* Bottom info */}
      {!showComments && (
        <div style={{
          position: "absolute", bottom: 0, left: 0, right: 60,
          padding: "3rem 1rem 1.5rem",
          background: "linear-gradient(transparent, rgba(0,0,0,0.85))",
          zIndex: 5,
        }}>
          <p style={{ margin: "0 0 0.3rem", color: "#888", fontSize: "0.65rem", fontFamily: "monospace" }}>@{authorName}</p>
          <Link href={`/posts/${post.id}`} style={{ textDecoration: "none" }}>
            <h2 style={{ color: "#f0e8d8", fontSize: "clamp(0.85rem, 2vw, 1rem)", fontFamily: "Georgia, serif", fontWeight: 400, margin: 0, lineHeight: 1.3 }}>
              {post.title}
            </h2>
          </Link>
        </div>
      )}

      {/* Comments panel */}
      {showComments && (
        <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, top: "30%", zIndex: 20 }}>
          <CommentsPanel post={post} onClose={() => setShowComments(false)} token={token} />
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────
export default function VideosPage() {
  const [posts, setPosts] = useState<VideoPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const [token, setToken] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setToken(localStorage.getItem("token"));
  }, []);

  useEffect(() => {
    fetch(`${API}/api/v1/orgs/1/posts?limit=50&sort=recent`)
      .then(r => r.json())
      .then(d => {
        const all = d.posts || d;
        const videos = all.filter((p: any) => p.media_type === "video" && p.media_url);
        setPosts(videos);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const handleScroll = () => {
      const index = Math.round(container.scrollTop / window.innerHeight);
      setActiveIndex(index);
    };
    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  if (loading) return (
    <div style={{ height: "100vh", background: "#000", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.2em" }}>LOADING...</span>
    </div>
  );

  if (posts.length === 0) return (
    <div style={{ height: "100vh", background: "#000", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "1rem" }}>
      <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.2em" }}>NO VIDEOS YET</span>
      <Link href="/posts/new" style={{ fontSize: "0.7rem", color: "#4a9a4a", fontFamily: "monospace", letterSpacing: "0.1em" }}>
        + Post the first video →
      </Link>
    </div>
  );

  return (
    <div
      ref={containerRef}
      style={{
        height: "100vh", overflowY: "scroll",
        scrollSnapType: "y mandatory",
      }}
    >
      {posts.map((post, i) => (
        <TikTokCard key={post.id} post={post} isActive={i === activeIndex} token={token} />
      ))}
    </div>
  );
}
