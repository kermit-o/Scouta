"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Eye, Radio } from "lucide-react";

interface Stream {
  room_name: string;
  title: string;
  viewer_count: number;
  host_username: string;
  host_display_name?: string;
  is_private: boolean;
}

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app/api/v1";

export default function LiveNowGrid() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    fetch(`${API}/live/active`)
      .then((r) => (r.ok ? r.json() : { streams: [] }))
      .then((d) => setStreams((d.streams || []).slice(0, 6)))
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  if (!loaded || streams.length === 0) return null;

  return (
    <section
      style={{
        padding: "4rem 1.5rem",
        borderTop: "1px solid #1a1a1a",
        background: "#0a0a0a",
      }}
    >
      <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.625rem", marginBottom: "1.75rem" }}>
          <span
            style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: "#e44",
              animation: "scoutaPulse 1.5s ease-in-out infinite",
            }}
          />
          <span style={{ color: "#e44", fontFamily: "monospace", fontSize: "0.75rem", letterSpacing: "0.25em", fontWeight: 700 }}>
            {streams.length} LIVE NOW
          </span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
            gap: "1rem",
          }}
        >
          {streams.map((s) => (
            <Link
              key={s.room_name}
              href={`/live/${s.room_name}`}
              style={{
                textDecoration: "none",
                background: "#0d0d0d",
                border: "1px solid #1a1a1a",
                borderRadius: "6px",
                overflow: "hidden",
                transition: "border-color 0.2s, transform 0.2s",
              }}
            >
              <div
                style={{
                  aspectRatio: "16/9",
                  background: "linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative",
                  color: "#222",
                }}
              >
                <Radio size={48} strokeWidth={1.25} />
                <span
                  style={{
                    position: "absolute",
                    top: "0.5rem",
                    left: "0.5rem",
                    background: "#e44",
                    color: "#fff",
                    fontSize: "0.55rem",
                    fontFamily: "monospace",
                    letterSpacing: "0.2em",
                    padding: "0.18rem 0.55rem",
                    fontWeight: 700,
                  }}
                >
                  LIVE
                </span>
                <span
                  style={{
                    position: "absolute",
                    bottom: "0.5rem",
                    right: "0.5rem",
                    background: "rgba(0,0,0,0.7)",
                    color: "#fff",
                    fontSize: "0.65rem",
                    fontFamily: "monospace",
                    padding: "0.2rem 0.5rem",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "0.3rem",
                  }}
                >
                  <Eye size={11} strokeWidth={1.75} />
                  {s.viewer_count}
                </span>
              </div>
              <div style={{ padding: "0.875rem 1rem" }}>
                <div
                  style={{
                    color: "#f0e8d8",
                    fontSize: "0.85rem",
                    fontFamily: "Georgia, serif",
                    marginBottom: "0.25rem",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {s.title}
                </div>
                <div style={{ color: "#666", fontSize: "0.65rem", fontFamily: "monospace" }}>
                  @{s.host_username}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
