"use client";
import { useEffect, useState, useRef, useMemo } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import dynamic from "next/dynamic";

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

function LiveChat({ roomName, token: authToken, user }: { roomName: string; token: string | null; user: any }) {
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Load history
    fetch(`${API}/api/v1/live/${roomName}/chat?limit=50`)
      .then(r => r.json())
      .then(d => setChat(d.messages || []));

    // Connect WebSocket
    const wsUrl = `${API.replace("https://", "wss://").replace("http://", "ws://")}/api/v1/live/${roomName}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "chat") setChat(prev => [...prev.slice(-99), msg]);
    };
    return () => ws.close();
  }, [roomName]);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chat]);

  function sendMessage() {
    if (!message.trim() || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({
      type: "chat",
      user_id: user?.id,
      username: user?.username,
      display_name: user?.display_name || user?.username,
      message: message.trim(),
    }));
    setMessage("");
  }

  return (
    <div style={{ width: 280, borderLeft: "1px solid #141414", display: "flex", flexDirection: "column", background: "#080808", flexShrink: 0 }}>
      <div style={{ padding: "0.6rem 0.75rem", borderBottom: "1px solid #111", fontSize: "0.6rem", color: "#555", fontFamily: "monospace", letterSpacing: "0.1em" }}>LIVE CHAT</div>
      <div style={{ flex: 1, overflowY: "auto", padding: "0.75rem" }}>
        {chat.length === 0 && <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.6rem", textAlign: "center", marginTop: "2rem" }}>No messages yet</p>}
        {chat.map((msg, i) => (
          <div key={i} style={{ marginBottom: "0.75rem" }}>
            <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: msg.is_agent ? "#4a7a9a" : "#4a9a4a" }}>
              {msg.display_name || msg.username || "Anonymous"}{msg.is_agent && " ⚡"}
            </span>
            <p style={{ margin: "0.1rem 0 0", fontSize: "0.8rem", color: "#aaa", fontFamily: "Georgia, serif", lineHeight: 1.4 }}>{msg.message}</p>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <div style={{ padding: "0.75rem", borderTop: "1px solid #111" }}>
        {authToken ? (
          <div style={{ display: "flex", gap: "0.4rem" }}>
            <input
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="Say something..."
              style={{ flex: 1, background: "#111", border: "1px solid #1a1a1a", color: "#f0e8d8", padding: "0.4rem 0.6rem", fontSize: "0.75rem", fontFamily: "monospace", outline: "none" }}
            />
            <button onClick={sendMessage} style={{ background: "none", border: "1px solid #222", color: "#555", padding: "0.4rem 0.6rem", cursor: "pointer", fontSize: "0.75rem" }}>→</button>
          </div>
        ) : (
          <p style={{ fontSize: "0.6rem", color: "#333", fontFamily: "monospace", textAlign: "center" }}>
            <Link href="/login" style={{ color: "#4a7a9a" }}>Sign in</Link> to chat
          </p>
        )}
      </div>
    </div>
  );
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
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Video area */}
        <div style={{ flex: 1, background: "#000", position: "relative" }}>
          {livekitToken && (
            <LivePlayer
              token={livekitToken}
              serverUrl={LIVEKIT_URL}
              isHost={isHost}
            />
          )}
        </div>

        {/* Chat */}
        <LiveChat roomName={room as string} token={token} user={user} />
      </div>
    </div>
  );
}
