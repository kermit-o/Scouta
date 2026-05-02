"use client";
import { Suspense, useEffect, useState, useRef, useMemo } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";
import dynamic from "next/dynamic";
import LiveChat from "./LiveChat";
import GiftPanel from "./GiftPanel";
import GiftAnimation from "./GiftAnimation";
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


// Next.js 15+ requires useSearchParams()/useParams() to live inside a <Suspense>
// boundary or static prerender fails. The inner LiveRoomContent holds the real
// page logic; this wrapper just exists to satisfy the boundary requirement.
export default function LiveRoomPage() {
  return (
    <Suspense fallback={
      <div style={{ height: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.2em" }}>CONNECTING...</p>
      </div>
    }>
      <LiveRoomContent />
    </Suspense>
  );
}

function LiveRoomContent() {
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
  const [showInvite, setShowInvite] = useState(false);
  const [inviteUsername, setInviteUsername] = useState("");
  const [inviteSent, setInviteSent] = useState(false);
  const [joinRequested, setJoinRequested] = useState(false);
  const [joinRequests, setJoinRequests] = useState<{username: string; display_name: string; user_id: number}[]>([]);
  const [joinAccepted, setJoinAccepted] = useState(false);
  const [coinBalance, setCoinBalance] = useState(0);
  // Private room access states
  const [accessBlock, setAccessBlock] = useState<string | null>(null); // password_required, invite_only, paid_entry:N, room_full
  const [roomPassword, setRoomPassword] = useState("");
  const [accessError, setAccessError] = useState("");
  const isCoHost = !isHost && searchParams.get('token') !== null && searchParams.get('host') === '1';

  // Fetch coin balance
  useEffect(() => {
    if (!token) return;
    fetch(`/api/proxy/coins/balance`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(d => { if (d.balance !== undefined) setCoinBalance(d.balance); })
      .catch(() => {});
  }, [token]);

  async function attemptJoin(pw?: string, payCoins?: boolean) {
    const body: any = {};
    if (pw) body.password = pw;
    const endpoint = token
      ? `/api/proxy/live/${room}/join`
      : `${API}/api/v1/live/${room}/join-anon`;
    const opts = token
      ? { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` } as Record<string, string>, body: JSON.stringify(body) }
      : { method: "GET" } as RequestInit;
    const res = await fetch(endpoint, opts);
    const d = await res.json();
    if (res.ok && d.token) {
      setLivekitToken(d.token);
      setStreamTitle(d.title || "");
      setAccessBlock(null);
      setAccessError("");
    } else if (res.status === 403 || res.status === 402) {
      const detail = d.detail || "";
      if (detail === "password_required" || detail === "wrong_password") {
        setAccessBlock("password_required");
        if (detail === "wrong_password") setAccessError("Wrong password");
      } else if (detail === "invite_only") {
        setAccessBlock("invite_only");
      } else if (detail.startsWith("paid_entry:")) {
        setAccessBlock(detail);
      } else if (detail === "room_full") {
        setAccessBlock("room_full");
      } else {
        window.location.href = "/live";
      }
    } else {
      window.location.href = "/live";
    }
  }

  useEffect(() => {
    if (!preToken) {
      attemptJoin();
    }
  }, [room, token, preToken]);

  // Handle join requests via LiveChat WebSocket
  useEffect(() => {
    const handler = (e: any) => {
      const msg = e.detail;
      if (msg.type === 'join_request' && isHost) {
        setJoinRequests(prev => prev.find((r: any) => r.username === msg.username) ? prev : [...prev, { username: msg.username, display_name: msg.display_name, user_id: msg.user_id }]);
      } else if (msg.type === 'join_accepted' && msg.username === (user as any)?.username) {
        // Join as co-host
        const newUrl = `/live/${msg.room_name || room}?token=${encodeURIComponent(msg.token)}&host=1`;
        window.location.href = newUrl;
      } else if (msg.type === 'join_rejected' && msg.username === (user as any)?.username) {
        setJoinRequested(false);
        alert('Your request to join was declined.');
      } else if (msg.type === 'kicked' && msg.username === (user as any)?.username) {
        alert('You have been removed from the live.');
        window.location.href = `/live/${room}`;
      } else if (msg.type === 'cohost_left') {
        // Co-host left — handled by LiveKit track unsubscribed
      }
    };
    window.addEventListener('live_ws_message', handler);
    return () => window.removeEventListener('live_ws_message', handler);
  }, [isHost, room, user]);

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

  async function requestJoin() {
    if (!token) return;
    setJoinRequested(true);
    await fetch(`/api/proxy/live/${room}/request-join`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    });
  }

  async function handleJoinResponse(username: string, accept: boolean) {
    if (!token) return;
    await fetch(`/api/proxy/live/${room}/accept-join`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ username, accept }),
    });
    setJoinRequests(prev => prev.filter(r => r.username !== username));
  }

  async function leaveCoHost() {
    if (!token) return;
    await fetch(`/api/proxy/live/${room}/leave`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    window.location.href = `/live/${room}`;
  }

  async function kickCoHost(username: string) {
    if (!token) return;
    await fetch(`/api/proxy/live/${room}/kick`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ username }),
    });
  }

  async function sendInvite() {
    if (!token || !inviteUsername.trim()) return;
    const res = await fetch(`/api/proxy/live/${room}/invite`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ username: inviteUsername.trim() }),
    });
    if (res.ok) {
      setInviteSent(true);
      setTimeout(() => { setInviteSent(false); setShowInvite(false); setInviteUsername(""); }, 3000);
    }
  }

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

  // Private room access blocks
  if (accessBlock) {
    const paidMatch = accessBlock.match(/^paid_entry:(\d+)$/);
    const cost = paidMatch ? parseInt(paidMatch[1]) : 0;

    return (
      <div style={{ height: "100vh", background: "#080808", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ background: "#0e0e0e", border: "1px solid #1a1a1a", padding: "2rem", maxWidth: 360, width: "90%", textAlign: "center" }}>
          {accessBlock === "password_required" && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>🔒</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>Private Room</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 1rem" }}>Enter the room password to join</p>
              {accessError && <p style={{ fontSize: "0.65rem", color: "#e44", fontFamily: "monospace", margin: "0 0 0.5rem" }}>{accessError}</p>}
              <input
                value={roomPassword}
                onChange={e => setRoomPassword(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") { setAccessError(""); attemptJoin(roomPassword); } }}
                placeholder="Password"
                type="password"
                autoFocus
                style={{ width: "100%", background: "#111", border: "1px solid #222", color: "#f0e8d8", padding: "0.6rem 0.75rem", fontFamily: "monospace", fontSize: "0.8rem", marginBottom: "0.75rem", boxSizing: "border-box", textAlign: "center" }}
              />
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <Link href="/live" style={{ flex: 1, display: "block", textAlign: "center", border: "1px solid #222", color: "#555", padding: "0.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back</Link>
                <button
                  onClick={() => { setAccessError(""); attemptJoin(roomPassword); }}
                  disabled={!roomPassword.trim()}
                  style={{ flex: 1, background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.5rem", fontFamily: "monospace", fontSize: "0.65rem", cursor: "pointer" }}
                >Enter</button>
              </div>
            </>
          )}

          {accessBlock === "invite_only" && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>✉️</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>Invite Only</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 1rem" }}>This room is invite-only. Ask the host for access.</p>
              <Link href="/live" style={{ display: "inline-block", border: "1px solid #222", color: "#4a7a9a", padding: "0.5rem 1.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back to Live</Link>
            </>
          )}

          {paidMatch && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>🪙</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>Paid Entry</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 0.25rem" }}>This room costs</p>
              <p style={{ fontSize: "1.2rem", color: "#9a6a4a", fontFamily: "monospace", margin: "0 0 0.5rem" }}>🪙 {cost} coins</p>
              <p style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", margin: "0 0 1rem" }}>Your balance: 🪙 {coinBalance.toLocaleString()}</p>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <Link href="/live" style={{ flex: 1, display: "block", textAlign: "center", border: "1px solid #222", color: "#555", padding: "0.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back</Link>
                <button
                  onClick={() => attemptJoin()}
                  disabled={coinBalance < cost}
                  style={{
                    flex: 1,
                    background: coinBalance >= cost ? "#1a2a1a" : "#0a0a0a",
                    border: `1px solid ${coinBalance >= cost ? "#2a4a2a" : "#1a1a1a"}`,
                    color: coinBalance >= cost ? "#4a9a4a" : "#555",
                    padding: "0.5rem",
                    fontFamily: "monospace",
                    fontSize: "0.65rem",
                    cursor: coinBalance >= cost ? "pointer" : "not-allowed",
                  }}
                >{coinBalance >= cost ? "Pay & Enter" : "Not enough coins"}</button>
              </div>
            </>
          )}

          {accessBlock === "followers_only" && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>👥</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>Followers Only</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 1rem" }}>You need to follow the host to join this room.</p>
              <Link href="/live" style={{ display: "inline-block", border: "1px solid #222", color: "#4a7a9a", padding: "0.5rem 1.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back to Live</Link>
            </>
          )}

          {accessBlock === "subscribers_only" && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>⭐</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>Subscribers Only</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 1rem" }}>You need an active subscription to the host to join.</p>
              <Link href="/live" style={{ display: "inline-block", border: "1px solid #222", color: "#4a7a9a", padding: "0.5rem 1.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back to Live</Link>
            </>
          )}

          {accessBlock === "vip_only" && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>💎</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>VIP Only</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 1rem" }}>This room is for VIP members only. Ask the host for access.</p>
              <Link href="/live" style={{ display: "inline-block", border: "1px solid #222", color: "#4a7a9a", padding: "0.5rem 1.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back to Live</Link>
            </>
          )}

          {accessBlock === "room_full" && (
            <>
              <p style={{ fontSize: "1.5rem", margin: "0 0 0.75rem" }}>🚫</p>
              <p style={{ fontSize: "0.9rem", color: "#f0e8d8", fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>Room Full</p>
              <p style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", margin: "0 0 1rem" }}>This room has reached its viewer limit.</p>
              <Link href="/live" style={{ display: "inline-block", border: "1px solid #222", color: "#4a7a9a", padding: "0.5rem 1.5rem", fontFamily: "monospace", fontSize: "0.65rem", textDecoration: "none" }}>Back to Live</Link>
            </>
          )}
        </div>
      </div>
    );
  }

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
        {token && <span style={{ fontSize: "0.6rem", color: "#9a6a4a", fontFamily: "monospace" }}>🪙 {coinBalance.toLocaleString()}</span>}
        {isHost && (
          <>
            <button
              onClick={() => setShowInvite(s => !s)}
              style={{ background: "none", border: "1px solid #4a7a9a", color: "#4a7a9a", padding: "0.25rem 0.75rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}
            >+ Invite</button>
            <button onClick={endStream} style={{ background: "none", border: "1px solid #e44", color: "#e44", padding: "0.25rem 0.75rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}>
              ■ End
            </button>
          </>
        )}
        {isCoHost && (
          <button onClick={leaveCoHost} style={{ background: "none", border: "1px solid #9a7a4a", color: "#9a7a4a", padding: "0.25rem 0.75rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}>
            ↩ Leave
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
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.92)", gap: "1rem", zIndex: 50 }}>
            <div style={{ fontSize: "3rem" }}>📡</div>
            <p style={{ color: "#f0e8d8", fontFamily: "Georgia, serif", fontSize: "1.25rem", margin: 0 }}>Stream has ended</p>
            <p style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem", margin: 0 }}>Thanks for watching</p>
            <Link href="/live" style={{ color: "#4a7a9a", fontFamily: "monospace", fontSize: "0.7rem", marginTop: "0.5rem", border: "1px solid #4a7a9a", padding: "0.4rem 1rem" }}>← Back to Live</Link>
          </div>
        )}

        {/* Invite modal */}
        {showInvite && isHost && (
          <div style={{ position: "absolute", top: 60, right: 12, background: "#0e0e0e", border: "1px solid #1a1a1a", padding: "1rem", zIndex: 40, width: 240 }}>
            <p style={{ fontSize: "0.6rem", color: "#555", fontFamily: "monospace", margin: "0 0 0.75rem", letterSpacing: "0.1em" }}>INVITE TO LIVE</p>
            {inviteSent ? (
              <p style={{ color: "#4a9a4a", fontFamily: "monospace", fontSize: "0.7rem" }}>✅ Invite sent!</p>
            ) : (
              <>
                <input
                  value={inviteUsername}
                  onChange={e => setInviteUsername(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && sendInvite()}
                  placeholder="@username"
                  style={{ width: "100%", background: "#111", border: "1px solid #222", color: "#f0e8d8", padding: "0.4rem 0.6rem", fontSize: "0.75rem", fontFamily: "monospace", outline: "none", marginBottom: "0.5rem", boxSizing: "border-box" }}
                />
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={sendInvite} style={{ flex: 1, background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.4rem", fontFamily: "monospace", fontSize: "0.65rem", cursor: "pointer" }}>Send</button>
                  <button onClick={() => setShowInvite(false)} style={{ background: "none", border: "1px solid #222", color: "#555", padding: "0.4rem", fontFamily: "monospace", fontSize: "0.65rem", cursor: "pointer" }}>✕</button>
                </div>
              </>
            )}
          </div>
        )}

        {/* Gift animations overlay */}
        <GiftAnimation />

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
        <div style={{ position: "absolute", right: 12, bottom: 80, display: "flex", flexDirection: "column", gap: "1rem" }}>
          <button style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, color: "#fff", cursor: "pointer", fontSize: "1.2rem" }}>♥</button>
          <button style={{ background: "rgba(0,0,0,0.5)", border: "none", borderRadius: "50%", width: 44, height: 44, color: "#fff", cursor: "pointer", fontSize: "1.2rem" }}>↗</button>
          {!isHost && (
            <GiftPanel
              roomName={room as string}
              token={token}
              balance={coinBalance}
              onBalanceUpdate={setCoinBalance}
            />
          )}
          {!isHost && token && !joinRequested && (
            <button
              onClick={requestJoin}
              style={{ background: "rgba(74,122,154,0.7)", border: "1px solid #4a7a9a", borderRadius: "50%", width: 44, height: 44, color: "#fff", cursor: "pointer", fontSize: "1rem" }}
              title="Request to join live"
            >🎙</button>
          )}
          {!isHost && joinRequested && (
            <div style={{ background: "rgba(74,154,74,0.3)", border: "1px solid #4a9a4a", borderRadius: "50%", width: 44, height: 44, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.8rem" }}>⏳</div>
          )}
        </div>

        {/* Host join request notifications */}
        {isHost && joinRequests.length > 0 && (
          <div style={{ position: "absolute", top: 60, right: 12, display: "flex", flexDirection: "column", gap: "0.5rem", zIndex: 50 }}>
            {joinRequests.map(req => (
              <div key={req.username} style={{ background: "rgba(8,8,8,0.95)", border: "1px solid #1a1a1a", padding: "0.75rem 1rem", display: "flex", alignItems: "center", gap: "0.75rem", minWidth: 240 }}>
                <div style={{ flex: 1 }}>
                  <p style={{ margin: 0, fontSize: "0.7rem", color: "#f0e8d8", fontFamily: "monospace" }}>🎙 <strong>{req.display_name}</strong></p>
                  <p style={{ margin: "0.2rem 0 0", fontSize: "0.6rem", color: "#555", fontFamily: "monospace" }}>wants to join your live</p>
                </div>
                <button
                  onClick={() => handleJoinResponse(req.username, true)}
                  style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.3rem 0.6rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}
                >✓ Accept</button>
                <button
                  onClick={() => handleJoinResponse(req.username, false)}
                  style={{ background: "none", border: "1px solid #2a1a1a", color: "#9a4a4a", padding: "0.3rem 0.6rem", fontFamily: "monospace", fontSize: "0.6rem", cursor: "pointer" }}
                >✕</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
