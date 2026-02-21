"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function EditProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const [form, setForm] = useState({
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
    if (!token) { router.push("/login"); return; }

    fetch("/api/proxy/auth/me", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => {
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
      .catch(() => router.push("/login"));
  }, [router]);

  async function handleSave() {
    setSaving(true);
    setError("");
    setSuccess(false);
    const token = localStorage.getItem("token");
    const res = await fetch("/api/proxy/auth/profile", {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    setSaving(false);
    if (res.ok) {
      // Actualizar localStorage
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      localStorage.setItem("user", JSON.stringify({
        ...user,
        display_name: data.display_name,
        username: data.username,
        avatar_url: data.avatar_url,
      }));
      setSuccess(true);
      setTimeout(() => router.push("/profile"), 1500);
    } else {
      setError(data.detail || "Failed to save");
    }
  }

  const inputStyle = {
    width: "100%", background: "#111", border: "1px solid #2a2a2a",
    color: "#e8e0d0", padding: "0.5rem 0.75rem", fontSize: "0.85rem",
    fontFamily: "monospace", outline: "none", boxSizing: "border-box" as const,
  };
  const labelStyle = {
    fontSize: "0.6rem", letterSpacing: "0.15em", color: "#555",
    textTransform: "uppercase" as const, display: "block", marginBottom: "0.4rem",
  };

  if (loading) return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#555", fontFamily: "monospace" }}>Loading...</p>
    </div>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", fontFamily: "monospace", padding: "2rem 1rem" }}>
      <div style={{ maxWidth: "500px", margin: "0 auto" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", marginBottom: "0.5rem" }}>Scouta</p>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 400, color: "#f0e8d8", marginBottom: "2rem" }}>Edit Profile</h1>

        {error && <div style={{ background: "#2a1a1a", border: "1px solid #4a2a2a", color: "#9a4a4a", padding: "0.5rem 0.75rem", fontSize: "0.75rem", marginBottom: "1rem" }}>{error}</div>}
        {success && <div style={{ background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a", padding: "0.5rem 0.75rem", fontSize: "0.75rem", marginBottom: "1rem" }}>✓ Profile saved! Redirecting...</div>}

        {/* Avatar preview */}
        <div style={{ marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "1rem" }}>
          <div style={{
            width: "64px", height: "64px", borderRadius: "50%",
            background: "#1a1a1a", border: "1px solid #2a2a2a",
            overflow: "hidden", flexShrink: 0,
          }}>
            {form.avatar_url ? (
              <img src={form.avatar_url} alt="avatar" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            ) : (
              <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", color: "#555", fontSize: "1.5rem" }}>
                {form.display_name?.[0]?.toUpperCase() || "?"}
              </div>
            )}
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Avatar URL</label>
            <input type="url" value={form.avatar_url}
              onChange={e => setForm({ ...form, avatar_url: e.target.value })}
              placeholder="https://..." style={inputStyle} />
          </div>
        </div>

        {[
          { label: "Display Name", key: "display_name", type: "text", placeholder: "Your name" },
          { label: "Username", key: "username", type: "text", placeholder: "@username" },
          { label: "Location", key: "location", type: "text", placeholder: "City, Country" },
          { label: "Website", key: "website", type: "url", placeholder: "https://..." },
          { label: "Interests", key: "interests", type: "text", placeholder: "AI, philosophy, design..." },
        ].map(f => (
          <div key={f.key} style={{ marginBottom: "1rem" }}>
            <label style={labelStyle}>{f.label}</label>
            <input type={f.type} value={(form as any)[f.key]}
              onChange={e => setForm({ ...form, [f.key]: e.target.value })}
              placeholder={f.placeholder} style={inputStyle} />
          </div>
        ))}

        <div style={{ marginBottom: "1.5rem" }}>
          <label style={labelStyle}>Bio</label>
          <textarea value={form.bio}
            onChange={e => setForm({ ...form, bio: e.target.value })}
            placeholder="Tell us about yourself..."
            rows={4}
            style={{ ...inputStyle, resize: "vertical" as const }} />
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button onClick={handleSave} disabled={saving} style={{
            flex: 1, background: saving ? "#1a1a1a" : "#1a2a1a",
            border: "1px solid #2a4a2a", color: saving ? "#444" : "#4a9a4a",
            padding: "0.6rem", cursor: saving ? "not-allowed" : "pointer",
            fontSize: "0.75rem", fontFamily: "monospace", letterSpacing: "0.1em",
          }}>
            {saving ? "Saving..." : "→ Save Profile"}
          </button>
          <button onClick={() => router.push("/profile")} style={{
            padding: "0.6rem 1rem", background: "transparent",
            border: "1px solid #2a2a2a", color: "#555",
            cursor: "pointer", fontSize: "0.75rem", fontFamily: "monospace",
          }}>
            Cancel
          </button>
        </div>
      </div>
    </main>
  );
}
