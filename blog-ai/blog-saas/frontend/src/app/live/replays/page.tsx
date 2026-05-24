"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

type Recording = {
  id: number;
  room_name: string;
  title: string | null;
  playback_url: string | null;
  duration_seconds: number | null;
  started_at: string | null;
  host_username: string | null;
  host_display_name: string | null;
};

function fmtDuration(s: number | null): string {
  if (!s) return "";
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

export default function ReplaysPage() {
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/live/recordings`, { cache: "no-store" })
      .then((r) => r.json())
      .then((d) => setRecordings(d.recordings || []))
      .catch(() => setRecordings([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main style={{ maxWidth: 960, margin: "2rem auto", padding: "0 1rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
        <h1 style={{ fontSize: "1.3rem", fontFamily: "monospace", letterSpacing: "0.05em" }}>Replays</h1>
        <Link href="/live" style={{ fontSize: "0.75rem", fontFamily: "monospace", color: "#777" }}>← Live now</Link>
      </div>

      {loading ? (
        <div style={{ opacity: 0.6 }}>Loading…</div>
      ) : recordings.length === 0 ? (
        <div style={{ opacity: 0.6, fontFamily: "monospace", fontSize: "0.85rem" }}>No replays yet.</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
          {recordings.map((r) => (
            <div key={r.id} style={{ border: "1px solid #1e1e1e", background: "#0c0c0c" }}>
              <video
                controls
                preload="metadata"
                src={r.playback_url || undefined}
                style={{ width: "100%", aspectRatio: "16 / 9", background: "#000", display: "block" }}
              />
              <div style={{ padding: "0.6rem 0.75rem" }}>
                <div style={{ fontSize: "0.85rem", color: "#f0e8d8", fontFamily: "Georgia, serif" }}>
                  {r.title || "Untitled live"}
                </div>
                <div style={{ fontSize: "0.65rem", color: "#666", fontFamily: "monospace", marginTop: "0.3rem", display: "flex", justifyContent: "space-between" }}>
                  <Link href={`/u/${r.host_username}`} style={{ color: "#4a9a4a", textDecoration: "none" }}>
                    @{r.host_username}
                  </Link>
                  <span>{fmtDuration(r.duration_seconds)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
