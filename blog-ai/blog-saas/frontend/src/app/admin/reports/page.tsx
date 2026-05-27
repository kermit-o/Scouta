"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { ArrowLeft, Check, Eye, X, Loader2, Flag, ShieldAlert } from "lucide-react";

const API = "/api/proxy/api/v1";

type Status = "open" | "reviewed" | "actioned" | "dismissed";

interface Report {
  id: number;
  reporter_user_id: number;
  target_type: string;
  target_id: string;
  reason: string;
  details: string | null;
  status: Status;
  created_at: string;
}

const FILTERS: { key: Status | "all"; label: string }[] = [
  { key: "open", label: "Open" },
  { key: "reviewed", label: "Reviewed" },
  { key: "actioned", label: "Actioned" },
  { key: "dismissed", label: "Dismissed" },
  { key: "all", label: "All" },
];

function timeAgo(d: string | null) {
  if (!d) return "";
  const m = Math.floor((Date.now() - new Date(d).getTime()) / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

function statusColor(status: Status): string {
  if (status === "open") return "#c8a96e";
  if (status === "actioned") return "#9a4a4a";
  if (status === "reviewed") return "#4a7a9a";
  return "#666";
}

// Link to the reported entity so a moderator can inspect it in one click.
function targetLink(r: Report): string | null {
  switch (r.target_type) {
    case "post": return `/posts/${r.target_id}`;
    case "user": return `/u/${r.target_id}`;
    case "live": return `/live/${r.target_id}`;
    default: return null;
  }
}

export default function AdminReportsPage() {
  const { token, isLoaded } = useAuth();
  const [filter, setFilter] = useState<Status | "all">("open");
  const [rows, setRows] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actingOn, setActingOn] = useState<number | null>(null);
  const [forbidden, setForbidden] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    const t = token || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
    if (!t) { setLoading(false); return; }
    try {
      const url = filter === "all"
        ? `${API}/admin/reports?status=&limit=200`
        : `${API}/admin/reports?status=${filter}&limit=200`;
      const r = await fetch(url, { headers: { Authorization: `Bearer ${t}` } });
      if (r.status === 403) { setForbidden(true); setLoading(false); return; }
      if (!r.ok) { setError(`Failed to load (${r.status})`); setLoading(false); return; }
      const d = await r.json();
      setRows(d.reports || []);
    } catch {
      setError("Network error.");
    }
    setLoading(false);
  }, [token, filter]);

  useEffect(() => {
    if (!isLoaded) return;
    load();
  }, [isLoaded, load]);

  async function resolve(rep: Report, status: Status) {
    setActingOn(rep.id);
    const t = token || localStorage.getItem("token");
    try {
      const r = await fetch(`${API}/admin/reports/${rep.id}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
        body: JSON.stringify({ status }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        alert(`Failed: ${d.detail || r.status}`);
      } else {
        setRows((prev) => prev.map((x) => x.id === rep.id ? { ...x, status } : x));
      }
    } catch {
      alert("Network error.");
    }
    setActingOn(null);
  }

  if (forbidden) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <div style={{ color: "#9a4a4a", display: "flex", justifyContent: "center", marginBottom: "1rem" }}>
            <ShieldAlert size={48} strokeWidth={1.25} />
          </div>
          <h1 style={h1}>Superuser only.</h1>
          <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.9rem", marginTop: "0.5rem" }}>
            You don't have permission to view this page.
          </p>
        </div>
      </main>
    );
  }

  const totalOpen = rows.filter((r) => r.status === "open").length;

  return (
    <main style={pageStyle}>
      <div style={container}>
        <Link href="/admin" style={backLink}>
          <ArrowLeft size={12} strokeWidth={1.75} />
          <span>Admin</span>
        </Link>

        <div style={{ marginBottom: "1.5rem", paddingBottom: "1rem", borderBottom: "1px solid #1a1a1a" }}>
          <p style={eyebrow}>SCOUTA / ADMIN / REPORTS</p>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem", marginTop: "0.4rem" }}>
            <h1 style={h1}>Moderation queue</h1>
            {filter === "open" && totalOpen > 0 && (
              <div style={{ textAlign: "right" }}>
                <p style={{ fontSize: "0.55rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: 0 }}>OPEN</p>
                <p style={{ fontSize: "1.2rem", fontFamily: "monospace", color: "#c8a96e", fontWeight: 700, margin: "0.2rem 0 0", lineHeight: 1 }}>
                  {totalOpen}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Filter pills */}
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
          {FILTERS.map((f) => {
            const active = filter === f.key;
            return (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                style={{
                  background: active ? "#1a2a1a" : "transparent",
                  border: `1px solid ${active ? "#2a4a2a" : "#1a1a1a"}`,
                  color: active ? "#4a9a4a" : "#666",
                  padding: "0.4rem 0.9rem", cursor: "pointer",
                  fontSize: "0.6rem", letterSpacing: "0.15em", textTransform: "uppercase", fontFamily: "monospace",
                }}
              >
                {f.label}
              </button>
            );
          })}
        </div>

        {error && <div style={errorBox}>{error}</div>}
        {loading && <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.78rem" }}>Loading...</p>}

        {!loading && rows.length === 0 && (
          <div style={{ padding: "3rem 1.5rem", textAlign: "center", border: "1px dashed #1a1a1a", background: "#0a0a0a" }}>
            <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.95rem", margin: "0 0 0.4rem" }}>Nothing here.</p>
            <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em" }}>
              {filter === "open" ? "No open reports." : `No ${filter} reports.`}
            </p>
          </div>
        )}

        {!loading && rows.map((rep) => {
          const isActing = actingOn === rep.id;
          const link = targetLink(rep);
          return (
            <div key={rep.id} style={row}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.85rem" }}>
                <div style={{
                  width: 36, height: 36, flexShrink: 0,
                  background: "#0d0d0d", border: "1px solid #1a1a1a",
                  display: "flex", alignItems: "center", justifyContent: "center", color: "#888",
                }}>
                  <Flag size={16} strokeWidth={1.5} />
                </div>

                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "baseline", gap: "0.6rem", flexWrap: "wrap" }}>
                    <span style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.95rem", textTransform: "capitalize" }}>
                      {rep.target_type}
                    </span>
                    <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.6rem", letterSpacing: "0.05em" }}>
                      #{rep.target_id}
                    </span>
                    {link && (
                      <Link href={link} target="_blank" style={{ color: "#4a7a9a", fontFamily: "monospace", fontSize: "0.6rem", textDecoration: "none" }}>
                        inspect →
                      </Link>
                    )}
                    <span style={{
                      marginLeft: "auto",
                      fontSize: "0.55rem", letterSpacing: "0.2em", textTransform: "uppercase",
                      color: statusColor(rep.status), fontFamily: "monospace",
                      border: `1px solid ${statusColor(rep.status)}33`, padding: "0.1rem 0.45rem",
                    }}>
                      {rep.status}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "baseline", gap: "0.6rem", marginTop: "0.4rem", flexWrap: "wrap" }}>
                    <span style={{ color: "#c8a96e", fontFamily: "monospace", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                      {rep.reason}
                    </span>
                    <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.6rem" }}>
                      by user #{rep.reporter_user_id}
                    </span>
                    <span style={{ marginLeft: "auto", color: "#444", fontFamily: "monospace", fontSize: "0.6rem", letterSpacing: "0.05em" }}>
                      {timeAgo(rep.created_at)} ago
                    </span>
                  </div>

                  {rep.details && (
                    <div style={{ marginTop: "0.6rem", padding: "0.55rem 0.7rem", background: "#0a0a0a", border: "1px solid #141414" }}>
                      <pre style={{ margin: 0, color: "#9a8a6a", fontSize: "0.72rem", fontFamily: "monospace", whiteSpace: "pre-wrap", wordBreak: "break-word" }}>{rep.details}</pre>
                    </div>
                  )}

                  {rep.status === "open" && (
                    <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.85rem", flexWrap: "wrap" }}>
                      <button onClick={() => resolve(rep, "actioned")} disabled={isActing}
                        style={{ ...actionBtn, background: "#2a1010", border: "1px solid #4a2020", color: "#c87a7a", opacity: isActing ? 0.5 : 1, cursor: isActing ? "not-allowed" : "pointer" }}>
                        {isActing ? <Loader2 size={12} strokeWidth={2} style={{ animation: "spin 1s linear infinite" }} /> : <Check size={12} strokeWidth={2} />}
                        <span>Actioned</span>
                      </button>
                      <button onClick={() => resolve(rep, "reviewed")} disabled={isActing}
                        style={{ ...actionBtn, background: "transparent", border: "1px solid #1a3a4a", color: "#4a7a9a", opacity: isActing ? 0.5 : 1, cursor: isActing ? "not-allowed" : "pointer" }}>
                        <Eye size={12} strokeWidth={2} />
                        <span>Reviewed</span>
                      </button>
                      <button onClick={() => resolve(rep, "dismissed")} disabled={isActing}
                        style={{ ...actionBtn, background: "transparent", border: "1px solid #2a2a2a", color: "#777", opacity: isActing ? 0.5 : 1, cursor: isActing ? "not-allowed" : "pointer" }}>
                        <X size={12} strokeWidth={2} />
                        <span>Dismiss</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </main>
  );
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#e8e0d0" };
const container: React.CSSProperties = { maxWidth: "880px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" };
const backLink: React.CSSProperties = {
  color: "#4a7a9a", fontSize: "0.7rem", fontFamily: "monospace",
  textDecoration: "none", letterSpacing: "0.1em",
  display: "inline-flex", alignItems: "center", gap: "0.4rem", marginBottom: "1.5rem",
};
const eyebrow: React.CSSProperties = {
  fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a",
  textTransform: "uppercase", fontFamily: "monospace", margin: 0,
};
const h1: React.CSSProperties = {
  fontSize: "clamp(1.5rem, 4vw, 2rem)", fontWeight: 400,
  fontFamily: "Georgia, serif", color: "#f0e8d8", margin: 0,
};
const errorBox: React.CSSProperties = {
  background: "#1a0a0a", border: "1px solid #2a1010",
  color: "#9a4a4a", padding: "0.6rem 0.85rem",
  fontSize: "0.75rem", fontFamily: "monospace", marginBottom: "1.25rem",
};
const row: React.CSSProperties = {
  background: "#0d0d0d", border: "1px solid #1a1a1a",
  padding: "1rem 1.1rem", marginBottom: "0.75rem",
};
const actionBtn: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: "0.4rem",
  padding: "0.45rem 0.85rem", fontSize: "0.65rem",
  letterSpacing: "0.15em", textTransform: "uppercase", fontFamily: "monospace",
};
