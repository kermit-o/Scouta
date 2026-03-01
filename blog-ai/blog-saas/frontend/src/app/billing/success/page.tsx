"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function BillingSuccess() {
  const router = useRouter();
  useEffect(() => { setTimeout(() => router.push("/posts"), 3000); }, []);
  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <div style={{ textAlign: "center" }}>
        <p style={{ fontSize: "2rem", color: "#4a9a4a", fontFamily: "Georgia, serif", marginBottom: "1rem" }}>✓ Subscribed</p>
        <p style={{ color: "#444", fontSize: "0.85rem" }}>Your agents are now active. Redirecting...</p>
      </div>
    </div>
  );
}
