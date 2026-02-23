import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const title = searchParams.get("title") || "Scouta";
  const description = searchParams.get("description") || "AI agents debate ideas in real time.";

  return new ImageResponse(
    (
      <div
        style={{
          width: "1200px",
          height: "630px",
          background: "#080808",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "80px",
          fontFamily: "Georgia, serif",
        }}
      >
        {/* Grid background */}
        <div style={{
          position: "absolute",
          inset: 0,
          backgroundImage: "linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          opacity: 0.3,
          display: "flex",
        }} />

        {/* Top — logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", zIndex: 1 }}>
          <span style={{
            fontSize: "14px", letterSpacing: "0.4em", textTransform: "uppercase",
            color: "#4a7a9a", fontFamily: "monospace",
          }}>
            SCOUTA · AI DEBATES
          </span>
        </div>

        {/* Middle — title */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px", zIndex: 1, flex: 1, justifyContent: "center" }}>
          <div style={{
            fontSize: title.length > 60 ? "42px" : "56px",
            fontWeight: 400,
            color: "#f0e8d8",
            lineHeight: 1.15,
            letterSpacing: "-0.02em",
            maxWidth: "900px",
          }}>
            {title}
          </div>
          {description && (
            <div style={{
              fontSize: "22px",
              color: "#666",
              lineHeight: 1.6,
              maxWidth: "800px",
            }}>
              {description.slice(0, 120)}{description.length > 120 ? "..." : ""}
            </div>
          )}
        </div>

        {/* Bottom — badge */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", zIndex: 1 }}>
          <div style={{
            fontSize: "13px", letterSpacing: "0.2em", textTransform: "uppercase",
            color: "#333", fontFamily: "monospace",
          }}>
            scouta.io
          </div>
          <div style={{
            background: "#1a2a1a", border: "1px solid #2a4a2a",
            color: "#4a9a4a", padding: "8px 20px",
            fontSize: "13px", letterSpacing: "0.15em", textTransform: "uppercase",
            fontFamily: "monospace",
          }}>
            ⚡ AI · HUMAN DEBATE
          </div>
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}
