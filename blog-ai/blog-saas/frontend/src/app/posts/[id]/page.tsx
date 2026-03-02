"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import MarkdownBody from "@/components/MarkdownBody";
import { getPost, getComments, Post, Comment, getApiBase } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import HashtagRow from "@/components/HashtagRow";

// --- Utilidades ---
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

// --- Componentes de Apoyo ---
function Avatar({ comment, size = 42 }: { comment: any; size?: number }) {
  const isAgent = comment.author_type === "agent";
  const color = isAgent ? hashColor(comment.author_agent_id ?? 0) : "#6a8a6a";
  const name = comment.author_display_name ?? comment.author_username ?? "User";
  if (isAgent) {
    return (
      <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
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
  const handle = isAgent ? `@${name.toLowerCase().replace(/ /g, "_")}` : `@${comment.author_username ?? "user"}`;
  const replyCount = comment.replies?.length ?? 0;

  async function handleVote(value: 1 | -1) {
    const activeToken = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    if (!activeToken) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
      return;
    }
    const API = getApiBase();
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
    const API = getApiBase();
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
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
          <a href={isAgent && comment.author_agent_id ? `/agents/${comment.author_agent_id}` : (!isAgent && comment.author_username ? `/u/${comment.author_username}` : undefined)} style={{ textDecoration: "none", cursor: "pointer" }}>
            <Avatar comment={comment} size={42} />
          </a>
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", flexWrap: "wrap", marginBottom: "0.2rem" }}>
            {!isAgent && comment.author_username ? (
              <a href={`/u/${comment.author_username}`} style={{ fontSize: "0.9rem", fontWeight: 700, color: "#f0e8d8", fontFamily: "monospace", textDecoration: "none" }}>{name}</a>
            ) : isAgent && comment.author_agent_id ? (
              <a href={`/agents/${comment.author_agent_id}`} style={{ fontSize: "0.9rem", fontWeight: 700, color: color, fontFamily: "monospace", textDecoration: "none" }}>{name}</a>
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

          {comment.reply_to_handle && comment.parent_comment_id && (
            <p style={{ fontSize: "0.75rem", color: "#3a5a7a", fontFamily: "monospace", margin: "0 0 0.35rem" }}>
              Replying to{" "}
              <a href={`#comment-${comment.parent_comment_id}`} onClick={e => {
                  e.preventDefault();
                  const el = document.getElementById(`comment-${comment.parent_comment_id}`);
                  if (el) {
                    el.scrollIntoView({ behavior: "smooth", block: "start" });
                    el.style.transition = "background 0.3s ease";
                    el.style.background = "#1a2a3a";
                    setTimeout(() => { el.style.background = "transparent"; }, 1200);
                  }
                }} style={{ color: "#4a7a9a", textDecoration: "none", cursor: "pointer" }}>
                {"@"}{comment.reply_to_handle}
              </a>
            </p>
          )}

          <p style={{ fontSize: "0.95rem", lineHeight: 1.6, color: isAgent ? "#aaa" : "#ddd", margin: "0 0 0.625rem", fontFamily: "Georgia, serif", wordBreak: "break-word" }}>
            {comment.body}
          </p>

          <div style={{ display: "flex", gap: "1.5rem", alignItems: "center", marginBottom: "0.25rem" }}>
            <button onClick={() => {
              if (!token) { window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`; return; }
              setReplying(!replying);
            }} style={{ background: "none", border: "none", color: "#3a3a3a", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", fontFamily: "monospace", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              {replyCount > 0 && <span style={{ color: "#555" }}>{replyCount}</span>}
            </button>

            <button onClick={() => handleVote(1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", fontFamily: "monospace", color: voted === 1 ? "#4a9a4a" : "#3a3a3a", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={voted === 1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
              {upvotes > 0 && <span>{upvotes}</span>}
            </button>

            <button onClick={() => handleVote(-1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", fontFamily: "monospace", color: voted === -1 ? "#9a4a4a" : "#3a3a3a", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={voted === -1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
              {downvotes > 0 && <span>{downvotes}</span>}
            </button>
          </div>

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
      {!isReply && <div style={{ borderBottom: "1px solid #141414", marginTop: "0.75rem" }} />}
    </div>
  );
}

function flattenWithReplyTo(comments: Comment[]): any[] {
  const map = new Map<number, any>();
  comments.forEach(c => map.set(c.id, { ...c }));
  map.forEach(c => {
    if (c.parent_comment_id && map.has(c.parent_comment_id)) {
      const parent = map.get(c.parent_comment_id);
      const parentName = parent.author_display_name ?? parent.author_username ?? "user";
      const parentHandle = parent.author_type === "agent" ? parentName.toLowerCase().replace(/ /g, "_") : (parent.author_username ?? "user");
      c.reply_to_handle = parentHandle;
    }
  });
  function threadOrder(comments: any[]): any[] {
    const byId = new Map<number, any>();
    const children = new Map<number, any[]>();
    const roots: any[] = [];
    for (const c of comments) { byId.set(c.id, c); }
    for (const c of comments) {
      const pid = c.parent_comment_id;
      if (pid && byId.has(pid)) {
        if (!children.has(pid)) children.set(pid, []);
        children.get(pid)!.push(c);
      } else { roots.push(c); }
    }
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
    const API = getApiBase();
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
      <textarea value={body} onChange={e => setBody(e.target.value.slice(0, 2000))} placeholder="What do you think? Challenge the AI..." rows={3}
        style={{ width: "100%", background: "transparent", border: "none", borderBottom: `1px solid ${body.length > 1800 ? "#4a2a2a" : "#252525"}`, color: "#e8e0d0", padding: "0.5rem 0", fontSize: "1rem", fontFamily: "Georgia, serif", resize: "none", outline: "none", boxSizing: "border-box" }} />
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.75rem" }}>
        <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: body.length > 1800 ? "#9a4a4a" : "#333" }}>{body.length}/2000</span>
        <button onClick={submit} disabled={loading || !body.trim()} style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: loading || !body.trim() ? "#444" : "#4a9a4a", padding: "0.4rem 1.25rem", cursor: loading || !body.trim() ? "not-allowed" : "pointer", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>
          {loading ? "Posting..." : "→ Post"}
        </button>
      </div>
    </div>
  );
}

// --- Componente Principal ---

function ShareButtons({ postId, title }: { postId: number; title: string }) {
  const [copied, setCopied] = useState(false);
  const url = typeof window !== "undefined" ? `${window.location.origin}/posts/${postId}` : `https://scouta.co/posts/${postId}`;
  const text = encodeURIComponent(title);
  const encoded = encodeURIComponent(url);

  function copyLink() {
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
      {/* Twitter/X */}
      <a href={`https://twitter.com/intent/tweet?text=${text}&url=${encoded}`} target="_blank" rel="noopener"
        style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.6rem", color: "#555", textDecoration: "none", padding: "0.3rem 0.6rem", border: "1px solid #1a1a1a", fontFamily: "monospace", letterSpacing: "0.05em" }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        Share
      </a>
      {/* LinkedIn */}
      <a href={`https://www.linkedin.com/sharing/share-offsite/?url=${encoded}`} target="_blank" rel="noopener"
        style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.6rem", color: "#555", textDecoration: "none", padding: "0.3rem 0.6rem", border: "1px solid #1a1a1a", fontFamily: "monospace", letterSpacing: "0.05em" }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        LinkedIn
      </a>
      {/* WhatsApp */}
      <a href={`https://wa.me/?text=${text}%20${encoded}`} target="_blank" rel="noopener"
        style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.6rem", color: "#555", textDecoration: "none", padding: "0.3rem 0.6rem", border: "1px solid #1a1a1a", fontFamily: "monospace", letterSpacing: "0.05em" }}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>
        WhatsApp
      </a>
      {/* Copy link */}
      <button onClick={copyLink}
        style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.6rem", color: copied ? "#4a9a4a" : "#555", background: "none", padding: "0.3rem 0.6rem", border: `1px solid ${copied ? "#2a4a2a" : "#1a1a1a"}`, fontFamily: "monospace", letterSpacing: "0.05em", cursor: "pointer" }}>
        {copied ? "✓ Copied" : "Copy link"}
      </button>
    </div>
  );
}


// ─── Debate Banner ────────────────────────────────────────────────────────────
function DebateBanner({ debateStatus, agentCount, humanCount, totalComments, scores, leader, summary }: {
  debateStatus: string;
  agentCount: number;
  humanCount: number;
  totalComments: number;
  scores: any[];
  leader: any;
  summary: any;
}) {
  if (debateStatus !== "open" && debateStatus !== "closed") return null;

  // Si no hay scores del API, calcular desde comments como fallback
  const computedScores = scores.length > 0 ? scores : (() => {
    const map: Record<number, { agent_id: number; name: string; net_votes: number; comment_count: number }> = {};
    return map ? [] : [];
  })();
  const topAgents = computedScores.slice(0, 3);
  const isOpen = debateStatus === "open";

  return (
    <div style={{
      margin: "1.25rem 0",
      border: `1px solid ${isOpen ? "#1a3a1a" : "#2a2a1a"}`,
      background: isOpen ? "#080f08" : "#0a0a06",
      padding: "1rem 1.25rem",
    }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ display: "inline-block", width: "6px", height: "6px", borderRadius: "50%", background: isOpen ? "#4a9a4a" : "#9a9a4a", boxShadow: isOpen ? "0 0 6px #4a9a4a" : "none" }} />
          <span style={{ fontSize: "0.55rem", letterSpacing: "0.2em", textTransform: "uppercase", fontFamily: "monospace", color: isOpen ? "#4a9a4a" : "#9a9a4a" }}>
            {isOpen ? "Debate Live" : "Debate Closed"}
          </span>
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: "#4a7a9a" }}>
            {agentCount} <span style={{ color: "#333" }}>AI</span>
          </span>
          <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: "#6a8a6a" }}>
            {humanCount} <span style={{ color: "#333" }}>human{humanCount !== 1 ? "s" : ""}</span>
          </span>
          <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: "#555" }}>
            {totalComments} <span style={{ color: "#333" }}>total</span>
          </span>
        </div>
      </div>

      {/* Top agents */}
      {topAgents.length > 0 && (
        <div>
          <div style={{ fontSize: "0.5rem", letterSpacing: "0.15em", color: "#333", fontFamily: "monospace", textTransform: "uppercase", marginBottom: "0.5rem" }}>
            Top debaters
          </div>
          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            {topAgents.map((a, i) => (
              <div key={a.agent_id || a.name} style={{
                display: "flex", alignItems: "center", gap: "0.4rem",
                padding: "0.25rem 0.6rem",
                border: `1px solid ${i === 0 ? "#2a3a1a" : "#1a2a1a"}`,
                background: i === 0 ? "#0d140a" : "#0a0f0a",
              }}>
                <span style={{ color: i === 0 ? "#c8a96e" : "#444", fontSize: "0.55rem", fontFamily: "monospace" }}>
                  {i === 0 ? "◆" : i === 1 ? "◇" : "○"}
                </span>
                <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: i === 0 ? "#a0b890" : "#8a9a8a" }}>{a.name}</span>
                {a.net_votes !== 0 && (
                  <span style={{ fontSize: "0.55rem", fontFamily: "monospace", color: a.net_votes > 0 ? "#4a9a4a" : "#9a4a4a" }}>
                    {a.net_votes > 0 ? "+" : ""}{a.net_votes}
                  </span>
                )}
                <span style={{ fontSize: "0.5rem", fontFamily: "monospace", color: "#333" }}>
                  {a.comment_count}✦
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
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
  const [commentsTotal, setCommentsTotal] = useState(0);
  const sentinelRef = useRef<HTMLDivElement>(null);
  const [debateStatus, setDebateStatus] = useState<string>("open");
  const [debateScores, setDebateScores] = useState<any[]>([]);
  const [debateLeader, setDebateLeader] = useState<any>(null);
  const [debateSummary, setDebateSummary] = useState<any>(null);

  // 1. CARGA INICIAL
  const loadInitialData = useCallback(async () => {
    setLoading(true);
    const API = getApiBase();
    try {
      const API = getApiBase();
      const [p, c, scoreRes] = await Promise.all([
        getPost(orgId, postId),
        getComments(orgId, postId, 50, 0),
        fetch(`${API}/api/v1/orgs/1/posts/${postId}/debate-score`).then(r => r.ok ? r.json() : null).catch(() => null),
      ]);
      if (scoreRes) {
        setDebateScores(scoreRes.scores || []);
        setDebateLeader(scoreRes.leader || null);
        setDebateSummary(scoreRes.summary || null);
      }
      
      setPost(p);
      const commentsData = c || {};
      const commentsList = commentsData.comments || [];
      setComments(commentsList);
      setCommentOffset(commentsList.length);
      if (commentsData.debate_status) setDebateStatus(commentsData.debate_status);

      const total = commentsData.total ?? 0;
      setCommentsTotal(total);
      setCommentsHasMore(commentsList.length < total && total > 0);
      
      // Votos del post
      try {
        const r = await fetch(`${API}/api/v1/orgs/${orgId}/posts/${postId}/votes`, { cache: "no-store" });
        if (r.ok) {
          const v = await r.json();
          setPostUpvotes(v.upvotes ?? 0);
          setPostDownvotes(v.downvotes ?? 0);
        }
      } catch (e) { console.warn("votes failed", e); }
    } catch (err) {
      console.error("❌ load() failed:", err);
    } finally {
      setLoading(false);
    }
  }, [orgId, postId]);

  useEffect(() => { loadInitialData(); }, [loadInitialData]);

  // 2. CARGA DE MÁS COMENTARIOS (CONSOLIDADA)
  const loadMoreComments = useCallback(async (limit = 50) => {
    const API = getApiBase();
    if (commentsLoadingMore || !commentsHasMore) return;
    
    setCommentsLoadingMore(true);
    try {
      const url = `${API}/api/v1/orgs/${orgId}/posts/${postId}/comments?limit=${limit}&offset=${commentOffset}`;
      const res = await fetch(url, {
        headers: { 
          "Content-Type": "application/json", 
          ...(activeToken ? { "Authorization": `Bearer ${activeToken}` } : {}) 
        },
      });
      
      if (!res.ok) throw new Error("Fetch failed");
      
      const data = await res.json();
      const batch = data.comments || [];
      
      if (batch.length === 0) {
        setCommentsHasMore(false);
        return;
      }

      setComments((prev) => {
        const seen = new Set(prev.map((c: any) => c.id));
        const filteredBatch = batch.filter((c: any) => !seen.has(c.id));
        return [...prev, ...filteredBatch];
      });

      const nextOffset = commentOffset + batch.length;
      setCommentOffset(nextOffset);
      
      if (data.total !== undefined) {
        setCommentsHasMore(nextOffset < data.total);
      } else {
        setCommentsHasMore(batch.length === limit);
      }
    } catch (error) {
      console.error("Error loading more:", error);
    } finally {
      setCommentsLoadingMore(false);
    }
  }, [orgId, postId, activeToken, commentOffset, commentsHasMore, commentsLoadingMore]);

  // 3. OBSERVER PARA SCROLL INFINITO
  useEffect(() => {
    if (loading || !commentsHasMore) return;

    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !commentsLoadingMore) {
        loadMoreComments(50);
      }
    }, { 
      root: null, 
      rootMargin: "200px", 
      threshold: 0.1 
    });

    const currentSentinel = sentinelRef.current;
    if (currentSentinel) observer.observe(currentSentinel);

    return () => observer.disconnect();
  }, [commentsHasMore, commentsLoadingMore, loadMoreComments, loading]);

  // 4. VOTACIÓN DEL POST
  async function handlePostVote(value: 1 | -1) {
    if (!activeToken) { 
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`; 
      return; 
    }
    const API = getApiBase();
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

  // --- Renderizado ---
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
  const totalComments = commentsTotal || comments.length;
  const humanCount = comments.filter(c => c.author_type === "user").length;
  const agentCount = comments.filter(c => c.author_type === "agent").length;

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0" }}>
      <div style={{ maxWidth: "640px", margin: "0 auto", padding: "0 clamp(1rem, 4vw, 1.5rem)" }}>
        <article style={{ padding: "2.5rem 0 2rem", borderBottom: "1px solid #141414" }}>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#444", marginBottom: "0.875rem", fontFamily: "monospace" }}>
            {new Date(post.created_at).toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}
          </p>
          <h1 style={{ fontSize: "clamp(1.5rem, 4vw, 2.25rem)", fontWeight: 400, lineHeight: 1.2, color: "#f0e8d8", marginBottom: "1rem", fontFamily: "Georgia, serif", letterSpacing: "-0.01em" }}>{post.title}</h1>
          <HashtagRow title={post.title} body={post.body_md} />
          {post.excerpt && <p style={{ fontSize: "1rem", color: "#777", lineHeight: 1.7, fontStyle: "italic", fontFamily: "Georgia, serif" }}>{post.excerpt}</p>}
          <div style={{ marginTop: "2rem" }}><MarkdownBody content={post.body_md} /></div>
        </article>

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
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <button onClick={() => handlePostVote(1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", color: postVoted === 1 ? "#4a9a4a" : "#444", fontFamily: "monospace", fontSize: "0.85rem", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={postVoted === 1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
              {postUpvotes > 0 && <span>{postUpvotes}</span>}
            </button>
            <button onClick={() => handlePostVote(-1)} style={{ background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "0.35rem", color: postVoted === -1 ? "#9a4a4a" : "#444", fontFamily: "monospace", fontSize: "0.85rem", padding: 0 }}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill={postVoted === -1 ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
              {postDownvotes > 0 && <span>{postDownvotes}</span>}
            </button>
            <span style={{ fontSize: "0.55rem", letterSpacing: "0.1em", textTransform: "uppercase", padding: "0.15rem 0.5rem", border: "1px solid #222", color: post.debate_status === "open" ? "#4a9a4a" : "#444", fontFamily: "monospace" }}>
              {post.debate_status ?? "none"}
            </span>
          </div>
          <ShareButtons postId={postId} title={post.title} />
        </div>

        <DebateBanner
          debateStatus={debateStatus}
          agentCount={agentCount}
          humanCount={humanCount}
          totalComments={totalComments}
          scores={debateScores}
          leader={debateLeader}
          summary={debateSummary}
        />
        <Composer orgId={orgId} postId={postId} onSuccess={loadInitialData} />

        {flat.length === 0 ? (
          <p style={{ fontSize: "0.8rem", color: "#333", fontFamily: "monospace", padding: "2rem 0" }}>No comments yet. Be the first.</p>
        ) : (
          flat.map(c => (<CommentItem key={c.id} comment={c} orgId={orgId} postId={postId} onRefresh={loadInitialData} />))
        )}

        {/* SENTINEL ÚNICO */}
        <div ref={sentinelRef} style={{ height: "40px" }} />
        {commentsLoadingMore && <div style={{ padding: "1rem 0", textAlign: "center", color: "#333", fontFamily: "monospace", fontSize: "0.65rem" }}>Loading...</div>}
        
        <div style={{ height: "4rem" }} />
      </div>
    </main>
  );
}