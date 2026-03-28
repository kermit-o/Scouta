"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

interface Stream {
  room_name: string;
  title: string;
  viewer_count: number;
  host_username: string;
  host_display_name: string;
  description?: string;
  started_at: string;
  is_private?: boolean;
  access_type?: string;
  entry_coin_cost?: number;
}

export default function LivePage() {
  const { token } = useAuth();
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);
  const [showStart, setShowStart] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [starting, setStarting] = useState(false);

  // Private room settings
  const [isPrivate, setIsPrivate] = useState(false);
  const [accessType, setAccessType] = useState("password");
  const [password, setPassword] = useState("");
  const [entryCost, setEntryCost] = useState("");
  const [maxViewers, setMaxViewers] = useState("");

  useEffect(() => {
    fetch(`${API}/api/v1/live/active`)
      .then(r => r.json())
      .then(d => { setStreams(d.streams || []); setLoading(false); });

    const interval = setInterval(() => {
      fetch(`${API}/api/v1/live/active`)
        .then(r => r.json())
        .then(d => setStreams(d.streams || []));
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  async function startLive() {
    if (!token || !title.trim()) return;
    setStarting(true);
    const body: any = { title, description };
    if (isPrivate) {
      body.is_private = true;
      body.access_type = accessType;
      if (accessType === "password") body.password = password;
      if (accessType === "paid") body.entry_coin_cost = parseInt(entryCost) || 0;
      if (maxViewers) body.max_viewer_limit = parseInt(maxViewers) || 0;
    }
    const res = await fetch(`/api/proxy/live/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      const d = await res.json();
      window.location.href = `/live/${d.room_name}?token=${d.token}&host=1`;
    } else {
      setStarting(false);
    }
  }

  function timeAgo(dateStr: string) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "just started";
    if (m < 60) return `${m}m ago`;
    return `${Math.floor(m / 60)}h ago`;
  }

  const inputStyle = { width: "100%", background: "#111", border: "1px solid #222", color: "#f0e8d8", padding: "0.6rem 0.75rem", fontFamily: "monospace", fontSize: "0.8rem", boxSizing: "border-box" as const };
  const labelStyle = { fontSize: "0.6rem", color: "#555", fontFamily: "monospace", letterSpacing: "0.1em", marginBottom: "0.4rem", display: "block" };

  return (
    <main style={{ minHeight: "100vh", background: "#080808", color: "#f0e8d8" }}>
      <div style={{ maxWidth: "900px", margin: "0 auto", padding: "2rem 1.5rem" }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "2rem", paddingBottom: "1.5rem", borderBottom: "1px solid #141414" }}>
          <div>
            <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: "0 0 0.5rem" }}>SCOUTA / LIVE</p>
            <h1 style={{ fontSize: "clamp(1.5rem, 4vw, 2.5rem)", fontWeight: 400, fontFamily: "Georgia, serif", margin: 0 }}>Live Debates</h1>
          </div>
          {token && (
            <button
              onClick={() => setShowStart(s => !s)}
              style={{ background: showStart ? "none" : "#1a1a1a", border: "1px solid #e44", color: "#e44", padding: "0.5rem 1.25rem", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.1em", cursor: "pointer" }}
            >
              {showStart ? "✕ Cancel" : "⏺ Go Live"}
            </button>
          )}
        </div>

        {/* Start live form */}
        {showStart && (
          <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", padding: "1.5rem", marginBottom: "2rem" }}>
            <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", marginBottom: "1rem", letterSpacing: "0.1em" }}>START A LIVE STREAM</p>
            <input
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="What are you debating today?"
              style={{ width: "100%", background: "#111", border: "1px solid #222", color: "#f0e8d8", padding: "0.75rem", fontFamily: "Georgia, serif", fontSize: "1rem", marginBottom: "0.75rem", boxSizing: "border-box" }}
            />
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Description (optional)"
              rows={2}
              style={{ width: "100%", background: "#111", border: "1px solid #222", color: "#f0e8d8", padding: "0.75rem", fontFamily: "monospace", fontSize: "0.8rem", marginBottom: "1rem", resize: "none", boxSizing: "border-box" }}
            />

            {/* Private room toggle */}
            <div style={{ marginBottom: "1rem", padding: "0.75rem", background: "#0a0a0a", border: "1px solid #181818" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={isPrivate}
                  onChange={e => setIsPrivate(e.target.checked)}
                  style={{ accentColor: "#9a6a4a" }}
                />
                <span style={{ fontSize: "0.7rem", color: "#f0e8d8", fontFamily: "monospace" }}>🔒 Private Room</span>
              </label>

              {isPrivate && (
                <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {/* Access type */}
                  <div>
                    <span style={labelStyle}>ACCESS TYPE</span>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      {[
                        { value: "password", label: "🔑 Password" },
                        { value: "invite_only", label: "✉️ Invite Only" },
                        { value: "paid", label: "🪙 Paid Entry" },
                      ].map(opt => (
                        <button
                          key={opt.value}
                          onClick={() => setAccessType(opt.value)}
                          style={{
                            background: accessType === opt.value ? "#1a2a1a" : "#111",
                            border: `1px solid ${accessType === opt.value ? "#4a9a4a" : "#222"}`,
                            color: accessType === opt.value ? "#4a9a4a" : "#666",
                            padding: "0.4rem 0.75rem",
                            fontFamily: "monospace",
                            fontSize: "0.65rem",
                            cursor: "pointer",
                          }}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Password field */}
                  {accessType === "password" && (
                    <div>
                      <span style={labelStyle}>ROOM PASSWORD</span>
                      <input
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        placeholder="Enter password"
                        type="password"
                        style={inputStyle}
                      />
                    </div>
                  )}

                  {/* Coin cost */}
                  {accessType === "paid" && (
                    <div>
                      <span style={labelStyle}>ENTRY COST (COINS)</span>
                      <input
                        value={entryCost}
                        onChange={e => setEntryCost(e.target.value.replace(/\D/g, ""))}
                        placeholder="e.g. 50"
                        style={inputStyle}
                      />
                    </div>
                  )}

                  {/* Max viewers */}
                  <div>
                    <span style={labelStyle}>MAX VIEWERS (0 = unlimited)</span>
                    <input
                      value={maxViewers}
                      onChange={e => setMaxViewers(e.target.value.replace(/\D/g, ""))}
                      placeholder="0"
                      style={inputStyle}
                    />
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={startLive}
              disabled={!title.trim() || starting || (isPrivate && accessType === "password" && !password.trim())}
              style={{ background: "#e44", border: "none", color: "#fff", padding: "0.75rem 2rem", fontFamily: "monospace", fontSize: "0.75rem", letterSpacing: "0.1em", cursor: "pointer" }}
            >
              {starting ? "Starting..." : isPrivate ? "🔒 Start Private Live" : "⏺ Start Live"}
            </button>
          </div>
        )}

        {/* Active streams */}
        {loading && <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem" }}>Loading...</p>}
        {!loading && streams.length === 0 && (
          <div style={{ padding: "4rem 0", textAlign: "center" }}>
            <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", marginBottom: "1rem" }}>No live streams right now.</p>
            {token && <p style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem" }}>Be the first to go live ↑</p>}
          </div>
        )}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
          {streams.map(s => (
            <Link key={s.room_name} href={`/live/${s.room_name}`} style={{ textDecoration: "none" }}>
              <div style={{ background: "#0e0e0e", border: `1px solid ${s.is_private ? "#2a1a1a" : "#1a1a1a"}`, padding: "1.25rem", position: "relative" }}>
                {/* Live + Private badges */}
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "#e44", boxShadow: "0 0 6px #e44" }} />
                  <span style={{ fontSize: "0.55rem", color: "#e44", fontFamily: "monospace", letterSpacing: "0.15em" }}>LIVE</span>
                  {s.is_private && (
                    <span style={{ fontSize: "0.5rem", color: "#9a6a4a", fontFamily: "monospace", letterSpacing: "0.1em", border: "1px solid #2a1a1a", padding: "0.1rem 0.4rem" }}>
                      🔒 {s.access_type === "paid" ? `🪙 ${s.entry_coin_cost}` : s.access_type === "invite_only" ? "INVITE" : "PRIVATE"}
                    </span>
                  )}
                  <span style={{ fontSize: "0.55rem", color: "#333", fontFamily: "monospace", marginLeft: "auto" }}>{s.viewer_count} viewers</span>
                </div>
                <h3 style={{ fontSize: "0.95rem", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem", lineHeight: 1.3 }}>{s.title}</h3>
                <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 0.5rem" }}>@{s.host_display_name || s.host_username}</p>
                <p style={{ fontSize: "0.6rem", color: "#333", fontFamily: "monospace", margin: 0 }}>{timeAgo(s.started_at)}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
