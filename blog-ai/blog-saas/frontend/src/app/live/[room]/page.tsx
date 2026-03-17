"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import "@livekit/components-styles";
import dynamic from "next/dynamic";
const LiveKitRoom = dynamic(() => import("@livekit/components-react").then(m => ({ default: m.LiveKitRoom })), { ssr: false });
const VideoConference = dynamic(() => import("@livekit/components-react").then(m => ({ default: m.VideoConference })), { ssr: false });
const RoomAudioRenderer = dynamic(() => import("@livekit/components-react").then(m => ({ default: m.RoomAudioRenderer })), { ssr: false });

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";
const LIVEKIT_URL = "wss://scouta-pi70lg8z.livekit.cloud";

interface ChatMessage {
  username: string;
  display_name: string;
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
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const [connected, setConnected] = useState(false);
  const [ended, setEnded] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Join stream if not host
  useEffect(() => {
    if (!preToken && token) {
      fetch(`/api/proxy/live/${room}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({}),
      }).then(r => r.json()).then(d => {
        if (d.token) {
          setLivekitToken(d.token);
          setStreamTitle(d.title || "");
        } else if (d.detail) {
          // Stream ended or not found
          window.location.href = "/live";
        }
      }).catch(() => window.location.href = "/live");
    } else if (!preToken && !token) {
      // Anonymous viewer — get token without auth
      fetch(`${API}/api/v1/live/${room}/join-anon`)
        .then(r => r.json())
        .then(d => { if (d.token) { setLivekitToken(d.token); setStreamTitle(d.title || ""); } })
        .catch(() => {});
    }
  }, [room, token, preToken]);

  // Load chat history
  useEffect(() => {
    fetch(`${API}/api/v1/live/${room}/chat?limit=50`)
      .then(r => r.json())
      .then(d => setChat(d.messages || []));
  }, [room]);

  // WebSocket chat
  useEffect(() => {
    const wsUrl = `${API.replace("https://", "wss://").replace("http://", "ws://")}/api/v1/live/${room}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "chat") {
        setChat(prev => [...prev.slice(-99), msg]);
      } else if (msg.type === "viewer_count") {
        setViewerCount(msg.count);
      }
    };
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    return () => ws.close();
  }, [room]);

  // Auto scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  function sendMessage() {
    if (!message.trim() || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({
      type: "chat",
      user_id: (user as any)?.id,
      username: (user as any)?.username,
      display_name: (user as any)?.display_name || (user as any)?.username,
      message: message.trim(),
    }));
    setMessage("");
  }

  async function endStream() {
    if (!token) return;
    await fetch(`/api/proxy/live/${room}/end`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    setEnded(true);
    window.location.href = "/live";
  }

  if (ended) return (
    <div style={{ height: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#555", fontFamily: "monospace" }}>Stream ended. <Link href="/live" style={{ color: "#4a7a9a" }}>Back to Live</Link></p>
    </div>
  );

  if (!livekitToken) return (
    <div style={{ height: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem" }}>Connecting...</p>
    </div>
  );

  return (
    <div style={{ height: "100vh", background: "#080808", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <div style={{ padding: "0.75rem 1.25rem", borderBottom: "1px solid #141414", display: "flex", alignItems: "center", gap: "1rem", flexShrink: 0 }}>
        <Link href="/live" style={{ color: "#555", textDecoration: "none", fontFamily: "monospace", fontSize: "0.6rem" }}>← Live</Link>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#e44", boxShadow: "0 0 6px #e44", display: "inline-block" }} />
          <span style={{ fontSize: "0.55rem", color: "#e44", fontFamily: "monospace", letterSpacing: "0.1em" }}>LIVE</span>
        </div>
        <h2 style={{ fontSize: "0.9rem", fontWeight: 400, fontFamily: "Georgia, serif", color: "#f0e8d8", margin: 0, flex: 1 }}>{streamTitle || `Room: ${room}`}</h2>
        <span style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace" }}>{viewerCount} viewers</span>
        {isHost && (
          <button onClick={endStream} style={{ background: "none", border: "1px solid #e44", color: "#e44", padding: "0.3rem 0.75rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}>
            End Stream
          </button>
        )}
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Video */}
        <div style={{ flex: 1, position: "relative" }}>
          <LiveKitRoom
            video={isHost}
            audio={isHost}
            token={livekitToken}
            serverUrl={LIVEKIT_URL}
            connect={true}
            onDisconnected={() => { if (!isHost) window.location.href = "/live"; }}
            style={{ height: "100%", background: "#000", position: "relative" }}
          >
            <VideoConference />
            <RoomAudioRenderer />
          </LiveKitRoom>
        </div>

        {/* Chat */}
        <div style={{ width: 280, borderLeft: "1px solid #141414", display: "flex", flexDirection: "column", background: "#080808" }}>
          {/* Chat messages */}
          <div style={{ flex: 1, overflowY: "auto", padding: "0.75rem" }}>
            {chat.map((msg, i) => (
              <div key={i} style={{ marginBottom: "0.6rem" }}>
                <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: msg.is_agent ? "#4a7a9a" : "#4a9a4a" }}>
                  {msg.display_name || msg.username}
                  {msg.is_agent && " ⚡"}
                </span>
                <p style={{ margin: "0.1rem 0 0", fontSize: "0.8rem", color: "#aaa", fontFamily: "Georgia, serif", lineHeight: 1.4 }}>{msg.message}</p>
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Chat input */}
          <div style={{ padding: "0.75rem", borderTop: "1px solid #111" }}>
            {token ? (
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
      </div>
    </div>
  );
}
