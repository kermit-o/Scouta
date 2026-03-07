"use client";
import { useState } from "react";

export default function EmailCapture({ source = "home" }: { source?: string }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "done" | "error">("idle");

  async function handleSubmit() {
    if (!email || !email.includes("@")) return;
    setStatus("loading");
    try {
      // Guardamos en localStorage como fallback + enviamos al backend si existe
      const existing = JSON.parse(localStorage.getItem("scouta_emails") || "[]");
      existing.push({ email, source, ts: Date.now() });
      localStorage.setItem("scouta_emails", JSON.stringify(existing));
      
      // Intentar enviar al backend
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app"}/api/v1/waitlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, source }),
      }).catch(() => {}); // silencioso si no existe el endpoint aún
      
      setStatus("done");
    } catch {
      setStatus("done"); // mostrar éxito igual
    }
  }

  if (status === "done") return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <span style={{ fontSize: "0.7rem", color: "#4a9a4a", fontFamily: "monospace", letterSpacing: "0.1em" }}>
        ✓ You&apos;re on the list
      </span>
    </div>
  );

  return (
    <div style={{ display: "flex", gap: "0", maxWidth: "420px", width: "100%" }}>
      <input
        type="email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        onKeyDown={e => e.key === "Enter" && handleSubmit()}
        placeholder="your@email.com"
        style={{
          flex: 1, background: "#0d0d0d", border: "1px solid #222",
          borderRight: "none", color: "#f0e8d8", padding: "0.75rem 1rem",
          fontSize: "0.8rem", fontFamily: "monospace", outline: "none",
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={status === "loading"}
        style={{
          background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
          padding: "0.75rem 1.25rem", fontSize: "0.7rem", letterSpacing: "0.15em",
          textTransform: "uppercase", fontFamily: "monospace", cursor: "pointer",
          whiteSpace: "nowrap",
        }}
      >
        {status === "loading" ? "..." : "Get Weekly Debates"}
      </button>
    </div>
  );
}
