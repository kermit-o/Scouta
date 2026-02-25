"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getApiBase } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

type Notification = {
  id: number;
  type: string;
  actor_name?: string | null;
  post_id?: number | null;
  post_title?: string | null;
  comment_id?: number | null;
  created_at?: string;
  read?: boolean;
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const API = getApiBase();
  const { token } = useAuth();
  

  useEffect(() => {
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    if (!t) {
      setLoading(false);
      return;
    }

    async function load() {
      try {
        const res = await fetch(`${API}/api/v1/notifications?limit=20&offset=0`, {
          headers: { Authorization: `Bearer ${t}` },
        });
        const data = await res.json();
        setNotifications(data.notifications ?? []);

        await fetch(`${API}/api/v1/notifications/read-all`, {
          method: "POST",
          headers: { Authorization: `Bearer ${t}` },
        });

        window.dispatchEvent(new Event("notifications:read-all"));
      } catch (e) {
        console.error("Error loading notifications", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [API, token]);

  const label = (n: Notification) => {
    if (n.type === "reply") return `${n.actor_name ?? "Someone"} replied to your comment`;
    if (n.type === "upvote") return `${n.actor_name ?? "Someone"} upvoted your comment`;
    return "New notification";
  };

  const handleClick = (n: Notification) => {
    if (n.post_id && n.comment_id) {
      router.push(`/posts/${n.post_id}#comment-${n.comment_id}`);
    } else if (n.post_id) {
      router.push(`/posts/${n.post_id}`);
    }
  };

  if (loading) return <div style={{ padding: "2rem" }}>Loading...</div>;

  return (
    <div style={{ maxWidth: "720px", margin: "2rem auto", padding: "0 1rem" }}>
      <h1 style={{ fontSize: "1.2rem", marginBottom: "1rem" }}>Notifications</h1>

      {notifications.length === 0 ? (
        <div style={{ opacity: 0.6 }}>No notifications yet.</div>
      ) : (
        notifications.map((n) => (
          <div
            key={n.id}
            onClick={() => handleClick(n)}
            style={{
              padding: "0.75rem 1rem",
              marginBottom: "0.5rem",
              border: "1px solid #2a2a2a",
              background: n.read ? "#111" : "#1a1a1a",
              cursor: "pointer",
            }}
          >
            <div style={{ fontSize: "0.85rem" }}>{label(n)}</div>
            {n.post_title && (
              <div style={{ fontSize: "0.75rem", opacity: 0.7, marginTop: "0.25rem" }}>
                {n.post_title}
              </div>
            )}
            {n.created_at && (
              <div style={{ fontSize: "0.7rem", opacity: 0.6, marginTop: "0.25rem" }}>
                {new Date(n.created_at).toLocaleString()}
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
