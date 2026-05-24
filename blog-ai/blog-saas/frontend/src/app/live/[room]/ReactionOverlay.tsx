"use client";

import { useEffect, useState } from "react";

type Floater = { id: number; emoji: string; x: number };

// Listens for "reaction" messages (forwarded by LiveChat as live_ws_message)
// and floats the emoji up the right edge, TikTok/Instagram-style. Ephemeral —
// nothing is persisted; floaters auto-remove after the animation.
export default function ReactionOverlay() {
  const [floaters, setFloaters] = useState<Floater[]>([]);

  useEffect(() => {
    let counter = 0;
    const handler = (e: Event) => {
      const msg = (e as CustomEvent).detail;
      if (!msg || msg.type !== "reaction") return;
      const id = ++counter;
      const x = Math.floor(Math.random() * 28);
      setFloaters((prev) => [...prev.slice(-30), { id, emoji: msg.emoji || "❤️", x }]);
      setTimeout(() => setFloaters((prev) => prev.filter((f) => f.id !== id)), 2500);
    };
    window.addEventListener("live_ws_message", handler);
    return () => window.removeEventListener("live_ws_message", handler);
  }, []);

  return (
    <div
      style={{
        position: "absolute",
        right: 16,
        bottom: 80,
        width: 60,
        height: "50vh",
        pointerEvents: "none",
        overflow: "hidden",
        zIndex: 40,
      }}
    >
      {floaters.map((f) => (
        <span
          key={f.id}
          style={{
            position: "absolute",
            bottom: 0,
            left: f.x,
            fontSize: "1.6rem",
            animation: "reactionFloat 2.5s ease-out forwards",
          }}
        >
          {f.emoji}
        </span>
      ))}
      <style>{`@keyframes reactionFloat {
        0% { transform: translateY(0) scale(0.6); opacity: 0; }
        15% { opacity: 1; transform: translateY(-5vh) scale(1); }
        100% { transform: translateY(-45vh) scale(1.1); opacity: 0; }
      }`}</style>
    </div>
  );
}
