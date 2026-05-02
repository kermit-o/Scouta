"use client";
import React, { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import {
  Coins, Wallet as WalletIcon, ArrowDownToLine, ArrowUpFromLine,
  Plus, Banknote, Gift, ShoppingCart, ArrowRightLeft, CheckCircle2, X,
  type LucideIcon,
} from "lucide-react";

interface Balance {
  balance: number;
  withdrawable_balance: number;
  lifetime_earned: number;
  lifetime_spent: number;
}

interface Transaction {
  id: number;
  amount: number;
  type: string;
  description: string;
  created_at: string;
}

const API = "/api/proxy/api/v1";

// Next.js 15+ requires useSearchParams() to live inside a <Suspense> boundary
// or the page can't be statically prerendered. Wrap the content in Suspense
// at the page boundary; the inner component is the real wallet page.
export default function WalletPage() {
  return (
    <Suspense fallback={
      <main style={pageStyle}>
        <div style={container}>
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.78rem" }}>Loading...</p>
        </div>
      </main>
    }>
      <WalletContent />
    </Suspense>
  );
}

function WalletContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { token, user, isLoaded } = useAuth();
  const [balance, setBalance] = useState<Balance | null>(null);
  const [txs, setTxs] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [purchaseBanner, setPurchaseBanner] = useState<{ coins: number } | null>(null);

  // Detect ?purchase=success&coins=N from Stripe Checkout success_url redirect.
  // Webhook may take 1-3s after redirect — poll balance for up to 15s if banner is visible.
  useEffect(() => {
    if (!searchParams) return;
    const purchase = searchParams.get("purchase");
    const coins = parseInt(searchParams.get("coins") || "0", 10);
    if (purchase === "success" && coins > 0) {
      setPurchaseBanner({ coins });
    }
  }, [searchParams]);

  const loadBalance = React.useCallback(async () => {
    if (!token) return;
    const headers = { Authorization: `Bearer ${token}` };
    const [bal, txsRes] = await Promise.all([
      fetch(`${API}/coins/balance`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${API}/coins/transactions?limit=25`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
    ]);
    if (bal) setBalance(bal);
    if (txsRes && Array.isArray(txsRes.transactions)) setTxs(txsRes.transactions);
  }, [token]);

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    loadBalance().then(() => setLoading(false));
  }, [token, loadBalance]);

  // Poll balance for up to 15s after a successful purchase, in case the
  // Stripe webhook hasn't credited yet by the time the redirect lands.
  useEffect(() => {
    if (!purchaseBanner || !token) return;
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      await loadBalance();
      if (attempts >= 8) clearInterval(interval); // ~16s
    }, 2000);
    return () => clearInterval(interval);
  }, [purchaseBanner, token, loadBalance]);

  function dismissBanner() {
    setPurchaseBanner(null);
    // Clear the query params so refresh doesn't re-show the banner.
    router.replace("/wallet");
  }

  if (isLoaded && !token) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, textAlign: "center", paddingTop: "5rem" }}>
          <p style={{ color: "#888", marginBottom: "1rem", fontFamily: "monospace", fontSize: "0.85rem" }}>
            Log in to see your wallet.
          </p>
          <Link href="/login" style={primaryBtn}>Log in</Link>
        </div>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <div style={container}>
        {/* Purchase success banner */}
        {purchaseBanner && (
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "0.85rem",
            background: "#0e1f0e",
            border: "1px solid #1f3a1f",
            padding: "0.85rem 1.1rem",
            marginBottom: "1.5rem",
          }}>
            <div style={{ color: "#4a9a4a", display: "flex", flexShrink: 0 }}>
              <CheckCircle2 size={20} strokeWidth={1.5} />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <p style={{
                color: "#9ad29a",
                fontFamily: "Georgia, serif",
                fontSize: "0.9rem",
                margin: 0,
              }}>
                Payment received. {purchaseBanner.coins.toLocaleString()} coins added to your wallet.
              </p>
              <p style={{
                color: "#4a7a4a",
                fontFamily: "monospace",
                fontSize: "0.6rem",
                letterSpacing: "0.05em",
                margin: "0.25rem 0 0",
              }}>
                If your balance hasn't updated yet, refresh in a few seconds.
              </p>
            </div>
            <button
              onClick={dismissBanner}
              aria-label="Dismiss"
              style={{
                background: "none", border: "none",
                color: "#4a7a4a", cursor: "pointer",
                display: "flex", padding: "0.25rem",
              }}
            >
              <X size={16} strokeWidth={1.5} />
            </button>
          </div>
        )}

        {/* Header */}
        <div style={{ marginBottom: "2rem", paddingBottom: "1.25rem", borderBottom: "1px solid #141414" }}>
          <p style={eyebrow}>SCOUTA / WALLET</p>
          <h1 style={h1}>Wallet</h1>
          <p style={{ color: "#555", fontSize: "0.78rem", fontFamily: "monospace", marginTop: "0.5rem" }}>
            @{user?.username}
          </p>
        </div>

        {loading && (
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.78rem" }}>Loading...</p>
        )}

        {!loading && (
          <>
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: "1rem",
              marginBottom: "2rem",
            }}>
              <Card icon={Coins} label="BALANCE" value={balance?.balance ?? 0} accent="#c8a96e" suffix="coins" big />
              <Card icon={WalletIcon} label="WITHDRAWABLE" value={balance?.withdrawable_balance ?? 0} accent="#4a9a4a" suffix="coins" />
              <Card icon={ArrowDownToLine} label="LIFETIME EARNED" value={balance?.lifetime_earned ?? 0} accent="#4a7a9a" suffix="coins" />
              <Card icon={ArrowUpFromLine} label="LIFETIME SPENT" value={balance?.lifetime_spent ?? 0} accent="#666" suffix="coins" />
            </div>

            <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "2.5rem" }}>
              <Link href="/wallet/buy" style={ctaPrimary}>
                <Plus size={14} strokeWidth={1.75} />
                Buy coins
              </Link>
              <Link href="/wallet/withdraw" style={ctaSecondary}>
                <Banknote size={14} strokeWidth={1.5} />
                Withdraw earnings
              </Link>
            </div>

            <div style={{ paddingBottom: "1rem", borderBottom: "1px solid #141414", marginBottom: "1rem" }}>
              <p style={eyebrow}>RECENT ACTIVITY</p>
              <h2 style={{ fontSize: "1.5rem", fontWeight: 400, fontFamily: "Georgia, serif", margin: "0.4rem 0 0", color: "#f0e8d8" }}>
                Last {txs.length} transactions
              </h2>
            </div>

            {txs.length === 0 ? (
              <div style={emptyBox}>
                <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.85rem", marginBottom: "0.4rem" }}>No transactions yet.</p>
                <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em" }}>
                  Buy coins or send a gift to see activity here.
                </p>
              </div>
            ) : (
              <div>
                {txs.map((t) => {
                  const Icon = txIcon(t.type);
                  return (
                    <div key={t.id} style={txRow}>
                      <div style={{
                        width: 32, height: 32, flexShrink: 0,
                        borderRadius: "50%", background: "#0d0d0d",
                        border: "1px solid #1a1a1a",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        color: t.amount >= 0 ? "#4a9a4a88" : "#9a6a4a88",
                      }}>
                        <Icon size={14} strokeWidth={1.5} />
                      </div>
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ color: "#e0d0b0", fontSize: "0.82rem", fontFamily: "Georgia, serif", marginBottom: "0.2rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {t.description || labelType(t.type)}
                        </div>
                        <div style={{ color: "#444", fontSize: "0.6rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>
                          {labelType(t.type)} · {formatDate(t.created_at)}
                        </div>
                      </div>
                      <div style={{
                        fontSize: "0.95rem", fontFamily: "monospace", fontWeight: 700,
                        color: t.amount >= 0 ? "#4a9a4a" : "#9a6a4a",
                        whiteSpace: "nowrap", marginLeft: "1rem",
                      }}>
                        {t.amount >= 0 ? "+" : ""}{t.amount}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}

function Card({ icon: Icon, label, value, accent, suffix, big }: { icon: LucideIcon; label: string; value: number; accent: string; suffix?: string; big?: boolean }) {
  return (
    <div style={{
      background: "#0d0d0d", border: "1px solid #1a1a1a",
      padding: "1.25rem 1.25rem 1.1rem",
      position: "relative",
    }}>
      <div style={{ position: "absolute", top: "1rem", right: "1rem", color: `${accent}66` }}>
        <Icon size={18} strokeWidth={1.5} />
      </div>
      <p style={{ fontSize: "0.55rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: "0 0 0.6rem" }}>{label}</p>
      <p style={{
        fontSize: big ? "2.25rem" : "1.6rem", fontFamily: "monospace",
        color: accent, margin: 0, lineHeight: 1, fontWeight: 600,
      }}>
        {value.toLocaleString()}
      </p>
      {suffix && (
        <p style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", letterSpacing: "0.15em", margin: "0.3rem 0 0" }}>
          {suffix.toUpperCase()}
        </p>
      )}
    </div>
  );
}

function txIcon(type: string): LucideIcon {
  switch (type) {
    case "purchase": return ShoppingCart;
    case "gift_sent":
    case "gift_received": return Gift;
    case "room_entry": return Banknote;
    case "withdrawal": return Banknote;
    case "subscription": return ArrowRightLeft;
    default: return ArrowRightLeft;
  }
}

function labelType(t: string): string {
  switch (t) {
    case "purchase": return "Purchase";
    case "gift_sent": return "Gift sent";
    case "gift_received": return "Gift received";
    case "room_entry": return "Paid entry";
    case "withdrawal": return "Withdrawal";
    case "subscription": return "Subscription";
    default: return t.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  }
}

function formatDate(s: string): string {
  try {
    const d = new Date(s);
    const now = Date.now();
    const diff = now - d.getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return "just now";
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return d.toLocaleDateString();
  } catch {
    return "";
  }
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#f0e8d8" };
const container: React.CSSProperties = { maxWidth: "880px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" };
const eyebrow: React.CSSProperties = { fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: 0 };
const h1: React.CSSProperties = { fontSize: "clamp(1.6rem, 4vw, 2.5rem)", fontWeight: 400, fontFamily: "Georgia, serif", margin: "0.4rem 0 0" };
const ctaPrimary: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: "0.45rem",
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.7rem 1.4rem", textDecoration: "none",
  fontSize: "0.72rem", letterSpacing: "0.15em", textTransform: "uppercase" as const,
  fontFamily: "monospace",
};
const ctaSecondary: React.CSSProperties = {
  display: "inline-flex", alignItems: "center", gap: "0.45rem",
  background: "transparent", border: "1px solid #2a2a2a", color: "#888",
  padding: "0.7rem 1.4rem", textDecoration: "none",
  fontSize: "0.72rem", letterSpacing: "0.15em", textTransform: "uppercase" as const,
  fontFamily: "monospace",
};
const primaryBtn: React.CSSProperties = {
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.75rem 1.75rem", textDecoration: "none",
  fontFamily: "monospace", fontSize: "0.75rem", letterSpacing: "0.15em",
  textTransform: "uppercase" as const, display: "inline-block",
};
const txRow: React.CSSProperties = {
  display: "flex", alignItems: "center", gap: "0.85rem",
  padding: "0.75rem 0", borderBottom: "1px solid #141414",
};
const emptyBox: React.CSSProperties = {
  textAlign: "center", padding: "3rem 1.5rem",
  border: "1px dashed #1a1a1a", background: "#0a0a0a",
};
