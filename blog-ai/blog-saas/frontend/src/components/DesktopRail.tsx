"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import {
  Home, Radio, Bot, MessagesSquare, Bell, Clapperboard, Wallet as WalletIcon,
  PenLine, ChevronUp, Settings, User, Pencil, ShieldCheck, LogOut, LogIn,
  type LucideIcon,
} from "lucide-react";

const HIDE_ON = ["/login", "/register", "/forgot-password", "/reset-password", "/verify-email"];

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  badgeKey?: "messages" | "alerts";
  authRequired?: boolean;
}

const PRIMARY: NavItem[] = [
  { href: "/posts", label: "Home", icon: Home },
  { href: "/live", label: "Live", icon: Radio },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/messages", label: "Messages", icon: MessagesSquare, badgeKey: "messages", authRequired: true },
  { href: "/notifications", label: "Alerts", icon: Bell, badgeKey: "alerts", authRequired: true },
];

const SECONDARY: NavItem[] = [
  { href: "/studio", label: "Studio", icon: Clapperboard, authRequired: true },
  { href: "/wallet", label: "Wallet", icon: WalletIcon, authRequired: true },
];

export default function DesktopRail() {
  const pathname = usePathname() || "";
  const router = useRouter();
  const { token, user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [counts, setCounts] = useState<{ messages: number; alerts: number }>({ messages: 0, alerts: 0 });
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!token) { setCounts({ messages: 0, alerts: 0 }); return; }
    const load = async () => {
      try {
        const [m, n] = await Promise.all([
          fetch("/api/proxy/api/v1/messages/unread-count", { headers: { Authorization: `Bearer ${token}` } })
            .then((r) => (r.ok ? r.json() : { unread: 0 })).catch(() => ({ unread: 0 })),
          fetch("/api/proxy/api/v1/notifications/unread-count", { headers: { Authorization: `Bearer ${token}` } })
            .then((r) => (r.ok ? r.json() : null)).catch(() => null),
        ]);
        setCounts({
          messages: m?.unread || 0,
          alerts: n?.unread || n?.count || 0,
        });
      } catch {}
    };
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [token]);

  useEffect(() => {
    if (!menuOpen) return;
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false);
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setMenuOpen(false); };
    window.addEventListener("mousedown", onClick);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onClick);
      window.removeEventListener("keydown", onKey);
    };
  }, [menuOpen]);

  useEffect(() => { setMenuOpen(false); }, [pathname]);

  if (HIDE_ON.some((p) => pathname.startsWith(p))) return null;

  const isActive = (href: string) => {
    if (href === "/posts") return pathname === "/" || pathname === "/posts" || pathname.startsWith("/posts/");
    return pathname === href || pathname.startsWith(href + "/");
  };

  const renderItem = (item: NavItem) => {
    const Icon = item.icon;
    const active = isActive(item.href);
    const badge = item.badgeKey ? counts[item.badgeKey] : 0;
    const href = item.authRequired && !token ? `/login?next=${encodeURIComponent(item.href)}` : item.href;
    return (
      <Link
        key={item.href}
        href={href}
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.85rem",
          padding: "0.65rem 0.85rem",
          textDecoration: "none",
          color: active ? "#f0e8d8" : "#888",
          background: active ? "#141414" : "transparent",
          borderLeft: `2px solid ${active ? "#c8a96e" : "transparent"}`,
          fontFamily: "Georgia, serif",
          fontSize: "0.95rem",
          transition: "background 0.15s, color 0.15s",
          position: "relative",
        }}
      >
        <Icon size={18} strokeWidth={active ? 2 : 1.5} />
        <span>{item.label}</span>
        {badge > 0 && (
          <span style={{
            marginLeft: "auto",
            background: "#1a2a1a",
            color: "#4a9a4a",
            border: "1px solid #2a4a2a",
            fontSize: "0.55rem",
            fontFamily: "monospace",
            padding: "0.1rem 0.4rem",
            letterSpacing: "0.05em",
          }}>
            {badge > 99 ? "99+" : badge}
          </span>
        )}
      </Link>
    );
  };

  return (
    <>
      <aside className="scouta-rail" aria-label="Primary">
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: "flex", alignItems: "center", gap: "0.55rem",
            padding: "1.5rem 1.25rem 1rem",
            textDecoration: "none",
          }}
        >
          <span style={{
            fontFamily: "Georgia, serif",
            fontSize: "1.1rem",
            color: "#f0e8d8",
            letterSpacing: "0.2em",
            textTransform: "uppercase",
          }}>
            Scouta
          </span>
        </Link>

        {/* Primary */}
        <nav style={{ display: "flex", flexDirection: "column", padding: "0 0.5rem" }}>
          {PRIMARY.map(renderItem)}
        </nav>

        {/* Divider */}
        <div style={{ height: 1, background: "#141414", margin: "1rem 1.25rem" }} />

        {/* Secondary (creator tools) */}
        <p style={{
          fontSize: "0.55rem", letterSpacing: "0.3em", color: "#444",
          textTransform: "uppercase", fontFamily: "monospace",
          margin: "0 1.4rem 0.4rem",
        }}>
          Studio
        </p>
        <nav style={{ display: "flex", flexDirection: "column", padding: "0 0.5rem" }}>
          {SECONDARY.map(renderItem)}
        </nav>

        {/* WRITE CTA */}
        {token && (
          <div style={{ padding: "1.25rem 1rem 0.5rem" }}>
            <Link
              href="/posts/new"
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.55rem",
                padding: "0.7rem",
                background: "#c8a96e",
                color: "#0a0a0a",
                textDecoration: "none",
                fontFamily: "monospace",
                fontSize: "0.7rem",
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                fontWeight: 700,
              }}
            >
              <PenLine size={14} strokeWidth={2} />
              Write
            </Link>
          </div>
        )}

        <div style={{ flex: 1 }} />

        {/* Bottom: profile or login */}
        <div style={{ padding: "0.5rem 0.75rem 1rem", borderTop: "1px solid #141414" }}>
          {token ? (
            <div style={{ position: "relative" }} ref={menuRef}>
              <button
                onClick={() => setMenuOpen((v) => !v)}
                aria-label="Account menu"
                aria-expanded={menuOpen}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.7rem",
                  padding: "0.5rem 0.6rem",
                  background: menuOpen ? "#141414" : "transparent",
                  border: "none",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "background 0.15s",
                }}
              >
                <span style={{
                  width: 32, height: 32, borderRadius: "50%",
                  background: "#1a1a1a", border: "1px solid #2a2a2a",
                  flexShrink: 0, overflow: "hidden",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  {user?.avatar_url ? (
                    <img src={user.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    <span style={{ color: "#888", fontFamily: "monospace", fontSize: "0.75rem" }}>
                      {(user?.display_name?.[0] || user?.username?.[0] || "?").toUpperCase()}
                    </span>
                  )}
                </span>
                <span style={{ flex: 1, minWidth: 0, overflow: "hidden" }}>
                  <span style={{
                    display: "block",
                    color: "#e0d0b0",
                    fontFamily: "Georgia, serif",
                    fontSize: "0.85rem",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}>
                    {user?.display_name || user?.username || "Account"}
                  </span>
                  {user?.username && (
                    <span style={{
                      display: "block",
                      color: "#444",
                      fontFamily: "monospace",
                      fontSize: "0.6rem",
                      letterSpacing: "0.05em",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}>
                      @{user.username}
                    </span>
                  )}
                </span>
                <ChevronUp
                  size={14}
                  strokeWidth={1.5}
                  style={{
                    color: "#666",
                    transform: menuOpen ? "rotate(0deg)" : "rotate(180deg)",
                    transition: "transform 0.15s",
                  }}
                />
              </button>

              {menuOpen && (
                <div
                  role="menu"
                  style={{
                    position: "absolute",
                    bottom: "calc(100% + 6px)",
                    left: 0,
                    right: 0,
                    background: "#0d0d0d",
                    border: "1px solid #1e1e1e",
                    boxShadow: "0 -4px 20px rgba(0,0,0,0.5)",
                    overflow: "hidden",
                  }}
                >
                  <DropItem href="/profile" icon={User} label="Profile" />
                  <DropItem href="/profile/edit" icon={Pencil} label="Edit profile" />
                  <DropItem href="/my-agents" icon={Bot} label="My agents" />
                  <DropItem href="/billing" icon={Settings} label="Settings" />
                  {(user as any)?.is_superuser && (
                    <DropItem href="/admin" icon={ShieldCheck} label="Admin" accent="#c8a96e" />
                  )}
                  <button
                    onClick={() => { logout(); setMenuOpen(false); router.push("/"); }}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.6rem",
                      width: "100%",
                      padding: "0.7rem 0.85rem",
                      background: "none",
                      border: "none",
                      borderTop: "1px solid #161616",
                      color: "#9a4a4a",
                      fontFamily: "monospace",
                      fontSize: "0.7rem",
                      letterSpacing: "0.05em",
                      cursor: "pointer",
                      textAlign: "left",
                    }}
                  >
                    <LogOut size={13} strokeWidth={1.75} />
                    Log out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              <Link
                href="/login"
                style={{
                  display: "flex", alignItems: "center", justifyContent: "center", gap: "0.4rem",
                  padding: "0.55rem 1rem",
                  fontSize: "0.65rem", letterSpacing: "0.15em", textTransform: "uppercase",
                  color: "#888", textDecoration: "none",
                  border: "1px solid #1e1e1e",
                  fontFamily: "monospace",
                }}
              >
                <LogIn size={12} strokeWidth={1.75} />
                Log in
              </Link>
              <Link
                href="/register"
                style={{
                  display: "flex", alignItems: "center", justifyContent: "center",
                  padding: "0.55rem 1rem",
                  fontSize: "0.65rem", letterSpacing: "0.15em", textTransform: "uppercase",
                  color: "#0a0a0a", textDecoration: "none",
                  background: "#c8a96e",
                  fontFamily: "monospace",
                  fontWeight: 700,
                }}
              >
                Join Scouta
              </Link>
            </div>
          )}
        </div>
      </aside>

      <style>{`
        .scouta-rail {
          display: none;
          position: fixed;
          top: 0; left: 0; bottom: 0;
          width: 240px;
          background: #0a0a0a;
          border-right: 1px solid #141414;
          flex-direction: column;
          z-index: 80;
          overflow-y: auto;
        }
        @media (min-width: 720px) {
          .scouta-rail { display: flex; }
        }
      `}</style>
    </>
  );
}

function DropItem({ href, icon: Icon, label, accent }: { href: string; icon: LucideIcon; label: string; accent?: string }) {
  return (
    <Link
      href={href}
      role="menuitem"
      style={{
        display: "flex",
        alignItems: "center",
        gap: "0.6rem",
        padding: "0.7rem 0.85rem",
        textDecoration: "none",
        color: accent || "#888",
        fontFamily: "monospace",
        fontSize: "0.7rem",
        letterSpacing: "0.05em",
        borderBottom: "1px solid #161616",
      }}
    >
      <Icon size={13} strokeWidth={1.75} />
      {label}
    </Link>
  );
}
