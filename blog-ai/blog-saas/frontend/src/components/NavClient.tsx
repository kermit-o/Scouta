"use client";

import Link from "next/link";
import NotificationBell from "@/components/NotificationBell";
import { useAuth } from "@/context/AuthContext";

export default function NavClient() {
  const { token } = useAuth();
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
      <NotificationBell />
      {token ? (
        <Link href="/profile" style={{ fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#444", textDecoration: "none" }}>
          Profile
        </Link>
      ) : (
        <Link href="/login" style={{ fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#444", textDecoration: "none" }}>
          Login
        </Link>
      )}
    </div>
  );
}
