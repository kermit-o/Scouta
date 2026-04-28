"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

function RegisterForm() {
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/posts";

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [cfToken, setCfToken] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    function renderWidget() {
      const el = document.getElementById("turnstile-register");
      if (el && !el.hasChildNodes() && (window as any).turnstile) {
        (window as any).turnstile.render("#turnstile-register", {
          sitekey: "0x4AAAAAACmEDpC_1uTRINU3",
          theme: "dark",
          callback: (token: string) => { (window as any).__cfTokenRegister = token; },
          "expired-callback": () => { (window as any).__cfTokenRegister = null; },
        });
      }
    }
    if (!document.querySelector('script[src*="turnstile"]')) {
      const s = document.createElement("script");
      s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js";
      s.async = true;
      s.onload = renderWidget;
      document.head.appendChild(s);
    } else {
      setTimeout(renderWidget, 500);
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      const t = (window as any).__cfTokenRegister;
      if (t) setCfToken(t);
    }, 500);
    return () => clearInterval(interval);
  }, []);

  async function handleSubmit() {
    if (loading) return;
    setError("");
    const token = (window as any).__cfTokenRegister || cfToken;
    if (!token) {
      setError("Please complete the verification.");
      return;
    }
    if (!email.trim() || !username.trim() || !password) {
      setError("Email, username, and password are required.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/proxy/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          username,
          display_name: displayName || username,
          password,
          cf_turnstile_token: token,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(typeof data.detail === "string" ? data.detail : "Registration failed");
      } else {
        setSuccess(true);
      }
    } catch {
      setError("Network error. Please try again.");
    }
    setLoading(false);
  }

  if (success) {
    return (
      <main style={pageStyle}>
        <div style={{ ...card, textAlign: "center" }}>
          <p style={eyebrow}>Check your inbox</p>
          <h1 style={h1}>Almost there.</h1>
          <p style={{ color: "#888", fontSize: "0.95rem", lineHeight: 1.6, fontFamily: "Georgia, serif", margin: "0 0 0.5rem" }}>
            We sent a verification link to
          </p>
          <p style={{ color: "#f0e8d8", fontSize: "0.9rem", fontFamily: "monospace", letterSpacing: "0.05em", margin: "0 0 1.5rem", wordBreak: "break-word" }}>
            {email}
          </p>
          <p style={{ color: "#555", fontSize: "0.75rem", fontFamily: "monospace", marginBottom: "2rem" }}>
            Click the link in that email to activate your account.
          </p>
          <Link href="/login" style={primaryBtn}>Go to login</Link>
        </div>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <div style={card}>
        <p style={eyebrow}>Create account</p>
        <h1 style={h1}>Join Scouta</h1>
        <p style={sub}>Free. No filters. Live talk.</p>

        {error && <div style={errorBox}>{error}</div>}

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
            placeholder="you@email.com"
            style={inputStyle}
            autoComplete="email"
          />
        </Field>

        <Field label="USERNAME">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ""))}
            placeholder="your_handle"
            style={inputStyle}
            autoComplete="username"
            maxLength={24}
          />
        </Field>

        <Field label="DISPLAY NAME">
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="How you want to appear (optional)"
            style={inputStyle}
            maxLength={48}
          />
        </Field>

        <Field label="PASSWORD">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            placeholder="At least 8 characters"
            style={inputStyle}
            autoComplete="new-password"
          />
        </Field>

        <div id="turnstile-register" style={{ margin: "0.75rem 0 1.25rem" }} />

        <button
          onClick={handleSubmit}
          disabled={loading || !email.trim() || !username.trim() || !password}
          style={{ ...primaryBtn, opacity: loading || !email.trim() || !username.trim() || !password ? 0.5 : 1 }}
        >
          {loading ? "Creating account..." : "Create account →"}
        </button>

        <p style={{ marginTop: "1.25rem", textAlign: "center", fontSize: "0.7rem", color: "#666", fontFamily: "monospace", letterSpacing: "0.05em" }}>
          Already have an account?{" "}
          <Link href={`/login?next=${encodeURIComponent(next)}`} style={{ color: "#4a9a4a", textDecoration: "none" }}>
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: "0.875rem" }}>
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
  textDecoration: "none",
  display: "inline-block",
  textAlign: "center" as const,
};

export default function RegisterPage() {
  return (
    <Suspense fallback={null}>
      <RegisterForm />
    </Suspense>
  );
}
