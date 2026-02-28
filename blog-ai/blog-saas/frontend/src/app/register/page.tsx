"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import Link from "next/link";

function RegisterForm() {
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") ?? "/posts";
  const [email, setEmail] = useState("");
  const [success, setSuccess] = useState(false);
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [cfToken, setCfToken] = useState("");

  useEffect(() => {
    const interval = setInterval(() => {
      if (typeof window !== "undefined" && (window as any).__cfTokenRegister) {
        setCfToken((window as any).__cfTokenRegister);
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
    const res = await fetch(`${API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, username, display_name: displayName, password, cf_turnstile_token: cfToken }),
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) { setError(data.detail ?? "Registration failed"); return; }
    setSuccess(true);
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

  if (success) return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <div style={{ textAlign: "center", color: "#e0e0e0", maxWidth: "400px", padding: "2rem" }}>
        <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>📬</div>
        <h2 style={{ color: "#fff", marginBottom: "0.5rem" }}>Check your email</h2>
        <p style={{ color: "#888" }}>We sent a verification link to <strong style={{color:"#fff"}}>{email}</strong></p>
        <p style={{ color: "#444", fontSize: "0.8rem", marginTop: "1rem" }}>Click the link to activate your account and start debating.</p>
      </div>
    </div>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: "380px", padding: "2rem 1.5rem", border: "1px solid #1e1e1e", background: "#0d0d0d" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: "0 0 0.5rem" }}>Join</p>
        <h1 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", margin: "0 0 2rem", fontFamily: "monospace" }}>The Feed</h1>

        {error && <div style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.5rem 0.75rem", fontSize: "0.7rem", marginBottom: "1rem" }}>{error}</div>}

        {[
          { label: "Email", value: email, set: setEmail, type: "email" },
          { label: "Username", value: username, set: setUsername, type: "text" },
          { label: "Display Name", value: displayName, set: setDisplayName, type: "text" },
          { label: "Password", value: password, set: setPassword, type: "password" },
        ].map(f => (
          <div key={f.label} style={{ marginBottom: "1rem" }}>
            <label style={labelStyle}>{f.label}</label>
            <input type={f.type} value={f.value} onChange={e => f.set(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleSubmit()} style={inputStyle} />
          </div>
        ))}

                {/* Cloudflare Turnstile */}
        <div id="turnstile-register" style={{ margin: "0.5rem 0" }}></div>
        <script dangerouslySetInnerHTML={{ __html: `
          if (typeof window !== 'undefined') {
            if (!document.querySelector('script[src*="turnstile"]')) {
              var s = document.createElement('script');
              s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onTurnstileLoadReg';
              s.async = true;
              document.head.appendChild(s);
            }
            window.onTurnstileLoadReg = function() {
              if (document.getElementById('turnstile-register') && !document.getElementById('turnstile-register').hasChildNodes()) {
                turnstile.render('#turnstile-register', {
                  sitekey: '0x4AAAAAACjhqLq_nAHMhdk_',
                  callback: function(token) { window.__cfTokenRegister = token; },
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
          {loading ? "Creating account..." : "→ Create Account"}
        </button>

        <div style={{ display: "flex", alignItems: "center", margin: "1rem 0" }}>
          <div style={{ flex: 1, height: "1px", background: "#1e1e1e" }} />
          <span style={{ color: "#333", fontSize: "0.65rem", padding: "0 0.75rem" }}>or</span>
          <div style={{ flex: 1, height: "1px", background: "#1e1e1e" }} />
        </div>
        <a href="https://scouta-production.up.railway.app/api/v1/auth/google" style={{
          display: "block", width: "100%", background: "#111", border: "1px solid #2a2a2a",
          color: "#e0e0e0", padding: "0.6rem", textAlign: "center", textDecoration: "none",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.05em",
          boxSizing: "border-box" as const, marginBottom: "1rem",
        }}>
          G &rarr; Continue with Google
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
