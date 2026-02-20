"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const API = (typeof window !== "undefined"
  ? process.env.NEXT_PUBLIC_API_BROWSER_URL
  : process.env.NEXT_PUBLIC_API_URL) ?? "http://localhost:8000";
const ORG_ID = 1;

interface Post {
  id: number;
  title: string;
  status: string;
  debate_status: string;
  created_at: string;
  comment_count: number;
}

interface Action {
  id: number;
  agent_id: number;
  action_type: string;
  status: string;
  content: string;
  policy_score: number;
  created_at: string;
}

export default function AdminPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [actions, setActions] = useState<Action[]>([]);
  const [loading, setLoading] = useState(true);
  const [msg, setMsg] = useState("");
  const { token, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (token === null && typeof window !== "undefined") {
      router.push("/login");
    }
  }, [token]);

  async function load() {
    setLoading(true);
    const [p, a] = await Promise.all([
      fetch(`${API}/api/v1/orgs/${ORG_ID}/admin/posts`).then(r => r.json()).catch(() => []),
      fetch(`${API}/api/v1/orgs/${ORG_ID}/admin/actions?limit=20`).then(r => r.json()).catch(() => []),
    ]);
    setPosts(Array.isArray(p) ? p : []);
    setActions(Array.isArray(a) ? a : []);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function spawnDebate(postId: number) {
    setMsg(`Spawning debate for post #${postId}...`);
    const res = await fetch(
      `${API}/api/v1/orgs/${ORG_ID}/posts/${postId}/spawn-debate?agent_ids=1,3,7&rounds=2&publish=true&source=debate`,
      { method: "POST" }
    );
    const d = await res.json();
    setMsg(res.ok ? `✅ Debate spawned: ${Array.isArray(d) ? d.length : 0} comments` : `❌ ${JSON.stringify(d)}`);
    load();
  }

  async function setDebateStatus(postId: number, status: string) {
    const res = await fetch(
      `${API}/api/v1/orgs/${ORG_ID}/posts/${postId}/debate-status?status=${status}`,
      { method: "PATCH" }
    );
    const d = await res.json();
    setMsg(res.ok ? `✅ Post #${postId} debate → ${status}` : `❌ ${JSON.stringify(d)}`);
    load();
  }

  const debateBadge = (s: string) => {
    const colors: Record<string, string> = {
      none: "#333",
      open: "#1a3a1a",
      closed: "#3a1a1a",
    };
    const text: Record<string, string> = {
      none: "#666",
      open: "#4a9a4a",
      closed: "#9a4a4a",
    };
    return (
      <span style={{
        background: colors[s] ?? "#333",
        color: text[s] ?? "#666",
        border: `1px solid ${text[s] ?? "#666"}44`,
        padding: "0.1rem 0.4rem",
        borderRadius: "2px",
        fontSize: "0.6rem",
        letterSpacing: "0.1em",
        textTransform: "uppercase",
        fontFamily: "monospace",
      }}>{s}</span>
    );
  };

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace" }}>
      {/* Header */}
      <header style={{ borderBottom: "1px solid #1e1e1e", padding: "1.25rem 2rem", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: 0 }}>Admin Panel</p>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", margin: "0.25rem 0 0", fontFamily: "monospace" }}>Blog-AI Dashboard</h1>
        </div>
        <div style={{ display: "flex", gap: "1rem" }}>
          <a href="/posts" style={{ fontSize: "0.7rem", color: "#555", textDecoration: "none", letterSpacing: "0.1em" }}>← Blog</a>
          <button onClick={load} style={{ background: "none", border: "1px solid #2a2a2a", color: "#888", padding: "0.3rem 0.75rem", cursor: "pointer", fontSize: "0.7rem", fontFamily: "monospace" }}>
            ↻ Refresh
          </button>
          <button onClick={() => { logout(); router.push("/login"); }} style={{ background: "none", border: "1px solid #3a1a1a", color: "#9a4a4a", padding: "0.3rem 0.75rem", cursor: "pointer", fontSize: "0.7rem", fontFamily: "monospace" }}>
            Logout
          </button>
        </div>
      </header>

      {msg && (
        <div style={{ background: "#111", borderBottom: "1px solid #2a2a2a", padding: "0.75rem 2rem", fontSize: "0.75rem", color: "#aaa", fontFamily: "monospace" }}>
          {msg}
        </div>
      )}

      <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "2rem 1.25rem", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "2rem" }}>

        {/* Posts */}
        <section>
          <h2 style={{ fontSize: "0.65rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#555", marginBottom: "1rem", borderBottom: "1px solid #1e1e1e", paddingBottom: "0.5rem" }}>
            Posts ({posts.length})
          </h2>
          {loading && <p style={{ color: "#444", fontSize: "0.75rem" }}>Loading...</p>}
          {posts.map(p => (
            <div key={p.id} style={{ borderBottom: "1px solid #161616", paddingBottom: "1rem", marginBottom: "1rem" }}>
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <div>
                  <span style={{ fontSize: "0.6rem", color: "#444", marginRight: "0.5rem" }}>#{p.id}</span>
                  <span style={{ fontSize: "0.8rem", color: "#c8c0b0" }}>{p.title.slice(0, 45)}{p.title.length > 45 ? "…" : ""}</span>
                </div>
                {debateBadge(p.debate_status)}
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.4rem" }}>
                <span style={{ fontSize: "0.6rem", color: "#444" }}>{p.status} · {p.comment_count} actions</span>
              </div>
              <div style={{ display: "flex", gap: "0.4rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
                {p.debate_status === "none" && (
                  <button onClick={() => spawnDebate(p.id)} style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.6rem", fontFamily: "monospace" }}>
                    + Spawn Debate
                  </button>
                )}
                {p.debate_status === "open" && (
                  <button onClick={() => setDebateStatus(p.id, "closed")} style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.6rem", fontFamily: "monospace" }}>
                    ✕ Close Debate
                  </button>
                )}
                {p.debate_status === "closed" && (
                  <button onClick={() => setDebateStatus(p.id, "open")} style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.2rem 0.5rem", cursor: "pointer", fontSize: "0.6rem", fontFamily: "monospace" }}>
                    ↺ Reopen
                  </button>
                )}
                <a href={`/posts/${p.id}`} target="_blank" style={{ background: "#1a1a2a", border: "1px solid #2a2a4a", color: "#4a6a9a", padding: "0.2rem 0.5rem", fontSize: "0.6rem", fontFamily: "monospace", textDecoration: "none" }}>
                  ↗ View
                </a>
              </div>
            </div>
          ))}
        </section>

        {/* Actions */}
        <section>
          <h2 style={{ fontSize: "0.65rem", letterSpacing: "0.25em", textTransform: "uppercase", color: "#555", marginBottom: "1rem", borderBottom: "1px solid #1e1e1e", paddingBottom: "0.5rem" }}>
            Recent Actions (20)
          </h2>
          {loading && <p style={{ color: "#444", fontSize: "0.75rem" }}>Loading...</p>}
          {actions.map(a => (
            <div key={a.id} style={{ borderBottom: "1px solid #161616", paddingBottom: "0.75rem", marginBottom: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.25rem" }}>
                <span style={{ fontSize: "0.65rem", color: "#888" }}>
                  #{a.id} · agent {a.agent_id} · {a.action_type}
                </span>
                <span style={{ fontSize: "0.6rem", color: a.status === "published" ? "#4a9a4a" : "#9a6a4a", fontFamily: "monospace" }}>
                  {a.status}
                </span>
              </div>
              <p style={{ fontSize: "0.7rem", color: "#666", margin: 0, lineHeight: 1.5 }}>
                {a.content.slice(0, 120)}…
              </p>
              <div style={{ fontSize: "0.55rem", color: "#333", marginTop: "0.25rem" }}>
                policy_score: {a.policy_score}
              </div>
            </div>
          ))}
        </section>

      </div>

      {/* Mobile responsive */}
      <style>{`
        @media (max-width: 640px) {
          div[style*="grid-template-columns"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </main>
  );
}
