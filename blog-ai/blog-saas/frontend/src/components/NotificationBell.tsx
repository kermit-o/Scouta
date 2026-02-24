"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getApiBase } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

type Notification = { id: number; read?: boolean };

export default function NotificationBell() {
  const [unread, setUnread] = useState(0);
  const router = useRouter();
  const API = getApiBase();
  const { token } = useAuth();

  const load = async (t: string) => {
    try {
      const res = await fetch(`${API}/api/v1/notifications?limit=20&offset=0`, {
        headers: { Authorization: `Bearer ${t}` },
      });
      const data = await res.json();
      const list: Notification[] = data.notifications ?? [];
      setUnread(list.filter((n) => !n.read).length);
    } catch (e) {
      console.error("NotificationBell load error", e);
    }
  };

  useEffect(() => {
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    if (!t) return;

    load(t);

    const refresh = () => load(t);
    window.addEventListener("notifications:read-all", refresh);
    return () => window.removeEventListener("notifications:read-all", refresh);
  }, [API, token]);

  return (
    <div style={{ position: "relative", cursor: "pointer" }} onClick={() => router.push("/notifications")}>
      🔔
      {unread > 0 && (
        <span
          style={{
            position: "absolute",
            top: "-5px",
            right: "-5px",
            background: "red",
            color: "white",
            fontSize: "0.6rem",
            padding: "2px 6px",
            borderRadius: "50%",
          }}
        >
          {unread}
        </span>
      )}
    </div>
  );
}
