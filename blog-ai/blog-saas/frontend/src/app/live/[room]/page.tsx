"use client";
import { useEffect, useState, useRef, useMemo } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import dynamic from "next/dynamic";
import LiveChat from "./LiveChat";
const LivePlayer = dynamic(() => import("./LivePlayer"), { ssr: false });
const LivePlayer = dynamic(() => import("./LivePlayer"), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";
const LIVEKIT_URL = "wss://scouta-pi70lg8z.livekit.cloud";

// Dynamic imports — no SSR
const LiveKitRoom = dynamic(() => import("@livekit/components-react").then(m => ({ default: m.LiveKitRoom })), { ssr: false });
const RoomAudioRenderer = dynamic(() => import("@livekit/components-react").then(m => ({ default: m.RoomAudioRenderer })), { ssr: false });
const TrackPlayer = dynamic(() => import("./TrackPlayer"), { ssr: false });

interface ChatMessage {
  username?: string;
  display_name?: string;
  message: string;
  is_agent: boolean;
}


export default function LiveRoomPage() {
  const { room } = useParams();
  const searchParams = useSearchParams();
  const { token, user } = useAuth();
  const isHost = searchParams.get("host") === "1";
  const preToken = searchParams.get("token");

  const [livekitToken, setLivekitToken] = useState<string | null>(preToken);
  const [streamTitle, setStreamTitle] = useState("");
  const [viewerCount, setViewerCount] = useState(0);
  const [ended, setEnded] = useState(false);
  const [blockedUsers, setBlockedUsers] = useState<Set<string>>(new Set());
  const [streamEnded, setStreamEnded] = useState(false);

  useEffect(() => {
    if (!preToken) {
      const endpoint = token
        ? `/api/proxy/live/${room}/join`
        : `${API}/api/v1/live/${room}/join-anon`;
      const opts = token
        ? { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({}) }
        : { method: "GET" } as RequestInit;
      fetch(endpoint, opts)
        .then(r => r.json())
        .then(d => { if (d.token) { setLivekitToken(d.token); setStreamTitle(d.title || ""); } else window.location.href = "/live"; })
        .catch(() => window.location.href = "/live");
    }
  }, [room, token, preToken]);

  // Poll viewer count
  useEffect(() => {
    const iv = setInterval(() => {
      fetch(`${API}/api/v1/live/active`)
        .then(r => r.json())
        .then(d => {
          const s = (d.streams || []).find((s: any) => s.room_name === room);
          if (s) setViewerCount(s.viewer_count);
        });
    }, 10000);
    return () => clearInterval(iv);
  }, [room]);

  async function endStream() {
    if (!token) return;
    await fetch(`/api/proxy/live/${room}/end`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    window.location.href = "/live";
  }

  if (ended) return (
    <div style={{ height: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#555", fontFamily: "monospace" }}>Stream ended. <Link href="/live" style={{ color: "#4a7a9a" }}>Back</Link></p>
    </div>
  );

  if (!livekitToken) return (
    <div style={{ height: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.2em" }}>CONNECTING...</p>
    </div>
  );

  return (
    <div style={{ height: "100vh", background: "#080808", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <div style={{ padding: "0.6rem 1.25rem", borderBottom: "1px solid #141414", display: "flex", alignItems: "center", gap: "1rem", flexShrink: 0 }}>
        <Link href="/live" style={{ color: "#555", textDecoration: "none", fontFamily: "monospace", fontSize: "0.6rem" }}>← Live</Link>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#e44", boxShadow: "0 0 6px #e44", display: "inline-block" }} />
        <span style={{ fontSize: "0.55rem", color: "#e44", fontFamily: "monospace", letterSpacing: "0.1em" }}>LIVE</span>
        <h2 style={{ fontSize: "0.9rem", fontWeight: 400, fontFamily: "Georgia, serif", color: "#f0e8d8", margin: 0, flex: 1 }}>{streamTitle || `Room: ${room}`}</h2>
        <span style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace" }}>{viewerCount} viewers</span>
        {isHost && (
          <button onClick={endStream} style={{ background: "none", border: "1px solid #e44", color: "#e44", padding: "0.25rem 0.75rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}>
            ■ End
          </button>
        )}
      </div>

      {/* Main */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden", background: "#000" }}>
        {/* Video full screen */}
        {livekitToken && !streamEnded && (
          <LivePlayer
            token={livekitToken}
            serverUrl={LIVEKIT_URL}
            isHost={isHost}
          />
        )}

        {/* Stream ended overlay */}
        {streamEnded && (
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.85)", gap: "1rem" }}>
            <p style={{ color: "#f0e8d8", fontFamily: "Georgia, serif", fontSize: "1.25rem" }}>Stream has ended</p>
            <Link href="/live" style={{ color: "#4a7a9a", fontFamily: "monospace", fontSize: "0.7rem" }}>← Back to Live</Link>
          </div>
        )}

        {/* Chat overlay — TikTok style */}
        <LiveChat
          roomName={room as string}
          token={token}
          user={user}
          isHost={isHost}
          blockedUsers={blockedUsers}
          onBlock={(username) => setBlockedUsers(prev => new Set([...prev, username]))}
        />

        {/* Right action buttons */}
        {!isHost && (
          <div style={{ position: "absolute", right: 12, bottom: 80, display: "flex", flexDirection: "column", gap: "1rem" }}>
            <button style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, color: "#fff", cursor: "pointer", fontSize: "1.2rem" }}>♥</button>
            <button style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, color: "#fff", cursor: "pointer", fontSize: "1.2rem" }}>↗</button>
          </div>
        )}
      </div>
    </div>
  );
}
