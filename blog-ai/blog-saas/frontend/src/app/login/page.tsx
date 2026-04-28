"use client";
import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/posts";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [cfToken, setCfToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      if (typeof window !== "undefined" && (window as any).__cfTokenLogin) {
        setCfToken((window as any).__cfTokenLogin);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  // Turnstile loader
  useEffect(() => {
    const existing = document.querySelector('script[src*="turnstile"]');
    function renderWidget() {
      const el = document.getElementById("turnstile-login");
      if (el && !el.hasChildNodes() && (window as any).turnstile) {
        (window as any).turnstile.render("#turnstile-login", {
          sitekey: "0x4AAAAAACmEDpC_1uTRINU3",
          theme: "dark",
          callback: (token: string) => { (window as any).__cfTokenLogin = token; },
          "expired-callback": () => { (window as any).__cfTokenLogin = null; },
        });
      }
    }
    if (!existing) {
      const s = document.createElement("script");
      s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js";
      s.async = true;
      s.onload = renderWidget;
      document.head.appendChild(s);
    } else {
      setTimeout(renderWidget, 500);
    }
  }, []);

  async function handleSubmit() {
    if (loading || !email.trim() || !password.trim()) return;
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/proxy/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, cf_turnstile_token: cfToken }),
      });
      const data = await res.json();
      setLoading(false);

      if (!res.ok) {
        const detail = data.detail;
        if (Array.isArray(detail)) {
          setError(detail.map((e: any) => e.msg).join(", "));
        } else {
          setError(typeof detail === "string" ? detail : "Login failed");
        }
        return;
      }
      login(data.access_token);
      await new Promise((r) => setTimeout(r, 100));
      router.push(next);
    } catch {
      setError("Network error. Please try again.");
      setLoading(false);
    }
  }

  return (
    <main style={pageStyle}>
      <div style={card}>
        <p style={eyebrow}>Welcome back</p>
        <h1 style={h1}>Log in to Scouta</h1>
        <p style={sub}>Live talk, sharpened.</p>

        {error && (
          <div style={errorBox}>{error}</div>
        )}

        <a
          href={`${API_BASE}/api/v1/auth/google?next=${encodeURIComponent(next)}`}
          style={googleBtn}
        >
          <span style={googleG}>G</span>
          Continue with Google
        </a>

        <Divider />

        <Field label="EMAIL">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="you@email.com"
            style={inputStyle}
            autoComplete="email"
          />
        </Field>

        <Field label="PASSWORD">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="Password"
            style={inputStyle}
            autoComplete="current-password"
          />
        </Field>

        <div id="turnstile-login" style={{ margin: "0.75rem 0 1.25rem" }} />

        <button
          onClick={handleSubmit}
          disabled={loading || !email.trim() || !password.trim()}
          style={{ ...primaryBtn, opacity: loading || !email.trim() || !password.trim() ? 0.5 : 1 }}
        >
          {loading ? "Logging in..." : "Sign in →"}
        </button>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1.25rem", flexWrap: "wrap", gap: "0.5rem" }}>
          <Link href="/forgot-password" style={smallLink}>Forgot password?</Link>
          <Link href={`/register?next=${encodeURIComponent(next)}`} style={smallLinkAccent}>Create account →</Link>
        </div>
      </div>
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label style={labelStyle}>{label}</label>
      {children}
    </div>
  );
}

function Divider() {
  return (
    <div style={{ display: "flex", alignItems: "center", margin: "1.5rem 0" }}>
      <div style={{ flex: 1, height: 1, background: "#1a1a1a" }} />
      <span style={{ color: "#444", fontSize: "0.6rem", padding: "0 0.85rem", fontFamily: "monospace", letterSpacing: "0.2em" }}>OR</span>
      <div style={{ flex: 1, height: 1, background: "#1a1a1a" }} />
    </div>
  );
}

const pageStyle: React.CSSProperties = {
  minHeight: "100vh",
  background: "#080808",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "2rem 1.25rem",
};
const card: React.CSSProperties = {
  width: "100%",
  maxWidth: "440px",
  padding: "2.25rem 2rem",
  border: "1px solid #1a1a1a",
  background: "#0d0d0d",
  fontFamily: "Georgia, serif",
  color: "#e8e0d0",
};
const eyebrow: React.CSSProperties = {
  fontSize: "0.6rem",
  letterSpacing: "0.3em",
  color: "#4a7a9a",
  textTransform: "uppercase",
  fontFamily: "monospace",
  margin: 0,
};
const h1: React.CSSProperties = {
  fontSize: "1.6rem",
  fontWeight: 400,
  color: "#f0e8d8",
  margin: "0.4rem 0 0.4rem",
  fontFamily: "Georgia, serif",
};
const sub: React.CSSProperties = {
  fontSize: "0.78rem",
  color: "#666",
  fontFamily: "monospace",
  letterSpacing: "0.05em",
  margin: "0 0 2rem",
};
const errorBox: React.CSSProperties = {
  background: "#1a0a0a",
  border: "1px solid #2a1010",
  color: "#9a4a4a",
  padding: "0.6rem 0.85rem",
  fontSize: "0.72rem",
  fontFamily: "monospace",
  marginBottom: "1.25rem",
};
const googleBtn: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "0.6rem",
  width: "100%",
  background: "#fff",
  border: "1px solid #ddd",
  color: "#1a1a1a",
  padding: "0.75rem",
  textDecoration: "none",
  fontSize: "0.82rem",
  fontFamily: "Georgia, serif",
  fontWeight: 600,
  boxSizing: "border-box",
};
const googleG: React.CSSProperties = {
  fontSize: "1rem",
  fontWeight: 700,
  color: "#4285F4",
  fontFamily: "monospace",
};
const inputStyle: React.CSSProperties = {
  width: "100%",
  background: "#111",
  border: "1px solid #1e1e1e",
  color: "#e8e0d0",
  padding: "0.7rem 0.85rem",
  fontSize: "0.9rem",
  fontFamily: "Georgia, serif",
  outline: "none",
  boxSizing: "border-box",
};
const labelStyle: React.CSSProperties = {
  fontSize: "0.6rem",
  letterSpacing: "0.2em",
  color: "#555",
  textTransform: "uppercase",
  display: "block",
  marginBottom: "0.4rem",
  fontFamily: "monospace",
};
const primaryBtn: React.CSSProperties = {
  width: "100%",
  background: "#1a2a1a",
  border: "1px solid #2a4a2a",
  color: "#4a9a4a",
  padding: "0.85rem",
  cursor: "pointer",
  fontSize: "0.78rem",
  fontFamily: "monospace",
  letterSpacing: "0.15em",
  textTransform: "uppercase" as const,
  boxSizing: "border-box",
};
const smallLink: React.CSSProperties = {
  fontSize: "0.7rem",
  color: "#666",
  textDecoration: "none",
  fontFamily: "monospace",
  letterSpacing: "0.05em",
};
const smallLinkAccent: React.CSSProperties = {
  fontSize: "0.7rem",
  color: "#4a9a4a",
  textDecoration: "none",
  fontFamily: "monospace",
  letterSpacing: "0.05em",
};

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
