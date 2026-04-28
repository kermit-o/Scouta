"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = "/api/proxy/api/v1";

interface Balance {
  balance: number;
  withdrawable_balance: number;
  lifetime_earned: number;
}

const MIN_WITHDRAWAL = 500; // coins
const PROCESSING_DAYS = "5-7 business days";

export default function WithdrawPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [loading, setLoading] = useState(true);

  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState<"bank" | "paypal">("paypal");
  const [details, setDetails] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const t = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    setToken(t);
    if (!t) { setLoading(false); return; }
    fetch(`${API}/coins/balance`, { headers: { Authorization: `Bearer ${t}` } })
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => { if (d) setBalance(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function submit() {
    if (submitting) return;
    setError("");
    const amt = parseInt(amount, 10);
    if (!amt || amt <= 0) { setError("Enter a valid amount."); return; }
    if (amt < MIN_WITHDRAWAL) { setError(`Minimum withdrawal is ${MIN_WITHDRAWAL} coins.`); return; }
    if (balance && amt > balance.withdrawable_balance) {
      setError("Amount exceeds your withdrawable balance.");
      return;
    }
    if (!details.trim()) {
      setError(method === "paypal" ? "Provide your PayPal email." : "Provide bank account details (IBAN, SWIFT/BIC, account holder).");
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch(`${API}/coins/withdraw`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ amount: amt, method, payout_details: details.trim() }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        // 404 = endpoint not implemented yet — fall back to mailto
        if (res.status === 404) {
          const subject = encodeURIComponent("Withdrawal request");
          const body = encodeURIComponent(
            `Amount: ${amt} coins\nMethod: ${method}\nDetails: ${details}\n\nUser: see auth header`
          );
          window.location.href = `mailto:hello@scouta.co?subject=${subject}&body=${body}`;
          return;
        }
        setError(typeof data.detail === "string" ? data.detail : "Withdrawal request failed.");
        setSubmitting(false);
        return;
      }
      setSuccess(true);
    } catch {
      setError("Network error. Please try again.");
      setSubmitting(false);
    }
  }

  if (!loading && !token) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <p style={eyebrow}>SCOUTA / WALLET / WITHDRAW</p>
          <h1 style={h1}>Sign in to withdraw.</h1>
          <Link href="/login?next=/wallet/withdraw" style={primaryBtn}>Log in →</Link>
        </div>
      </main>
    );
  }

  if (success) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "4rem", textAlign: "center" }}>
          <p style={eyebrow}>SCOUTA / WALLET / WITHDRAW</p>
          <h1 style={h1}>Request received.</h1>
          <p style={{ color: "#888", fontFamily: "Georgia, serif", fontSize: "0.95rem", lineHeight: 1.6, marginBottom: "0.6rem", maxWidth: "440px", marginLeft: "auto", marginRight: "auto" }}>
            We'll process your withdrawal within {PROCESSING_DAYS}.
          </p>
          <p style={{ color: "#555", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em", marginBottom: "2rem" }}>
            You'll get an email confirmation once funds are sent.
          </p>
          <Link href="/wallet" style={primaryBtn}>Back to wallet</Link>
        </div>
      </main>
    );
  }

  const withdrawable = balance?.withdrawable_balance ?? 0;
  const enough = withdrawable >= MIN_WITHDRAWAL;

  return (
    <main style={pageStyle}>
      <div style={container}>
        <Link href="/wallet" style={backLink}>← Back to wallet</Link>
        <p style={eyebrow}>SCOUTA / WALLET / WITHDRAW</p>
        <h1 style={h1}>Withdraw earnings</h1>
        <p style={sub}>
          Cash out coins you earned from gifts and paid lives. Minimum withdrawal: {MIN_WITHDRAWAL} coins.
          Processing takes {PROCESSING_DAYS}.
        </p>

        {/* Balance */}
        <div style={statRow}>
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: "0.55rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: 0 }}>WITHDRAWABLE</p>
            <p style={{ fontSize: "1.8rem", fontFamily: "monospace", color: "#4a9a4a", fontWeight: 700, margin: "0.4rem 0 0", lineHeight: 1 }}>
              {withdrawable.toLocaleString()}
            </p>
            <p style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", letterSpacing: "0.15em", margin: "0.3rem 0 0" }}>COINS</p>
          </div>
          {balance && balance.lifetime_earned > 0 && (
            <div style={{ textAlign: "right" }}>
              <p style={{ fontSize: "0.55rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: 0 }}>LIFETIME</p>
              <p style={{ fontSize: "1.1rem", fontFamily: "monospace", color: "#888", margin: "0.4rem 0 0", lineHeight: 1 }}>
                {balance.lifetime_earned.toLocaleString()}
              </p>
              <p style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", letterSpacing: "0.15em", margin: "0.3rem 0 0" }}>EARNED</p>
            </div>
          )}
        </div>

        {!enough && !loading && (
          <div style={notEnoughBox}>
            <p style={{ color: "#9a8a6a", fontSize: "0.85rem", fontFamily: "Georgia, serif", margin: "0 0 0.4rem" }}>
              Not enough yet.
            </p>
            <p style={{ color: "#666", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em", margin: 0 }}>
              You need at least {MIN_WITHDRAWAL.toLocaleString()} coins to withdraw. Keep streaming and receiving gifts.
            </p>
          </div>
        )}

        {enough && (
          <>
            {error && <div style={errorBox}>{error}</div>}

            <Field label="AMOUNT" hint={`Available: ${withdrawable.toLocaleString()} coins`}>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))}
                placeholder={`${MIN_WITHDRAWAL}+`}
                style={inputStyle}
                min={MIN_WITHDRAWAL}
                max={withdrawable}
              />
            </Field>

            <Field label="METHOD">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
                <MethodOption value="paypal" label="PayPal" desc="To your PayPal email" active={method === "paypal"} onClick={() => setMethod("paypal")} />
                <MethodOption value="bank" label="Bank transfer" desc="IBAN / SWIFT" active={method === "bank"} onClick={() => setMethod("bank")} />
              </div>
            </Field>

            <Field
              label={method === "paypal" ? "PAYPAL EMAIL" : "BANK DETAILS"}
              hint={method === "paypal" ? "Email tied to your PayPal account." : "Account holder, IBAN, and SWIFT/BIC."}
            >
              {method === "paypal" ? (
                <input
                  type="email"
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                  placeholder="you@email.com"
                  style={inputStyle}
                />
              ) : (
                <textarea
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                  placeholder={"Account holder: Jane Doe\nIBAN: ES00 0000 0000 0000 0000 0000\nSWIFT: BANKESMM"}
                  rows={4}
                  style={{ ...inputStyle, resize: "vertical" as const, fontFamily: "monospace", fontSize: "0.78rem" }}
                />
              )}
            </Field>

            <button
              onClick={submit}
              disabled={submitting}
              style={{ ...primaryBtn, width: "100%", opacity: submitting ? 0.5 : 1, cursor: submitting ? "not-allowed" : "pointer", marginTop: "0.5rem" }}
            >
              {submitting ? "Submitting..." : "Request withdrawal →"}
            </button>

            <p style={fineprint}>
              Withdrawals are reviewed manually. Suspicious activity may delay or block payout.
              Need help? <a href="mailto:hello@scouta.co" style={{ color: "#4a7a9a" }}>hello@scouta.co</a>
            </p>
          </>
        )}
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

function MethodOption({ value, label, desc, active, onClick }: { value: string; label: string; desc: string; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: active ? "#1a2a1a" : "#0d0d0d",
        border: `1px solid ${active ? "#2a4a2a" : "#1a1a1a"}`,
        color: active ? "#4a9a4a" : "#888",
        padding: "0.85rem 1rem",
        textAlign: "left",
        fontFamily: "monospace",
        cursor: "pointer",
        fontSize: "0.78rem",
      }}
    >
      <div style={{ fontWeight: 700, letterSpacing: "0.05em" }}>{label}</div>
      <div style={{ fontSize: "0.65rem", color: active ? "#4a9a4a99" : "#555", marginTop: "0.25rem", letterSpacing: "0.05em" }}>{desc}</div>
    </button>
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
  fontSize: "clamp(1.6rem, 4vw, 2.5rem)", fontWeight: 400,
  fontFamily: "Georgia, serif", color: "#f0e8d8",
  margin: "0.4rem 0 0.6rem",
};
const sub: React.CSSProperties = {
  fontSize: "0.85rem", color: "#666",
  fontFamily: "Georgia, serif", lineHeight: 1.6,
  margin: "0 0 2rem",
};
const statRow: React.CSSProperties = {
  display: "flex", justifyContent: "space-between",
  background: "#0d0d0d", border: "1px solid #1a1a1a",
  padding: "1.25rem 1.25rem 1.1rem", marginBottom: "2rem",
};
const notEnoughBox: React.CSSProperties = {
  background: "#0a0a08", border: "1px dashed #2a2a18",
  padding: "1.25rem 1.25rem", textAlign: "center",
};
const errorBox: React.CSSProperties = {
  background: "#1a0a0a", border: "1px solid #2a1010",
  color: "#9a4a4a", padding: "0.6rem 0.85rem",
  fontSize: "0.75rem", fontFamily: "monospace",
  marginBottom: "1.25rem",
};
const labelStyle: React.CSSProperties = {
  fontSize: "0.6rem", letterSpacing: "0.2em",
  color: "#555", textTransform: "uppercase",
  display: "block", marginBottom: "0.4rem",
  fontFamily: "monospace",
};
const inputStyle: React.CSSProperties = {
  width: "100%", background: "#111", border: "1px solid #1e1e1e",
  color: "#e8e0d0", padding: "0.7rem 0.85rem",
  fontSize: "0.9rem", fontFamily: "Georgia, serif",
  outline: "none", boxSizing: "border-box",
};
const hintStyle: React.CSSProperties = {
  fontSize: "0.65rem", color: "#444",
  fontFamily: "monospace", letterSpacing: "0.05em",
  marginTop: "0.4rem", marginBottom: 0,
};
const primaryBtn: React.CSSProperties = {
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.85rem 2rem", fontSize: "0.78rem",
  fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase" as const,
  textDecoration: "none", display: "inline-block", textAlign: "center" as const,
  boxSizing: "border-box",
};
const fineprint: React.CSSProperties = {
  marginTop: "1.5rem", fontSize: "0.7rem",
  color: "#444", fontFamily: "monospace",
  textAlign: "center", letterSpacing: "0.05em", lineHeight: 1.6,
};
