"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import NotificationBell from "./NotificationBell";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { token, user, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const navLinks = [
    { href: "/posts", label: "Feed" },
    { href: "/posts?sort=hot", label: "Hot" },
    { href: "/posts?sort=top", label: "Top" },
    { href: "/posts?sort=commented", label: "Active" },
  ];

  const isActive = (href: string) => pathname === href.split("?")[0];

  return (
    <header style={{
      position: "sticky", top: 0, zIndex: 100,
      background: scrolled ? "rgba(8,8,8,0.97)" : "#0a0a0a",
      borderBottom: `1px solid ${scrolled ? "#1e1e1e" : "transparent"}`,
      backdropFilter: scrolled ? "blur(8px)" : "none",
      transition: "all 0.2s ease",
    }}>
      <div style={{
        maxWidth: "1100px", margin: "0 auto",
        padding: "0 1.5rem",
        height: "52px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        {/* Logo */}
        <Link href="/posts" style={{
          fontFamily: "Georgia, serif", fontSize: "1.1rem",
          color: "#f0e8d8", textDecoration: "none",
          letterSpacing: "0.15em", textTransform: "uppercase",
          fontWeight: 400,
        }}>
          Scouta
        </Link>

        {/* Nav links — centro */}
        <nav style={{ display: "flex", gap: "0.25rem" }}>
          {navLinks.map(link => (
            <Link key={link.href} href={link.href} style={{
              fontSize: "0.65rem", letterSpacing: "0.15em",
              textTransform: "uppercase", textDecoration: "none",
              color: isActive(link.href) ? "#e0d0b0" : "#555",
              padding: "0.4rem 0.75rem",
              borderBottom: isActive(link.href) ? "1px solid #e0d0b0" : "1px solid transparent",
              transition: "color 0.15s",
            }}>
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right side */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          {token ? (
            <>
              {user && (
                <Link href="/admin" style={{
                  fontSize: "0.6rem", letterSpacing: "0.1em",
                  color: "#555", textDecoration: "none", padding: "0.3rem 0.5rem",
                }}>
                  Admin
                </Link>
              )}
              <Link href="/posts/new" style={{
                fontSize: "0.6rem", letterSpacing: "0.15em", textTransform: "uppercase",
                color: "#c8a96e", textDecoration: "none", padding: "0.3rem 0.75rem",
                border: "1px solid #3a2a10",
              }}>
                + Write
              </Link>
              <NotificationBell />

              {/* Avatar + dropdown */}
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
                    <img src={user.avatar_url} alt="avatar"
                      style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  ) : (
                    <span style={{ color: "#888", fontSize: "0.75rem", fontFamily: "monospace" }}>
                      {user?.display_name?.[0]?.toUpperCase() || "?"}
                    </span>
                  )}
                </button>

                {menuOpen && (
                  <div style={{
                    position: "absolute", top: "calc(100% + 8px)", right: 0,
                    background: "#0d0d0d", border: "1px solid #1e1e1e",
                    minWidth: "160px", zIndex: 200,
                  }}
                    onMouseLeave={() => setMenuOpen(false)}
                  >
                    <div style={{ padding: "0.75rem 1rem", borderBottom: "1px solid #1a1a1a" }}>
                      <div style={{ fontSize: "0.8rem", color: "#e0d0b0", fontFamily: "monospace" }}>
                        {user?.display_name || user?.username}
                      </div>
                      <div style={{ fontSize: "0.65rem", color: "#444", fontFamily: "monospace" }}>
                        @{user?.username}
                      </div>
                    </div>
                    {[
                      { href: "/profile", label: "Profile" },
                      { href: "/profile/edit", label: "Edit Profile" },
                    ].map(item => (
                      <Link key={item.href} href={item.href}
                        onClick={() => setMenuOpen(false)}
                        style={{
                          display: "block", padding: "0.6rem 1rem",
                          fontSize: "0.7rem", color: "#888", textDecoration: "none",
                          fontFamily: "monospace", letterSpacing: "0.05em",
                          borderBottom: "1px solid #1a1a1a",
                        }}>
                        {item.label}
                      </Link>
                    ))}
                    <button
                      onClick={() => { logout(); setMenuOpen(false); router.push("/"); }}
                      style={{
                        display: "block", width: "100%", textAlign: "left",
                        padding: "0.6rem 1rem", fontSize: "0.7rem", color: "#555",
                        fontFamily: "monospace", letterSpacing: "0.05em",
                        background: "none", border: "none", cursor: "pointer",
                      }}>
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <Link href="/login" style={{
                fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase",
                color: "#555", textDecoration: "none", padding: "0.4rem 0.75rem",
                border: "1px solid #1e1e1e",
              }}>Login</Link>
              <Link href="/register" style={{
                fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase",
                color: "#e0d0b0", textDecoration: "none", padding: "0.4rem 0.75rem",
                border: "1px solid #3a3020",
              }}>Join</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
