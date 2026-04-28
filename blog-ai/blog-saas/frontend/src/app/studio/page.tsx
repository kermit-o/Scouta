"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

const API = "/api/proxy/api/v1";

interface Transaction {
  id: number;
  amount: number;
  type: string;
  description: string;
  reference_id?: string;
  created_at: string;
}

interface Balance {
  balance: number;
  withdrawable_balance: number;
  lifetime_earned: number;
}

interface Earnings {
  this_week?: number;
  this_month?: number;
  all_time?: number;
}

interface Profile {
  id: number;
  username: string;
  display_name?: string;
  follower_count?: number;
  post_count?: number;
}

interface TopFan { name: string; coins: number; gifts: number }

export default function StudioPage() {
  const { token, user, isLoaded } = useAuth();
  const [balance, setBalance] = useState<Balance | null>(null);
  const [earnings, setEarnings] = useState<Earnings | null>(null);
  const [txs, setTxs] = useState<Transaction[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) { setLoading(false); return; }
    const headers = { Authorization: `Bearer ${token}` };
    Promise.all([
      fetch(`${API}/coins/balance`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${API}/coins/earnings`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${API}/coins/transactions?limit=100`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
      fetch(`${API}/profile/me`, { headers }).then(r => r.ok ? r.json() : null).catch(() => null),
    ]).then(([bal, earn, txsRes, prof]) => {
      if (bal) setBalance(bal);
      if (earn) setEarnings(earn);
      if (txsRes && Array.isArray(txsRes.transactions)) setTxs(txsRes.transactions);
      if (prof) setProfile(prof);
      setLoading(false);
    });
  }, [token]);

  // Compute top fans from gift_received transactions
  const topFans: TopFan[] = useMemo(() => {
    const giftsReceived = txs.filter(t => t.type === "gift_received" && t.amount > 0);
    const byFan = new Map<string, { coins: number; gifts: number }>();
    for (const t of giftsReceived) {
      const match = (t.description || "").match(/from\s+(.+?)(?:\s+\(|$)/i);
      const name = match?.[1]?.trim() || "Anonymous";
      const cur = byFan.get(name) || { coins: 0, gifts: 0 };
      cur.coins += t.amount;
      cur.gifts += 1;
      byFan.set(name, cur);
    }
    return Array.from(byFan.entries())
      .map(([name, v]) => ({ name, coins: v.coins, gifts: v.gifts }))
      .sort((a, b) => b.coins - a.coins)
      .slice(0, 5);
  }, [txs]);

  const recentGifts = useMemo(
    () => txs.filter(t => t.type === "gift_received").slice(0, 8),
    [txs]
  );

  if (isLoaded && !token) {
    return (
      <main style={pageStyle}>
        <div style={{ ...container, textAlign: "center", paddingTop: "5rem" }}>
          <p style={{ color: "#888", marginBottom: "1rem", fontFamily: "monospace", fontSize: "0.85rem" }}>
            Studio is for logged-in creators.
          </p>
          <Link href="/login" style={primaryBtn}>Log in →</Link>
        </div>
      </main>
    );
  }

  return (
    <main style={pageStyle}>
      <div style={container}>
        {/* Header */}
        <div style={{ marginBottom: "2rem", paddingBottom: "1.25rem", borderBottom: "1px solid #141414" }}>
          <p style={eyebrow}>SCOUTA / STUDIO</p>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <h1 style={h1}>Studio</h1>
              <p style={{ color: "#555", fontSize: "0.78rem", fontFamily: "monospace", margin: "0.5rem 0 0" }}>
                @{profile?.username || user?.username}
              </p>
            </div>
            <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
              <Link href="/live/start" style={ctaPrimary}>Go Live →</Link>
              <Link href="/posts/new" style={ctaSecondary}>+ Write</Link>
            </div>
          </div>
        </div>

        {loading && (
          <p style={{ color: "#444", fontFamily: "monospace", fontSize: "0.78rem" }}>Loading...</p>
        )}

        {!loading && (
          <>
            {/* Stat cards */}
            <div style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "0.875rem",
              marginBottom: "2.5rem",
            }}>
              <Stat label="EARNED ALL TIME" value={balance?.lifetime_earned ?? earnings?.all_time ?? 0} accent="#4a9a4a" suffix="coins" />
              <Stat label="WITHDRAWABLE" value={balance?.withdrawable_balance ?? 0} accent="#c8a96e" suffix="coins" />
              <Stat label="POSTS" value={profile?.post_count ?? 0} accent="#4a7a9a" />
              <Stat label="FOLLOWERS" value={profile?.follower_count ?? 0} accent="#9a6a4a" />
            </div>

            {/* Earnings split */}
            {earnings && (earnings.this_week !== undefined || earnings.this_month !== undefined) && (
              <div style={{ marginBottom: "2.5rem", paddingBottom: "1.5rem", borderBottom: "1px solid #141414" }}>
                <p style={eyebrow}>EARNINGS</p>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.875rem", marginTop: "0.75rem" }}>
                  <Stat label="THIS WEEK" value={earnings.this_week ?? 0} accent="#4a9a4a" suffix="coins" small />
                  <Stat label="THIS MONTH" value={earnings.this_month ?? 0} accent="#4a9a4a" suffix="coins" small />
                  <Stat label="ALL TIME" value={earnings.all_time ?? balance?.lifetime_earned ?? 0} accent="#4a9a4a" suffix="coins" small />
                </div>
                <Link href="/wallet" style={{
                  display: "inline-block", marginTop: "1rem",
                  fontSize: "0.7rem", color: "#4a7a9a", textDecoration: "none",
                  fontFamily: "monospace", letterSpacing: "0.1em",
                }}>
                  Manage wallet & withdraw →
                </Link>
              </div>
            )}

            {/* Top Fans */}
            <Section title="Top fans" subtitle="Your biggest gifters of all time">
              {topFans.length === 0 ? (
                <Empty body="No fans yet." sub="When viewers send gifts, they'll show up here." />
              ) : (
                <div>
                  {topFans.map((fan, i) => (
                    <div key={fan.name} style={fanRow}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flex: 1, minWidth: 0 }}>
                        <span style={{
                          width: 24, height: 24, borderRadius: "50%",
                          background: "#1a1a1a", color: "#888",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: "0.7rem", fontFamily: "monospace", fontWeight: 700,
                          flexShrink: 0,
                        }}>
                          {i + 1}
                        </span>
                        <span style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.9rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {fan.name}
                        </span>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexShrink: 0 }}>
                        <span style={{ color: "#444", fontSize: "0.65rem", fontFamily: "monospace" }}>
                          {fan.gifts} {fan.gifts === 1 ? "gift" : "gifts"}
                        </span>
                        <span style={{ color: "#c8a96e", fontSize: "0.85rem", fontFamily: "monospace", fontWeight: 700, minWidth: "60px", textAlign: "right" }}>
                          {fan.coins.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Section>

            {/* Recent gifts */}
            <Section title="Recent gifts" subtitle="Last gifts received">
              {recentGifts.length === 0 ? (
                <Empty body="No gifts received yet." sub="Stream live and let viewers send gifts." cta={{ href: "/live/start", label: "Start a stream" }} />
              ) : (
                <div>
                  {recentGifts.map(t => (
                    <div key={t.id} style={txRow}>
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ color: "#e0d0b0", fontFamily: "Georgia, serif", fontSize: "0.85rem", marginBottom: "0.2rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {t.description}
                        </div>
                        <div style={{ color: "#444", fontSize: "0.6rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>
                          {formatDate(t.created_at)}
                        </div>
                      </div>
                      <div style={{ color: "#4a9a4a", fontSize: "0.95rem", fontFamily: "monospace", fontWeight: 700, marginLeft: "1rem", whiteSpace: "nowrap" }}>
                        +{t.amount}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Section>

            {/* Coming soon */}
            <Section title="Coming soon" subtitle="">
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.875rem" }}>
                {[
                  { title: "Stream history", body: "Past streams with peak viewers, duration, and gifts per session." },
                  { title: "Audience growth", body: "Follower trend, retention, and best-performing content." },
                  { title: "Clip studio", body: "Auto-generated highlights from your live streams." },
                ].map((c) => (
                  <div key={c.title} style={comingCard}>
                    <p style={{ color: "#888", fontSize: "0.85rem", fontFamily: "Georgia, serif", margin: "0 0 0.4rem" }}>{c.title}</p>
                    <p style={{ color: "#555", fontSize: "0.7rem", fontFamily: "monospace", lineHeight: 1.55, margin: 0 }}>{c.body}</p>
                  </div>
                ))}
              </div>
            </Section>
          </>
        )}
      </div>
    </main>
  );
}

function Stat({ label, value, accent, suffix, small }: { label: string; value: number; accent: string; suffix?: string; small?: boolean }) {
  return (
    <div style={{ background: "#0d0d0d", border: "1px solid #1a1a1a", padding: "1.1rem 1.1rem 1rem" }}>
      <p style={{ fontSize: "0.55rem", letterSpacing: "0.25em", color: "#555", fontFamily: "monospace", margin: "0 0 0.55rem" }}>{label}</p>
      <p style={{
        fontSize: small ? "1.4rem" : "1.75rem", fontFamily: "monospace",
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

function Section({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: "2.5rem" }}>
      <div style={{ paddingBottom: "0.75rem", borderBottom: "1px solid #141414", marginBottom: "0.75rem" }}>
        <h2 style={{ fontSize: "1.25rem", fontWeight: 400, fontFamily: "Georgia, serif", color: "#f0e8d8", margin: 0 }}>{title}</h2>
        {subtitle && <p style={{ color: "#555", fontSize: "0.7rem", fontFamily: "monospace", margin: "0.3rem 0 0", letterSpacing: "0.05em" }}>{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}

function Empty({ body, sub, cta }: { body: string; sub: string; cta?: { href: string; label: string } }) {
  return (
    <div style={{ padding: "2.5rem 1.5rem", textAlign: "center", border: "1px dashed #1a1a1a", background: "#0a0a0a" }}>
      <p style={{ color: "#777", fontSize: "0.85rem", fontFamily: "Georgia, serif", marginBottom: "0.4rem" }}>{body}</p>
      <p style={{ color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.05em", marginBottom: cta ? "1rem" : 0 }}>
        {sub}
      </p>
      {cta && <Link href={cta.href} style={ctaPrimary}>{cta.label}</Link>}
    </div>
  );
}

function formatDate(s: string): string {
  try {
    const d = new Date(s);
    const m = Math.floor((Date.now() - d.getTime()) / 60000);
    if (m < 1) return "just now";
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return d.toLocaleDateString();
  } catch { return ""; }
}

const pageStyle: React.CSSProperties = { minHeight: "100vh", background: "#080808", color: "#f0e8d8" };
const container: React.CSSProperties = { maxWidth: "960px", margin: "0 auto", padding: "2.5rem 1.5rem 5rem" };
const eyebrow: React.CSSProperties = { fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: 0 };
const h1: React.CSSProperties = { fontSize: "clamp(1.6rem, 4vw, 2.5rem)", fontWeight: 400, fontFamily: "Georgia, serif", margin: "0.4rem 0 0" };
const ctaPrimary: React.CSSProperties = {
  background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
  padding: "0.65rem 1.4rem", textDecoration: "none",
  fontSize: "0.7rem", letterSpacing: "0.15em", textTransform: "uppercase",
  fontFamily: "monospace", display: "inline-block",
};
const ctaSecondary: React.CSSProperties = {
  background: "transparent", border: "1px solid #2a2a2a", color: "#888",
  padding: "0.65rem 1.4rem", textDecoration: "none",
  fontSize: "0.7rem", letterSpacing: "0.15em", textTransform: "uppercase",
  fontFamily: "monospace", display: "inline-block",
};
const primaryBtn = ctaPrimary;
const fanRow: React.CSSProperties = {
  display: "flex", alignItems: "center", justifyContent: "space-between",
  padding: "0.75rem 0", borderBottom: "1px solid #141414",
};
const txRow: React.CSSProperties = {
  display: "flex", alignItems: "center", justifyContent: "space-between",
  padding: "0.75rem 0", borderBottom: "1px solid #141414",
};
const comingCard: React.CSSProperties = {
  background: "#0a0a0a", border: "1px dashed #1a1a1a",
  padding: "1.1rem 1.1rem 1rem",
};
