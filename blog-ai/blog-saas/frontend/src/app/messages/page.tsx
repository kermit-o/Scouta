"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

function timeAgo(d: string) {
  const diff = Date.now() - new Date(d).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

export default function MessagesPage() {
  const router = useRouter();
  const [convs, setConvs] = useState<any[]>([]);
  const [activeConv, setActiveConv] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [body, setBody] = useState("");
  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const ws = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const me = user as any;

  const API = "/api/proxy";

  const loadConvs = useCallback(async () => {
    if (!token) return;
    const r = await fetch(`${API}/api/v1/messages/conversations`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (r.ok) setConvs(await r.json());
    setLoading(false);
  }, [token]);

  const { user, isLoaded } = useAuth() as any;
  const [token, setToken] = useState<string | null>(null);

  // Leer token directo de localStorage — más fiable que el contexto
  useEffect(() => {
    const t = localStorage.getItem("token");
    setToken(t);
  }, [isLoaded]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!token) {
      router.push("/login?next=/messages");
      return;
    }
    loadConvs();
  }, [token, isLoaded, loadConvs]);

  if (!isLoaded) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
    </main>
  );

  async function openConv(conv: any) {
    setActiveConv(conv);
    setMessages([]);
    ws.current?.close();

    const r = await fetch(`${API}/api/v1/messages/conversations/${conv.id}/messages`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (r.ok) setMessages(await r.json());

    // WebSocket — conectar directo al backend (bypass proxy)
    const backendHost = process.env.NEXT_PUBLIC_API_URL?.replace("https://", "wss://").replace("http://", "ws://") || `${window.location.protocol === "https:" ? "wss" : "ws"}://scouta-production.up.railway.app`;
    const wsUrl = `${backendHost}/api/v1/messages/ws/${conv.id}?token=${token}`;
    const socket = new WebSocket(wsUrl);
    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "message" || data.type === "new_message") {
        setMessages(prev => [...prev, data]);
        loadConvs();
      }
    };
    ws.current = socket;

    // Marcar como leído
    setConvs(prev => prev.map(c => c.id === conv.id ? { ...c, unread: 0 } : c));
  }

  async function sendMessage() {
    if (!body.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    ws.current.send(body.trim());
    setBody("");
  }

  async function searchUsers(q: string) {
    setSearch(q);
    if (q.length < 2) { setSearchResults([]); return; }
    const r = await fetch(`${API}/api/v1/users/search?q=${encodeURIComponent(q)}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (r.ok) setSearchResults(await r.json());
  }

  async function startConv(username: string) {
    const r = await fetch(`${API}/api/v1/messages/start/${username}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }
    });
    if (r.ok) {
      const conv = await r.json();
      setSearch(""); setSearchResults([]);
      await loadConvs();
      openConv(conv);
    }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const totalUnread = convs.reduce((a, c) => a + (c.unread || 0), 0);

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <div style={{ borderBottom: "1px solid #141414", padding: "1.25rem 2rem", display: "flex", alignItems: "center", gap: "1rem" }}>
        <Link href="/posts" style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#444", textDecoration: "none" }}>← Feed</Link>
        <span style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#555", fontFamily: "monospace" }}>
          Messages {totalUnread > 0 && <span style={{ color: "#4a9a4a" }}>· {totalUnread}</span>}
        </span>
      </div>

      <div style={{ display: "flex", flex: 1, maxWidth: "900px", width: "100%", margin: "0 auto", height: "calc(100vh - 60px)" }}>
        {/* Sidebar */}
        <div style={{ width: "280px", borderRight: "1px solid #0f0f0f", display: "flex", flexDirection: "column", flexShrink: 0 }}>
          {/* Search */}
          <div style={{ padding: "1rem", borderBottom: "1px solid #0f0f0f", position: "relative" }}>
            <input
              value={search}
              onChange={e => searchUsers(e.target.value)}
              placeholder="Find user..."
              style={{ width: "100%", background: "#111", border: "1px solid #1a1a1a", color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.8rem", fontFamily: "monospace", outline: "none", boxSizing: "border-box" }}
            />
            {searchResults.length > 0 && (
              <div style={{ position: "absolute", left: "1rem", right: "1rem", background: "#111", border: "1px solid #1a1a1a", zIndex: 10 }}>
                {searchResults.map((u: any) => (
                  <div key={u.id} onClick={() => startConv(u.username)} style={{ padding: "0.75rem", cursor: "pointer", borderBottom: "1px solid #0f0f0f", fontSize: "0.8rem" }}>
                    <span style={{ color: "#d8d0c0", fontFamily: "Georgia, serif" }}>{u.display_name || u.username}</span>
                    <span style={{ color: "#333", fontFamily: "monospace", marginLeft: "0.5rem", fontSize: "0.65rem" }}>@{u.username}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Conversation list */}
          <div style={{ flex: 1, overflowY: "auto" }}>
            {loading ? (
              <p style={{ color: "#2a2a2a", fontFamily: "monospace", fontSize: "0.75rem", padding: "1rem" }}>Loading...</p>
            ) : convs.length === 0 ? (
              <p style={{ color: "#2a2a2a", fontFamily: "monospace", fontSize: "0.75rem", padding: "1rem", textAlign: "center" }}>No conversations yet</p>
            ) : convs.map(c => (
              <div key={c.id} onClick={() => openConv(c)} style={{
                padding: "0.875rem 1rem", cursor: "pointer", borderBottom: "1px solid #0f0f0f",
                background: activeConv?.id === c.id ? "#111" : "transparent",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  {c.other_user?.avatar_url ? (
                    <img src={c.other_user.avatar_url} style={{ width: 36, height: 36, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
                  ) : (
                    <div style={{ width: 36, height: 36, borderRadius: "50%", background: "#1a2a1a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.8rem", color: "#4a9a4a", fontFamily: "monospace", flexShrink: 0 }}>
                      {(c.other_user?.display_name || "?")[0].toUpperCase()}
                    </div>
                  )}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontSize: "0.85rem", color: "#d8d0c0", fontFamily: "Georgia, serif" }}>{c.other_user?.display_name}</span>
                      <span style={{ fontSize: "0.6rem", color: "#2a2a2a", fontFamily: "monospace" }}>{c.last_message_at ? timeAgo(c.last_message_at) : ""}</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <p style={{ fontSize: "0.7rem", color: "#333", margin: 0, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", maxWidth: "160px" }}>{c.last_message_preview}</p>
                      {c.unread > 0 && <span style={{ background: "#1a3a1a", color: "#4a9a4a", fontSize: "0.55rem", padding: "0.1rem 0.4rem", fontFamily: "monospace" }}>{c.unread}</span>}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat area */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {!activeConv ? (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <p style={{ color: "#2a2a2a", fontFamily: "monospace", fontSize: "0.8rem" }}>Select a conversation or search for a user</p>
            </div>
          ) : (
            <>
              {/* Chat header */}
              <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid #0f0f0f", display: "flex", alignItems: "center", gap: "0.75rem" }}>
                {activeConv.other_user?.avatar_url ? (
                  <img src={activeConv.other_user.avatar_url} style={{ width: 32, height: 32, borderRadius: "50%", objectFit: "cover" }} />
                ) : (
                  <div style={{ width: 32, height: 32, borderRadius: "50%", background: "#1a2a1a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", color: "#4a9a4a", fontFamily: "monospace" }}>
                    {(activeConv.other_user?.display_name || "?")[0].toUpperCase()}
                  </div>
                )}
                <Link href={`/u/${activeConv.other_user?.username}`} style={{ textDecoration: "none" }}>
                  <span style={{ fontSize: "0.9rem", color: "#d8d0c0", fontFamily: "Georgia, serif" }}>{activeConv.other_user?.display_name}</span>
                  <span style={{ fontSize: "0.65rem", color: "#333", fontFamily: "monospace", marginLeft: "0.5rem" }}>@{activeConv.other_user?.username}</span>
                </Link>
              </div>

              {/* Messages */}
              <div style={{ flex: 1, overflowY: "auto", padding: "1rem 1.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {messages.map((m, i) => {
                  const isMe = m.sender_id === me?.id;
                  return (
                    <div key={m.id || i} style={{ display: "flex", justifyContent: isMe ? "flex-end" : "flex-start" }}>
                      <div style={{
                        maxWidth: "70%", padding: "0.5rem 0.875rem",
                        background: isMe ? "#1a2a1a" : "#111",
                        border: `1px solid ${isMe ? "#2a4a2a" : "#1a1a1a"}`,
                        fontSize: "0.875rem", color: "#d8d0c0", fontFamily: "Georgia, serif", lineHeight: 1.5,
                      }}>
                        {m.body}
                        <div style={{ fontSize: "0.55rem", color: "#2a2a2a", fontFamily: "monospace", marginTop: "0.25rem", textAlign: isMe ? "right" : "left" }}>
                          {m.created_at ? timeAgo(m.created_at) : ""}
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>

              {/* Input */}
              <div style={{ padding: "1rem 1.5rem", borderTop: "1px solid #0f0f0f", display: "flex", gap: "0.75rem", alignItems: "flex-end" }}>
                <textarea
                  value={body}
                  onChange={e => setBody(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder="Type a message..."
                  rows={1}
                  style={{ flex: 1, background: "transparent", border: "none", borderBottom: "1px solid #1a1a1a", color: "#e8e0d0", padding: "0.5rem 0", fontSize: "0.9rem", fontFamily: "Georgia, serif", resize: "none", outline: "none" }}
                />
                <button onClick={sendMessage} disabled={!body.trim()} style={{
                  background: "#1a2a1a", border: "1px solid #2a4a2a",
                  color: !body.trim() ? "#444" : "#4a9a4a",
                  padding: "0.4rem 1rem", cursor: !body.trim() ? "not-allowed" : "pointer",
                  fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.1em", flexShrink: 0,
                }}>→</button>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
