"use client";
import { useState } from "react";
import Link from "next/link";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!email) return;
    setLoading(true);
    await fetch("/api/proxy/auth/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    setLoading(false);
    setSent(true);
  }

  const inputStyle = {
    width: "100%", background: "#111", border: "1px solid #2a2a2a",
    color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.85rem",
    fontFamily: "monospace", outline: "none", boxSizing: "border-box" as const,
  };

  if (sent) return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <div style={{ textAlign: "center", color: "#e0e0e0", maxWidth: "400px", padding: "2rem" }}>
        <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>📬</div>
        <h2 style={{ color: "#fff", marginBottom: "0.5rem" }}>Check your email</h2>
        <p style={{ color: "#888" }}>If <strong style={{ color: "#fff" }}>{email}</strong> exists, you'll receive a reset link shortly.</p>
        <p style={{ marginTop: "1.5rem" }}>
          <Link href="/login" style={{ color: "#4a7a9a", fontSize: "0.8rem", textDecoration: "none" }}>← Back to login</Link>
        </p>
      </div>
    </div>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: "380px", padding: "2rem 1.5rem", border: "1px solid #1e1e1e", background: "#0d0d0d" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: "0 0 0.5rem" }}>Scouta</p>
        <h1 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", margin: "0 0 0.5rem" }}>Forgot password</h1>
        <p style={{ color: "#555", fontSize: "0.75rem", marginBottom: "1.5rem" }}>Enter your email and we'll send a reset link.</p>

        <label style={{ fontSize: "0.6rem", letterSpacing: "0.15em", color: "#555", textTransform: "uppercase", display: "block", marginBottom: "0.4rem" }}>Email</label>
        <input
          type="email" value={email}
          onChange={e => setEmail(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSubmit()}
          style={inputStyle}
        />

        <button onClick={handleSubmit} disabled={loading} style={{
          width: "100%", marginTop: "1rem", background: loading ? "#1a1a1a" : "#1a2a1a",
          border: "1px solid #2a4a2a", color: loading ? "#444" : "#4a9a4a",
          padding: "0.6rem", cursor: loading ? "not-allowed" : "pointer",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.1em",
        }}>
          {loading ? "Sending..." : "→ Send Reset Link"}
        </button>

        <p style={{ fontSize: "0.65rem", color: "#444", textAlign: "center", marginTop: "1rem" }}>
          <Link href="/login" style={{ color: "#4a7a9a", textDecoration: "none" }}>← Back to login</Link>
        </p>
      </div>
    </main>
  );
}
