"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

type AccessType = "password" | "invite_only" | "paid" | "followers" | "subscribers" | "vip";

const ACCESS_OPTIONS: Array<{ value: AccessType; label: string; description: string }> = [
  { value: "password", label: "Password", description: "Viewers enter a password to join" },
  { value: "invite_only", label: "Invite only", description: "Only people you invite can join" },
  { value: "paid", label: "Paid entry", description: "Viewers spend coins to join" },
  { value: "followers", label: "Followers", description: "Only your followers can join" },
  { value: "subscribers", label: "Subscribers", description: "Only paid subscribers can join" },
  { value: "vip", label: "VIP list", description: "Only your VIP list" },
];

export default function StartLivePage() {
  const router = useRouter();
  const { token, isLoaded } = useAuth();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const [accessType, setAccessType] = useState<AccessType>("password");
  const [password, setPassword] = useState("");
  const [entryCost, setEntryCost] = useState("");
  const [maxViewers, setMaxViewers] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (isLoaded && !token) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, textAlign: "center", paddingTop: "5rem" }}>
          <p style={{ color: "#888", marginBottom: "1rem", fontFamily: "monospace", fontSize: "0.8rem" }}>You need to be logged in to start a live.</p>
          <Link href="/login" style={primaryBtn}>Log in →</Link>
        </div>
      </main>
    );
  }

  async function submit() {
    if (!token || !title.trim()) return;
    setSubmitting(true);
    setError("");

    // Check camera + mic BEFORE creating the live_streams row — otherwise a
    // device without a camera (or with permissions denied) leaves a zombie
    // row marked status='live' that nobody can publish to and only the host
    // can end. Stop the tracks immediately; the actual broadcast happens
    // inside LiveKitRoom on the next page.
    try {
      const probe = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      probe.getTracks().forEach((t) => t.stop());
    } catch (err: unknown) {
      const name = (err as { name?: string })?.name || "";
      let msg = "No camera or microphone available. Use a device with both to go live.";
      if (name === "NotAllowedError" || name === "SecurityError") {
        msg = "Camera/mic access denied. Enable permissions in your browser and try again.";
      } else if (name === "NotFoundError" || name === "OverconstrainedError") {
        msg = "No camera or microphone detected on this device.";
      } else if (name === "NotReadableError") {
        msg = "Camera or microphone is already in use by another app.";
      }
      setError(msg);
      setSubmitting(false);
      return;
    }

    const body: Record<string, unknown> = {
      title: title.trim(),
      description: description.trim(),
    };
    if (isPrivate) {
      body.is_private = true;
      body.access_type = accessType;
      if (accessType === "password") body.password = password;
      if (accessType === "paid") body.entry_coin_cost = parseInt(entryCost) || 0;
      if (maxViewers) body.max_viewer_limit = parseInt(maxViewers) || 0;
    }

    const res = await fetch("/api/proxy/live/start", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(body),
    });

    const text = await res.text();
    let data: any = {};
    try { data = JSON.parse(text); } catch { data = { detail: text }; }

    if (!res.ok || !data.room_name) {
      setError(typeof data.detail === "string" ? `HTTP ${res.status}: ${data.detail}` : `HTTP ${res.status}`);
      setSubmitting(false);
      return;
    }

    // starter=1 marks this tab as the original host (creator of the stream),
    // not a co-host who arrived via join_accepted. The room page uses this
    // flag to decide who sees the End/Invite buttons and who runs the
    // thumbnail capture loop. Co-host invitations don't add starter=1.
    router.push(`/live/${data.room_name}?token=${data.token}&host=1&starter=1`);
  }

  const canSubmit = !!title.trim() && !submitting && (!isPrivate || accessType !== "password" || !!password.trim());

  return (
    <main style={pageStyle}>
      <div style={container}>
        <Link href="/live" style={backLink}>← Back to live</Link>
        <p style={eyebrow}>SCOUTA / GO LIVE</p>
        <h1 style={h1}>Start a live</h1>
        <p style={{ color: "#666", fontSize: "0.85rem", marginBottom: "2.5rem", lineHeight: 1.6 }}>
          Pick a topic. AI co-hosts will jump in to challenge takes and surface counter-arguments.
        </p>

        {error ? <p style={errorStyle}>{error}</p> : null}

        <label style={labelStyle}>TITLE</label>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What's the topic?"
          style={inputStyle}
          autoFocus
        />

        <label style={{ ...labelStyle, marginTop: "1.25rem" }}>DESCRIPTION</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional. Set the stage."
          rows={3}
          style={{ ...inputStyle, resize: "vertical", fontFamily: "monospace" }}
        />

        <div style={privateBox}>
          <label style={{ display: "flex", alignItems: "center", gap: "0.6rem", cursor: "pointer", padding: "0.85rem 1rem" }}>
            <input
              type="checkbox"
              checked={isPrivate}
              onChange={(e) => setIsPrivate(e.target.checked)}
              style={{ accentColor: "#9a6a4a" }}
            />
            <span style={{ fontSize: "0.78rem", color: "#f0e8d8", fontFamily: "monospace", letterSpacing: "0.05em" }}>
              Private room
            </span>
            <span style={{ fontSize: "0.65rem", color: "#555", fontFamily: "monospace", marginLeft: "auto" }}>
              Restrict who can join
            </span>
          </label>

          {isPrivate && (
            <div style={{ borderTop: "1px solid #1a1a1a", padding: "1rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={labelStyle}>ACCESS TYPE</label>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.5rem" }}>
                  {ACCESS_OPTIONS.map((opt) => (
                    <button
                      key={opt.value}
                      onClick={() => setAccessType(opt.value)}
                      style={{
                        background: accessType === opt.value ? "#1a2a1a" : "#101010",
                        border: `1px solid ${accessType === opt.value ? "#4a9a4a" : "#1e1e1e"}`,
                        color: accessType === opt.value ? "#4a9a4a" : "#777",
                        padding: "0.6rem 0.75rem",
                        fontFamily: "monospace",
                        fontSize: "0.7rem",
                        textAlign: "left",
                        cursor: "pointer",
                      }}
                    >
                      <div style={{ fontWeight: 700, letterSpacing: "0.06em" }}>{opt.label}</div>
                      <div style={{ fontSize: "0.6rem", color: "#555", marginTop: "0.2rem" }}>{opt.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              {accessType === "password" && (
                <div>
                  <label style={labelStyle}>PASSWORD</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Required"
                    style={inputStyle}
                  />
                </div>
              )}

              {accessType === "paid" && (
                <div>
                  <label style={labelStyle}>ENTRY COST (COINS)</label>
                  <input
                    value={entryCost}
                    onChange={(e) => setEntryCost(e.target.value.replace(/\D/g, ""))}
                    placeholder="e.g. 50"
                    style={inputStyle}
                  />
                </div>
              )}

              <div>
                <label style={labelStyle}>MAX VIEWERS</label>
                <input
                  value={maxViewers}
                  onChange={(e) => setMaxViewers(e.target.value.replace(/\D/g, ""))}
                  placeholder="0 = unlimited"
                  style={inputStyle}
                />
              </div>
            </div>
          )}
        </div>

        <button onClick={submit} disabled={!canSubmit} style={{ ...submitBtn, opacity: canSubmit ? 1 : 0.4, cursor: canSubmit ? "pointer" : "not-allowed" }}>
          {submitting ? "Starting..." : isPrivate ? "Start private live →" : "Start live →"}
        </button>
      </div>
    </main>
  );
}

const pageStyle: React.CSSProperties = {
  minHeight: "100vh",
  background: "#080808",
  color: "#f0e8d8",
};
const container: React.CSSProperties = {
  maxWidth: "640px",
  margin: "0 auto",
  padding: "3rem 1.5rem 5rem",
};
const backLink: React.CSSProperties = {
  color: "#4a7a9a",
  fontSize: "0.7rem",
  fontFamily: "monospace",
  textDecoration: "none",
  letterSpacing: "0.1em",
  display: "inline-block",
  marginBottom: "2rem",
};
const eyebrow: React.CSSProperties = {
  fontSize: "0.6rem",
  letterSpacing: "0.3em",
  color: "#4a7a9a",
  textTransform: "uppercase",
  fontFamily: "monospace",
  margin: "0 0 0.75rem",
};
const h1: React.CSSProperties = {
  fontSize: "clamp(1.75rem, 4vw, 2.75rem)",
  fontWeight: 400,
  fontFamily: "Georgia, serif",
  color: "#f0e8d8",
  margin: "0 0 0.75rem",
};
const labelStyle: React.CSSProperties = {
  fontSize: "0.6rem",
  color: "#666",
  fontFamily: "monospace",
  letterSpacing: "0.15em",
  marginBottom: "0.45rem",
  display: "block",
};
const inputStyle: React.CSSProperties = {
  width: "100%",
  background: "#0e0e0e",
  border: "1px solid #1e1e1e",
  color: "#f0e8d8",
  padding: "0.75rem 0.9rem",
  fontFamily: "Georgia, serif",
  fontSize: "0.95rem",
  boxSizing: "border-box",
};
const privateBox: React.CSSProperties = {
  marginTop: "2rem",
  background: "#0a0a0a",
  border: "1px solid #181818",
  borderRadius: "0",
};
const submitBtn: React.CSSProperties = {
  marginTop: "2rem",
  background: "#1a2a1a",
  border: "1px solid #2a4a2a",
  color: "#4a9a4a",
  padding: "0.95rem 2rem",
  fontFamily: "monospace",
  fontSize: "0.78rem",
  letterSpacing: "0.15em",
  textTransform: "uppercase",
  width: "100%",
};
const primaryBtn: React.CSSProperties = {
  background: "#1a2a1a",
  border: "1px solid #2a4a2a",
  color: "#4a9a4a",
  padding: "0.75rem 1.75rem",
  textDecoration: "none",
  fontFamily: "monospace",
  fontSize: "0.75rem",
  letterSpacing: "0.15em",
  textTransform: "uppercase",
  display: "inline-block",
};
const errorStyle: React.CSSProperties = {
  color: "#e44",
  fontSize: "0.78rem",
  fontFamily: "monospace",
  background: "#1a0a0a",
  border: "1px solid #2a1010",
  padding: "0.75rem 1rem",
  marginBottom: "1.5rem",
};
