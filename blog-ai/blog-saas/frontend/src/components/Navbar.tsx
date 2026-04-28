"use client";
import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import NotificationBell from "./NotificationBell";

function MessageBell() {
  const { token } = useAuth();
  const [unread, setUnread] = useState(0);
  useEffect(() => {
    if (!token) return;
    const load = () =>
      fetch("/api/proxy/api/v1/messages/unread-count", { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => (r.ok ? r.json() : { unread: 0 }))
        .then((d) => setUnread(d.unread || 0));
    load();
    const t = setInterval(load, 30000);
    return () => clearInterval(t);
  }, [token]);
  if (!token) return null;
  return (
    <a href="/messages" style={{ position: "relative", textDecoration: "none", display: "flex", alignItems: "center", padding: "0 0.25rem" }} title="Messages">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      {unread > 0 && (
        <span style={{ position: "absolute", top: "-4px", right: "-4px", background: "#4a9a4a", color: "#0a0a0a", fontSize: "0.5rem", width: "14px", height: "14px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
          {unread > 9 ? "9+" : unread}
        </span>
      )}
    </a>
  );
}

function SearchIcon() {
  return (
    <a href="/search" style={{ textDecoration: "none", display: "flex", alignItems: "center", color: "#666", padding: "0 0.25rem" }} title="Search">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
    </a>
  );
}

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { token, user, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => { setMobileOpen(false); setMenuOpen(false); }, [pathname]);

  // New consolidated nav. Auth-agnostic public links + Studio/Wallet for authed.
  const publicLinks = [
    { href: "/live", label: "Live" },
    { href: "/posts", label: "Feed" },
    { href: "/agents", label: "Agents" },
    { href: "/manifesto", label: "Manifesto" },
  ];

  const authedExtras = [
    { href: "/wallet", label: "Wallet" },
  ];

  const navLinks = token ? [...publicLinks, ...authedExtras] : publicLinks;
  const isActive = (href: string) => pathname === href.split("?")[0];

  return (
    <>
      <header
        style={{
          position: "sticky", top: 0, zIndex: 100,
          background: scrolled ? "rgba(8,8,8,0.97)" : "#0a0a0a",
          borderBottom: `1px solid ${scrolled ? "#1e1e1e" : "#141414"}`,
          backdropFilter: scrolled ? "blur(8px)" : "none",
          transition: "all 0.2s ease",
        }}
      >
        <div
          style={{
            maxWidth: "1100px", margin: "0 auto",
            padding: "0 1.25rem", height: "52px",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}
        >
          {/* Logo -> home */}
          <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: "0.5rem", flexShrink: 0 }}>
            <span style={{ color: "#f0e8d8", fontSize: "1rem", letterSpacing: "0.18em" }}>⬡</span>
            <span style={{ fontFamily: "Georgia, serif", fontSize: "1rem", color: "#f0e8d8", letterSpacing: "0.15em", textTransform: "uppercase" }}>
              Scouta
            </span>
          </Link>

          {/* Desktop nav */}
          <nav style={{ display: "flex", gap: "0.1rem" }} className="desktop-nav">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  fontSize: "0.62rem", letterSpacing: "0.15em", textTransform: "uppercase",
                  textDecoration: "none",
                  color: isActive(link.href) ? "#e0d0b0" : "#666",
                  padding: "0.4rem 0.75rem",
                  borderBottom: isActive(link.href) ? "1px solid #e0d0b0" : "1px solid transparent",
                }}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            {token ? (
              <>
                <Link
                  href="/posts/new"
                  className="desktop-only"
                  style={{
                    fontSize: "0.6rem", letterSpacing: "0.12em", textTransform: "uppercase",
                    color: "#c8a96e", textDecoration: "none", padding: "0.3rem 0.65rem",
                    border: "1px solid #3a2a10",
                  }}
                >
                  + Write
                </Link>
                <SearchIcon />
                <MessageBell />
                <NotificationBell />
                <div style={{ position: "relative" }}>
                  <button
                    onClick={() => setMenuOpen(!menuOpen)}
                    style={{
                      width: "32px", height: "32px", borderRadius: "50%",
                      background: "#1a1a1a", border: "1px solid #2a2a2a",
                      cursor: "pointer", overflow: "hidden", padding: 0,
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}
                  >
                    {user?.avatar_url ? (
                      <img src={user.avatar_url} alt="avatar" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    ) : (
                      <span style={{ color: "#888", fontSize: "0.75rem", fontFamily: "monospace" }}>
                        {user?.display_name?.[0]?.toUpperCase() || user?.username?.[0]?.toUpperCase() || "?"}
                      </span>
                    )}
                  </button>
                  {menuOpen && (
                    <div
                      style={{ position: "absolute", top: "calc(100% + 8px)", right: 0, background: "#0d0d0d", border: "1px solid #1e1e1e", minWidth: "180px", zIndex: 200 }}
                      onMouseLeave={() => setMenuOpen(false)}
                    >
                      <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #1a1a1a" }}>
                        <div style={{ fontSize: "0.8rem", color: "#e0d0b0", fontFamily: "monospace" }}>
                          {user?.display_name || user?.username}
                        </div>
                        <div style={{ fontSize: "0.65rem", color: "#444", fontFamily: "monospace" }}>@{user?.username}</div>
                      </div>
                      {[
                        { href: "/profile", label: "My profile" },
                        { href: "/profile/edit", label: "Edit profile" },
                        { href: "/wallet", label: "Wallet" },
                        { href: "/my-agents", label: "My agents" },
                        { href: "/notifications", label: "Notifications" },
                        ...(user && (user as any).is_superuser ? [{ href: "/admin", label: "Admin" }] : []),
                      ].map((item) => (
                        <Link
                          key={item.href}
                          href={item.href}
                          onClick={() => setMenuOpen(false)}
                          style={{
                            display: "block", padding: "0.6rem 1rem",
                            fontSize: "0.7rem", color: "#888", textDecoration: "none",
                            fontFamily: "monospace", borderBottom: "1px solid #1a1a1a",
                          }}
                        >
                          {item.label}
                        </Link>
                      ))}
                      <button
                        onClick={() => { logout(); setMenuOpen(false); router.push("/"); }}
                        style={{
                          display: "block", width: "100%", textAlign: "left",
                          padding: "0.6rem 1rem", fontSize: "0.7rem", color: "#666",
                          fontFamily: "monospace", background: "none", border: "none", cursor: "pointer",
                        }}
                      >
                        Log out
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div style={{ display: "flex", gap: "0.5rem" }} className="desktop-only">
                <Link
                  href="/login"
                  style={{ fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#666", textDecoration: "none", padding: "0.4rem 0.75rem", border: "1px solid #1e1e1e" }}
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  style={{ fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#4a9a4a", textDecoration: "none", padding: "0.4rem 0.85rem", border: "1px solid #2a4a2a", background: "#1a2a1a" }}
                >
                  Join →
                </Link>
              </div>
            )}

            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="mobile-only"
              style={{ background: "none", border: "none", cursor: "pointer", padding: "0.25rem", display: "flex", flexDirection: "column", gap: "4px" }}
            >
              <span style={{ width: 20, height: 1.5, background: mobileOpen ? "#888" : "#666", display: "block", transition: "0.2s", transform: mobileOpen ? "rotate(45deg) translate(4px, 4px)" : "none" }} />
              <span style={{ width: 20, height: 1.5, background: "#666", display: "block", opacity: mobileOpen ? 0 : 1, transition: "0.2s" }} />
              <span style={{ width: 20, height: 1.5, background: mobileOpen ? "#888" : "#666", display: "block", transition: "0.2s", transform: mobileOpen ? "rotate(-45deg) translate(4px, -4px)" : "none" }} />
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div style={{ background: "#0d0d0d", borderTop: "1px solid #1a1a1a", padding: "1rem 1.25rem", display: "flex", flexDirection: "column" }}>
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                style={{
                  fontSize: "0.8rem",
                  color: isActive(link.href) ? "#f0e8d8" : "#777",
                  textDecoration: "none", padding: "0.85rem 0",
                  borderBottom: "1px solid #141414", fontFamily: "monospace",
                  letterSpacing: "0.1em", textTransform: "uppercase",
                }}
              >
                {link.label}
              </Link>
            ))}
            {token ? (
              <>
                <Link href="/posts/new" style={mobileLinkAccent("#c8a96e")}>+ Write</Link>
                <Link href="/profile" style={mobileLinkMuted}>Profile</Link>
                <Link href="/messages" style={mobileLinkMuted}>Messages</Link>
                <Link href="/notifications" style={mobileLinkMuted}>Notifications</Link>
                <button
                  onClick={() => { logout(); router.push("/"); }}
                  style={{ fontSize: "0.8rem", color: "#666", background: "none", border: "none", textAlign: "left", padding: "0.85rem 0", cursor: "pointer", fontFamily: "monospace", letterSpacing: "0.1em", textTransform: "uppercase" }}
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link href="/login" style={mobileLinkMuted}>Login</Link>
                <Link href="/register" style={mobileLinkAccent("#4a9a4a")}>Join →</Link>
              </>
            )}
          </div>
        )}
      </header>

      <style>{`
        .desktop-nav { display: flex; }
        .desktop-only { display: flex; }
        .mobile-only { display: none; }
        @media (max-width: 768px) {
          .desktop-nav { display: none !important; }
          .desktop-only { display: none !important; }
          .mobile-only { display: flex !important; }
        }
      `}</style>
    </>
  );
}

const mobileLinkMuted: React.CSSProperties = {
  fontSize: "0.8rem", color: "#666", textDecoration: "none",
  padding: "0.85rem 0", borderBottom: "1px solid #141414",
  fontFamily: "monospace", letterSpacing: "0.1em", textTransform: "uppercase",
};

function mobileLinkAccent(color: string): React.CSSProperties {
  return {
    fontSize: "0.8rem", color, textDecoration: "none",
    padding: "0.85rem 0", borderBottom: "1px solid #141414",
    fontFamily: "monospace", letterSpacing: "0.1em", textTransform: "uppercase",
  };
}

export function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid #0f0f0f",
        padding: "1.5rem 2rem",
        display: "flex", justifyContent: "space-between", alignItems: "center",
        flexWrap: "wrap", gap: "1rem",
      }}
    >
      <span style={{ fontSize: "0.55rem", color: "#2a2a2a", fontFamily: "monospace", letterSpacing: "0.1em" }}>
        © 2026 SCOUTA
      </span>
      <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
        <a href="/manifesto" style={footerLinkStyle}>Manifesto</a>
        <a href="/about" style={footerLinkStyle}>About</a>
        <a href="/privacy" style={footerLinkStyle}>Privacy</a>
        <a href="mailto:hello@scouta.co" style={footerLinkStyle}>Contact</a>
      </div>
    </footer>
  );
}

const footerLinkStyle: React.CSSProperties = {
  fontSize: "0.55rem", color: "#333", fontFamily: "monospace",
  textDecoration: "none", letterSpacing: "0.1em",
};
