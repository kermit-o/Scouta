"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ArrowRight, Coins, ShoppingCart, Sparkles, Loader2 } from "lucide-react";

const API = "/api/proxy/api/v1";

interface Package {
  id: string | number;
  name?: string;
  coins?: number;
  bonus_coins?: number;
  price_usd?: number;
  price_cents?: number;
  description?: string;
  is_popular?: boolean;
}

interface Balance {
  balance: number;
  withdrawable_balance: number;
}

function priceLabel(p: Package): string {
  const usd = p.price_usd ?? (p.price_cents ? p.price_cents / 100 : 0);
  if (usd <= 0) return "Free";
  return usd >= 1 ? `$${usd.toFixed(usd % 1 === 0 ? 0 : 2)}` : `$${usd.toFixed(2)}`;
}

function totalCoins(p: Package): number {
  return (p.coins || 0) + (p.bonus_coins || 0);
}

export default function BuyCoinsPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [packages, setPackages] = useState<Package[]>([]);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState<Package["id"] | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    const t = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    setToken(t);

    Promise.all([
      fetch(`${API}/coins/packages`).then((r) => (r.ok ? r.json() : null)).catch(() => null),
      t ? fetch(`${API}/coins/balance`, { headers: { Authorization: `Bearer ${t}` } }).then((r) => (r.ok ? r.json() : null)).catch(() => null) : Promise.resolve(null),
    ]).then(([pkgs, bal]) => {
      const list = Array.isArray(pkgs) ? pkgs : (pkgs?.packages || pkgs?.items || []);
      setPackages(list);
      if (bal) setBalance(bal);
      setLoading(false);
    });
  }, []);

  async function buy(pkg: Package) {
    if (!token) {
      router.push("/login?next=/wallet/buy");
      return;
    }
    setPurchasing(pkg.id);
    setError("");
    setSuccess("");
    try {
      const res = await fetch(`${API}/coins/purchase`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ package_id: pkg.id }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(typeof data.detail === "string" ? data.detail : "Purchase failed.");
        setPurchasing(null);
        return;
      }
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
        return;
      }
      setSuccess(`Added ${totalCoins(pkg).toLocaleString()} coins to your wallet.`);
      setTimeout(() => router.push("/wallet"), 1500);
    } catch {
      setError("Network error.");
      setPurchasing(null);
    }
  }

  if (!loading && !token) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, paddingTop: "5rem", textAlign: "center" }}>
          <p style={eyebrow}>SCOUTA / WALLET / BUY</p>
          <h1 style={h1}>Sign in to buy coins.</h1>
          <Link href="/login?next=/wallet/buy" style={primaryBtn}>
            <span>Log in</span>
            <ArrowRight size={14} strokeWidth={1.75} />
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <div style={container}>
        <Link href="/wallet" style={backLink}>
          <ArrowLeft size={12} strokeWidth={1.75} />
          <span>Back to wallet</span>
        </Link>
        <p style={eyebrow}>SCOUTA / WALLET / BUY</p>
        <h1 style={h1}>Buy coins</h1>
        <p style={sub}>
          Use coins to send gifts, unlock paid lives, and tip creators. 80% of every gift goes to the creator.
        </p>

        {balance && (
          <div style={balanceBox}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "0.45rem", color: "#555", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.15em" }}>
              <Coins size={12} strokeWidth={1.75} />
              CURRENT BALANCE
            </span>
            <span style={{ color: "#c8a96e", fontSize: "1rem", fontFamily: "monospace", fontWeight: 700 }}>
              {balance.balance.toLocaleString()} coins
            </span>
          </div>
        )}

        {error && <div style={errorBox}>{error}</div>}
        {success && <div style={successBox}>{success}</div>}

        {loading && (
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.78rem" }}>Loading packages...</p>
        )}

        {!loading && packages.length === 0 && (
          <div style={emptyBox}>
            <div style={{ color: "#1a1a1a", margin: "0 0 1.25rem", display: "flex", justifyContent: "center" }}>
              <ShoppingCart size={48} strokeWidth={1} />
            </div>
            <p style={{ color: "#666", fontFamily: "Georgia, serif", fontSize: "0.95rem", marginBottom: "0.4rem" }}>
              No packages available right now.
            </p>
            <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.05em" }}>
              Check back soon.
            </p>
          </div>
        )}

        {!loading && packages.length > 0 && (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "1rem",
          }}>
            {packages.map((p) => {
              const total = totalCoins(p);
              const isPurchasing = purchasing === p.id;
              const value = total / Math.max(1, p.price_usd ?? (p.price_cents ? p.price_cents / 100 : 1));
              return (
                <div key={p.id} style={{
                  position: "relative",
                  background: "#0d0d0d",
                  border: `1px solid ${p.is_popular ? "#2a3a1a" : "#1a1a1a"}`,
                  padding: "1.5rem 1.25rem",
                  display: "flex", flexDirection: "column",
                }}>
                  {p.is_popular && (
                    <span style={popularBadge}>
                      <Sparkles size={9} strokeWidth={2} />
                      POPULAR
                    </span>
                  )}
                  <div style={{ position: "absolute", top: "1rem", right: "1rem", color: "#c8a96e44", display: "flex" }}>
                    <Coins size={16} strokeWidth={1.5} />
                  </div>
                  <p style={{ fontSize: "0.6rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: "0 0 0.5rem", textTransform: "uppercase" }}>
                    {p.name || `${p.coins} coins`}
                  </p>
                  <p style={{
                    fontSize: "2rem", fontFamily: "monospace", color: "#c8a96e",
                    margin: 0, lineHeight: 1, fontWeight: 600,
                  }}>
                    {(p.coins || 0).toLocaleString()}
                  </p>
                  <p style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", letterSpacing: "0.15em", margin: "0.3rem 0 0" }}>
                    COINS
                  </p>
                  {p.bonus_coins ? (
                    <p style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.7rem", color: "#4a9a4a", fontFamily: "monospace", marginTop: "0.5rem", letterSpacing: "0.05em" }}>
                      <Sparkles size={11} strokeWidth={1.75} />
                      + {p.bonus_coins.toLocaleString()} bonus
                    </p>
                  ) : null}
                  {p.description && (
                    <p style={{ fontSize: "0.78rem", color: "#666", fontFamily: "Georgia, serif", lineHeight: 1.55, margin: "0.85rem 0 0" }}>
                      {p.description}
                    </p>
                  )}
                  <div style={{ flex: 1 }} />
                  <div style={{ marginTop: "1.25rem", borderTop: "1px solid #1a1a1a", paddingTop: "1rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "0.75rem" }}>
                      <span style={{ color: "#f0e8d8", fontSize: "1.4rem", fontFamily: "Georgia, serif" }}>
                        {priceLabel(p)}
                      </span>
                      {p.bonus_coins && total !== p.coins && (
                        <span style={{ color: "#444", fontSize: "0.6rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>
                          {Math.round(value)}/$
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => buy(p)}
                      disabled={isPurchasing || purchasing !== null}
                      style={{
                        ...buyBtn,
                        opacity: isPurchasing || (purchasing !== null && purchasing !== p.id) ? 0.5 : 1,
                        cursor: isPurchasing || (purchasing !== null && purchasing !== p.id) ? "not-allowed" : "pointer",
                      }}
                    >
                      {isPurchasing ? (
                        <>
                          <Loader2 size={13} strokeWidth={2} style={{ animation: "spin 1s linear infinite" }} />
                          <span>Processing...</span>
                        </>
                      ) : (
                        <>
                          <ShoppingCart size={13} strokeWidth={1.75} />
                          <span>Buy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <p style={fineprint}>
          All payments processed securely. Coins are non-refundable once spent.
          Need help? <a href="mailto:hello@scouta.co" style={{ color: "#4a7a9a" }}>hello@scouta.co</a>
        </p>
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
  fontSize: "clamp(1.6rem, 4vw, 2.5rem)", fontWeight: 400,
  fontFamily: "Georgia, serif", color: "#f0e8d8",
  margin: "0.4rem 0 0.6rem",
};
const sub: React.CSSProperties = {
  fontSize: "0.85rem", color: "#666",
  fontFamily: "Georgia, serif", lineHeight: 1.6,
  margin: "0 0 2rem", maxWidth: "560px",
};
const balanceBox: React.CSSProperties = {
  display: "flex", justifyContent: "space-between", alignItems: "center",
  background: "#0d0d0d", border: "1px solid #1a1a1a",
  padding: "0.85rem 1.1rem", marginBottom: "1.5rem",
};
const errorBox: React.CSSProperties = {
  background: "#1a0a0a", border: "1px solid #2a1010",
  color: "#9a4a4a", padding: "0.6rem 0.85rem",
  fontSize: "0.75rem", fontFamily: "monospace",
  marginBottom: "1.25rem",
};
const successBox: React.CSSProperties = {
  background: "#0a1a0a", border: "1px solid #102a10",
  color: "#4a9a4a", padding: "0.6rem 0.85rem",
  fontSize: "0.75rem", fontFamily: "monospace",
  marginBottom: "1.25rem", letterSpacing: "0.05em",
};
const popularBadge: React.CSSProperties = {
  position: "absolute", top: "-1px", right: "-1px",
  background: "#2a4a2a", color: "#4a9a4a",
  fontSize: "0.55rem", letterSpacing: "0.2em",
  fontFamily: "monospace", padding: "0.25rem 0.55rem",
  fontWeight: 700,
  display: "inline-flex", alignItems: "center", gap: "0.3rem",
};
const buyBtn: React.CSSProperties = {
  width: "100%", background: "#1a2a1a",
  border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.75rem", fontSize: "0.75rem",
  fontFamily: "monospace", letterSpacing: "0.15em", textTransform: "uppercase",
  boxSizing: "border-box",
  display: "inline-flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
};
const primaryBtn: React.CSSProperties = {
  ...buyBtn,
  textAlign: "center" as const,
  textDecoration: "none", padding: "0.85rem 2rem", width: "auto",
};
const emptyBox: React.CSSProperties = {
  padding: "4rem 1.5rem", textAlign: "center",
  border: "1px dashed #1a1a1a", background: "#0a0a0a",
};
const fineprint: React.CSSProperties = {
  marginTop: "2rem", fontSize: "0.7rem",
  color: "#444", fontFamily: "monospace",
  textAlign: "center", letterSpacing: "0.05em",
};
