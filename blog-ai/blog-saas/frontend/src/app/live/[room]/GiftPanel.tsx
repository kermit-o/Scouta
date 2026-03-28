"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

interface Gift {
  id: number;
  name: string;
  emoji: string;
  coin_cost: number;
  animation_type: string;
}

interface Props {
  roomName: string;
  token: string | null;
  balance: number;
  onBalanceUpdate: (newBalance: number) => void;
}

export default function GiftPanel({ roomName, token, balance, onBalanceUpdate }: Props) {
  const [open, setOpen] = useState(false);
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [sending, setSending] = useState<number | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API}/api/v1/live/gifts/catalog`)
      .then(r => r.json())
      .then(d => setGifts(d.gifts || []))
      .catch(() => {});
  }, []);

  async function sendGift(gift: Gift) {
    if (!token || sending) return;
    if (balance < gift.coin_cost) {
      setError("Not enough coins");
      setTimeout(() => setError(""), 2000);
      return;
    }
    setSending(gift.id);
    setError("");
    try {
      const res = await fetch(`/api/proxy/live/${roomName}/gift`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ gift_id: gift.id }),
      });
      const data = await res.json();
      if (res.ok && data.ok) {
        onBalanceUpdate(data.new_balance);
        setOpen(false);
      } else {
        setError(data.detail || "Failed to send gift");
        setTimeout(() => setError(""), 2000);
      }
    } catch {
      setError("Network error");
      setTimeout(() => setError(""), 2000);
    } finally {
      setSending(null);
    }
  }

  if (!token) return null;

  return (
    <>
      {/* Gift button */}
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          background: open ? "rgba(154,106,74,0.7)" : "rgba(0,0,0,0.5)",
          border: open ? "1px solid #9a6a4a" : "none",
          borderRadius: "50%",
          width: 44,
          height: 44,
          color: "#fff",
          cursor: "pointer",
          fontSize: "1.2rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
        title="Send a gift"
      >
        🎁
      </button>

      {/* Gift drawer */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: 0,
            left: 0,
            right: 0,
            background: "rgba(8,8,8,0.97)",
            borderTop: "1px solid #1a1a1a",
            padding: "1rem 1.25rem 1.5rem",
            zIndex: 60,
            backdropFilter: "blur(10px)",
          }}
        >
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <div>
              <span style={{ fontSize: "0.6rem", color: "#555", fontFamily: "monospace", letterSpacing: "0.15em" }}>SEND A GIFT</span>
              <span style={{ fontSize: "0.65rem", color: "#9a6a4a", fontFamily: "monospace", marginLeft: "1rem" }}>🪙 {balance.toLocaleString()}</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              style={{ background: "none", border: "none", color: "#555", cursor: "pointer", fontSize: "1rem" }}
            >✕</button>
          </div>

          {/* Error */}
          {error && (
            <p style={{ fontSize: "0.65rem", color: "#e44", fontFamily: "monospace", margin: "0 0 0.75rem" }}>{error}</p>
          )}

          {/* Gift grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "0.75rem" }}>
            {gifts.map(gift => {
              const canAfford = balance >= gift.coin_cost;
              return (
                <button
                  key={gift.id}
                  onClick={() => sendGift(gift)}
                  disabled={!canAfford || sending === gift.id}
                  style={{
                    background: sending === gift.id ? "#1a2a1a" : canAfford ? "#0e0e0e" : "#0a0a0a",
                    border: `1px solid ${canAfford ? "#1a1a1a" : "#111"}`,
                    borderRadius: 8,
                    padding: "0.75rem 0.5rem",
                    cursor: canAfford ? "pointer" : "not-allowed",
                    opacity: canAfford ? 1 : 0.4,
                    display: "flex",
                    flexDirection: "column" as const,
                    alignItems: "center",
                    gap: "0.3rem",
                    transition: "border-color 0.15s",
                  }}
                >
                  <span style={{ fontSize: "1.5rem" }}>{gift.emoji}</span>
                  <span style={{ fontSize: "0.6rem", color: "#f0e8d8", fontFamily: "monospace" }}>{gift.name}</span>
                  <span style={{ fontSize: "0.55rem", color: "#9a6a4a", fontFamily: "monospace" }}>🪙 {gift.coin_cost}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}
