"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Home, Radio, Plus, MessagesSquare, User, PenLine, Bot } from "lucide-react";

const HIDE_ON = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];

export default function MobileTabBar() {
  const pathname = usePathname() || "";
  const { token, user } = useAuth();
  const [createOpen, setCreateOpen] = useState(false);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!token) { setUnread(0); return; }
    const load = () =>
      fetch("/api/proxy/api/v1/messages/unread-count", { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => (r.ok ? r.json() : { unread: 0 }))
        .then((d) => setUnread(d.unread || 0))
        .catch(() => {});
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [token]);

  if (HIDE_ON.some((p) => pathname.startsWith(p))) return null;

  const isActive = (href: string) => {
    if (href === "/posts") return pathname === "/" || pathname === "/posts" || pathname.startsWith("/posts/");
    if (href === "/profile") return pathname === "/profile" || pathname.startsWith("/profile/") || pathname.startsWith("/u/");
    return pathname === href || pathname.startsWith(href + "/");
  };

  const profileHref = token ? "/profile" : "/login?next=/profile";
  const inboxHref = token ? "/messages" : "/login?next=/messages";

  return (
    <>
      <nav className="scouta-mtab" aria-label="Primary navigation">
        <TabLink href="/posts" label="Feed" icon={Home} active={isActive("/posts")} />
        <TabLink href="/live" label="Live" icon={Radio} active={isActive("/live")} />
        <button
          onClick={() => (token ? setCreateOpen(true) : (window.location.href = "/login?next=/posts/new"))}
          aria-label="Create"
          className="scouta-mtab-create"
        >
          <Plus size={22} strokeWidth={2.25} />
        </button>
        <TabLink href={inboxHref} label="Inbox" icon={MessagesSquare} active={isActive("/messages")} badge={unread} />
        <TabLink href={profileHref} label={token ? "Me" : "Sign in"} icon={User} active={isActive("/profile")} avatarUrl={user?.avatar_url} />
      </nav>

      {createOpen && <CreateSheet onClose={() => setCreateOpen(false)} />}

      <style>{`
        .scouta-mtab {
          display: none;
          position: fixed;
          left: 0; right: 0; bottom: 0;
          height: 60px;
          background: rgba(8,8,8,0.97);
          border-top: 1px solid #161616;
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          z-index: 100;
          padding: 0 0.25rem;
          align-items: center;
          justify-content: space-around;
          padding-bottom: env(safe-area-inset-bottom, 0);
        }
        @media (max-width: 720px) {
          .scouta-mtab { display: flex; }
        }
        .scouta-mtab-create {
          display: flex; align-items: center; justify-content: center;
          width: 48px; height: 48px;
          border-radius: 999px;
          background: #c8a96e;
          color: #0a0a0a;
          border: none;
          cursor: pointer;
          flex-shrink: 0;
          box-shadow: 0 4px 12px rgba(200,169,110,0.25);
          transition: transform 0.15s ease;
        }
        .scouta-mtab-create:active { transform: scale(0.92); }
      `}</style>
    </>
  );
}

function TabLink({
  href, label, icon: Icon, active, badge, avatarUrl,
}: {
  href: string;
  label: string;
  icon: typeof Home;
  active: boolean;
  badge?: number;
  avatarUrl?: string | null;
}) {
  return (
    <Link
      href={href}
      aria-label={label}
      style={{
        flex: 1,
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "0.2rem",
        textDecoration: "none",
        color: active ? "#f0e8d8" : "#555",
        position: "relative",
        transition: "color 0.15s",
      }}
    >
      {avatarUrl ? (
        <span style={{
          width: 22, height: 22, borderRadius: "50%", overflow: "hidden",
          border: active ? "1.5px solid #f0e8d8" : "1.5px solid transparent",
          display: "block",
        }}>
          <img src={avatarUrl} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </span>
      ) : (
        <Icon size={20} strokeWidth={active ? 2 : 1.5} />
      )}
      <span style={{
        fontSize: "0.55rem",
        fontFamily: "monospace",
        letterSpacing: "0.05em",
        textTransform: "uppercase",
        fontWeight: active ? 700 : 400,
      }}>
        {label}
      </span>
      {badge ? (
        <span style={{
          position: "absolute",
          top: "6px",
          left: "calc(50% + 4px)",
          minWidth: 14, height: 14, padding: "0 4px",
          background: "#4a9a4a", color: "#0a0a0a",
          borderRadius: 999, fontSize: "0.5rem",
          fontFamily: "monospace", fontWeight: 700,
          display: "flex", alignItems: "center", justifyContent: "center",
        }}>
          {badge > 9 ? "9+" : badge}
        </span>
      ) : null}
    </Link>
  );
}

function CreateSheet({ onClose }: { onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  const items = [
    { href: "/posts/new", icon: PenLine, label: "Write a post", desc: "Share a take, story, or thread.", color: "#c8a96e" },
    { href: "/live/start", icon: Radio, label: "Go Live", desc: "Start streaming with AI co-hosts.", color: "#9a4a4a" },
    { href: "/my-agents", icon: Bot, label: "New agent", desc: "Create an AI co-host.", color: "#4a7a9a" },
  ];

  return (
    <div role="dialog" aria-modal="true" aria-label="Create">
      <div
        onClick={onClose}
        style={{
          position: "fixed", inset: 0,
          background: "rgba(0,0,0,0.6)",
          zIndex: 200,
          animation: "scoutaFade 0.18s ease-out",
        }}
      />
      <div style={{
        position: "fixed", left: 0, right: 0, bottom: 0,
        background: "#0d0d0d",
        borderTop: "1px solid #1a1a1a",
        zIndex: 201,
        paddingBottom: "calc(0.5rem + env(safe-area-inset-bottom, 0))",
        animation: "scoutaSlideUp 0.22s ease-out",
      }}>
        <div style={{ width: 36, height: 4, background: "#2a2a2a", borderRadius: 2, margin: "0.7rem auto 0.5rem" }} />
        <p style={{
          fontSize: "0.55rem", letterSpacing: "0.3em", color: "#555",
          textTransform: "uppercase", textAlign: "center",
          fontFamily: "monospace", margin: "0 0 0.5rem",
        }}>
          Create
        </p>
        {items.map((item, i) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onClose}
              style={{
                display: "flex", alignItems: "center", gap: "1rem",
                padding: "1rem 1.25rem",
                textDecoration: "none",
                borderTop: i > 0 ? "1px solid #141414" : "1px solid #1a1a1a",
              }}
            >
              <div style={{
                width: 36, height: 36, flexShrink: 0,
                background: `${item.color}1a`,
                border: `1px solid ${item.color}40`,
                color: item.color,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <Icon size={16} strokeWidth={1.75} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.95rem", margin: 0 }}>
                  {item.label}
                </p>
                <p style={{ color: "#555", fontFamily: "monospace", fontSize: "0.65rem", letterSpacing: "0.05em", margin: "0.2rem 0 0" }}>
                  {item.desc}
                </p>
              </div>
            </Link>
          );
        })}
        <button
          onClick={onClose}
          style={{
            display: "block", width: "100%",
            padding: "0.95rem 1.25rem",
            background: "none",
            border: "none",
            borderTop: "1px solid #141414",
            color: "#666",
            fontFamily: "monospace",
            fontSize: "0.7rem",
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            cursor: "pointer",
            textAlign: "center",
          }}
        >
          Cancel
        </button>
      </div>
      <style>{`
        @keyframes scoutaFade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes scoutaSlideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
      `}</style>
    </div>
  );
}
