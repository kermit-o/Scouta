"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

interface ChatMessage {
  username?: string;
  display_name?: string;
  message: string;
  is_agent?: boolean;
  type?: string;
}

interface Props {
  roomName: string;
  token: string | null;
  user: any;
  isHost: boolean;
  onBlock?: (username: string) => void;
  blockedUsers?: Set<string>;
}

export default function LiveChat({ roomName, token, user, isHost, onBlock, blockedUsers = new Set() }: Props) {
  const [chat, setChat] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const wsRef = useRef<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [showInput, setShowInput] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/v1/live/${roomName}/chat?limit=50`)
      .then(r => r.json())
      .then(d => setChat(d.messages || []));

    const wsUrl = `${API.replace("https://", "wss://").replace("http://", "ws://")}/api/v1/live/${roomName}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === "chat" || msg.type === "system") {
        setChat(prev => [...prev.slice(-199), msg]);
      } else if (msg.type === "stream_ended") {
        window.location.href = "/live?ended=1";
      }
    };
    return () => ws.close();
  }, [roomName]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

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

  const visibleChat = chat.filter(m => !blockedUsers.has(m.username || ""));

  return (
    <div style={{
      position: "absolute", bottom: 0, left: 0,
      width: "60%", maxWidth: 360,
      padding: "0.75rem",
      background: "linear-gradient(transparent, rgba(0,0,0,0.5))",
      pointerEvents: "none",
    }}>
      {/* Chat messages — TikTok style */}
      <div style={{ marginBottom: "0.5rem", maxHeight: "35vh", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
        {visibleChat.slice(-20).map((msg, i) => (
          <div key={i} style={{ pointerEvents: "auto" }}>
            {msg.type === "system" ? (
              <p style={{ fontSize: "0.65rem", color: "rgba(255,255,255,0.5)", fontFamily: "monospace", margin: 0 }}>{msg.message}</p>
            ) : (
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.4rem", flexWrap: "wrap" }}>
                <Link href={`/u/${msg.username}`} style={{ textDecoration: "none", flexShrink: 0 }}>
                  <span style={{ fontSize: "0.65rem", fontFamily: "monospace", fontWeight: 700, color: msg.is_agent ? "#4a7a9a" : "#4a9a4a", cursor: "pointer" }}>
                    {msg.display_name || msg.username}
                    {msg.is_agent && " ⚡"}
                  </span>
                </Link>
                <span style={{ fontSize: "0.8rem", color: "#fff", fontFamily: "Georgia, serif", lineHeight: 1.3, textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}>
                  {msg.message}
                </span>
                {isHost && msg.username && msg.username !== user?.username && (
                  <button
                    onClick={() => onBlock?.(msg.username!)}
                    style={{ background: "none", border: "none", color: "rgba(255,255,255,0.3)", cursor: "pointer", fontSize: "0.6rem", padding: 0, marginLeft: 4 }}
                    title="Block from live"
                  >✕</button>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div style={{ pointerEvents: "auto" }}>
        {token ? (
          showInput ? (
            <div style={{ display: "flex", gap: "0.4rem" }}>
              <input
                autoFocus
                value={message}
                onChange={e => setMessage(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") { sendMessage(); setShowInput(false); } if (e.key === "Escape") setShowInput(false); }}
                onBlur={() => { if (!message.trim()) setShowInput(false); }}
                placeholder="Say something..."
                style={{ flex: 1, background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.2)", color: "#fff", padding: "0.4rem 0.75rem", fontSize: "0.8rem", fontFamily: "monospace", outline: "none", borderRadius: 20, backdropFilter: "blur(4px)" }}
              />
              <button onClick={() => { sendMessage(); setShowInput(false); }} style={{ background: "rgba(255,255,255,0.2)", border: "none", color: "#fff", width: 32, height: 32, borderRadius: "50%", cursor: "pointer", fontSize: "0.8rem" }}>→</button>
            </div>
          ) : (
            <button
              onClick={() => setShowInput(true)}
              style={{ background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.2)", color: "rgba(255,255,255,0.7)", padding: "0.4rem 1rem", fontFamily: "monospace", fontSize: "0.7rem", borderRadius: 20, cursor: "pointer", backdropFilter: "blur(4px)" }}
            >💬 Comment...</button>
          )
        ) : (
          <Link href="/login" style={{ fontSize: "0.65rem", color: "rgba(255,255,255,0.5)", fontFamily: "monospace", textDecoration: "none" }}>Sign in to chat</Link>
        )}
      </div>
    </div>
  );
}
