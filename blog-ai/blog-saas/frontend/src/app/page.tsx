"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import HeroLiveDebate from "@/components/HeroLiveDebate";
import LiveNowGrid from "@/components/LiveNowGrid";
import EmailCapture from "@/components/EmailCapture";

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  return (
    <main style={{ minHeight: "100vh", background: "#080808", color: "#e8e0d0", fontFamily: "'Georgia', 'Times New Roman', serif", overflowX: "hidden" }}>

      {/* Nav */}
      <nav style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        padding: "1rem 1.5rem",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        borderBottom: "1px solid #1a1a1a", background: "rgba(8,8,8,0.93)", backdropFilter: "blur(8px)",
      }}>
        <Link href="/" style={{ fontSize: "0.7rem", letterSpacing: "0.3em", textTransform: "uppercase", color: "#f0e8d8", fontFamily: "monospace", textDecoration: "none" }}>
          ⬡ SCOUTA
        </Link>
        <div style={{ display: "flex", gap: "0.85rem", alignItems: "center" }}>
          <Link href="/live" className="navlink">Live</Link>
          <Link href="/posts" className="navlink">Feed</Link>
          <Link href="/login" className="navlink hide-sm">Login</Link>
          <Link href="/register" style={{
            fontSize: "0.65rem", letterSpacing: "0.15em", textTransform: "uppercase",
            background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
            padding: "0.45rem 0.95rem", textDecoration: "none", fontFamily: "monospace",
          }}>Join →</Link>
        </div>
      </nav>

      {/* HERO */}
      <section style={{
        minHeight: "100vh",
        display: "flex", alignItems: "center", justifyContent: "center",
        padding: "7rem 1.5rem 4rem", position: "relative",
      }}>
        <div style={{
          position: "absolute", inset: 0, zIndex: 0,
          backgroundImage: "linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px)",
          backgroundSize: "60px 60px", opacity: 0.15,
        }} />
        <div style={{
          position: "absolute", top: "40%", left: "30%", transform: "translate(-50%, -50%)",
          width: "600px", height: "400px",
          background: "radial-gradient(ellipse, rgba(74,122,154,0.06) 0%, transparent 70%)",
          zIndex: 0, pointerEvents: "none",
        }} />

        <div className="hero-grid" style={{
          position: "relative", zIndex: 1,
          maxWidth: "1100px", width: "100%",
          display: "grid", gridTemplateColumns: "minmax(0,1fr) minmax(0,1fr)",
          gap: "3rem", alignItems: "center",
        }}>
          <div style={{
            opacity: mounted ? 1 : 0,
            transform: mounted ? "translateY(0)" : "translateY(20px)",
            transition: "opacity 0.8s ease, transform 0.8s ease",
          }}>
            <p style={{ fontSize: "0.65rem", letterSpacing: "0.4em", textTransform: "uppercase", color: "#4a7a9a", fontFamily: "monospace", marginBottom: "1.5rem" }}>
              For people who actually talk
            </p>
            <h1 style={{
              fontSize: "clamp(2.25rem, 6vw, 4.5rem)", fontWeight: 400, lineHeight: 1.05,
              letterSpacing: "-0.02em", color: "#f0e8d8", marginBottom: "1.5rem",
            }}>
              Live talk,<br />
              <em style={{ color: "#888", fontStyle: "italic" }}>sharpened.</em>
            </h1>
            <p style={{ fontSize: "clamp(0.95rem, 1.5vw, 1.1rem)", color: "#666", lineHeight: 1.7, maxWidth: "440px", marginBottom: "2rem" }}>
              Stream live with AI co-hosts that fact-check, contradict, and keep
              the conversation honest. Built for podcasters, debaters, coaches —
              anyone who actually has something to say.
            </p>
            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
              <Link href="/register" style={ctaPrimary}>Start a stream →</Link>
              <Link href="/live" style={ctaSecondary}>Watch Live</Link>
            </div>
          </div>

          <div style={{
            display: "flex", justifyContent: "center",
            opacity: mounted ? 1 : 0,
            transform: mounted ? "scale(1)" : "scale(0.97)",
            transition: "opacity 1s ease 0.3s, transform 1s ease 0.3s",
          }}>
            <HeroLiveDebate />
          </div>
        </div>
      </section>

      <LiveNowGrid />

      {/* Why Scouta */}
      <section style={{ padding: "6rem 1.5rem", borderTop: "1px solid #1a1a1a" }}>
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.3em", textTransform: "uppercase", color: "#555", fontFamily: "monospace", marginBottom: "0.75rem" }}>
            Why Scouta
          </p>
          <h2 style={{ fontSize: "clamp(1.75rem, 4vw, 2.75rem)", fontWeight: 400, color: "#f0e8d8", marginBottom: "3rem", lineHeight: 1.2, maxWidth: "640px" }}>
            Built for substance,<br/>
            <em style={{ color: "#666" }}>not viral noise.</em>
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "2rem" }}>
            {[
              { n: "01", title: "AI co-hosts", body: "Real-time fact-checks, devil's advocates, and second opinions during your stream. Your conversation, sharper." },
              { n: "02", title: "No gatekeeping", body: "Your audience finds you because they want to. No algorithm hiding your stream. No shadow ban." },
              { n: "03", title: "Keep 80%", body: "Direct gift tipping during lives. Real money, instantly. No ads diluting your stream. Built-in creator economy." },
            ].map((s) => (
              <div key={s.n} style={{ borderTop: "1px solid #2a2a2a", paddingTop: "1.5rem" }}>
                <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#333", fontFamily: "monospace", marginBottom: "0.75rem" }}>{s.n}</p>
                <h3 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", marginBottom: "0.75rem" }}>{s.title}</h3>
                <p style={{ fontSize: "0.85rem", color: "#666", lineHeight: 1.7 }}>{s.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Who is it for */}
      <section style={{ padding: "5rem 1.5rem", borderTop: "1px solid #1a1a1a", background: "#0a0a0a" }}>
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.3em", textTransform: "uppercase", color: "#555", fontFamily: "monospace", marginBottom: "0.75rem" }}>
            Who streams here
          </p>
          <h2 style={{ fontSize: "clamp(1.5rem, 3.5vw, 2.25rem)", fontWeight: 400, color: "#f0e8d8", marginBottom: "2.5rem", lineHeight: 1.2 }}>
            Made for talkers, not creators of background noise.
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1rem" }}>
            {[
              { label: "Podcasters", body: "Go live with episodes. Get an audience that argues back." },
              { label: "Debaters", body: "Take any topic. AI plays devil's advocate so you don't have to." },
              { label: "Coaches", body: "Live sessions, paid or free. AI takes notes, audience asks questions." },
              { label: "Teachers", body: "Live lectures with an AI TA that summarizes and clarifies." },
              { label: "AMA hosts", body: "Q&A streams where AI moderates and surfaces best questions." },
              { label: "Thinkers", body: "Anyone with takes longer than 60 seconds." },
            ].map((u) => (
              <div key={u.label} style={{
                border: "1px solid #1a1a1a", padding: "1rem 1.25rem",
                background: "#0d0d0d",
              }}>
                <h4 style={{ color: "#4a9a4a", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.15em", marginBottom: "0.5rem", fontWeight: 700 }}>
                  {u.label.toUpperCase()}
                </h4>
                <p style={{ color: "#777", fontSize: "0.78rem", lineHeight: 1.6 }}>{u.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Email capture */}
      <section style={{ padding: "5rem 1.5rem", borderTop: "1px solid #1a1a1a", textAlign: "center" }}>
        <div style={{ maxWidth: "500px", margin: "0 auto" }}>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.3em", color: "#444", textTransform: "uppercase", fontFamily: "monospace", marginBottom: "1rem" }}>
            Stay close
          </p>
          <h2 style={{ fontSize: "clamp(1.5rem, 3.5vw, 2.25rem)", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif", lineHeight: 1.2, marginBottom: "0.75rem" }}>
            Best lives of the week,<br />
            <em style={{ color: "#666" }}>delivered.</em>
          </h2>
          <p style={{ color: "#444", fontSize: "0.8rem", fontFamily: "monospace", marginBottom: "2rem" }}>
            Top streams. Best AI takes. Conversations worth watching.
          </p>
          <div style={{ display: "flex", justifyContent: "center" }}>
            <EmailCapture source="home_v3" />
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section style={{ padding: "8rem 1.5rem", borderTop: "1px solid #1a1a1a", textAlign: "center", position: "relative" }}>
        <div style={{
          position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
          width: "500px", height: "300px",
          background: "radial-gradient(ellipse, rgba(74,122,154,0.05) 0%, transparent 70%)", pointerEvents: "none",
        }} />
        <div style={{ position: "relative", zIndex: 1 }}>
          <h2 style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", fontWeight: 400, color: "#f0e8d8", lineHeight: 1.1, marginBottom: "1.5rem", letterSpacing: "-0.02em" }}>
            Got something to say?<br />
            <em style={{ color: "#666", fontStyle: "italic" }}>Say it live.</em>
          </h2>
          <p style={{ fontSize: "1rem", color: "#555", marginBottom: "2.5rem" }}>
            Free to join. No filters. Just talk.
          </p>
          <Link href="/register" style={ctaPrimary}>Start a stream →</Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid #1a1a1a", padding: "2rem",
        display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem",
      }}>
        <span style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#333", textTransform: "uppercase", fontFamily: "monospace" }}>
          ⬡ SCOUTA © 2026
        </span>
        <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
          {[
            { label: "Manifesto", href: "/manifesto" },
            { label: "Feed", href: "/posts" },
            { label: "About", href: "/about" },
            { label: "Privacy", href: "/privacy" },
            { label: "Login", href: "/login" },
          ].map((l) => (
            <Link key={l.href} href={l.href} style={{
              fontSize: "0.6rem", color: "#333", textDecoration: "none",
              letterSpacing: "0.1em", textTransform: "uppercase", fontFamily: "monospace",
            }}>
              {l.label}
            </Link>
          ))}
        </div>
      </footer>

      <style>{`
        .navlink {
          font-size: 0.65rem;
          letter-spacing: 0.15em;
          color: #888;
          text-decoration: none;
          text-transform: uppercase;
          font-family: monospace;
        }
        .navlink:hover { color: #f0e8d8; }
        @media (max-width: 900px) {
          .hero-grid { grid-template-columns: 1fr !important; gap: 2.5rem !important; }
        }
        @media (max-width: 480px) {
          .hide-sm { display: none !important; }
        }
      `}</style>
    </main>
  );
}

const ctaPrimary = {
  background: "#1a2a1a",
  border: "1px solid #2a4a2a",
  color: "#4a9a4a",
  padding: "0.875rem 2rem",
  textDecoration: "none",
  fontSize: "0.8rem",
  letterSpacing: "0.15em",
  textTransform: "uppercase" as const,
  fontFamily: "monospace",
  display: "inline-block",
};

const ctaSecondary = {
  background: "transparent",
  border: "1px solid #2a2a2a",
  color: "#888",
  padding: "0.875rem 2rem",
  textDecoration: "none",
  fontSize: "0.8rem",
  letterSpacing: "0.15em",
  textTransform: "uppercase" as const,
  fontFamily: "monospace",
  display: "inline-block",
};
