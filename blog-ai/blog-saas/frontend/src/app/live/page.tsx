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
}

export default function LivePage() {
  const { token } = useAuth();
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);
  const [showStart, setShowStart] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [starting, setStarting] = useState(false);

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
    const res = await fetch(`/api/proxy/live/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ title, description }),
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
            <button
              onClick={startLive}
              disabled={!title.trim() || starting}
              style={{ background: "#e44", border: "none", color: "#fff", padding: "0.75rem 2rem", fontFamily: "monospace", fontSize: "0.75rem", letterSpacing: "0.1em", cursor: "pointer" }}
            >
              {starting ? "Starting..." : "⏺ Start Live"}
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
              <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", padding: "1.25rem", position: "relative" }}>
                {/* Live badge */}
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <span style={{ display: "inline-block", width: 6, height: 6, borderRadius: "50%", background: "#e44", boxShadow: "0 0 6px #e44" }} />
                  <span style={{ fontSize: "0.55rem", color: "#e44", fontFamily: "monospace", letterSpacing: "0.15em" }}>LIVE</span>
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
