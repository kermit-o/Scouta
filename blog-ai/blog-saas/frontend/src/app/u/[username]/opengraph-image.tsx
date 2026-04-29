import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Scouta profile";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

function initials(name: string): string {
  return name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();
}

export default async function ProfileOGImage({ params }: { params: { username: string } }) {
  let displayName = params.username;
  let username = params.username;
  let bio = "";
  let avatarUrl = "";
  let followers = 0;
  let comments = 0;
  let likes = 0;

  try {
    const res = await fetch(`${API}/api/v1/u/${params.username}`, {
      next: { revalidate: 300 },
    });
    if (res.ok) {
      const data = await res.json();
      displayName = data.display_name || data.username || params.username;
      username = data.username || params.username;
      bio = (data.bio || "").slice(0, 200);
      avatarUrl = data.avatar_url || "";
      followers = data.followers || 0;
      comments = data.comment_count || 0;
      likes = data.likes_received || 0;
    }
  } catch {}

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background: "#080808",
          color: "#f0e8d8",
          padding: "80px",
          position: "relative",
        }}
      >
        {/* Background grid */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px)",
            backgroundSize: "60px 60px",
            opacity: 0.18,
            display: "flex",
          }}
        />

        {/* Brand row */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            position: "relative",
            zIndex: 1,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ fontSize: 26, color: "#f0e8d8", fontFamily: "monospace" }}>⬡</div>
            <div
              style={{
                fontSize: 17,
                letterSpacing: 7,
                color: "#f0e8d8",
                fontFamily: "monospace",
                textTransform: "uppercase",
              }}
            >
              Scouta
            </div>
          </div>
          <div
            style={{
              fontSize: 14,
              letterSpacing: 4,
              color: "#444",
              fontFamily: "monospace",
              textTransform: "uppercase",
              display: "flex",
            }}
          >
            PROFILE
          </div>
        </div>

        {/* Main row: avatar + identity */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 48,
            marginTop: 60,
            position: "relative",
            zIndex: 1,
          }}
        >
          {avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatarUrl}
              alt=""
              width={180}
              height={180}
              style={{
                width: 180,
                height: 180,
                borderRadius: 999,
                objectFit: "cover",
                border: "2px solid #1a2a1a",
              }}
            />
          ) : (
            <div
              style={{
                width: 180,
                height: 180,
                borderRadius: 999,
                background: "#1a2a1a",
                border: "2px solid #2a4a2a",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 64,
                color: "#4a9a4a",
                fontFamily: "monospace",
                fontWeight: 700,
              }}
            >
              {initials(displayName)}
            </div>
          )}

          <div style={{ display: "flex", flexDirection: "column", flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize: 64,
                lineHeight: 1.05,
                color: "#f0e8d8",
                fontFamily: "Georgia, serif",
                letterSpacing: -1,
                display: "flex",
              }}
            >
              {displayName}
            </div>
            <div
              style={{
                fontSize: 22,
                color: "#666",
                fontFamily: "monospace",
                letterSpacing: 2,
                marginTop: 8,
                display: "flex",
              }}
            >
              @{username}
            </div>
          </div>
        </div>

        {/* Bio */}
        {bio && (
          <div
            style={{
              marginTop: 36,
              fontSize: 24,
              color: "#888",
              fontFamily: "Georgia, serif",
              lineHeight: 1.5,
              maxWidth: 1040,
              display: "flex",
              maxHeight: 110,
              overflow: "hidden",
              position: "relative",
              zIndex: 1,
            }}
          >
            {bio}
          </div>
        )}

        {/* Spacer + stats bottom */}
        <div style={{ flex: 1, display: "flex" }} />
        <div
          style={{
            display: "flex",
            gap: 64,
            position: "relative",
            zIndex: 1,
          }}
        >
          <Stat value={followers} label="FOLLOWERS" />
          <Stat value={comments} label="COMMENTS" />
          <Stat value={likes} label="LIKES" />
        </div>

        {/* Bottom strip */}
        <div
          style={{
            position: "absolute",
            bottom: 32,
            left: 80,
            right: 80,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: 14,
            color: "#444",
            fontFamily: "monospace",
            letterSpacing: 1.5,
          }}
        >
          <div>Live talk, sharpened.</div>
          <div>scouta.co/u/{username}</div>
        </div>
      </div>
    ),
    size
  );
}

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ fontSize: 36, color: "#f0e8d8", fontFamily: "monospace", fontWeight: 700 }}>
        {value.toLocaleString()}
      </div>
      <div
        style={{
          fontSize: 12,
          color: "#444",
          fontFamily: "monospace",
          letterSpacing: 4,
          marginTop: 4,
          textTransform: "uppercase",
          display: "flex",
        }}
      >
        {label}
      </div>
    </div>
  );
}
