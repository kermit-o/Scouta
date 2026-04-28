"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = "/api/proxy/api/v1";

interface Form {
  display_name: string;
  username: string;
  bio: string;
  avatar_url: string;
  interests: string;
  website: string;
  location: string;
}

export default function EditProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState<Form>({
    display_name: "",
    username: "",
    bio: "",
    avatar_url: "",
    interests: "",
    website: "",
    location: "",
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login?next=/profile/edit"); return; }

    fetch(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.ok ? r.json() : Promise.reject(r))
      .then((data) => {
        setForm({
          display_name: data.display_name || "",
          username: data.username || "",
          bio: data.bio || "",
          avatar_url: data.avatar_url || "",
          interests: data.interests || "",
          website: data.website || "",
          location: data.location || "",
        });
        setLoading(false);
      })
      .catch(() => { router.push("/login?next=/profile/edit"); });
  }, [router]);

  async function handleSave() {
    if (saving) return;
    setSaving(true);
    setError("");
    setSuccess(false);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API}/auth/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      setSaving(false);
      if (!res.ok) {
        setError(typeof data.detail === "string" ? data.detail : "Failed to save");
        return;
      }
      try {
        const user = JSON.parse(localStorage.getItem("user") || "{}");
        localStorage.setItem("user", JSON.stringify({
          ...user,
          display_name: data.display_name,
          username: data.username,
          avatar_url: data.avatar_url,
        }));
      } catch {}
      setSuccess(true);
      setTimeout(() => router.push("/profile"), 1200);
    } catch {
      setSaving(false);
      setError("Network error. Please try again.");
    }
  }

  if (loading) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
        </div>
      </main>
    );
  }

  const initial = (form.display_name || form.username || "?")[0]?.toUpperCase();

  return (
    <main style={pageStyle}>
      <div style={container}>
        <Link href="/profile" style={backLink}>← Back to profile</Link>

        <p style={eyebrow}>SCOUTA / EDIT PROFILE</p>
        <h1 style={h1}>Edit profile</h1>
        <p style={sub}>How others see you on Scouta.</p>

        {error && <div style={errorBox}>{error}</div>}
        {success && <div style={successBox}>Saved. Redirecting...</div>}

        {/* Avatar */}
        <div style={{ display: "flex", gap: "1.25rem", alignItems: "center", marginBottom: "1.5rem" }}>
          <div style={avatarBox}>
            {form.avatar_url ? (
              <img src={form.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <span style={{ color: "#4a9a4a", fontSize: "1.5rem", fontFamily: "monospace", fontWeight: 700 }}>
                {initial}
              </span>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>AVATAR URL</label>
            <input
              type="url"
              value={form.avatar_url}
              onChange={(e) => setForm({ ...form, avatar_url: e.target.value })}
              placeholder="https://..."
              style={inputStyle}
            />
          </div>
        </div>

        <Field label="DISPLAY NAME">
          <input
            type="text"
            value={form.display_name}
            onChange={(e) => setForm({ ...form, display_name: e.target.value })}
            placeholder="Your name"
            style={inputStyle}
            maxLength={48}
          />
        </Field>

        <Field label="USERNAME" hint="Lowercase, no spaces. Will appear as @handle.">
          <input
            type="text"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, "") })}
            placeholder="your_handle"
            style={inputStyle}
            maxLength={24}
          />
        </Field>

        <Field label="BIO" hint="What you do, what you talk about.">
          <textarea
            value={form.bio}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
            placeholder="A line or two about yourself."
            rows={4}
            style={{ ...inputStyle, resize: "vertical" as const, fontFamily: "Georgia, serif" }}
            maxLength={280}
          />
        </Field>

        <Field label="LOCATION">
          <input
            type="text"
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            placeholder="City, Country"
            style={inputStyle}
          />
        </Field>

        <Field label="WEBSITE">
          <input
            type="url"
            value={form.website}
            onChange={(e) => setForm({ ...form, website: e.target.value })}
            placeholder="https://..."
            style={inputStyle}
          />
        </Field>

        <Field label="INTERESTS" hint="Comma-separated.">
          <input
            type="text"
            value={form.interests}
            onChange={(e) => setForm({ ...form, interests: e.target.value })}
            placeholder="AI, philosophy, design"
            style={inputStyle}
          />
        </Field>

        <div style={{ display: "flex", gap: "0.75rem", marginTop: "1.5rem" }}>
          <button
            onClick={handleSave}
            disabled={saving}
            style={{ ...primaryBtn, opacity: saving ? 0.5 : 1, cursor: saving ? "not-allowed" : "pointer" }}
          >
            {saving ? "Saving..." : "Save profile →"}
          </button>
          <button
            onClick={() => router.push("/profile")}
            style={cancelBtn}
          >
            Cancel
          </button>
        </div>
      </div>
    </main>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: "1.1rem" }}>
      <label style={labelStyle}>{label}</label>
      {children}
      {hint && <p style={hintStyle}>{hint}</p>}
    </div>
  );
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#e8e0d0" };
const container: React.CSSProperties = { maxWidth: "560px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" };
const backLink: React.CSSProperties = {
  color: "#4a7a9a", fontSize: "0.7rem", fontFamily: "monospace",
  textDecoration: "none", letterSpacing: "0.1em",
  display: "inline-block", marginBottom: "1.5rem",
};
const eyebrow: React.CSSProperties = {
  fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a",
  textTransform: "uppercase", fontFamily: "monospace", margin: 0,
};
const h1: React.CSSProperties = {
  fontSize: "clamp(1.5rem, 3.5vw, 2rem)", fontWeight: 400,
  fontFamily: "Georgia, serif", color: "#f0e8d8",
  margin: "0.4rem 0 0.4rem",
};
const sub: React.CSSProperties = {
  fontSize: "0.78rem", color: "#666", fontFamily: "monospace",
  letterSpacing: "0.05em", margin: "0 0 2rem",
};
const errorBox: React.CSSProperties = {
  background: "#1a0a0a", border: "1px solid #2a1010",
  color: "#9a4a4a", padding: "0.6rem 0.85rem",
  fontSize: "0.72rem", fontFamily: "monospace",
  marginBottom: "1.25rem",
};
const successBox: React.CSSProperties = {
  background: "#0a1a0a", border: "1px solid #102a10",
  color: "#4a9a4a", padding: "0.6rem 0.85rem",
  fontSize: "0.72rem", fontFamily: "monospace",
  marginBottom: "1.25rem", letterSpacing: "0.05em",
};
const avatarBox: React.CSSProperties = {
  width: 72, height: 72, borderRadius: "50%",
  background: "#1a2a1a", border: "1px solid #2a4a2a",
  overflow: "hidden", flexShrink: 0,
  display: "flex", alignItems: "center", justifyContent: "center",
};
const inputStyle: React.CSSProperties = {
  width: "100%", background: "#111", border: "1px solid #1e1e1e",
  color: "#e8e0d0", padding: "0.7rem 0.85rem",
  fontSize: "0.9rem", fontFamily: "Georgia, serif",
  outline: "none", boxSizing: "border-box",
};
const labelStyle: React.CSSProperties = {
  fontSize: "0.6rem", letterSpacing: "0.2em",
  color: "#555", textTransform: "uppercase",
  display: "block", marginBottom: "0.4rem",
  fontFamily: "monospace",
};
const hintStyle: React.CSSProperties = {
  fontSize: "0.65rem", color: "#444",
  fontFamily: "monospace", letterSpacing: "0.05em",
  marginTop: "0.4rem", marginBottom: 0,
};
const primaryBtn: React.CSSProperties = {
  flex: 1, background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.85rem", fontSize: "0.75rem",
  fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
  boxSizing: "border-box",
};
const cancelBtn: React.CSSProperties = {
  padding: "0.85rem 1.5rem", background: "transparent",
  border: "1px solid #2a2a2a", color: "#777",
  cursor: "pointer", fontSize: "0.75rem",
  fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
};
