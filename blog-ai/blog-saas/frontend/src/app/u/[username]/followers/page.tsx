"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function FollowersPage() {
  const { username } = useParams();
  const router = useRouter();
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [sort, setSort] = useState<"recent" | "alpha">("recent");

  useEffect(() => {
    setLoading(true);
    fetch(`/api/proxy/api/v1/u/${username}/followers?sort=${sort}`)
      .then(r => r.json())
      .then(d => { setUsers(Array.isArray(d) ? d : []); setLoading(false); });
  }, [username, sort]);

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0" }}>
      <div style={{ borderBottom: "1px solid #141414", padding: "1.25rem 2rem" }}>
        <Link href={`/u/${username}`} style={{ fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase", color: "#444", textDecoration: "none" }}>← @{username}</Link>
      </div>

      <div style={{ maxWidth: "580px", margin: "0 auto", padding: "2.5rem 1.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "2rem" }}>
          <h1 style={{ fontSize: "0.7rem", letterSpacing: "0.3em", textTransform: "uppercase", color: "#555", margin: 0, fontFamily: "monospace" }}>
            Followers {!loading && `· ${users.length}`}
          </h1>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {(["recent", "alpha"] as const).map(s => (
              <button key={s} onClick={() => setSort(s)} style={{
                background: "none", border: `1px solid ${sort === s ? "#3a3a3a" : "#1a1a1a"}`,
                color: sort === s ? "#f0e8d8" : "#333",
                padding: "0.25rem 0.75rem", cursor: "pointer",
                fontSize: "0.6rem", fontFamily: "monospace", letterSpacing: "0.1em", textTransform: "uppercase",
              }}>
                {s === "recent" ? "Recent" : "A–Z"}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</p>
        ) : users.length === 0 ? (
          <p style={{ color: "#2a2a2a", fontFamily: "monospace", fontSize: "0.8rem", textAlign: "center", padding: "3rem 0" }}>No followers yet.</p>
        ) : (
          users.map(u => (
            <Link key={u.id} href={`/u/${u.username}`} style={{ textDecoration: "none", display: "block" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "1rem", padding: "0.875rem 0", borderBottom: "1px solid #0f0f0f" }}>
                {u.avatar_url ? (
                  <img src={u.avatar_url} alt={u.display_name} style={{ width: 40, height: 40, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
                ) : (
                  <div style={{ width: 40, height: 40, borderRadius: "50%", background: "#1a2a1a", border: "1px solid #2a4a2a", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.9rem", color: "#4a9a4a", fontFamily: "monospace", flexShrink: 0 }}>
                    {(u.display_name || u.username)[0].toUpperCase()}
                  </div>
                )}
                <div>
                  <div style={{ fontSize: "0.9rem", color: "#d8d0c0", fontFamily: "Georgia, serif" }}>{u.display_name}</div>
                  <div style={{ fontSize: "0.65rem", color: "#333", fontFamily: "monospace" }}>@{u.username}</div>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>
    </main>
  );
}
