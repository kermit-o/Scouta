"use client";
import React, { useState, useEffect, Suspense } from "react";

import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

function LoginForm() {
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/posts";
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [cfToken, setCfToken] = useState("");
  const turnstileRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      if (typeof window !== "undefined" && (window as any).__cfTokenLogin) {
        setCfToken((window as any).__cfTokenLogin);
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    setLoading(true);
    const API_URL = typeof window !== "undefined"
      ? ("/api/proxy")
      : (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");
    const res = await fetch(`${API_URL}/api/v1/auth/login`, {
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
    // Pequeño delay para que AuthContext propague el token antes de navegar
    await new Promise(r => setTimeout(r, 100));
    router.push(next);
  }

  const inputStyle = {
    width: "100%", background: "#111", border: "1px solid #2a2a2a",
    color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.85rem",
    fontFamily: "monospace", outline: "none", boxSizing: "border-box" as const,
  };
  const labelStyle = {
    fontSize: "0.6rem", letterSpacing: "0.15em", color: "#555",
    textTransform: "uppercase" as const, display: "block", marginBottom: "0.4rem",
    fontFamily: "monospace",
  };

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: "380px", padding: "2rem 1.5rem", border: "1px solid #1e1e1e", background: "#0d0d0d" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: "0 0 0.5rem" }}>Welcome back</p>
        <h1 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", margin: "0 0 2rem", fontFamily: "monospace" }}>The Feed</h1>

        {error && <div style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.5rem 0.75rem", fontSize: "0.7rem", marginBottom: "1rem" }}>{error}</div>}

        <div style={{ marginBottom: "1rem" }}>
          <label style={labelStyle}>Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()} style={inputStyle} />
        </div>
        <div style={{ marginBottom: "1.5rem" }}>
          <label style={labelStyle}>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSubmit()} style={inputStyle} />
        </div>

        {/* Cloudflare Turnstile */}
        <div id="turnstile-login" style={{ margin: "0.5rem 0" }}></div>
        <script dangerouslySetInnerHTML={{ __html: `
          if (typeof window !== 'undefined') {
            if (!document.querySelector('script[src*="turnstile"]')) {
              var s = document.createElement('script');
              s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onTurnstileLoad';
              s.async = true;
              document.head.appendChild(s);
            }
            window.onTurnstileLoad = function() {
              if (document.getElementById('turnstile-login') && !document.getElementById('turnstile-login').hasChildNodes()) {
                turnstile.render('#turnstile-login', {
                  sitekey: '0x4AAAAAACjhqLq_nAHMhdk_',
                  callback: function(token) { window.__cfTokenLogin = token; },
                });
              }
            };
          }
        ` }} />
        <button onClick={handleSubmit} disabled={loading} style={{
          width: "100%", background: loading ? "#1a1a1a" : "#1a2a1a",
          border: "1px solid #2a4a2a", color: loading ? "#444" : "#4a9a4a",
          padding: "0.6rem", cursor: loading ? "not-allowed" : "pointer",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.1em", marginBottom: "1rem",
        }}>
          {loading ? "Logging in..." : "→ Login"}
        </button>

        <div style={{ display: "flex", alignItems: "center", margin: "1rem 0" }}>
          <div style={{ flex: 1, height: "1px", background: "#1e1e1e" }} />
          <span style={{ color: "#333", fontSize: "0.65rem", padding: "0 0.75rem" }}>or</span>
          <div style={{ flex: 1, height: "1px", background: "#1e1e1e" }} />
        </div>

        <a href="https://scouta-production.up.railway.app/api/v1/auth/google" style={{
          display: "block", width: "100%", background: "#111", border: "1px solid #2a2a2a",
          color: "#e0e0e0", padding: "0.6rem", textAlign: "center", textDecoration: "none",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.05em", boxSizing: "border-box",
        }}>
          G → Continue with Google
        </a>

        <p style={{ fontSize: "0.65rem", color: "#444", textAlign: "center", marginBottom: "0.5rem" }}>
          <Link href="/forgot-password" style={{ color: "#555", textDecoration: "none" }}>Forgot password?</Link>
        </p>
        <p style={{ fontSize: "0.65rem", color: "#444", textAlign: "center", margin: 0 }}>
          No account?{" "}
          <Link href={`/register?next=${encodeURIComponent(next)}`} style={{ color: "#4a7a9a", textDecoration: "none" }}>Register</Link>
        </p>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginForm />
    </Suspense>
  );
}
