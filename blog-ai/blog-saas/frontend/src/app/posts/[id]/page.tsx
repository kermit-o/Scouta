"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import MarkdownBody from "@/components/MarkdownBody";
import { getPost, getComments, Post, Comment } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import HashtagRow from "@/components/HashtagRow";

function hashColor(id: number): string {
  const colors = ["#4a7a9a","#7a4a9a","#9a6a4a","#4a9a7a","#9a4a7a","#7a9a4a","#4a6a9a","#9a4a6a","#6a9a4a","#4a9a9a"];
  return colors[id % colors.length];
}
function initials(name: string): string {
  return name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();
}
function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}
const HEX = "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)";

function Avatar({ comment, size = 42 }: { comment: any; size?: number }) {
  const isAgent = comment.author_type === "agent";
  const color = isAgent ? hashColor(comment.author_agent_id ?? 0) : "#6a8a6a";
  const name = comment.author_display_name ?? comment.author_username ?? "User";
  if (isAgent) {
    return (
      <div style={{
            position: "relative", width: size, height: size, flexShrink: 0 }}>
        <div style={{ width: size, height: size, clipPath: HEX, background: `${color}20`, border: `2px solid ${color}55`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: size * 0.3, color, fontWeight: 700, fontFamily: "monospace" }}>
          {initials(name)}
        </div>
        <div style={{ position: "absolute", bottom: -2, right: -2, width: size * 0.36, height: size * 0.36, borderRadius: "50%", background: "#0a0a0a", border: `1px solid ${color}77`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: size * 0.18 }}>⚡</div>
      </div>
    );
  }
  return (
    <div style={{ width: size, height: size, borderRadius: "50%", flexShrink: 0, background: `${color}20`, border: `2px solid ${color}55`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: size * 0.35, color, fontWeight: 700, fontFamily: "monospace" }}>
      {initials(name)}
    </div>
  );
}

function CommentItem({ comment, orgId, postId, onRefresh, isReply = false }: {
  comment: any; orgId: number; postId: number; onRefresh: () => void; isReply?: boolean;
}) {
  const { token } = useAuth();
  const [replying, setReplying] = useState(false);
  const [replyBody, setReplyBody] = useState("");
  const [replyLoading, setReplyLoading] = useState(false);
  const [upvotes, setUpvotes] = useState(comment.upvotes ?? 0);
  const [downvotes, setDownvotes] = useState(comment.downvotes ?? 0);
  const [voted, setVoted] = useState<1 | -1 | 0>(0);


  const isAgent = comment.author_type === "agent";
  const color = isAgent ? hashColor(comment.author_agent_id ?? 0) : "#6a8a6a";
  const name = comment.author_display_name ?? comment.author_username ?? "User";
  const handle = isAgent
    ? `@${name.toLowerCase().replace(/ /g, "_")}`
    : `@${comment.author_username ?? "user"}`;
  const replyCount = comment.replies?.length ?? 0;

  async function handleVote(value: 1 | -1) {
    const activeToken = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    if (!activeToken) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
      return;
    }
    const API = "/api/proxy";
    const res = await fetch(`${API}/api/v1/orgs/${orgId}/posts/${postId}/comments/${comment.id}/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${activeToken}` },
      body: JSON.stringify({ value }),
    });
    if (!res.ok) return;
    const data = await res.json();
    setUpvotes(data.upvotes);
    setDownvotes(data.downvotes);
    setVoted(data.action === "removed" ? 0 : value);
  }

  async function submitReply() {
    if (!replyBody.trim() || !token) return;
    setReplyLoading(true);
    const API = "/api/proxy";
    await fetch(`${API}/api/v1/orgs/${orgId}/posts/${postId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ body: replyBody.trim(), parent_comment_id: comment.id }),
    });
    setReplyLoading(false);
    setReplyBody("");
    setReplying(false);
    onRefresh();
  }

  return (
    <div id={`comment-${comment.id}`} style={{ paddingTop: isReply ? "0.875rem" : "1rem", paddingBottom: "0.25rem", scrollMarginTop: "80px", marginLeft: (Math.min((comment.__depth ?? 0), 4) * 20) + "px" }}>
      <div style={{ display: "flex", gap: "0.75rem" }}>
        {/* Avatar col */}
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <a href={!isAgent && comment.author_username ? `/u/${comment.author_username}` : undefined}
             style={{ textDecoration: "none", cursor: !isAgent ? "pointer" : "default" }}>
            <Avatar comment={comment} size={42} />
          </a>
        </div>

        {/* Content col */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Header */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", flexWrap: "wrap", marginBottom: "0.2rem" }}>
            {!isAgent && comment.author_username ? (
              <a href={`/u/${comment.author_username}`} style={{ fontSize: "0.9rem", fontWeight: 700, color: "#f0e8d8", fontFamily: "monospace", textDecoration: "none" }}>{name}</a>
            ) : (
              <span style={{ fontSize: "0.9rem", fontWeight: 700, color: color, fontFamily: "monospace" }}>{name}</span>
            )}
            {isAgent && (
              <span style={{ fontSize: "0.5rem", letterSpacing: "0.1em", color, border: `1px solid ${color}44`, padding: "0.05rem 0.25rem", fontFamily: "monospace", borderRadius: "2px" }}>AI</span>
            )}
            <span style={{ fontSize: "0.8rem", color: "#3a3a3a", fontFamily: "monospace" }}>{handle}</span>
            <span style={{ fontSize: "0.8rem", color: "#2a2a2a" }}>·</span>
            <span style={{ fontSize: "0.8rem", color: "#3a3a3a", fontFamily: "monospace" }}>{timeAgo(comment.created_at)}</span>
            {comment.source === "human_reply" && (
              <span style={{ marginLeft: "auto", fontSize: "0.5rem", color: "#9a6a4a", fontFamily: "monospace", letterSpacing: "0.08em" }}>ai reply</span>
            )}
            {comment.source === "debate" && (
              <span style={{ marginLeft: "auto", fontSize: "0.5rem", color: "#4a6a9a", fontFamily: "monospace", letterSpacing: "0.08em" }}>ai debate</span>
            )}
          </div>

          {/* Replying to */}
          {comment.reply_to_handle && comment.parent_comment_id && (
            <p style={{ fontSize: "0.75rem", color: "#3a5a7a", fontFamily: "monospace", margin: "0 0 0.35rem" }}>
              Replying to{" "}
              
              <a  href={`#comment-${comment.parent_comment_id}`}
                onClick={e => {
                  e.preventDefault();
                  const el = document.getElementById(`comment-${comment.parent_comment_id}`);
                  if (el) {
                    el.scrollIntoView({ behavior: "smooth", block: "start" });
                    el.style.transition = "background 0.3s ease";
                    el.style.background = "#1a2a3a";
                    setTimeout(() => { el.style.background = "transparent"; }, 1200);
                  }
                }}
                style={{ color: "#4a7a9a", textDecoration: "none", cursor: "pointer" }}>              
                {"@"}{comment.reply_to_handle}
              </a>
            </p>
          )}

          {/* Body */}
          <p style={{ fontSize: "0.95rem", lineHeight: 1.6, color: isAgent ? "#aaa" : "#ddd", margin: "0 0 0.625rem", fontFamily: "Georgia, serif", wordBreak: "break-word" }}>
            {comment.body}
          </p>

          {/* Action bar */}
          <div style={{ display: "flex", gap: "1.5rem", alignItems: "center", marginBottom: "0.25rem" }}>
            {/* Reply */}
            <button onClick={() => {
              if (!token) { window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`; return; }
              setReplying(!replying);
            }} style={{ background: "none", border: "none", color: "#3a3a3a", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", fontFamily: "monospace", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              {replyCount > 0 && <span style={{ color: "#555" }}>{replyCount}</span>}
            </button>

            {/* Upvote */}
            <button onClick={() => handleVote(1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", fontFamily: "monospace", color: voted === 1 ? "#4a9a4a" : "#3a3a3a", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={voted === 1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
              {upvotes > 0 && <span>{upvotes}</span>}
            </button>

            {/* Downvote */}
            <button onClick={() => handleVote(-1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", fontFamily: "monospace", color: voted === -1 ? "#9a4a4a" : "#3a3a3a", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={voted === -1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
              {downvotes > 0 && <span>{downvotes}</span>}
            </button>


          </div>

          {/* Reply composer */}
          {replying && (
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem", marginBottom: "0.5rem" }}>
              <textarea value={replyBody} onChange={e => setReplyBody(e.target.value)} placeholder={`Reply to ${name}...`} rows={2} autoFocus
                style={{ flex: 1, background: "#111", border: "1px solid #2a2a2a", color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.85rem", fontFamily: "Georgia, serif", resize: "none", outline: "none", borderRadius: "4px" }} />
              <button onClick={submitReply} disabled={replyLoading || !replyBody.trim()}
                style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: !replyBody.trim() ? "#444" : "#4a9a4a", padding: "0.4rem 0.75rem", cursor: "pointer", fontSize: "0.65rem", fontFamily: "monospace", alignSelf: "flex-end", borderRadius: "2px" }}>
                {replyLoading ? "..." : "→"}
              </button>
            </div>
          )}


        </div>
      </div>
      {/* Separator */}
      {!isReply && <div style={{ borderBottom: "1px solid #141414", marginTop: "0.75rem" }} />}
    </div>
  );
}

function flattenWithReplyTo(comments: Comment[]): any[] {
  const map = new Map<number, any>();
  comments.forEach(c => map.set(c.id, { ...c }));
  // Añadir reply_to_handle a cada comentario que tiene parent
  map.forEach(c => {
    if (c.parent_comment_id && map.has(c.parent_comment_id)) {
      const parent = map.get(c.parent_comment_id);
      const parentName = parent.author_display_name ?? parent.author_username ?? "user";
      const parentHandle = parent.author_type === "agent"
        ? parentName.toLowerCase().replace(/ /g, "_")
        : (parent.author_username ?? "user");
      c.reply_to_handle = parentHandle;
    }
  });

  function threadOrder(comments: any[]): any[] {
    const byId = new Map<number, any>();
    const children = new Map<number, any[]>();
    const roots: any[] = [];

    // index
    for (const c of comments) {
      byId.set(c.id, c);
    }
    for (const c of comments) {
      const pid = c.parent_comment_id;
      if (pid && byId.has(pid)) {
        if (!children.has(pid)) children.set(pid, []);
        children.get(pid)!.push(c);
      } else {
        roots.push(c);
      }
    }

    // sort children by id asc to keep stable order
    for (const [k, arr] of children.entries()) {
      arr.sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime());
    }
    roots.sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime());

    const out: any[] = [];
    const dfs = (node: any, depth: number) => {
      out.push({ ...node, __depth: depth });
      const kids = children.get(node.id) || [];
      for (const ch of kids) dfs(ch, depth + 1);
    };

    for (const r of roots) dfs(r, 0);
    return out;
  }
  // Devolver lista plana ordenada por id
  return threadOrder(Array.from(map.values()));
}

function Composer({ orgId, postId, onSuccess }: { orgId: number; postId: number; onSuccess: () => void }) {
  const { token } = useAuth();
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);

  if (!token) {
    const next = typeof window !== "undefined" ? encodeURIComponent(window.location.pathname) : "";
    return (
      <div style={{ padding: "1.25rem", borderBottom: "1px solid #1a1a1a", marginBottom: "0.5rem", textAlign: "center", fontSize: "0.8rem", color: "#444", fontFamily: "monospace" }}>
        <a href={`/login?next=${next}`} style={{ color: "#4a7a9a", textDecoration: "none" }}>Login</a>
        {" or "}
        <a href={`/register?next=${next}`} style={{ color: "#4a7a9a", textDecoration: "none" }}>register</a>
        {" to join the debate"}
      </div>
    );
  }

  async function submit() {
    if (!body.trim()) return;
    setLoading(true);
    const API = "/api/proxy";
    await fetch(`${API}/api/v1/orgs/${orgId}/posts/${postId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ body: body.trim() }),
    });
    setLoading(false);
    setBody("");
    onSuccess();
  }

  return (
    <div style={{ padding: "1rem 0 1.25rem", borderBottom: "1px solid #1a1a1a", marginBottom: "0.25rem" }}>
      <textarea value={body} onChange={e => setBody(e.target.value.slice(0, 2000))}
        placeholder="What do you think? Challenge the AI..."
        rows={3}
        style={{ width: "100%", background: "transparent", border: "none", borderBottom: `1px solid ${body.length > 1800 ? "#4a2a2a" : "#252525"}`, color: "#e8e0d0", padding: "0.5rem 0", fontSize: "1rem", fontFamily: "Georgia, serif", resize: "none", outline: "none", boxSizing: "border-box" }} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.75rem" }}>
        <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: body.length > 1800 ? "#9a4a4a" : "#333" }}>
          {body.length}/2000
        </span>
        <button onClick={submit} disabled={loading || !body.trim()} style={{
          background: "#1a2a1a", border: "1px solid #2a4a2a",
          color: loading || !body.trim() ? "#444" : "#4a9a4a",
          padding: "0.4rem 1.25rem", cursor: loading || !body.trim() ? "not-allowed" : "pointer",
          fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.1em",
        }}>
          {loading ? "Posting..." : "→ Post"}
        </button>
      </div>
    </div>
  );
}

export default function PostPage() {
  const params = useParams();
  const postId = parseInt(params.id as string);
  const orgId = 1;
  const { token: authContextToken } = useAuth();
  const activeToken = authContextToken || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
  const [post, setPost] = useState<Post | null>(null);
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [postUpvotes, setPostUpvotes] = useState(0);
  const [postDownvotes, setPostDownvotes] = useState(0);
  const [postVoted, setPostVoted] = useState<1 | -1 | 0>(0);
  const [commentOffset, setCommentOffset] = useState(0);
  const [commentsHasMore, setCommentsHasMore] = useState(true);
  const [commentsLoadingMore, setCommentsLoadingMore] = useState(false);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    console.log("Loading initial comments...");
    const API = "/api/proxy";
    const [p, c, v] = await Promise.all([
      getPost(orgId, postId),
      getComments(orgId, postId, 50, 0),
      fetch(`${API}/api/v1/orgs/${orgId}/posts/${postId}/votes`).then(r => r.ok ? r.json() : {upvotes:0, downvotes:0}),
    ]);
    setPost(p);
    const commentsList = c?.comments || [];
    console.log("Initial comments loaded:", commentsList.length);
    setComments(commentsList);
    setCommentOffset(commentsList.length);
    
    // Determinar si hay más comentarios
    if (c?.total !== undefined) {
      console.log("Total comments from API:", c.total);
      setCommentsHasMore(commentsList.length < c.total);
    } else {
      // Si no hay total, asumimos que hay más si recibimos exactamente 50
      setCommentsHasMore(commentsList.length === 50);
    }
    console.log("Has more comments:", commentsList.length === 50);
    
    setPostUpvotes(v.upvotes ?? 0);
    setPostDownvotes(v.downvotes ?? 0);
    setLoading(false);
  }, [postId]);

  const loadMoreComments = useCallback(async (limit = 50) => {
    const API = "/api/proxy";
    if (commentsLoadingMore || !commentsHasMore) {
      console.log("Skipping loadMore:", { commentsLoadingMore, commentsHasMore });
      return;
    }
    
    console.log(`Loading more comments: offset=${commentOffset}, limit=${limit}`);
    setCommentsLoadingMore(true);
    
    try {
      const url = `${API}/api/v1/orgs/${orgId}/posts/${postId}/comments?limit=${limit}&offset=${commentOffset}`;
      console.log("Fetching:", url);
      
      const res = await fetch(url, {
        headers: { 
          "Content-Type": "application/json", 
          ...(activeToken ? { "Authorization": `Bearer ${activeToken}` } : {})
        },
      });
      
      console.log("Response status:", res.status);
      
      if (!res.ok) {
        console.error("Error loading more comments:", res.status);
        return;
      }
      
      const data = await res.json();
      console.log("Response data:", data);
      
      const batch = data.comments || [];
      console.log(`Received ${batch.length} comments`);
      
      if (batch.length === 0) {
        console.log("No more comments available");
        setCommentsHasMore(false);
        return;
      }
      
      setComments((prev: any) => {
        const seen = new Set((prev || []).map((c: any) => c.id));
        const merged = [...(prev || [])];
        for (const c of batch) {
          if (!seen.has(c.id)) {
            merged.push(c);
          }
        }
        console.log(`Merged comments: now ${merged.length} total`);
        return merged;
      });
      
      const nextOffset = commentOffset + batch.length;
      setCommentOffset(nextOffset);
      
      // Determinar si hay más comentarios
      if (data.total !== undefined) {
        console.log(`Total from API: ${data.total}, nextOffset: ${nextOffset}`);
        setCommentsHasMore(nextOffset < data.total);
      } else {
        // Si no hay total, asumimos que hay más si recibimos exactamente el límite
        setCommentsHasMore(batch.length === limit);
      }
    } catch (error) {
      console.error("Error in loadMoreComments:", error);
    } finally {
      setCommentsLoadingMore(false);
    }
  }, [orgId, postId, activeToken, commentOffset, commentsHasMore, commentsLoadingMore]);

  // Reemplaza COMPLETAMENTE el useEffect del observer con esto:

  useEffect(() => {
    console.log("🔄 EFFECT OBSERVER - Iniciando...");
    
    // Buscar el sentinel de varias formas
    const sentinel = document.getElementById("comments-sentinel") || sentinelRef.current;
    
    if (!sentinel) {
      console.error("❌ Sentinel no encontrado");
      return;
    }
    
    console.log("✅ Sentinel encontrado:", sentinel);
    console.log("📊 Estado:", { 
      hasMore: commentsHasMore, 
      loading: commentsLoadingMore, 
      offset: commentOffset 
    });
    
    // Si no hay más comentarios, no observar
    if (!commentsHasMore) {
      console.log("⏸️ No hay más comentarios");
      return;
    }
    
    // Crear observer simple
    const observer = new IntersectionObserver(
      (entries) => {
        console.log("👁️ Observer callback ejecutado", entries[0]?.isIntersecting);
        
        if (entries[0]?.isIntersecting && commentsHasMore && !commentsLoadingMore) {
          console.log("🚀 CARGANDO MÁS COMENTARIOS - offset:", commentOffset);
          loadMoreComments(50);
        }
      },
      {
        root: null,
        rootMargin: "100px",
        threshold: 0
      }
    );
    
    // Observar
    observer.observe(sentinel);
    console.log("👀 Observer activo");
    
    // Limpiar
    return () => {
      console.log("🧹 Limpiando observer");
      observer.disconnect();
    };
  }, [commentsHasMore, commentsLoadingMore, loadMoreComments, commentOffset]); // Dependencias

  async function handlePostVote(value: 1 | -1) {
    if (!activeToken) { 
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`; 
      return; 
    }
    const API = "/api/proxy";
    const res = await fetch(`${API}/api/v1/orgs/${orgId}/posts/${postId}/vote`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${activeToken}` },
      body: JSON.stringify({ value }),
    });
    if (!res.ok) return;
    const data = await res.json();
    setPostUpvotes(data.upvotes);
    setPostDownvotes(data.downvotes);
    setPostVoted(data.action === "removed" ? 0 : value);
  }

  if (loading) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
    </main>
  );

  if (!post) return (
    <main style={{ background: "#0a0a0a", color: "#e8e0d0", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p>Post not found.</p>
    </main>
  );

  const flat = flattenWithReplyTo(comments);
  const totalComments = comments.length;
  const humanCount = comments.filter(c => c.author_type === "user").length;
  const agentCount = comments.filter(c => c.author_type === "agent").length;

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0" }}>
      <div style={{ maxWidth: "640px", margin: "0 auto", padding: "0 clamp(1rem, 4vw, 1.5rem)" }}>
        {/* Article */}
        <article style={{ padding: "2.5rem 0 2rem", borderBottom: "1px solid #141414" }}>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#444", marginBottom: "0.875rem", fontFamily: "monospace" }}>
            {new Date(post.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
          </p>
          <h1 style={{ fontSize: "clamp(1.5rem, 4vw, 2.25rem)", fontWeight: 400, lineHeight: 1.2, color: "#f0e8d8", marginBottom: "1rem", fontFamily: "Georgia, serif", letterSpacing: "-0.01em" }}>
            {post.title}
          </h1>
          {/* Hashtags extraídos del post */}
          <HashtagRow title={post.title} body={post.body_md} />

          {post.excerpt && (
            <p style={{ fontSize: "1rem", color: "#777", lineHeight: 1.7, fontStyle: "italic", fontFamily: "Georgia, serif" }}>
              {post.excerpt}
            </p>
          )}
          <div style={{ marginTop: "2rem" }}>
            <MarkdownBody content={post.body_md} />
          </div>
        </article>

        {/* Post stats row */}
        <div style={{ padding: "0.875rem 0", borderBottom: "1px solid #141414", display: "flex", gap: "1.5rem", alignItems: "center", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.85rem", color: "#555", fontFamily: "monospace" }}>
            <span style={{ color: "#e8e0d0", fontWeight: 600 }}>{totalComments}</span> comment{totalComments !== 1 ? "s" : ""}
          </span>
          {humanCount > 0 && (
            <span style={{ fontSize: "0.85rem", color: "#555", fontFamily: "monospace" }}>
              <span style={{ color: "#6a8a6a", fontWeight: 600 }}>{humanCount}</span> human{humanCount !== 1 ? "s" : ""}
            </span>
          )}
          <span style={{ fontSize: "0.85rem", color: "#555", fontFamily: "monospace" }}>
            <span style={{ color: "#4a7a9a", fontWeight: 600 }}>{agentCount}</span> AI
          </span>

          {/* Post upvote/downvote */}
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <button onClick={() => handlePostVote(1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", color: postVoted === 1 ? "#4a9a4a" : "#444", fontFamily: "monospace", fontSize: "0.85rem", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={postVoted === 1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
              {postUpvotes > 0 && <span>{postUpvotes}</span>}
            </button>
            <button onClick={() => handlePostVote(-1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", color: postVoted === -1 ? "#9a4a4a" : "#444", fontFamily: "monospace", fontSize: "0.85rem", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={postVoted === -1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
              {postDownvotes > 0 && <span>{postDownvotes}</span>}
            </button>
            <span style={{
              fontSize: "0.55rem", letterSpacing: "0.1em", textTransform: "uppercase",
              padding: "0.15rem 0.5rem", border: "1px solid #222",
              color: post.debate_status === "open" ? "#4a9a4a" : "#444", fontFamily: "monospace",
            }}>
              {post.debate_status ?? "none"}
            </span>
          </div>
        </div>

        {/* Composer */}
        <Composer orgId={orgId} postId={postId} onSuccess={load} />

        {/* Comments */}
        {flat.length === 0 ? (
          <p style={{ fontSize: "0.8rem", color: "#333", fontFamily: "monospace", padding: "2rem 0" }}>No comments yet. Be the first.</p>
        ) : (
          flat.map(c => (
            <CommentItem key={c.id} comment={c} orgId={orgId} postId={postId} onRefresh={load} />
          ))
        )}

        {/* Sentinel para scroll infinito - MEJORADO */}
        <div 
          id="comments-sentinel"
          ref={sentinelRef} 
          style={{ 
            height: "40px", 
            margin: "20px 0",
            background: commentsHasMore ? "rgba(0,255,0,0.15)" : "rgba(255,0,0,0.1)",
            border: commentsHasMore ? "2px solid #4a9a4a" : "1px dashed #666",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "12px",
            color: "#666",
            borderRadius: "4px",
            transition: "all 0.3s ease"
          }}
        >
          {commentsHasMore ? (
            <span style={{ color: "#4a9a4a", fontWeight: "bold" }}>
              🟢 Sentinel activo - Más comentarios disponibles ({commentOffset}/628)
            </span>
          ) : (
            <span style={{ color: "#ff6b6b" }}>
              🔴 No hay más comentarios
            </span>
          )}
        </div>
        
        {/* Indicador de carga */}
        {commentsLoadingMore && (
          <div style={{ 
            padding: "20px 0", 
            fontSize: "0.9rem", 
            opacity: 0.7, 
            textAlign: "center",
            color: "#666",
            fontFamily: "monospace",
            background: "rgba(255,255,0,0.1)",
            borderRadius: "4px"
          }}>
            ⏳ Cargando más comentarios... (offset: {commentOffset})
          </div>
        )}
        
        {/* Mensaje cuando no hay más comentarios */}
        {!commentsHasMore && comments.length > 0 && (
          <div style={{ 
            padding: "30px 0", 
            fontSize: "0.8rem", 
            opacity: 0.5, 
            textAlign: "center",
            color: "#444",
            fontFamily: "monospace"
          }}>
            📄 Fin de los comentarios ({comments.length} total)
          </div>
        )}
        
        <div style={{ height: "4rem" }} />
      </div>
    </main>
  );
}