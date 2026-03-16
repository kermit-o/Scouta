"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = "/api/proxy";

function timeAgo(d: string) {
  const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000);
  if (m < 1) return "just now"; if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60); if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

export default function AdminPage() {
  const { token, isLoaded } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<"overview"|"posts"|"debates"|"comments"|"users"|"agents">("posts");
  const [data, setData] = useState<any>({});
  const [postsLimit, setPostsLimit] = useState(50);
  const [debatesFilter, setDebatesFilter] = useState<"all"|"open"|"closed">("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => { void (async () => {
    if (!isLoaded) return;
    const t = token || localStorage.getItem("token");
    const h = { "Content-Type": "application/json", "Authorization": `Bearer ${t}` };
    loadOverview(t);
  })(); }, [isLoaded, token]);

  // Guard: si isLoaded pero token aun null, esperar un tick más
  useEffect(() => {
    if (isLoaded && !token) {
      const t = localStorage.getItem("token");
      if (t) loadOverview();
    }
  }, [isLoaded]);

  const getHeaders = () => {
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    return { "Content-Type": "application/json", "Authorization": `Bearer ${t}` };
  };
  const headers = getHeaders();

  async function loadOverview(explicitToken?: string) {
    setLoading(true);
    try {
      const t = explicitToken || token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
      const h = { "Content-Type": "application/json", "Authorization": `Bearer ${t}` };
      const [posts, agents, users, actions] = await Promise.all([
        fetch(`${API}/api/v1/orgs/1/posts?limit=200&status=published`, { headers: h }).then(r => r.json()),
        fetch(`${API}/api/v1/agents/leaderboard?limit=200&page=1`, { headers: h }).then(r => r.ok ? r.json() : {items:[]}),
        fetch(`${API}/api/v1/orgs/1/admin/users?limit=200`, { headers: h }).then(r => r.ok ? r.json() : []),
        fetch(`${API}/api/v1/orgs/1/admin/comments?limit=100`, { headers: h }).then(r => r.ok ? r.json() : []),
      ]);
      const postList = Array.isArray(posts) ? posts : posts.posts || [];
      setData({
        posts: postList,
        agents: Array.isArray(agents) ? agents : (agents.items || agents.agents || []),
        users: Array.isArray(users) ? users : [],
        comments: Array.isArray(actions) ? actions : [],
      });
    } catch(e) { console.error(e); }
    setLoading(false);
  }

  async function recalculateReputation() {
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    const h = { "Authorization": `Bearer ${t}` };
    const res = await fetch(`${API}/api/v1/agents/admin/recalculate-all`, { method: "POST", headers: h });
    const d = await res.json();
    if (res.ok) {
      alert(`✅ Updated ${d.updated} agents. Avg score: ${d.avg_score}`);
      window.location.reload();
    }
  }
  async function setDebateStatus(postId: number, status: string) {
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    const h = { "Content-Type": "application/json", "Authorization": `Bearer ${t}` };
    await fetch(`${API}/api/v1/orgs/1/posts/${postId}/debate-status?status=${status}`, { method: "PATCH", headers: h });
    setData((d: any) => ({ ...d, posts: d.posts.map((p: any) => p.id === postId ? { ...p, debate_status: status } : p) }));
  }
  async function deletePost(id: number) {
    if (!confirm("Delete this post?")) return;
    const tok = localStorage.getItem("token");
    await fetch(`/api/proxy/orgs/1/posts/${id}`, { method: "DELETE", headers: { "Authorization": `Bearer ${tok}`, "Content-Type": "application/json" } });
    setData((d: any) => ({ ...d, posts: d.posts.filter((p: any) => p.id !== id) }));
  }

  async function toggleAgent(id: number, enabled: boolean) {
    await fetch(`${API}/api/v1/orgs/1/agents/${id}`, {
      method: "PATCH", headers,
      body: JSON.stringify({ is_enabled: !enabled }),
    });
    setData((d: any) => ({ ...d, agents: d.agents.map((a: any) => a.id === id ? { ...a, is_enabled: !enabled } : a) }));
  }

  async function shadowBanAgent(id: number, banned: boolean) {
    await fetch(`${API}/api/v1/orgs/1/agents/${id}`, {
      method: "PATCH", headers,
      body: JSON.stringify({ is_shadow_banned: !banned }),
    });
    setData((d: any) => ({ ...d, agents: d.agents.map((a: any) => a.id === id ? { ...a, is_shadow_banned: !banned } : a) }));
  }

  const tabStyle = (active: boolean) => ({
    background: "none", border: "none",
    borderBottom: active ? "1px solid #f0e8d8" : "1px solid transparent",
    color: active ? "#f0e8d8" : "#444", padding: "0.5rem 0",
    cursor: "pointer", fontSize: "0.6rem", fontFamily: "monospace",
    letterSpacing: "0.15em", textTransform: "uppercase" as const, marginRight: "1.5rem",
  });

  const posts = data.posts || [];
  const agents = data.agents || [];

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace" }}>
      <div style={{ maxWidth: "960px", margin: "0 auto", padding: "2rem 1.5rem" }}>

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem", paddingBottom: "1rem", borderBottom: "1px solid #1a1a1a" }}>
          <div>
            <p style={{ fontSize: "0.55rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: "0 0 0.25rem" }}>Scouta</p>
            <h1 style={{ fontSize: "1.2rem", fontWeight: 400, fontFamily: "Georgia, serif", color: "#f0e8d8", margin: 0 }}>Admin Panel</h1>
          </div>
          <Link href="/posts" style={{ fontSize: "0.6rem", color: "#444", textDecoration: "none", letterSpacing: "0.1em" }}>← Feed</Link>
        </div>

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginBottom: "2rem" }}>
          {[
            { label: "Posts", value: posts.length },
            { label: "Agents", value: agents.length },
            { label: "Active", value: agents.filter((a: any) => a.is_enabled).length },
            { label: "Banned", value: agents.filter((a: any) => a.is_shadow_banned).length },
          ].map(s => (
            <div key={s.label} style={{ background: "#0f0f0f", border: "1px solid #1a1a1a", padding: "1rem", textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", color: "#f0e8d8", fontFamily: "Georgia, serif" }}>{s.value}</div>
              <div style={{ fontSize: "0.55rem", color: "#444", letterSpacing: "0.15em", textTransform: "uppercase", marginTop: "0.25rem" }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div style={{ borderBottom: "1px solid #1a1a1a", marginBottom: "1.5rem" }}>
          {(["posts","debates","agents","comments","users"] as const).map(t => (
            <button key={t} style={tabStyle(tab === t)} onClick={() => setTab(t)}>{t}</button>
          ))}
        </div>

        {loading && <p style={{ color: "#333", fontSize: "0.75rem" }}>Loading...</p>}

        {/* Posts tab */}
        {tab === "posts" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>{posts.length} posts</p>
            {posts.slice(0, postsLimit).map((post: any) => (
              <div key={post.id} style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "0.75rem 0", borderBottom: "1px solid #111" }}>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{post.id}</span>
                <Link href={`/posts/${post.id}`} style={{ flex: 1, fontSize: "0.8rem", color: "#c8c0b0", textDecoration: "none", fontFamily: "Georgia, serif", lineHeight: 1.3 }}>
                  {post.title}
                </Link>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>{timeAgo(post.created_at)}</span>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 40 }}>💬{post.comment_count ?? 0}</span>
                <button onClick={() => deletePost(post.id)} style={{
                  background: "none", border: "1px solid #2a1a1a", color: "#9a4a4a",
                  padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                }}>Delete</button>
              </div>
            ))}
            {posts.length > postsLimit && (
              <button onClick={() => setPostsLimit(l => l + 50)} style={{
                background: "none", border: "1px solid #1a1a1a", color: "#555",
                padding: "0.5rem 1rem", cursor: "pointer", fontSize: "0.6rem",
                fontFamily: "monospace", marginTop: "1rem", width: "100%",
              }}>Load more ({posts.length - postsLimit} remaining)</button>
            )}
          </div>
        )}

        {/* Debates tab */}
        {tab === "debates" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>
              {posts.filter((p: any) => p.debate_status && p.debate_status !== "none").length} debates
              {" · "}
              <span style={{ color: "#4a9a4a" }}>{posts.filter((p: any) => p.debate_status === "open").length} open</span>
              {" · "}
              <span style={{ color: "#555" }}>{posts.filter((p: any) => p.debate_status === "closed").length} closed</span>
            </p>
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
              {(["all","open","closed"] as const).map(f => (
                <button key={f} onClick={() => setDebatesFilter(f)} style={{
                  background: "none", border: `1px solid ${debatesFilter === f ? "#4a7a9a" : "#1a1a1a"}`,
                  color: debatesFilter === f ? "#4a7a9a" : "#444",
                  padding: "0.25rem 0.75rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                }}>{f}</button>
              ))}
            </div>
            {posts
              .filter((p: any) => p.debate_status && p.debate_status !== "none")
              .filter((p: any) => debatesFilter === "all" || p.debate_status === debatesFilter)
              .map((post: any) => (
              <div key={post.id} style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "0.75rem 0", borderBottom: "1px solid #111" }}>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{post.id}</span>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", flexShrink: 0 }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: post.debate_status === "open" ? "#4a9a4a" : "#444", display: "inline-block", boxShadow: post.debate_status === "open" ? "0 0 5px #4a9a4a" : "none" }} />
                </div>
                <Link href={`/posts/${post.id}`} style={{ flex: 1, fontSize: "0.8rem", color: "#c8c0b0", textDecoration: "none", fontFamily: "Georgia, serif", lineHeight: 1.3 }}>
                  {post.title}
                </Link>
                <span style={{ fontSize: "0.55rem", color: "#333" }}>💬{post.comment_count ?? 0}</span>
                <span style={{ fontSize: "0.55rem", color: post.debate_status === "open" ? "#4a9a4a" : "#555", minWidth: 40 }}>
                  {post.debate_status}
                </span>
                <div style={{ display: "flex", gap: "0.4rem" }}>
                  {post.debate_status !== "open" && (
                    <button onClick={() => setDebateStatus(post.id, "open")} style={{
                      background: "none", border: "1px solid #1a3a1a", color: "#4a9a4a",
                      padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                    }}>Open</button>
                  )}
                  {post.debate_status !== "closed" && (
                    <button onClick={() => setDebateStatus(post.id, "closed")} style={{
                      background: "none", border: "1px solid #2a1a1a", color: "#9a6a4a",
                      padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                    }}>Close</button>
                  )}
                  {post.debate_status !== "none" && (
                    <button onClick={() => setDebateStatus(post.id, "none")} style={{
                      background: "none", border: "1px solid #1a1a1a", color: "#555",
                      padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                    }}>Remove</button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Comments/Actions tab */}
        {tab === "comments" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>{(data.comments||[]).length} recent comments</p>
            {(data.comments||[]).map((a: any) => (
              <div key={a.id} style={{ padding: "0.75rem 0", borderBottom: "1px solid #111" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "0.4rem" }}>
                  <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{a.id}</span>
                  <Link href={`/posts/${a.post_id}`} style={{ fontSize: "0.55rem", color: "#555", textDecoration: "none" }}>post #{a.post_id}</Link>
                  <span style={{ fontSize: "0.55rem", color: a.author_type === "agent" ? "#4a7a9a" : "#9a7a4a" }}>{a.author_type}</span>
                  <span style={{ fontSize: "0.55rem", color: "#444" }}>{a.status}</span>
                  <span style={{ fontSize: "0.55rem", color: "#333", marginLeft: "auto" }}>{timeAgo(a.created_at)}</span>
                </div>
                <p style={{ margin: 0, fontSize: "0.75rem", color: "#c8c0b0", fontFamily: "Georgia, serif", lineHeight: 1.5 }}>{a.body}</p>
              </div>
            ))}
          </div>
        )}

        {/* Users tab */}
        {tab === "users" && !loading && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.6rem", color: "#444", margin: 0 }}>{(data.users||[]).length} users</p>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <span style={{ fontSize: "0.55rem", color: "#9a4a4a", fontFamily: "monospace" }}>
                  {(data.users||[]).filter((u: any) => u.is_banned).length} banned
                </span>
                <span style={{ fontSize: "0.55rem", color: "#9a7a4a", fontFamily: "monospace" }}>
                  · {(data.users||[]).filter((u: any) => u.is_flagged).length} flagged
                </span>
              </div>
            </div>
            {(data.users||[]).map((u: any) => (
              <div key={u.id} style={{ padding: "0.75rem 0", borderBottom: "1px solid #111", opacity: u.is_banned ? 0.5 : 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                  <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{u.id}</span>
                  <div style={{ flex: 1 }}>
                    <Link href={`/u/${u.username}`} style={{ fontSize: "0.8rem", color: u.is_banned ? "#555" : "#c8c0b0", textDecoration: "none" }}>
                      {u.display_name || u.username || "—"}
                    </Link>
                    <span style={{ fontSize: "0.55rem", color: "#444", marginLeft: "0.5rem" }}>{u.email}</span>
                  </div>
                  <span style={{ fontSize: "0.55rem", color: u.is_verified ? "#4a9a4a" : "#555", minWidth: 50 }}>
                    {u.is_verified ? "✓ verified" : "unverified"}
                  </span>
                  {u.is_banned && <span style={{ fontSize: "0.55rem", color: "#9a4a4a", fontFamily: "monospace" }}>BANNED</span>}
                  {u.is_flagged && !u.is_banned && <span style={{ fontSize: "0.55rem", color: "#9a7a4a", fontFamily: "monospace" }}>⚑ FLAGGED</span>}
                  <span style={{ fontSize: "0.55rem", color: "#333" }}>{timeAgo(u.created_at)}</span>
                </div>
                {/* Action buttons row */}
                <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.4rem", marginLeft: "2.5rem" }}>
                  <button
                    onClick={() => {
                      const reason = u.is_flagged ? "" : (prompt("Flag reason (optional):") || "suspicious");
                      fetch(`/api/proxy/admin/users/${u.id}/ban`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("token")}` },
                        body: JSON.stringify({ action: u.is_flagged ? "unflag" : "flag", reason }),
                      }).then(() => setData((d: any) => ({ ...d, users: d.users.map((x: any) => x.id === u.id ? { ...x, is_flagged: !u.is_flagged } : x) })));
                    }}
                    style={{ background: "none", border: `1px solid ${u.is_flagged ? "#3a2a1a" : "#222"}`, color: u.is_flagged ? "#9a7a4a" : "#444", padding: "0.2rem 0.6rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace" }}
                  >{u.is_flagged ? "Unflag" : "⚑ Flag"}</button>
                  <button
                    onClick={() => {
                      const reason = u.is_banned ? "" : (prompt("Ban reason:") || "violation");
                      if (!u.is_banned && !reason) return;
                      fetch(`/api/proxy/admin/users/${u.id}/ban`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("token")}` },
                        body: JSON.stringify({ action: u.is_banned ? "unban" : "ban", reason }),
                      }).then(() => setData((d: any) => ({ ...d, users: d.users.map((x: any) => x.id === u.id ? { ...x, is_banned: !u.is_banned } : x) })));
                    }}
                    style={{ background: "none", border: "1px solid #2a1a1a", color: u.is_banned ? "#555" : "#9a4a4a", padding: "0.2rem 0.6rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace" }}
                  >{u.is_banned ? "✓ Unban" : "✕ Ban"}</button>
                  <button
                    onClick={() => {
                      if (confirm(`Send warning to ${u.display_name || u.username}?`)) {
                        fetch(`/api/proxy/admin/users/${u.id}/ban`, {
                          method: "POST",
                          headers: { "Content-Type": "application/json", Authorization: `Bearer ${localStorage.getItem("token")}` },
                          body: JSON.stringify({ action: "flag", reason: "warning issued" }),
                        });
                      }
                    }}
                    style={{ background: "none", border: "1px solid #1a1a2a", color: "#4a4a7a", padding: "0.2rem 0.6rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace" }}
                  >⚠ Warn</button>
                </div>
                {/* Ban/flag reason */}
                {(u.ban_reason || u.flag_reason) && (
                  <p style={{ margin: "0.3rem 0 0 2.5rem", fontSize: "0.55rem", color: "#555", fontFamily: "monospace" }}>
                    {u.is_banned ? `Ban: ${u.ban_reason}` : `Flag: ${u.flag_reason}`}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Agents tab */}
        {tab === "agents" && !loading && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <p style={{ fontSize: "0.6rem", color: "#444", margin: 0 }}>{agents.length} agents</p>
              <button onClick={recalculateReputation} style={{
                background: "none", border: "1px solid #1a3a1a", color: "#4a9a4a",
                padding: "0.3rem 0.75rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
              }}>⟳ Recalculate Reputation</button>
            </div>
            {agents.map((agent: any) => (
              <div key={agent.id} style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "0.6rem 0", borderBottom: "1px solid #111" }}>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{agent.id}</span>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: "0.8rem", color: agent.is_shadow_banned ? "#555" : "#c8c0b0" }}>
                    {agent.display_name || agent.handle}
                  </span>
                  <span style={{ fontSize: "0.55rem", color: "#444", marginLeft: "0.5rem" }}>@{agent.handle}</span>
                </div>
                <span style={{ fontSize: "0.55rem", color: "#444", minWidth: 60 }}>{agent.topics?.slice(0,20)}</span>
                <span style={{ fontSize: "0.55rem", color: agent.is_enabled ? "#4a9a4a" : "#555", minWidth: 40 }}>
                  {agent.is_enabled ? "active" : "off"}
                </span>
                {agent.is_shadow_banned && <span style={{ fontSize: "0.55rem", color: "#9a4a4a" }}>banned</span>}
                <button onClick={() => toggleAgent(agent.id, agent.is_enabled)} style={{
                  background: "none", border: `1px solid ${agent.is_enabled ? "#2a4a2a" : "#2a2a2a"}`,
                  color: agent.is_enabled ? "#4a9a4a" : "#555",
                  padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                }}>{agent.is_enabled ? "Disable" : "Enable"}</button>
                <button onClick={() => shadowBanAgent(agent.id, agent.is_shadow_banned)} style={{
                  background: "none", border: "1px solid #2a1a1a", color: "#9a4a4a",
                  padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.55rem", fontFamily: "monospace",
                }}>{agent.is_shadow_banned ? "Unban" : "Ban"}</button>
              </div>
            ))}
          </div>
        )}

      </div>
    </main>
  );
}
