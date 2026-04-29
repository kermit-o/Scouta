"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Search, Bell } from "lucide-react";

const HIDE_ON = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];

export default function MobileTopBar() {
  const pathname = usePathname() || "";
  const { token } = useAuth();
  const [unreadAlerts, setUnreadAlerts] = useState(0);

  useEffect(() => {
    if (!token) { setUnreadAlerts(0); return; }
    const load = () =>
      fetch("/api/proxy/api/v1/notifications/unread-count", { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d) setUnreadAlerts(d.unread || d.count || 0); })
        .catch(() => {});
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [token]);

  if (HIDE_ON.some((p) => pathname.startsWith(p))) return null;

  return (
    <>
      <header className="scouta-mtop">
        <Link
          href="/"
          aria-label="Scouta home"
          style={{
            textDecoration: "none",
            display: "flex", alignItems: "center", gap: "0.5rem",
          }}
        >
          <span style={{
            fontFamily: "Georgia, serif", fontSize: "1rem", color: "#f0e8d8",
            letterSpacing: "0.18em", textTransform: "uppercase",
          }}>
            Scouta
          </span>
        </Link>

        <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
          <Link
            href="/search"
            aria-label="Search"
            style={iconBtn}
          >
            <Search size={18} strokeWidth={1.5} />
          </Link>
          {token ? (
            <Link
              href="/notifications"
              aria-label="Notifications"
              style={{ ...iconBtn, position: "relative" }}
            >
              <Bell size={18} strokeWidth={1.5} />
              {unreadAlerts > 0 && (
                <span style={{
                  position: "absolute",
                  top: 6, right: 6,
                  minWidth: 8, height: 8,
                  background: "#e44",
                  borderRadius: 999,
                }} />
              )}
            </Link>
          ) : (
            <Link
              href="/login"
              style={{
                fontSize: "0.6rem",
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                color: "#4a9a4a",
                textDecoration: "none",
                padding: "0.4rem 0.85rem",
                border: "1px solid #2a4a2a",
                background: "#1a2a1a",
                fontFamily: "monospace",
                marginLeft: "0.25rem",
              }}
            >
              Sign in
            </Link>
          )}
        </div>
      </header>

      <style>{`
        .scouta-mtop {
          display: none;
          position: sticky;
          top: 0;
          z-index: 90;
          height: 52px;
          padding: 0 1rem;
          background: rgba(8,8,8,0.97);
          border-bottom: 1px solid #141414;
          backdrop-filter: blur(8px);
          -webkit-backdrop-filter: blur(8px);
          align-items: center;
          justify-content: space-between;
        }
        @media (max-width: 720px) {
          .scouta-mtop { display: flex; }
        }
      `}</style>
    </>
  );
}

const iconBtn: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  width: 40,
  height: 40,
  color: "#888",
  textDecoration: "none",
};
