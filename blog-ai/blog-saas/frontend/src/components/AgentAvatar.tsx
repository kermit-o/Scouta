"use client";

import { Comment } from "@/lib/api";

interface AgentAvatarProps {
  comment: Comment;
  size?: number;
}

const AGENT_COLORS: Record<number, string> = {
  1: "#4a7a9a", 2: "#9a7a4a", 3: "#7a4a9a", 4: "#4a9a7a",
  5: "#9a4a7a", 6: "#7a9a4a", 7: "#9a6a4a", 8: "#4a6a9a",
  9: "#6a4a9a", 10: "#9a4a6a",
};

function hashColor(id: number): string {
  return AGENT_COLORS[id] ?? `hsl(${(id * 47) % 360}, 40%, 45%)`;
}

function initials(name: string): string {
  return name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
}

// Hexagonal clip path for agent badge
const HEX_CLIP = "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)";

export function AgentAvatar({ comment, size = 36 }: AgentAvatarProps) {
  const isAgent = comment.author_type === "agent";

  if (isAgent) {
    const agentId = comment.author_agent_id ?? 0;
    const color = hashColor(agentId);
    const name = comment.author_display_name ?? `Agent ${agentId}`;

    return (
      <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
        {/* Hexagon avatar */}
        <div style={{
          width: size,
          height: size,
          clipPath: HEX_CLIP,
          background: `${color}22`,
          border: `1px solid ${color}66`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: size * 0.28,
          color,
          fontFamily: "monospace",
          fontWeight: 600,
          letterSpacing: "0.05em",
        }}>
          {initials(name)}
        </div>
        {/* AI badge */}
        <div style={{
          position: "absolute",
          bottom: -2,
          right: -2,
          width: size * 0.38,
          height: size * 0.38,
          borderRadius: "50%",
          background: "#0a0a0a",
          border: `1px solid ${color}88`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: size * 0.18,
        }}>
          ⚡
        </div>
      </div>
    );
  }

  // Human avatar
  const avatarUrl = comment.author_avatar_url;
  const name = comment.author_display_name ?? comment.author_username ?? "User";
  const color = "#6a8a6a";

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      {avatarUrl ? (
        <img
          src={avatarUrl}
          alt={name}
          style={{
            width: size,
            height: size,
            borderRadius: "50%",
            objectFit: "cover",
            border: `1px solid ${color}66`,
          }}
        />
      ) : (
        <div style={{
          width: size,
          height: size,
          borderRadius: "50%",
          background: `${color}22`,
          border: `1px solid ${color}66`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: size * 0.32,
          color,
          fontFamily: "monospace",
          fontWeight: 600,
        }}>
          {initials(name)}
        </div>
      )}
    </div>
  );
}
