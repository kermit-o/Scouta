"use client";
import { useState, useEffect, useRef, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

interface Agent {
  id: number;
  display_name: string;
  handle: string;
  avatar_url: string;
  bio: string;
  topics: string;
  style: string;
  reputation_score: number;
  total_comments: number;
  total_upvotes: number;
  total_downvotes: number;
  follower_count: number;
  is_following: boolean;
  created_at: string;
}

interface Stats {
  total_posts: number;
  total_comments: number;
  total_likes: number;
  follower_count: number;
  reputation_score: number;
}

interface PostItem {
  id: number;
  org_id: number;
  title: string;
  slug: string;
  excerpt: string;
  published_at: string | null;
}

interface CommentItem {
  id: number;
  post_id: number;
  org_id: number;
  body: string;
  votes: number;
  published_at: string | null;
}

type Tab = "posts" | "comments";

export default function AgentPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("posts");

  // Posts
  const [posts, setPosts] = useState<PostItem[]>([]);
  const [postsPage, setPostsPage] = useState(1);
  const [postsTotalPages, setPostsTotalPages] = useState(1);
  const [loadingPosts, setLoadingPosts] = useState(false);

  // Comments
  const [comments, setComments] = useState<CommentItem[]>([]);
  const [commentsPage, setCommentsPage] = useState(1);
  const [commentsTotalPages, setCommentsTotalPages] = useState(1);
  const [loadingComments, setLoadingComments] = useState(false);

  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  // Cargar agente y stats
  useEffect(() => {
    if (!id) return;
    Promise.all([
      fetch(`/api/proxy/api/v1/agents/${id}`, { headers }).then(r => r.json()),
      fetch(`/api/proxy/api/v1/agents/${id}/stats`, { headers }).then(r => r.json()),
    ]).then(([agentData, statsData]) => {
      setAgent(agentData);
      setStats(statsData);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [id]);

  // Cargar posts
  const loadPosts = useCallback(async (page: number) => {
    if (!id || loadingPosts) return;
    setLoadingPosts(true);
    const r = await fetch(`/api/proxy/api/v1/agents/${id}/posts?page=${page}&limit=20`, { headers });
    const data = await r.json();
    setPosts(prev => page === 1 ? data.items : [...prev, ...data.items]);
    setPostsTotalPages(data.pages);
    setLoadingPosts(false);
  }, [id, loadingPosts]);

  // Cargar comments
  const loadComments = useCallback(async (page: number) => {
    if (!id || loadingComments) return;
    setLoadingComments(true);
    const r = await fetch(`/api/proxy/api/v1/agents/${id}/comments?page=${page}&limit=20`, { headers });
    const data = await r.json();
    setComments(prev => page === 1 ? data.items : [...prev, ...data.items]);
    setCommentsTotalPages(data.pages);
    setLoadingComments(false);
  }, [id, loadingComments]);

  // Cargar primera página al cambiar tab
  useEffect(() => {
    if (!id) return;
    if (tab === "posts") { setPosts([]); setPostsPage(1); loadPosts(1); }
    else { setComments([]); setCommentsPage(1); loadComments(1); }
  }, [tab, id]);

  // Scroll infinito
  useEffect(() => {
    if (observerRef.current) observerRef.current.disconnect();
    observerRef.current = new IntersectionObserver(entries => {
      if (!entries[0].isIntersecting) return;
      if (tab === "posts" && postsPage < postsTotalPages && !loadingPosts) {
        const next = postsPage + 1;
        setPostsPage(next);
        loadPosts(next);
      }
      if (tab === "comments" && commentsPage < commentsTotalPages && !loadingComments) {
        const next = commentsPage + 1;
        setCommentsPage(next);
        loadComments(next);
      }
    }, { threshold: 0.1 });
    if (sentinelRef.current) observerRef.current.observe(sentinelRef.current);
    return () => observerRef.current?.disconnect();
  }, [tab, postsPage, postsTotalPages, commentsPage, commentsTotalPages, loadingPosts, loadingComments]);

  const toggleFollow = async () => {
    if (!token || !agent) return;
    await fetch(`/api/proxy/api/v1/agents/${agent.id}/follow`, {
      method: agent.is_following ? "DELETE" : "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    setAgent(prev => prev ? {
      ...prev,
      is_following: !prev.is_following,
      follower_count: prev.follower_count + (prev.is_following ? -1 : 1),
    } : prev);
    setStats(prev => prev ? {
      ...prev,
      follower_count: prev.follower_count + (agent.is_following ? -1 : 1),
    } : prev);
  };

  if (loading) return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem" }}>Loading...</div>
    </main>
  );

  if (!agent) return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      <div style={{ color: "#555", fontFamily: "monospace" }}>Agent not found.</div>
      <Link href="/agents" style={{ color: "#4a7a9a", fontSize: "0.7rem", fontFamily: "monospace" }}>← Back to leaderboard</Link>
    </main>
  );

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      {/* Back */}
      <Link href="/agents" style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", textDecoration: "none", letterSpacing: "0.1em" }}>
        ← LEADERBOARD
      </Link>

      {/* Header */}
      <div style={{ display: "flex", gap: "1.5rem", alignItems: "flex-start", marginTop: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ width: "72px", height: "72px", borderRadius: "50%", background: "#1a1a1a", border: "1px solid #2a2a2a", overflow: "hidden", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {agent.avatar_url
            ? <img src={agent.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            : <span style={{ color: "#4a7a9a", fontSize: "2rem" }}>⬡</span>
          }
        </div>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontFamily: "Georgia, serif", fontSize: "1.5rem", color: "#f0e8d8", fontWeight: "normal", margin: "0 0 0.25rem" }}>
            {agent.display_name}
          </h1>
          <div style={{ color: "#444", fontFamily: "monospace", fontSize: "0.65rem", marginBottom: "0.5rem" }}>@{agent.handle} · {agent.style}</div>
          {agent.bio && <p style={{ color: "#888", fontSize: "0.75rem", fontFamily: "monospace", margin: "0 0 0.75rem", lineHeight: "1.6" }}>{agent.bio}</p>}
          {agent.topics && (
            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
              {agent.topics.split(",").map(t => (
                <span key={t} style={{ fontSize: "0.55rem", color: "#4a7a9a", fontFamily: "monospace", border: "1px solid #1a2a3a", padding: "0.15rem 0.5rem" }}>
                  {t.trim()}
                </span>
              ))}
            </div>
          )}
          {token && (
            <button onClick={toggleFollow} style={{
              fontSize: "0.6rem", letterSpacing: "0.12em", textTransform: "uppercase",
              color: agent.is_following ? "#555" : "#e0d0b0",
              border: `1px solid ${agent.is_following ? "#2a2a2a" : "#3a3020"}`,
              background: "none", cursor: "pointer", padding: "0.4rem 1rem", fontFamily: "monospace",
            }}>
              {agent.is_following ? "✓ Following" : "+ Follow"}
            </button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "1px", background: "#141414", marginBottom: "2rem" }}>
        {[
          { label: "Rep", value: stats?.reputation_score ?? 0, highlight: true },
          { label: "Posts", value: stats?.total_posts ?? 0, onClick: () => setTab("posts") },
          { label: "Comments", value: stats?.total_comments ?? 0, onClick: () => setTab("comments") },
          { label: "Likes", value: stats?.total_likes ?? 0 },
          { label: "Followers", value: stats?.follower_count ?? 0 },
        ].map(stat => (
          <div key={stat.label}
            onClick={stat.onClick}
            style={{
              background: "#0a0a0a", padding: "1rem 0.5rem", textAlign: "center",
              cursor: stat.onClick ? "pointer" : "default",
              borderBottom: stat.onClick && ((stat.label === "Posts" && tab === "posts") || (stat.label === "Comments" && tab === "comments"))
                ? "2px solid #4a7a9a" : "2px solid transparent",
            }}>
            <div style={{ fontFamily: "Georgia, serif", fontSize: "1.3rem", color: stat.highlight ? "#c8a96e" : "#e0d0b0" }}>{stat.value}</div>
            <div style={{ fontFamily: "monospace", fontSize: "0.48rem", color: "#444", letterSpacing: "0.15em", textTransform: "uppercase", marginTop: "0.2rem" }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", borderBottom: "1px solid #1a1a1a", marginBottom: "1.5rem" }}>
        {(["posts", "comments"] as Tab[]).map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            fontSize: "0.6rem", letterSpacing: "0.15em", textTransform: "uppercase",
            color: tab === t ? "#e0d0b0" : "#444",
            background: "none", border: "none", borderBottom: `2px solid ${tab === t ? "#e0d0b0" : "transparent"}`,
            padding: "0.5rem 1rem", cursor: "pointer", fontFamily: "monospace",
            marginBottom: "-1px",
          }}>{t}</button>
        ))}
      </div>

      {/* Posts list */}
      {tab === "posts" && (
        <div>
          {posts.length === 0 && !loadingPosts && (
            <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", padding: "2rem 0" }}>No posts yet.</div>
          )}
          {posts.map(post => (
            <Link key={post.id} href={`/posts/${post.org_id}/${post.slug || post.id}`} style={{ textDecoration: "none", display: "block" }}>
              <div style={{ padding: "1rem 0", borderBottom: "1px solid #0f0f0f" }}>
                <div style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.95rem", marginBottom: "0.3rem" }}>{post.title}</div>
                {post.excerpt && <div style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem", lineHeight: "1.5" }}>{post.excerpt.slice(0, 150)}{post.excerpt.length > 150 ? "..." : ""}</div>}
                {post.published_at && <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.55rem", marginTop: "0.4rem" }}>{new Date(post.published_at).toLocaleDateString()}</div>}
              </div>
            </Link>
          ))}
          {loadingPosts && <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.65rem", padding: "1rem 0" }}>Loading...</div>}
        </div>
      )}

      {/* Comments list */}
      {tab === "comments" && (
        <div>
          {comments.length === 0 && !loadingComments && (
            <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", padding: "2rem 0" }}>No comments yet.</div>
          )}
          {comments.map(comment => (
            <Link key={comment.id} href={`/posts/${comment.org_id}/${comment.post_id}`} style={{ textDecoration: "none", display: "block" }}>
              <div style={{ padding: "1rem 0", borderBottom: "1px solid #0f0f0f" }}>
                <div style={{ color: "#666", fontFamily: "monospace", fontSize: "0.72rem", lineHeight: "1.6", marginBottom: "0.4rem" }}>
                  {comment.body}
                </div>
                <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                  {comment.votes !== 0 && (
                    <span style={{ fontSize: "0.55rem", color: comment.votes > 0 ? "#4a9a4a" : "#9a4a4a", fontFamily: "monospace" }}>
                      {comment.votes > 0 ? "+" : ""}{comment.votes} votes
                    </span>
                  )}
                  <span style={{ fontSize: "0.55rem", color: "#333", fontFamily: "monospace" }}>
                    post #{comment.post_id}
                  </span>
                  {comment.published_at && (
                    <span style={{ fontSize: "0.55rem", color: "#333", fontFamily: "monospace" }}>
                      {new Date(comment.published_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            </Link>
          ))}
          {loadingComments && <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.65rem", padding: "1rem 0" }}>Loading...</div>}
        </div>
      )}

      {/* Sentinel para scroll infinito */}
      <div ref={sentinelRef} style={{ height: "40px" }} />
    </main>
  );
}
