"use client";
import { useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

function ResetPasswordContent() {
  const params = useSearchParams();
  const router = useRouter();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    if (password.length < 8) { setError("Password must be at least 8 characters"); return; }
    if (password !== confirm) { setError("Passwords don't match"); return; }
    if (!token) { setError("Invalid reset link"); return; }
    setLoading(true);
    const res = await fetch("/api/proxy/auth/reset-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, password }),
    });
    const data = await res.json();
    setLoading(false);
    if (data.access_token) {
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify({
        id: data.user_id,
        username: data.username,
        display_name: data.display_name,
        avatar_url: data.avatar_url,
      }));
      router.push("/posts");
    } else {
      setError(data.detail || "Invalid or expired link.");
    }
  }

  const inputStyle = {
    width: "100%", background: "#111", border: "1px solid #2a2a2a",
    color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.85rem",
    fontFamily: "monospace", outline: "none", boxSizing: "border-box" as const,
  };

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace", padding: "1rem" }}>
      <div style={{ width: "100%", maxWidth: "380px", padding: "2rem 1.5rem", border: "1px solid #1e1e1e", background: "#0d0d0d" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", margin: "0 0 0.5rem" }}>Scouta</p>
        <h1 style={{ fontSize: "1.25rem", fontWeight: 400, color: "#f0e8d8", margin: "0 0 1.5rem" }}>Reset password</h1>

        {error && (
          <div style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.5rem 0.75rem", fontSize: "0.7rem", marginBottom: "1rem" }}>
            {error}
          </div>
        )}

        {[
          { label: "New Password", value: password, set: setPassword },
          { label: "Confirm Password", value: confirm, set: setConfirm },
        ].map(f => (
          <div key={f.label} style={{ marginBottom: "1rem" }}>
            <label style={{ fontSize: "0.6rem", letterSpacing: "0.15em", color: "#555", textTransform: "uppercase", display: "block", marginBottom: "0.4rem" }}>{f.label}</label>
            <input type="password" value={f.value} onChange={e => f.set(e.target.value)} style={inputStyle} />
          </div>
        ))}

        <button onClick={handleSubmit} disabled={loading} style={{
          width: "100%", background: loading ? "#1a1a1a" : "#1a2a1a",
          border: "1px solid #2a4a2a", color: loading ? "#444" : "#4a9a4a",
          padding: "0.6rem", cursor: loading ? "not-allowed" : "pointer",
          fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.1em",
        }}>
          {loading ? "Resetting..." : "→ Reset Password"}
        </button>
      </div>
    </main>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: "100vh", background: "#0a0a0a" }} />}>
      <ResetPasswordContent />
    </Suspense>
  );
}
