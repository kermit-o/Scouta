"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

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
    setError("");
    const token = (window as any).__cfTokenRegister || cfToken;
    if (!token) {
      setError("Please complete the CAPTCHA verification.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/proxy/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, username, display_name: displayName, password, cf_turnstile_token: token }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(typeof data.detail === "string" ? data.detail : "Registration failed");
      } else {
        setSuccess(true);
      }
    } catch (e) {
      setError("Network error. Please try again.");
    }
    setLoading(false);
  }

  const input: React.CSSProperties = {
    width: "100%", background: "#111", border: "1px solid #2a2a2a",
    color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.85rem",
    fontFamily: "monospace", outline: "none", boxSizing: "border-box",
    marginBottom: "1rem",
  };
  const label: React.CSSProperties = {
    fontSize: "0.6rem", letterSpacing: "0.15em", color: "#555",
    textTransform: "uppercase", display: "block", marginBottom: "0.4rem",
    fontFamily: "monospace",
  };

  if (success) return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ textAlign: "center", color: "#e0e0e0", maxWidth: "400px", padding: "2rem", fontFamily: "monospace" }}>
        <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>📬</div>
        <h2 style={{ color: "#fff", marginBottom: "0.5rem" }}>Check your email</h2>
        <p style={{ color: "#888" }}>We sent a verification link to <strong style={{ color: "#fff" }}>{email}</strong></p>
        <p style={{ color: "#444", fontSize: "0.8rem", marginTop: "1rem" }}>Click the link to activate your account.</p>
      </div>
    </div>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: "380px", padding: "2rem 1.5rem", border: "1px solid #1e1e1e", background: "#0d0d0d" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: "0 0 0.5rem" }}>Join</p>
        <h1 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", margin: "0 0 2rem" }}>The Feed</h1>

        {error && (
          <div style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.5rem 0.75rem", fontSize: "0.7rem", marginBottom: "1rem" }}>
            {error}
          </div>
        )}

        <label style={label}>Email</label>
        <input type="email" value={email} onChange={e => setEmail(e.target.value)} style={input} />

        <label style={label}>Username</label>
        <input type="text" value={username} onChange={e => setUsername(e.target.value)} style={input} />

        <label style={label}>Display Name</label>
        <input type="text" value={displayName} onChange={e => setDisplayName(e.target.value)} style={input} />

        <label style={label}>Password</label>
        <input type="password" value={password} onChange={e => setPassword(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSubmit()} style={input} />

        <div id="turnstile-register" style={{ margin: "0.5rem 0 1rem" }}></div>

        <button onClick={handleSubmit} disabled={loading} style={{
          width: "100%", background: loading ? "#1a1a1a" : "#1a2a1a",
          border: "1px solid #2a4a2a", color: loading ? "#444" : "#4a9a4a",
          padding: "0.6rem", cursor: loading ? "not-allowed" : "pointer",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.1em", marginBottom: "1rem",
        }}>
          {loading ? "Creating account..." : "→ Create Account"}
        </button>

        <div style={{ display: "flex", alignItems: "center", margin: "1rem 0" }}>
          <div style={{ flex: 1, height: "1px", background: "#1e1e1e" }} />
          <span style={{ color: "#333", fontSize: "0.65rem", padding: "0 0.75rem" }}>or</span>
          <div style={{ flex: 1, height: "1px", background: "#1e1e1e" }} />
        </div>

        <a href="/api/proxy/api/v1/auth/google" style={{
          display: "block", width: "100%", background: "#111", border: "1px solid #2a2a2a",
          color: "#e0e0e0", padding: "0.6rem", textAlign: "center", textDecoration: "none",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.05em",
          boxSizing: "border-box", marginBottom: "1rem",
        }}>
          G → Continue with Google
        </a>

        <p style={{ fontSize: "0.65rem", color: "#444", textAlign: "center", margin: 0 }}>
          Already have an account?{" "}
          <Link href={`/login?next=${encodeURIComponent(next)}`} style={{ color: "#4a7a9a", textDecoration: "none" }}>Login</Link>
        </p>
      </div>
    </main>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={null}>
      <RegisterForm />
    </Suspense>
  );
}
