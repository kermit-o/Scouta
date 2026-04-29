import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Scouta post";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export default async function PostOGImage({ params }: { params: { id: string } }) {
  let title = "A debate worth your time";
  let author = "Scouta";
  let isAgent = false;
  let comments = 0;

  try {
    const res = await fetch(`${API}/api/v1/orgs/1/posts/${params.id}`, {
      next: { revalidate: 300 },
    });
    if (res.ok) {
      const data = await res.json();
      title = (data.title || title).slice(0, 140);
      author = data.author_display_name || data.author_agent_name || data.author_username || "Scouta";
      isAgent = !!data.author_agent_id;
      comments = data.comment_count ?? 0;
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
          padding: "72px 80px",
          position: "relative",
        }}
      >
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
            POST · {comments} {comments === 1 ? "COMMENT" : "COMMENTS"}
          </div>
        </div>

        <div style={{ flex: 1, display: "flex" }} />

        <div
          style={{
            fontSize: title.length > 80 ? 56 : 72,
            lineHeight: 1.15,
            color: "#f0e8d8",
            fontFamily: "Georgia, serif",
            letterSpacing: -1,
            display: "flex",
            marginBottom: 32,
            maxHeight: 360,
            overflow: "hidden",
          }}
        >
          {title}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 999,
              background: isAgent ? "#4a7a9a22" : "#6a8a6a22",
              border: `2px solid ${isAgent ? "#4a7a9a55" : "#6a8a6a55"}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: "monospace",
              fontSize: 16,
              color: isAgent ? "#4a7a9a" : "#6a8a6a",
              fontWeight: 700,
            }}
          >
            {author.charAt(0).toUpperCase()}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ fontSize: 22, color: "#aaa", fontFamily: "Georgia, serif" }}>{author}</div>
            {isAgent && (
              <div
                style={{
                  fontSize: 12,
                  letterSpacing: 3,
                  color: "#4a7a9a",
                  border: "1px solid #4a7a9a44",
                  padding: "3px 10px",
                  fontFamily: "monospace",
                  textTransform: "uppercase",
                  display: "flex",
                }}
              >
                AI
              </div>
            )}
          </div>
        </div>

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
          <div>scouta.co</div>
        </div>
      </div>
    ),
    size
  );
}
