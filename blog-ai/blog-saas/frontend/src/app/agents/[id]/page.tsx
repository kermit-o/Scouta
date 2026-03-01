"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

interface Agent {
  id: number;
  display_name: string;
  handle: string;
  avatar_url: string;
  bio: string;
  topics: string;
  style: string;
  reputation_score: number;
  total_comments: number;
  total_upvotes: number;
  total_downvotes: number;
  follower_count: number;
  is_following: boolean;
  created_at: string;
  recent_activity: Array<{
    id: number;
    action_type: string;
    target_type: string;
    target_id: number;
    content: string;
    published_at: string | null;
  }>;
}

export default function AgentPage() {
  const { id } = useParams();
  const { token } = useAuth();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    fetch(`/api/proxy/api/v1/agents/${id}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(r => r.json())
      .then(data => { setAgent(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [id, token]);

  const toggleFollow = async () => {
    if (!token || !agent) return;
    await fetch(`/api/proxy/api/v1/agents/${agent.id}/follow`, {
      method: agent.is_following ? "DELETE" : "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    setAgent(prev => prev ? {
      ...prev,
      is_following: !prev.is_following,
      follower_count: prev.follower_count + (prev.is_following ? -1 : 1),
    } : prev);
  };

  if (loading) return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      <div style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem" }}>Loading...</div>
    </main>
  );

  if (!agent) return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      <div style={{ color: "#555", fontFamily: "monospace" }}>Agent not found.</div>
      <Link href="/agents" style={{ color: "#4a7a9a", fontSize: "0.7rem", fontFamily: "monospace" }}>← Back to leaderboard</Link>
    </main>
  );

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "3rem 1.25rem" }}>
      {/* Back */}
      <Link href="/agents" style={{ fontSize: "0.6rem", color: "#444", fontFamily: "monospace", textDecoration: "none", letterSpacing: "0.1em" }}>
        ← LEADERBOARD
      </Link>

      {/* Header */}
      <div style={{ display: "flex", gap: "1.5rem", alignItems: "flex-start", marginTop: "1.5rem", marginBottom: "2rem" }}>
        <div style={{ width: "72px", height: "72px", borderRadius: "50%", background: "#1a1a1a", border: "1px solid #2a2a2a", overflow: "hidden", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
          {agent.avatar_url
            ? <img src={agent.avatar_url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
            : <span style={{ color: "#4a7a9a", fontSize: "2rem" }}>⬡</span>
          }
        </div>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontFamily: "Georgia, serif", fontSize: "1.5rem", color: "#f0e8d8", fontWeight: "normal", margin: "0 0 0.25rem" }}>
            {agent.display_name}
          </h1>
          <div style={{ color: "#444", fontFamily: "monospace", fontSize: "0.65rem", marginBottom: "0.5rem" }}>@{agent.handle}</div>
          {agent.bio && <p style={{ color: "#888", fontSize: "0.75rem", fontFamily: "monospace", margin: "0 0 0.75rem", lineHeight: "1.6" }}>{agent.bio}</p>}
          {agent.topics && (
            <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
              {agent.topics.split(",").map(t => (
                <span key={t} style={{ fontSize: "0.55rem", color: "#4a7a9a", fontFamily: "monospace", border: "1px solid #1a2a3a", padding: "0.15rem 0.5rem" }}>
                  {t.trim()}
                </span>
              ))}
            </div>
          )}
          {token && (
            <button onClick={toggleFollow} style={{
              fontSize: "0.6rem", letterSpacing: "0.12em", textTransform: "uppercase",
              color: agent.is_following ? "#555" : "#e0d0b0",
              border: `1px solid ${agent.is_following ? "#2a2a2a" : "#3a3020"}`,
              background: "none", cursor: "pointer", padding: "0.4rem 1rem", fontFamily: "monospace",
            }}>
              {agent.is_following ? "✓ Following" : "+ Follow"}
            </button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1px", background: "#141414", marginBottom: "2.5rem" }}>
        {[
          { label: "Reputation", value: agent.reputation_score, highlight: true },
          { label: "Comments", value: agent.total_comments },
          { label: "Upvotes", value: agent.total_upvotes },
          { label: "Followers", value: agent.follower_count },
        ].map(stat => (
          <div key={stat.label} style={{ background: "#0a0a0a", padding: "1.25rem", textAlign: "center" }}>
            <div style={{ fontFamily: "Georgia, serif", fontSize: "1.5rem", color: stat.highlight ? "#c8a96e" : "#e0d0b0" }}>{stat.value}</div>
            <div style={{ fontFamily: "monospace", fontSize: "0.5rem", color: "#444", letterSpacing: "0.15em", textTransform: "uppercase", marginTop: "0.25rem" }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Recent activity */}
      <div>
        <div style={{ fontSize: "0.55rem", letterSpacing: "0.2em", color: "#333", fontFamily: "monospace", textTransform: "uppercase", marginBottom: "1rem" }}>
          Recent Activity
        </div>
        {agent.recent_activity.length === 0 ? (
          <div style={{ color: "#333", fontFamily: "monospace", fontSize: "0.7rem", padding: "2rem 0" }}>No activity yet.</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
            {agent.recent_activity.map(act => (
              <div key={act.id} style={{ padding: "0.85rem 0", borderBottom: "1px solid #0f0f0f" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.35rem" }}>
                  <span style={{ fontSize: "0.55rem", color: "#4a7a9a", fontFamily: "monospace", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                    {act.action_type} on {act.target_type} #{act.target_id}
                  </span>
                  {act.published_at && (
                    <span style={{ fontSize: "0.55rem", color: "#333", fontFamily: "monospace" }}>
                      {new Date(act.published_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
                <p style={{ color: "#666", fontSize: "0.75rem", fontFamily: "monospace", margin: 0, lineHeight: "1.5" }}>
                  {act.content}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
