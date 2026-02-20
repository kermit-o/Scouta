"use client";

import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

interface Notification {
  id: number;
  type: string;
  comment_id: number | null;
  actor_name: string | null;
  post_id: number | null;
  post_title: string | null;
  read: number;
  created_at: string;
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

export default function NotificationBell() {
  const { token } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const ref = useRef<HTMLDivElement>(null);

  const API = "/api/proxy";

  async function fetchNotifications() {
    if (!token) return;
    const res = await fetch(`${API}/api/v1/notifications`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return;
    const data = await res.json();
    setUnread(data.unread ?? 0);
    setNotifications(data.notifications ?? []);
  }

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [token]);

  // Cerrar al click fuera
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  async function handleOpen() {
    setOpen(!open);
    if (!open && unread > 0) {
      await fetch(`${API}/api/v1/notifications/read-all`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setUnread(0);
      setNotifications(prev => prev.map(n => ({ ...n, read: 1 })));
    }
  }

  function handleClick(n: Notification) {
    setOpen(false);
    if (n.post_id && n.comment_id) {
      router.push(`/posts/${n.post_id}#comment-${n.comment_id}`);
    } else if (n.post_id) {
      router.push(`/posts/${n.post_id}`);
    }
  }

  function notifLabel(n: Notification): string {
    if (n.type === "reply") return `${n.actor_name ?? "Someone"} replied to your comment`;
    if (n.type === "upvote") return `${n.actor_name ?? "Someone"} upvoted your comment`;
    return "New notification";
  }

  function notifIcon(type: string): string {
    if (type === "reply") return "💬";
    if (type === "upvote") return "↑";
    return "🔔";
  }

  if (!token) return null;

  return (
    <div ref={ref} style={{ position: "relative" }}>
      <button
        onClick={handleOpen}
        style={{
          background: "none", border: "none", cursor: "pointer",
          color: unread > 0 ? "#e8e0d0" : "#555",
          fontSize: "1rem", padding: "0.2rem 0.4rem",
          position: "relative", display: "flex", alignItems: "center",
        }}
      >
        🔔
        {unread > 0 && (
          <span style={{
            position: "absolute", top: -2, right: -2,
            background: "#9a4a4a", color: "#fff",
            fontSize: "0.5rem", fontFamily: "monospace",
            width: 14, height: 14, borderRadius: "50%",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 700,
          }}>
            {unread > 9 ? "9+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div style={{
          position: "absolute", top: "calc(100% + 8px)", right: 0,
          width: 300, background: "#0d0d0d", border: "1px solid #222",
          zIndex: 999, boxShadow: "0 8px 32px #000a",
          maxHeight: 400, overflowY: "auto",
        }}>
          <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #1a1a1a", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#555", fontFamily: "monospace" }}>
              Notifications
            </span>
          </div>

          {notifications.length === 0 ? (
            <div style={{ padding: "1.5rem 1rem", textAlign: "center", fontSize: "0.75rem", color: "#333", fontFamily: "monospace" }}>
              No notifications yet
            </div>
          ) : (
            notifications.map(n => (
              <button
                key={n.id}
                onClick={() => handleClick(n)}
                style={{
                  width: "100%", background: n.read ? "none" : "#1a1a1a",
                  border: "none", borderBottom: "1px solid #111",
                  padding: "0.75rem 1rem", cursor: "pointer",
                  textAlign: "left", display: "flex", gap: "0.625rem", alignItems: "flex-start",
                }}
              >
                <span style={{ fontSize: "0.9rem", flexShrink: 0, marginTop: 1 }}>{notifIcon(n.type)}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: "0.75rem", color: n.read ? "#666" : "#ccc", margin: "0 0 0.2rem", lineHeight: 1.4, fontFamily: "Georgia, serif" }}>
                    {notifLabel(n)}
                  </p>
                  {n.post_title && (
                    <p style={{ fontSize: "0.65rem", color: "#444", margin: "0 0 0.2rem", fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {n.post_title}
                    </p>
                  )}
                  <p style={{ fontSize: "0.6rem", color: "#333", margin: 0, fontFamily: "monospace" }}>
                    {timeAgo(n.created_at)}
                  </p>
                </div>
                {!n.read && (
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#4a7a9a", flexShrink: 0, marginTop: 4 }} />
                )}
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
