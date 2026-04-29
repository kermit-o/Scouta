import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Live on Scouta";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export default async function LiveOGImage({ params }: { params: { room: string } }) {
  let title = "Live now on Scouta";
  let host = "Scouta";
  let viewers = 0;
  let isLive = true;
  let isPrivate = false;

  try {
    const res = await fetch(`${API}/api/v1/live/active`, { next: { revalidate: 30 } });
    if (res.ok) {
      const data = await res.json();
      const stream = (data.streams || []).find((s: any) => s.room_name === params.room);
      if (stream) {
        title = (stream.title || title).slice(0, 140);
        host = stream.host_display_name || stream.host_username || "Scouta";
        viewers = stream.viewer_count || 0;
        isPrivate = !!stream.is_private;
      } else {
        isLive = false;
        title = "Stream ended";
      }
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
          {isLive && (
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  background: "#e44",
                  color: "#fff",
                  padding: "8px 18px",
                  fontFamily: "monospace",
                  fontSize: 16,
                  letterSpacing: 5,
                  fontWeight: 700,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: 999,
                    background: "#fff",
                    display: "flex",
                  }}
                />
                LIVE
              </div>
              {isPrivate && (
                <div
                  style={{
                    fontSize: 14,
                    letterSpacing: 4,
                    color: "#9a6a4a",
                    border: "1px solid #2a1a10",
                    padding: "8px 14px",
                    fontFamily: "monospace",
                    textTransform: "uppercase",
                    display: "flex",
                  }}
                >
                  PRIVATE
                </div>
              )}
            </div>
          )}
        </div>

        {/* Spacer */}
        <div style={{ flex: 1, display: "flex" }} />

        {/* Title */}
        <div
          style={{
            fontSize: title.length > 80 ? 56 : 76,
            lineHeight: 1.1,
            color: "#f0e8d8",
            fontFamily: "Georgia, serif",
            letterSpacing: -1,
            display: "flex",
            marginBottom: 36,
            maxHeight: 360,
            overflow: "hidden",
            position: "relative",
            zIndex: 1,
          }}
        >
          {title}
        </div>

        {/* Host + viewers */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            position: "relative",
            zIndex: 1,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: 999,
                background: "#1a2a1a",
                border: "2px solid #2a4a2a",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 18,
                color: "#4a9a4a",
                fontFamily: "monospace",
                fontWeight: 700,
              }}
            >
              {(host[0] || "S").toUpperCase()}
            </div>
            <div style={{ fontSize: 24, color: "#aaa", fontFamily: "Georgia, serif" }}>
              hosted by {host}
            </div>
          </div>
          {isLive && viewers > 0 && (
            <div
              style={{
                fontSize: 20,
                color: "#666",
                fontFamily: "monospace",
                letterSpacing: 2,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span style={{ color: "#f0e8d8", fontWeight: 700 }}>{viewers.toLocaleString()}</span>
              <span style={{ textTransform: "uppercase", fontSize: 14 }}>WATCHING</span>
            </div>
          )}
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
          <div>scouta.co/live/{params.room}</div>
        </div>
      </div>
    ),
    size
  );
}
