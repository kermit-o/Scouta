"use client";
import React, { useEffect, useState, useRef, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = "/api/proxy/api/v1";
const QUICK_EMOJIS = ["🙂", "👍", "🔥", "💯", "❤️", "👏", "🤝", "👀", "🚀", "💪"];

interface User {
  id: number;
  username: string;
  display_name?: string;
  avatar_url?: string;
}

interface Conversation {
  id: number;
  other_user: User;
  last_message_preview?: string;
  last_message_at?: string;
  unread?: number;
}

interface Message {
  id?: number;
  sender_id: number;
  body: string;
  created_at?: string;
}

function timeAgo(d: string) {
  try {
    const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000);
    if (m < 1) return "now";
    if (m < 60) return `${m}m`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h`;
    return `${Math.floor(h / 24)}d`;
  } catch { return ""; }
}

function initials(name: string): string {
  return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}

export default function MessagesPage() {
  const router = useRouter();
  const auth = useAuth() as any;
  const me = auth.user;
  const [token, setToken] = useState<string | null>(null);
  const [myId, setMyId] = useState<number | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("token");
    if (!t) return;
    setToken(t);
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      try { setMyId(JSON.parse(savedUser).id); } catch {}
    }
    fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${t}` } })
      .then((r) => (r.ok ? r.json() : null))
      .then((u) => { if (u?.id) setMyId(u.id); });
  }, []);

  const [convs, setConvs] = useState<Conversation[]>([]);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [body, setBody] = useState("");
  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const ws = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const loadConvs = useCallback(async () => {
    if (!token) return;
    const r = await fetch(`${API}/messages/conversations`, { headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) setConvs(await r.json());
    setLoading(false);
  }, [token]);

  useEffect(() => { if (token) loadConvs(); }, [token, loadConvs]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function openConv(conv: Conversation) {
    setActiveConv(conv);
    setMessages([]);
    ws.current?.close();
    const r = await fetch(`${API}/messages/conversations/${conv.id}/messages`, { headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) setMessages(await r.json());

    const backendHost = (process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app")
      .replace("https://", "wss://").replace("http://", "ws://");
    const socket = new WebSocket(`${backendHost}/api/v1/messages/ws/${conv.id}?token=${token}`);
    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.type === "message" || data.type === "new_message") {
          setMessages((prev) => [...prev, data]);
          loadConvs();
        }
      } catch {}
    };
    ws.current = socket;
    setConvs((prev) => prev.map((c) => (c.id === conv.id ? { ...c, unread: 0 } : c)));
  }

  function sendMessage() {
    if (!body.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) return;
    ws.current.send(body.trim());
    setBody("");
  }

  async function searchUsers(q: string) {
    setSearch(q);
    if (q.length < 2) { setSearchResults([]); return; }
    const r = await fetch(`${API}/users/search?q=${encodeURIComponent(q)}`, { headers: { Authorization: `Bearer ${token}` } });
    if (r.ok) setSearchResults(await r.json());
  }

  async function startConv(username: string) {
    const r = await fetch(`${API}/messages/start/${username}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (r.ok) {
      const conv = await r.json();
      setSearch(""); setSearchResults([]);
      await loadConvs();
      openConv(conv);
    }
  }

  if (!token) {
    return (
      <main style={pageStyle}>
        <div style={{ ...emptyContainer }}>
          <p style={eyebrow}>SCOUTA / MESSAGES</p>
          <h1 style={h1}>Sign in to read messages.</h1>
          <Link href="/login?next=/messages" style={primaryBtn}>Log in →</Link>
        </div>
      </main>
    );
  }

  const totalUnread = convs.reduce((a, c) => a + (c.unread || 0), 0);

  return (
    <main style={{ minHeight: "100vh", background: "#080808", color: "#e8e0d0" }}>
      <div className="msg-layout" style={{ maxWidth: "1100px", margin: "0 auto", display: "flex", height: "calc(100vh - 52px)" }}>
        {/* Sidebar — list */}
        <aside
          className="msg-sidebar"
          style={{
            width: "300px",
            borderRight: "1px solid #141414",
            display: activeConv ? undefined : "flex",
            flexDirection: "column",
            flexShrink: 0,
          }}
        >
          <div style={{ padding: "1.25rem 1.25rem 1rem", borderBottom: "1px solid #141414" }}>
            <p style={eyebrow}>SCOUTA / MESSAGES</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginTop: "0.4rem" }}>
              <h1 style={{ ...h1Compact, margin: 0 }}>Messages</h1>
              {totalUnread > 0 && (
                <span style={{
                  background: "#1a2a1a", color: "#4a9a4a",
                  border: "1px solid #2a4a2a",
                  fontSize: "0.6rem", padding: "0.15rem 0.45rem",
                  fontFamily: "monospace", letterSpacing: "0.1em",
                }}>
                  {totalUnread} new
                </span>
              )}
            </div>
          </div>
          <div style={{ padding: "0.75rem", borderBottom: "1px solid #141414", position: "relative" }}>
            <input
              value={search}
              onChange={(e) => searchUsers(e.target.value)}
              placeholder="Find user..."
              style={searchInput}
            />
            {searchResults.length > 0 && (
              <div style={{
                position: "absolute", left: "0.75rem", right: "0.75rem", top: "calc(100% - 0.25rem)",
                background: "#0d0d0d", border: "1px solid #1e1e1e", zIndex: 10,
              }}>
                {searchResults.map((u) => (
                  <div
                    key={u.id}
                    onClick={() => startConv(u.username)}
                    style={{ padding: "0.65rem 0.85rem", cursor: "pointer", borderBottom: "1px solid #141414" }}
                  >
                    <span style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.85rem" }}>
                      {u.display_name || u.username}
                    </span>
                    <span style={{ color: "#444", fontFamily: "monospace", marginLeft: "0.5rem", fontSize: "0.65rem", letterSpacing: "0.05em" }}>
                      @{u.username}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div style={{ flex: 1, overflowY: "auto" }}>
            {loading ? (
              <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.72rem", padding: "1rem", letterSpacing: "0.05em" }}>Loading...</p>
            ) : convs.length === 0 ? (
              <div style={{ padding: "2rem 1rem", textAlign: "center" }}>
                <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.85rem", margin: "0 0 0.4rem" }}>No conversations yet.</p>
                <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.65rem", letterSpacing: "0.05em", margin: 0 }}>
                  Search for someone above.
                </p>
              </div>
            ) : (
              convs.map((c) => (
                <div
                  key={c.id}
                  onClick={() => openConv(c)}
                  style={{
                    padding: "0.85rem 1rem",
                    cursor: "pointer",
                    borderBottom: "1px solid #141414",
                    background: activeConv?.id === c.id ? "#0e0e0e" : "transparent",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    {c.other_user?.avatar_url ? (
                      <img src={c.other_user.avatar_url} alt="" style={{ width: 36, height: 36, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
                    ) : (
                      <div style={avatarFallback(36)}>{initials(c.other_user?.display_name || c.other_user?.username || "?")}</div>
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                        <span style={{ fontSize: "0.85rem", color: "#e0d0b0", fontFamily: "Georgia, serif", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", flex: 1, minWidth: 0 }}>
                          {c.other_user?.display_name || c.other_user?.username}
                        </span>
                        {c.last_message_at && (
                          <span style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", flexShrink: 0, marginLeft: "0.5rem" }}>
                            {timeAgo(c.last_message_at)}
                          </span>
                        )}
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.15rem", alignItems: "center" }}>
                        <p style={{
                          fontSize: "0.7rem", color: "#555", margin: 0,
                          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                          flex: 1, minWidth: 0, fontFamily: "Georgia, serif",
                        }}>
                          {c.last_message_preview || ""}
                        </p>
                        {c.unread ? (
                          <span style={{
                            background: "#1a2a1a", color: "#4a9a4a", border: "1px solid #2a4a2a",
                            fontSize: "0.55rem", padding: "0.05rem 0.35rem",
                            fontFamily: "monospace", flexShrink: 0, marginLeft: "0.5rem",
                          }}>
                            {c.unread}
                          </span>
                        ) : null}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Active conversation */}
        <section className="msg-main" style={{ flex: 1, display: "flex", flexDirection: "column", background: "#0a0a0a" }}>
          {!activeConv ? (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
              <p style={{ fontSize: "3rem", color: "#1a1a1a", margin: "0 0 1rem", lineHeight: 1, fontFamily: "monospace" }}>⬡</p>
              <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.95rem", margin: "0 0 0.4rem" }}>
                Pick a conversation.
              </p>
              <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em" }}>
                Or search for a user to start one.
              </p>
            </div>
          ) : (
            <>
              {/* Header */}
              <div style={{ padding: "0.85rem 1.25rem", borderBottom: "1px solid #141414", display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <button
                  onClick={() => setActiveConv(null)}
                  className="msg-back"
                  style={{
                    background: "none", border: "none", color: "#666",
                    cursor: "pointer", padding: 0,
                    fontSize: "0.75rem", fontFamily: "monospace",
                    letterSpacing: "0.1em", marginRight: "0.25rem",
                  }}
                >
                  ←
                </button>
                {activeConv.other_user?.avatar_url ? (
                  <img src={activeConv.other_user.avatar_url} alt="" style={{ width: 32, height: 32, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
                ) : (
                  <div style={avatarFallback(32)}>{initials(activeConv.other_user?.display_name || activeConv.other_user?.username || "?")}</div>
                )}
                <Link href={`/u/${activeConv.other_user?.username}`} style={{ textDecoration: "none", display: "flex", flexDirection: "column", minWidth: 0 }}>
                  <span style={{ fontSize: "0.9rem", color: "#e0d0b0", fontFamily: "Georgia, serif" }}>
                    {activeConv.other_user?.display_name || activeConv.other_user?.username}
                  </span>
                  <span style={{ fontSize: "0.65rem", color: "#444", fontFamily: "monospace", letterSpacing: "0.05em" }}>
                    @{activeConv.other_user?.username}
                  </span>
                </Link>
              </div>

              {/* Messages */}
              <div style={{ flex: 1, overflowY: "auto", padding: "1.25rem 1rem", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {messages.length === 0 && (
                  <div style={{ textAlign: "center", padding: "2rem 0" }}>
                    <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em" }}>
                      Say hi.
                    </p>
                  </div>
                )}
                {messages.map((m, i) => {
                  const isMe = m.sender_id === (myId || me?.id);
                  const showAvatar = !isMe && (i === 0 || messages[i - 1]?.sender_id !== m.sender_id);
                  return (
                    <div key={m.id || i} style={{ display: "flex", flexDirection: isMe ? "row-reverse" : "row", alignItems: "flex-end", gap: "0.5rem" }}>
                      {!isMe && (
                        <div style={{ width: 24, height: 24, flexShrink: 0, visibility: showAvatar ? "visible" : "hidden" }}>
                          {activeConv.other_user?.avatar_url ? (
                            <img src={activeConv.other_user.avatar_url} alt="" style={{ width: 24, height: 24, borderRadius: "50%", objectFit: "cover" }} />
                          ) : (
                            <div style={{ ...avatarFallback(24), fontSize: "0.55rem" }}>{initials(activeConv.other_user?.display_name || "?")}</div>
                          )}
                        </div>
                      )}
                      <div style={{
                        maxWidth: "72%",
                        padding: "0.6rem 0.95rem",
                        borderRadius: isMe ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
                        background: isMe ? "#1a2e1a" : "#161616",
                        border: `1px solid ${isMe ? "#2a4a2a" : "#1e1e1e"}`,
                        fontSize: "0.9rem", color: "#e8e0d0",
                        fontFamily: "Georgia, serif",
                        lineHeight: 1.5, wordBreak: "break-word",
                      }}>
                        {m.body}
                        <div style={{
                          fontSize: "0.55rem", color: isMe ? "#3a6a4a" : "#444",
                          fontFamily: "monospace", marginTop: "0.3rem",
                          textAlign: isMe ? "right" : "left", letterSpacing: "0.05em",
                        }}>
                          {m.created_at ? timeAgo(m.created_at) : ""}
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div ref={bottomRef} />
              </div>

              {/* Composer */}
              <div style={{ padding: "0.65rem 0.85rem 0.85rem", borderTop: "1px solid #141414", background: "#0d0d0d" }}>
                <div style={{ display: "flex", gap: "0.4rem", marginBottom: "0.55rem", overflowX: "auto", paddingBottom: "0.2rem" }}>
                  {QUICK_EMOJIS.map((e) => (
                    <button
                      key={e}
                      onClick={() => setBody((b) => b + e)}
                      style={{
                        background: "none", border: "1px solid #1a1a1a",
                        cursor: "pointer", fontSize: "0.95rem", padding: "0.2rem 0.45rem",
                        flexShrink: 0, lineHeight: 1,
                      }}
                    >
                      {e}
                    </button>
                  ))}
                </div>
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-end" }}>
                  <textarea
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder="Type a message..."
                    rows={1}
                    style={{
                      flex: 1, background: "#111", border: "1px solid #1e1e1e",
                      borderRadius: "20px", color: "#e8e0d0",
                      padding: "0.6rem 1rem", fontSize: "0.9rem",
                      fontFamily: "Georgia, serif", resize: "none", outline: "none",
                    }}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!body.trim()}
                    style={{
                      width: 38, height: 38, borderRadius: "50%", flexShrink: 0,
                      background: !body.trim() ? "#0d0d0d" : "#1a2a1a",
                      border: `1px solid ${!body.trim() ? "#1a1a1a" : "#2a4a2a"}`,
                      color: !body.trim() ? "#333" : "#4a9a4a",
                      cursor: !body.trim() ? "not-allowed" : "pointer",
                      fontSize: "1rem", display: "flex", alignItems: "center", justifyContent: "center",
                    }}
                  >
                    ↑
                  </button>
                </div>
              </div>
            </>
          )}
        </section>
      </div>

      <style>{`
        .msg-back { display: none; }
        @media (max-width: 720px) {
          .msg-sidebar { width: 100% !important; display: ${" "}; }
          .msg-main { display: ${" "}; }
        }
      `}</style>
      <MobileVisibilityFix activeConv={activeConv} />
    </main>
  );
}

// Apply mobile visibility classes outside JSX to keep the style block simple.
function MobileVisibilityFix({ activeConv }: { activeConv: Conversation | null }) {
  useEffect(() => {
    const sidebar = document.querySelector<HTMLElement>(".msg-sidebar");
    const main = document.querySelector<HTMLElement>(".msg-main");
    const back = document.querySelectorAll<HTMLElement>(".msg-back");
    const isMobile = window.matchMedia("(max-width: 720px)").matches;
    if (!sidebar || !main) return;
    if (isMobile) {
      if (activeConv) {
        sidebar.style.display = "none";
        main.style.display = "flex";
        back.forEach((b) => (b.style.display = "inline-block"));
      } else {
        sidebar.style.display = "flex";
        main.style.display = "none";
        back.forEach((b) => (b.style.display = "none"));
      }
    } else {
      sidebar.style.display = "flex";
      main.style.display = "flex";
      back.forEach((b) => (b.style.display = "none"));
    }
  }, [activeConv]);
  return null;
}

function avatarFallback(size: number): React.CSSProperties {
  return {
    width: size, height: size, borderRadius: "50%",
    background: "#1a2a1a", border: "1px solid #2a4a2a",
    display: "flex", alignItems: "center", justifyContent: "center",
    fontSize: size * 0.36, color: "#4a9a4a",
    fontFamily: "monospace", fontWeight: 700, flexShrink: 0,
  };
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#e8e0d0" };
const emptyContainer: React.CSSProperties = {
  maxWidth: "560px", margin: "0 auto",
  padding: "5rem 1.5rem", textAlign: "center" as const,
};
const eyebrow: React.CSSProperties = {
  fontSize: "0.55rem", letterSpacing: "0.3em", color: "#4a7a9a",
  textTransform: "uppercase", fontFamily: "monospace", margin: 0,
};
const h1: React.CSSProperties = {
  fontSize: "clamp(1.5rem, 3.5vw, 2rem)", fontWeight: 400,
  fontFamily: "Georgia, serif", color: "#f0e8d8",
  margin: "0.4rem 0 1.5rem",
};
const h1Compact: React.CSSProperties = {
  fontSize: "1.4rem", fontWeight: 400,
  fontFamily: "Georgia, serif", color: "#f0e8d8",
};
const primaryBtn: React.CSSProperties = {
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.85rem 2rem", textDecoration: "none",
  fontSize: "0.78rem", fontFamily: "monospace",
  letterSpacing: "0.15em", textTransform: "uppercase" as const,
  display: "inline-block",
};
const searchInput: React.CSSProperties = {
  width: "100%", background: "#111", border: "1px solid #1e1e1e",
  color: "#e8e0d0", padding: "0.55rem 0.8rem",
  fontSize: "0.78rem", fontFamily: "monospace",
  letterSpacing: "0.05em", outline: "none", boxSizing: "border-box",
};
