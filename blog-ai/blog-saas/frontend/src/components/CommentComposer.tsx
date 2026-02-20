"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { postComment } from "@/lib/api";

interface CommentComposerProps {
  orgId: number;
  postId: number;
  parentCommentId?: number;
  onSuccess?: () => void;
  placeholder?: string;
  compact?: boolean;
}

export function CommentComposer({
  orgId,
  postId,
  parentCommentId,
  onSuccess,
  placeholder = "Join the debate...",
  compact = false,
}: CommentComposerProps) {
  const { token, logout } = useAuth();
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!token) {
    const next = typeof window !== "undefined" ? encodeURIComponent(window.location.pathname) : "";
    return (
      <div style={{
        padding: compact ? "0.75rem 1rem" : "1rem 1.25rem",
        background: "#0d0d0d",
        border: "1px solid #1e1e1e",
        borderRadius: "4px",
        fontSize: "0.75rem",
        color: "#555",
        fontFamily: "monospace",
        textAlign: "center",
      }}>
        <a href={`/login?next=${next}`} style={{ color: "#4a7a9a", textDecoration: "none" }}>Login</a>
        {" or "}
        <a href={`/register?next=${next}`} style={{ color: "#4a7a9a", textDecoration: "none" }}>register</a>
        {" to join the debate"}
      </div>
    );
  }

  async function handleSubmit() {
    if (!body.trim() || !token) return;
    setLoading(true);
    setError("");
    const result = await postComment(orgId, postId, body.trim(), token, parentCommentId);
    setLoading(false);
    if (!result) {
      setError("Failed to post comment");
      return;
    }
    setBody("");
    onSuccess?.();
  }

  return (
    <div style={{ marginBottom: compact ? "0.75rem" : "1.5rem" }}>
      <textarea
        value={body}
        onChange={e => setBody(e.target.value)}
        placeholder={placeholder}
        rows={compact ? 2 : 3}
        style={{
          width: "100%",
          background: "#0d0d0d",
          border: "1px solid #2a2a2a",
          borderRadius: "4px",
          color: "#e8e0d0",
          padding: "0.75rem 1rem",
          fontSize: "0.85rem",
          fontFamily: "'Georgia', serif",
          lineHeight: 1.6,
          resize: "vertical",
          outline: "none",
          boxSizing: "border-box",
        }}
        onFocus={e => e.target.style.borderColor = "#3a3a3a"}
        onBlur={e => e.target.style.borderColor = "#2a2a2a"}
      />
      {error && (
        <p style={{ fontSize: "0.7rem", color: "#9a4a4a", margin: "0.25rem 0", fontFamily: "monospace" }}>
          {error}
        </p>
      )}
      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "0.5rem" }}>
        <button
          onClick={handleSubmit}
          disabled={loading || !body.trim()}
          style={{
            background: loading || !body.trim() ? "#111" : "#1a2a1a",
            border: "1px solid #2a4a2a",
            color: loading || !body.trim() ? "#333" : "#4a9a4a",
            padding: "0.35rem 0.75rem",
            cursor: loading || !body.trim() ? "not-allowed" : "pointer",
            fontSize: "0.7rem",
            fontFamily: "monospace",
            letterSpacing: "0.1em",
            borderRadius: "2px",
          }}
        >
          {loading ? "Posting..." : "→ Post"}
        </button>
      </div>
    </div>
  );
}
