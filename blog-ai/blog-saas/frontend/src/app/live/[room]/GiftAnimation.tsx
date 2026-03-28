"use client";
import { useEffect, useState, useRef } from "react";

interface GiftEvent {
  id: number;
  sender: string;
  emoji: string;
  gift_name: string;
  coin_amount: number;
  animation: "float" | "burst" | "fullscreen";
}

let _giftId = 0;

export default function GiftAnimation() {
  const [gifts, setGifts] = useState<GiftEvent[]>([]);

  useEffect(() => {
    const handler = (e: any) => {
      const msg = e.detail;
      if (msg.type !== "gift") return;
      const giftEvent: GiftEvent = {
        id: ++_giftId,
        sender: msg.sender || "Someone",
        emoji: msg.emoji || "🎁",
        gift_name: msg.gift_name || "Gift",
        coin_amount: msg.coin_amount || 0,
        animation: msg.animation || "float",
      };
      setGifts(prev => [...prev.slice(-9), giftEvent]);
      // Auto-remove after animation
      const duration = giftEvent.animation === "fullscreen" ? 3500 : giftEvent.animation === "burst" ? 2500 : 3500;
      setTimeout(() => {
        setGifts(prev => prev.filter(g => g.id !== giftEvent.id));
      }, duration);
    };
    window.addEventListener("live_ws_message", handler);
    return () => window.removeEventListener("live_ws_message", handler);
  }, []);

  return (
    <>
      {/* Inject keyframes once */}
      <style>{`
        @keyframes giftFloat {
          0% { opacity: 1; transform: translateY(0) scale(1); }
          70% { opacity: 1; transform: translateY(-200px) scale(1.1); }
          100% { opacity: 0; transform: translateY(-300px) scale(0.8); }
        }
        @keyframes giftBurst {
          0% { opacity: 0; transform: scale(0.3); }
          30% { opacity: 1; transform: scale(1.3); }
          60% { opacity: 1; transform: scale(1); }
          100% { opacity: 0; transform: scale(0.5); }
        }
        @keyframes giftFullscreen {
          0% { opacity: 0; transform: scale(0.5); }
          15% { opacity: 1; transform: scale(1.2); }
          30% { opacity: 1; transform: scale(1); }
          80% { opacity: 1; transform: scale(1); }
          100% { opacity: 0; transform: scale(0.8); }
        }
      `}</style>

      {/* Float animations — bottom-left area */}
      {gifts.filter(g => g.animation === "float").map((g, i) => (
        <div
          key={g.id}
          style={{
            position: "absolute",
            bottom: 100 + (i * 20),
            left: 20 + (i * 15),
            animation: "giftFloat 3s ease-out forwards",
            pointerEvents: "none",
            zIndex: 55,
            display: "flex",
            alignItems: "center",
            gap: "0.4rem",
          }}
        >
          <span style={{ fontSize: "1.8rem" }}>{g.emoji}</span>
          <div>
            <p style={{ margin: 0, fontSize: "0.6rem", color: "#9a6a4a", fontFamily: "monospace", textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}>
              {g.sender}
            </p>
            <p style={{ margin: 0, fontSize: "0.55rem", color: "#fff", fontFamily: "monospace", textShadow: "0 1px 3px rgba(0,0,0,0.8)" }}>
              sent {g.gift_name}
            </p>
          </div>
        </div>
      ))}

      {/* Burst animations — center */}
      {gifts.filter(g => g.animation === "burst").map(g => (
        <div
          key={g.id}
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            animation: "giftBurst 2s ease-out forwards",
            pointerEvents: "none",
            zIndex: 55,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "4rem" }}>{g.emoji}</div>
          <p style={{
            margin: "0.25rem 0 0",
            fontSize: "0.7rem",
            color: "#fff",
            fontFamily: "monospace",
            textShadow: "0 2px 6px rgba(0,0,0,0.9)",
          }}>
            {g.sender} sent {g.gift_name}
          </p>
        </div>
      ))}

      {/* Fullscreen animations */}
      {gifts.filter(g => g.animation === "fullscreen").map(g => (
        <div
          key={g.id}
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(0,0,0,0.6)",
            animation: "giftFullscreen 3s ease-out forwards",
            pointerEvents: "none",
            zIndex: 56,
          }}
        >
          <div style={{ fontSize: "6rem" }}>{g.emoji}</div>
          <p style={{
            margin: "0.5rem 0 0.25rem",
            fontSize: "1.1rem",
            color: "#f0e8d8",
            fontFamily: "Georgia, serif",
            textShadow: "0 2px 8px rgba(0,0,0,0.9)",
          }}>
            {g.gift_name}
          </p>
          <p style={{
            margin: 0,
            fontSize: "0.7rem",
            color: "#9a6a4a",
            fontFamily: "monospace",
            textShadow: "0 2px 6px rgba(0,0,0,0.9)",
          }}>
            from {g.sender} · 🪙 {g.coin_amount}
          </p>
        </div>
      ))}
    </>
  );
}
