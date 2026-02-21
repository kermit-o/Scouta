"use client";
import { useState, useEffect } from "react";

function calcTimeAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
  return `${Math.floor(diff / 86400)}d`;
}

export default function TimeAgo({ dateStr }: { dateStr: string }) {
  const [label, setLabel] = useState(() => calcTimeAgo(dateStr));

  useEffect(() => {
    const interval = setInterval(() => setLabel(calcTimeAgo(dateStr)), 30000);
    return () => clearInterval(interval);
  }, [dateStr]);

  return <span style={{ fontSize: "0.75rem", color: "#444", fontFamily: "monospace" }}>{label}</span>;
}
