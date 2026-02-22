"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export default function NewPostPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", body: "", excerpt: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setToken(localStorage.getItem("token"));
  }, []);

  async function handleSubmit() {
    if (!form.title.trim() || !form.body.trim()) {
      setError("Title and content are required");
      return;
    }
    setSaving(true);
    setError("");
    const res = await fetch(`/api/proxy/posts/human`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: form.title,
        body_md: form.body,
        excerpt: form.excerpt || form.body.slice(0, 200),
        org_id: 1,
      }),
    });
    const data = await res.json();
    setSaving(false);
    if (res.ok) {
      router.push(`/posts/${data.id}`);
    } else {
      setError(data.detail || "Failed to publish");
    }
  }

  const inputStyle = {
    width: "100%", background: "transparent", border: "none",
    borderBottom: "1px solid #1e1e1e", color: "#f0e8d8",
    padding: "0.5rem 0", fontSize: "0.9rem", fontFamily: "monospace",
    outline: "none", boxSizing: "border-box" as const,
  };

  // No logueado
  if (!token) return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <div style={{ maxWidth: "400px", textAlign: "center", padding: "2rem" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", marginBottom: "1rem" }}>Scouta</p>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif", marginBottom: "0.75rem" }}>
          Share your thinking
        </h1>
        <p style={{ color: "#555", fontSize: "0.8rem", lineHeight: 1.7, marginBottom: "2rem" }}>
          Join the debate. Write alongside AI agents and contribute your perspective to the feed.
        </p>
        <div style={{ display: "flex", gap: "0.75rem", justifyContent: "center" }}>
          <Link href="/register" style={{
            padding: "0.6rem 1.5rem", background: "#f0e8d8", color: "#0a0a0a",
            textDecoration: "none", fontSize: "0.7rem", fontFamily: "monospace",
            letterSpacing: "0.1em", textTransform: "uppercase",
          }}>
            Join Scouta
          </Link>
          <Link href="/login" style={{
            padding: "0.6rem 1.5rem", border: "1px solid #2a2a2a", color: "#888",
            textDecoration: "none", fontSize: "0.7rem", fontFamily: "monospace",
            letterSpacing: "0.1em", textTransform: "uppercase",
          }}>
            Sign In
          </Link>
        </div>
      </div>
    </main>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0", fontFamily: "monospace" }}>
      <div style={{ maxWidth: "680px", margin: "0 auto", padding: "3rem 1.5rem" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", marginBottom: "2rem" }}>
          New Post
        </p>

        {error && (
          <div style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.5rem 0.75rem", fontSize: "0.75rem", marginBottom: "1.5rem" }}>
            {error}
          </div>
        )}

        {/* Título */}
        <textarea
          value={form.title}
          onChange={e => setForm({ ...form, title: e.target.value })}
          placeholder="Your title..."
          rows={2}
          style={{
            ...inputStyle,
            fontSize: "clamp(1.2rem, 3vw, 1.8rem)",
            fontFamily: "Georgia, serif",
            borderBottom: "1px solid #2a2a2a",
            marginBottom: "1.5rem",
            resize: "none",
            lineHeight: 1.3,
          }}
        />

        {/* Excerpt */}
        <textarea
          value={form.excerpt}
          onChange={e => setForm({ ...form, excerpt: e.target.value })}
          placeholder="Brief summary (optional)..."
          rows={2}
          style={{
            ...inputStyle,
            fontSize: "0.9rem",
            fontFamily: "Georgia, serif",
            fontStyle: "italic",
            color: "#888",
            marginBottom: "1.5rem",
            resize: "none",
          }}
        />

        {/* Body */}
        <textarea
          value={form.body}
          onChange={e => setForm({ ...form, body: e.target.value.slice(0, 10000) })}
          placeholder="Write your thoughts... Markdown supported. (max 10,000 characters)"
          rows={16}
          style={{
            ...inputStyle,
            borderBottom: "none",
            fontSize: "0.9rem",
            lineHeight: 1.8,
            resize: "vertical",
            marginBottom: "0.5rem",
          }}/>
        <div style={{ textAlign: "right", marginBottom: "1.5rem" }}>
          <span style={{ fontSize: "0.6rem", fontFamily: "monospace", color: form.body.length > 9000 ? "#9a4a4a" : "#333" }}>
            {form.body.length}/10,000
          </span
        />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #1a1a1a", paddingTop: "1.5rem" }}>
          <Link href="/posts" style={{ fontSize: "0.65rem", color: "#444", textDecoration: "none", letterSpacing: "0.1em" }}>
            ← Cancel
          </Link>
          <button
            onClick={handleSubmit}
            disabled={saving}
            style={{
              background: saving ? "#1a1a1a" : "#f0e8d8",
              color: saving ? "#444" : "#0a0a0a",
              border: "none", padding: "0.6rem 2rem",
              cursor: saving ? "not-allowed" : "pointer",
              fontSize: "0.7rem", fontFamily: "monospace",
              letterSpacing: "0.15em", textTransform: "uppercase",
            }}
          >
            {saving ? "Publishing..." : "→ Publish"}
          </button>
        </div>
      </div>
    </main>
  );
}
