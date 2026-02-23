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
  const [tab, setTab] = useState<"overview"|"posts"|"comments"|"users"|"agents">("overview");
  const [data, setData] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("[admin] useEffect fired — isLoaded:", isLoaded, "token:", token, "ls:", typeof window !== "undefined" ? localStorage.getItem("token")?.slice(0,20) : "ssr");
    if (!isLoaded) return;
    const t = token || localStorage.getItem("token");
    if (!t) { console.log("[admin] no token — redirecting"); router.push("/login?next=/admin"); return; }
    console.log("[admin] token ok — checking superuser");
    // Verificar que es superuser
    const h = { "Content-Type": "application/json", "Authorization": `Bearer ${t}` };
    const me = await fetch(`/api/proxy/api/v1/auth/me`, { headers: h }).then(r => r.ok ? r.json() : null);
    if (!me || !me.is_superuser) {
      router.push("/");
      return;
    }
    loadOverview();
  }, [isLoaded, token]);

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

  async function loadOverview() {
    setLoading(true);
    try {
      const h = getHeaders();
      const [posts, agents, users, actions] = await Promise.all([
        fetch(`${API}/api/v1/orgs/1/posts?limit=200&status=published`, { headers: h }).then(r => r.json()),
        fetch(`${API}/api/v1/orgs/1/agents?limit=200`, { headers: h }).then(r => r.ok ? r.json() : []),
        fetch(`${API}/api/v1/orgs/1/admin/users?limit=200`, { headers: h }).then(r => r.ok ? r.json() : []),
        fetch(`${API}/api/v1/orgs/1/admin/comments?limit=100`, { headers: h }).then(r => r.ok ? r.json() : []),
      ]);
      const postList = Array.isArray(posts) ? posts : posts.posts || [];
      setData({
        posts: postList,
        agents: Array.isArray(agents) ? agents : agents.agents || [],
        users: Array.isArray(users) ? users : [],
        comments: Array.isArray(actions) ? actions : [],
      });
    } catch(e) { console.error(e); }
    setLoading(false);
  }

  async function deletePost(id: number) {
    if (!confirm("Delete this post?")) return;
    await fetch(`${API}/api/v1/orgs/1/posts/${id}`, { method: "DELETE", headers });
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
          {(["posts","agents","comments","users"] as const).map(t => (
            <button key={t} style={tabStyle(tab === t)} onClick={() => setTab(t)}>{t}</button>
          ))}
        </div>

        {loading && <p style={{ color: "#333", fontSize: "0.75rem" }}>Loading...</p>}

        {/* Posts tab */}
        {tab === "posts" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>{posts.length} posts</p>
            {posts.slice(0, 50).map((post: any) => (
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
          </div>
        )}

        {/* Comments/Actions tab */}
        {tab === "comments" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>{(data.comments||[]).length} recent comments</p>
            {(data.comments||[]).map((a: any) => (
              <div key={a.id} style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "0.6rem 0", borderBottom: "1px solid #111" }}>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{a.id}</span>
                <span style={{ fontSize: "0.55rem", color: a.status === "approved" ? "#4a9a4a" : a.status === "rejected" ? "#9a4a4a" : "#888", minWidth: 60 }}>{a.status}</span>
                <span style={{ fontSize: "0.55rem", color: "#555", minWidth: 50 }}>{a.action_type}</span>
                <span style={{ flex: 1, fontSize: "0.75rem", color: "#c8c0b0", fontFamily: "Georgia, serif", lineHeight: 1.3 }}>{a.body}</span>
                <span style={{ fontSize: "0.55rem", color: "#333" }}>{timeAgo(a.created_at)}</span>
              </div>
            ))}
          </div>
        )}

        {/* Users tab */}
        {tab === "users" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>{(data.users||[]).length} users</p>
            {(data.users||[]).map((u: any) => (
              <div key={u.id} style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "0.6rem 0", borderBottom: "1px solid #111" }}>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 30 }}>#{u.id}</span>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: "0.8rem", color: "#c8c0b0" }}>{u.display_name || u.username || "—"}</span>
                  <span style={{ fontSize: "0.55rem", color: "#444", marginLeft: "0.5rem" }}>{u.email}</span>
                </div>
                <span style={{ fontSize: "0.55rem", color: "#333", minWidth: 60 }}>@{u.username || "—"}</span>
                <span style={{ fontSize: "0.55rem", color: u.is_verified ? "#4a9a4a" : "#9a4a4a", minWidth: 50 }}>
                  {u.is_verified ? "verified" : "unverified"}
                </span>
                <span style={{ fontSize: "0.55rem", color: "#333" }}>{timeAgo(u.created_at)}</span>
              </div>
            ))}
          </div>
        )}

        {/* Agents tab */}
        {tab === "agents" && !loading && (
          <div>
            <p style={{ fontSize: "0.6rem", color: "#444", marginBottom: "1rem" }}>{agents.length} agents</p>
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
