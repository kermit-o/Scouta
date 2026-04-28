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

function timeAgo(dateStr: string) {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just started";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

function privateBadge(s: Stream): string | null {
  if (!s.is_private) return null;
  if (s.access_type === "paid") return `${s.entry_coin_cost} coins`;
  if (s.access_type === "invite_only") return "Invite";
  if (s.access_type === "followers") return "Followers";
  if (s.access_type === "subscribers") return "Subs";
  if (s.access_type === "vip") return "VIP";
  return "Private";
}

export default function LivePage() {
  const { token } = useAuth();
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let stop = false;
    const load = async () => {
      try {
        const r = await fetch(`${API}/api/v1/live/active`);
        const d = await r.json();
        if (!stop) setStreams(d.streams || []);
      } catch {}
      if (!stop) setLoading(false);
    };
    load();
    const interval = setInterval(load, 10000);
    return () => { stop = true; clearInterval(interval); };
  }, []);

  return (
    <main style={{ minHeight: "100vh", background: "#080808", color: "#f0e8d8" }}>
      <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" }}>
        {/* Header */}
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem",
          marginBottom: "2rem", paddingBottom: "1.5rem", borderBottom: "1px solid #141414",
        }}>
          <div>
            <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: "0 0 0.5rem" }}>
              SCOUTA / LIVE
            </p>
            <h1 style={{ fontSize: "clamp(1.6rem, 4vw, 2.5rem)", fontWeight: 400, fontFamily: "Georgia, serif", margin: 0 }}>
              Live now
            </h1>
            <p style={{ color: "#555", fontSize: "0.75rem", fontFamily: "monospace", marginTop: "0.5rem", margin: "0.5rem 0 0" }}>
              {loading ? "Loading..." : streams.length === 0 ? "Nobody's live yet" : `${streams.length} streaming right now`}
            </p>
          </div>

          {token && (
            <Link
              href="/live/start"
              style={{
                background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
                padding: "0.65rem 1.5rem", textDecoration: "none",
                fontSize: "0.72rem", letterSpacing: "0.15em", textTransform: "uppercase",
                fontFamily: "monospace",
              }}
            >
              Go Live →
            </Link>
          )}
        </div>

        {/* Empty state */}
        {!loading && streams.length === 0 && (
          <div style={{
            padding: "5rem 1.5rem", textAlign: "center",
            border: "1px dashed #1a1a1a", background: "#0a0a0a",
          }}>
            <p style={{ fontSize: "3rem", color: "#1a1a1a", margin: "0 0 1rem", lineHeight: 1, fontFamily: "monospace" }}>⬡</p>
            <p style={{ color: "#666", fontSize: "0.9rem", fontFamily: "Georgia, serif", marginBottom: "0.5rem" }}>
              Nobody's live yet.
            </p>
            <p style={{ color: "#444", fontSize: "0.75rem", fontFamily: "monospace", marginBottom: "1.5rem", letterSpacing: "0.05em" }}>
              Be the first.
            </p>
            {token ? (
              <Link href="/live/start" style={{
                background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
                padding: "0.7rem 1.75rem", textDecoration: "none",
                fontSize: "0.72rem", letterSpacing: "0.15em", textTransform: "uppercase",
                fontFamily: "monospace", display: "inline-block",
              }}>Start a stream →</Link>
            ) : (
              <Link href="/register" style={{
                background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
                padding: "0.7rem 1.75rem", textDecoration: "none",
                fontSize: "0.72rem", letterSpacing: "0.15em", textTransform: "uppercase",
                fontFamily: "monospace", display: "inline-block",
              }}>Sign up to go live →</Link>
            )}
          </div>
        )}

        {/* Grid */}
        {streams.length > 0 && (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: "1rem",
          }}>
            {streams.map((s) => {
              const badge = privateBadge(s);
              return (
                <Link key={s.room_name} href={`/live/${s.room_name}`} style={{ textDecoration: "none" }}>
                  <div style={{
                    background: "#0d0d0d",
                    border: `1px solid ${s.is_private ? "#241818" : "#1a1a1a"}`,
                    overflow: "hidden",
                    transition: "border-color 0.15s",
                  }}>
                    {/* Thumb */}
                    <div style={{
                      aspectRatio: "16/9",
                      background: "linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)",
                      position: "relative",
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      <span style={{ fontSize: "2.5rem", opacity: 0.18, color: "#fff" }}>⬡</span>
                      <span style={{
                        position: "absolute", top: "0.5rem", left: "0.5rem",
                        background: "#e44", color: "#fff",
                        fontSize: "0.55rem", fontFamily: "monospace", letterSpacing: "0.2em",
                        padding: "0.18rem 0.55rem", fontWeight: 700,
                      }}>
                        LIVE
                      </span>
                      {badge && (
                        <span style={{
                          position: "absolute", top: "0.5rem", right: "0.5rem",
                          background: "rgba(0,0,0,0.7)", color: "#9a6a4a",
                          fontSize: "0.55rem", fontFamily: "monospace", letterSpacing: "0.1em",
                          padding: "0.18rem 0.5rem", border: "1px solid #2a1a10",
                        }}>
                          {badge}
                        </span>
                      )}
                      <span style={{
                        position: "absolute", bottom: "0.5rem", right: "0.5rem",
                        background: "rgba(0,0,0,0.75)", color: "#fff",
                        fontSize: "0.65rem", fontFamily: "monospace",
                        padding: "0.15rem 0.5rem",
                      }}>
                        {s.viewer_count}
                      </span>
                    </div>

                    {/* Body */}
                    <div style={{ padding: "0.95rem 1rem 1.1rem" }}>
                      <h3 style={{
                        color: "#f0e8d8", fontSize: "0.95rem", fontFamily: "Georgia, serif",
                        fontWeight: 400, margin: "0 0 0.4rem", lineHeight: 1.35,
                        display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}>
                        {s.title}
                      </h3>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ color: "#666", fontSize: "0.65rem", fontFamily: "monospace" }}>
                          @{s.host_username}
                        </span>
                        <span style={{ color: "#444", fontSize: "0.6rem", fontFamily: "monospace" }}>
                          {timeAgo(s.started_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
