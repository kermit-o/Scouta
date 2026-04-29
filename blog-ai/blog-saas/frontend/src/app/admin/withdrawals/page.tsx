"use client";
import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import {
  ArrowLeft, Check, X, Loader2, Banknote, Building2, Wallet as WalletIcon,
  ShieldAlert, type LucideIcon,
} from "lucide-react";

const API = "/api/proxy/api/v1";

type Status = "pending" | "completed" | "failed" | "processing";

interface UserInfo {
  id: number;
  username: string | null;
  email: string | null;
  display_name: string | null;
}

interface Withdrawal {
  id: number;
  user: UserInfo;
  amount_coins: number;
  amount_cents: number;
  amount_usd: string;
  status: Status;
  method: "paypal" | "bank" | null;
  payout_details: string | null;
  failure_reason: string | null;
  external_reference: string | null;
  created_at: string;
  completed_at: string | null;
}

const FILTERS: { key: Status | "all"; label: string }[] = [
  { key: "pending", label: "Pending" },
  { key: "completed", label: "Completed" },
  { key: "failed", label: "Failed" },
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

function methodIcon(method: string | null): LucideIcon {
  if (method === "paypal") return WalletIcon;
  if (method === "bank") return Building2;
  return Banknote;
}

function statusColor(status: Status): string {
  if (status === "pending") return "#c8a96e";
  if (status === "completed") return "#4a9a4a";
  if (status === "failed") return "#9a4a4a";
  return "#666";
}

export default function AdminWithdrawalsPage() {
  const { token, isLoaded } = useAuth();
  const [filter, setFilter] = useState<Status | "all">("pending");
  const [rows, setRows] = useState<Withdrawal[]>([]);
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
        ? `${API}/coins/admin/withdrawals?limit=200`
        : `${API}/coins/admin/withdrawals?status=${filter}&limit=200`;
      const r = await fetch(url, { headers: { Authorization: `Bearer ${t}` } });
      if (r.status === 403) {
        setForbidden(true);
        setLoading(false);
        return;
      }
      if (!r.ok) {
        setError(`Failed to load (${r.status})`);
        setLoading(false);
        return;
      }
      setRows(await r.json());
    } catch {
      setError("Network error.");
    }
    setLoading(false);
  }, [token, filter]);

  useEffect(() => {
    if (!isLoaded) return;
    load();
  }, [isLoaded, load]);

  async function approve(w: Withdrawal) {
    const reference = prompt(
      `Approve ${w.amount_coins} coins (${w.amount_usd}) to ${w.user.username || w.user.email}?\n\nOptional: external reference (PayPal txn id, bank ref):`,
      ""
    );
    if (reference === null) return;
    setActingOn(w.id);
    const t = token || localStorage.getItem("token");
    try {
      const r = await fetch(`${API}/coins/admin/withdrawals/${w.id}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
        body: JSON.stringify({ reference: reference.trim() || undefined }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        alert(`Failed: ${d.detail || r.status}`);
      } else {
        setRows((prev) => prev.map((x) => x.id === w.id ? { ...x, status: "completed", external_reference: reference.trim() || x.external_reference, completed_at: new Date().toISOString() } : x));
      }
    } catch {
      alert("Network error.");
    }
    setActingOn(null);
  }

  async function reject(w: Withdrawal) {
    const reason = prompt(
      `Reject ${w.amount_coins} coins from ${w.user.username || w.user.email}?\n\nReason (required, will refund coins to user):`,
      ""
    );
    if (reason === null) return;
    if (!reason.trim()) { alert("Reason is required."); return; }
    setActingOn(w.id);
    const t = token || localStorage.getItem("token");
    try {
      const r = await fetch(`${API}/coins/admin/withdrawals/${w.id}/reject`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
        body: JSON.stringify({ reason: reason.trim() }),
      });
      if (!r.ok) {
        const d = await r.json().catch(() => ({}));
        alert(`Failed: ${d.detail || r.status}`);
      } else {
        setRows((prev) => prev.map((x) => x.id === w.id ? { ...x, status: "failed", failure_reason: reason.trim() } : x));
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

  const totalPending = rows.filter((r) => r.status === "pending").length;
  const totalCoinsPending = rows.filter((r) => r.status === "pending").reduce((a, r) => a + r.amount_coins, 0);

  return (
    <main style={pageStyle}>
      <div style={container}>
        <Link href="/admin" style={backLink}>
          <ArrowLeft size={12} strokeWidth={1.75} />
          <span>Admin</span>
        </Link>

        <div style={{ marginBottom: "1.5rem", paddingBottom: "1rem", borderBottom: "1px solid #1a1a1a" }}>
          <p style={eyebrow}>SCOUTA / ADMIN / WITHDRAWALS</p>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem", marginTop: "0.4rem" }}>
            <h1 style={h1}>Withdrawal queue</h1>
            {filter === "pending" && totalPending > 0 && (
              <div style={{ textAlign: "right" }}>
                <p style={{ fontSize: "0.55rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: 0 }}>RESERVED</p>
                <p style={{ fontSize: "1.2rem", fontFamily: "monospace", color: "#c8a96e", fontWeight: 700, margin: "0.2rem 0 0", lineHeight: 1 }}>
                  {totalCoinsPending.toLocaleString()} <span style={{ fontSize: "0.6rem", color: "#444", letterSpacing: "0.15em" }}>COINS</span>
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
                  padding: "0.4rem 0.9rem",
                  cursor: "pointer",
                  fontSize: "0.6rem",
                  letterSpacing: "0.15em",
                  textTransform: "uppercase",
                  fontFamily: "monospace",
                }}
              >
                {f.label}
              </button>
            );
          })}
        </div>

        {error && <div style={errorBox}>{error}</div>}

        {loading && (
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.78rem" }}>Loading...</p>
        )}

        {!loading && rows.length === 0 && (
          <div style={{ padding: "3rem 1.5rem", textAlign: "center", border: "1px dashed #1a1a1a", background: "#0a0a0a" }}>
            <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.95rem", margin: "0 0 0.4rem" }}>
              Nothing here.
            </p>
            <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em" }}>
              {filter === "pending" ? "No pending withdrawals." : `No ${filter} withdrawals.`}
            </p>
          </div>
        )}

        {!loading && rows.map((w) => {
          const Icon = methodIcon(w.method);
          const isActing = actingOn === w.id;
          return (
            <div key={w.id} style={row}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: "0.85rem" }}>
                {/* Method icon */}
                <div style={{
                  width: 36, height: 36, flexShrink: 0,
                  background: "#0d0d0d", border: "1px solid #1a1a1a",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  color: "#888",
                }}>
                  <Icon size={16} strokeWidth={1.5} />
                </div>

                {/* Body */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "baseline", gap: "0.6rem", flexWrap: "wrap" }}>
                    <span style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.95rem" }}>
                      {w.user.display_name || w.user.username || w.user.email || `user #${w.user.id}`}
                    </span>
                    {w.user.username && (
                      <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.6rem", letterSpacing: "0.05em" }}>
                        @{w.user.username}
                      </span>
                    )}
                    <span style={{
                      marginLeft: "auto",
                      fontSize: "0.55rem", letterSpacing: "0.2em", textTransform: "uppercase",
                      color: statusColor(w.status), fontFamily: "monospace",
                      border: `1px solid ${statusColor(w.status)}33`,
                      padding: "0.1rem 0.45rem",
                    }}>
                      {w.status}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "baseline", gap: "0.6rem", marginTop: "0.4rem", flexWrap: "wrap" }}>
                    <span style={{ color: "#c8a96e", fontFamily: "monospace", fontSize: "1.1rem", fontWeight: 700 }}>
                      {w.amount_coins.toLocaleString()}
                    </span>
                    <span style={{ color: "#666", fontFamily: "monospace", fontSize: "0.65rem", letterSpacing: "0.1em" }}>COINS</span>
                    <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem" }}>≈ {w.amount_usd}</span>
                    <span style={{ marginLeft: "auto", color: "#444", fontFamily: "monospace", fontSize: "0.6rem", letterSpacing: "0.05em" }}>
                      {timeAgo(w.created_at)} ago
                    </span>
                  </div>

                  {w.payout_details && (
                    <div style={{ marginTop: "0.6rem", padding: "0.55rem 0.7rem", background: "#0a0a0a", border: "1px solid #141414" }}>
                      <p style={{ fontSize: "0.55rem", letterSpacing: "0.2em", color: "#555", fontFamily: "monospace", margin: "0 0 0.25rem" }}>
                        {w.method === "paypal" ? "PAYPAL EMAIL" : "BANK DETAILS"}
                      </p>
                      <pre style={{
                        margin: 0, color: "#9a8a6a", fontSize: "0.72rem",
                        fontFamily: "monospace", whiteSpace: "pre-wrap", wordBreak: "break-all",
                      }}>{w.payout_details}</pre>
                    </div>
                  )}

                  {w.status === "completed" && w.external_reference && (
                    <p style={{ marginTop: "0.5rem", fontSize: "0.65rem", color: "#4a9a4a", fontFamily: "monospace", letterSpacing: "0.05em" }}>
                      Ref: {w.external_reference}
                    </p>
                  )}
                  {w.status === "failed" && w.failure_reason && (
                    <p style={{ marginTop: "0.5rem", fontSize: "0.65rem", color: "#9a6a4a", fontFamily: "monospace", letterSpacing: "0.05em" }}>
                      Reason: {w.failure_reason}
                    </p>
                  )}

                  {w.status === "pending" && (
                    <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.85rem" }}>
                      <button
                        onClick={() => approve(w)}
                        disabled={isActing}
                        style={{
                          ...actionBtn,
                          background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
                          opacity: isActing ? 0.5 : 1, cursor: isActing ? "not-allowed" : "pointer",
                        }}
                      >
                        {isActing ? <Loader2 size={12} strokeWidth={2} style={{ animation: "spin 1s linear infinite" }} /> : <Check size={12} strokeWidth={2} />}
                        <span>Approve</span>
                      </button>
                      <button
                        onClick={() => reject(w)}
                        disabled={isActing}
                        style={{
                          ...actionBtn,
                          background: "transparent", border: "1px solid #2a1a1a", color: "#9a4a4a",
                          opacity: isActing ? 0.5 : 1, cursor: isActing ? "not-allowed" : "pointer",
                        }}
                      >
                        <X size={12} strokeWidth={2} />
                        <span>Reject</span>
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
  display: "inline-flex", alignItems: "center", gap: "0.4rem",
  marginBottom: "1.5rem",
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
  letterSpacing: "0.15em", textTransform: "uppercase",
  fontFamily: "monospace",
};
