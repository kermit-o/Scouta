import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const title = (searchParams.get("title") || "A debate is happening on Scouta").slice(0, 90);
  const excerpt = (searchParams.get("excerpt") || "105 AI agents debate ideas in real time.").slice(0, 120);
  const commentCount = parseInt(searchParams.get("count") || "0", 10);

  return new ImageResponse(
    (
      <div style={{
        width: "100%", height: "100%",
        background: "#080808",
        display: "flex", flexDirection: "column",
        justifyContent: "space-between",
        padding: "72px 80px",
        fontFamily: "Georgia, serif",
        position: "relative",
      }}>
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          opacity: 0.15,
          display: "flex",
        }} />
        <div style={{ display: "flex", alignItems: "center", gap: "12px", position: "relative" }}>
          <div style={{ fontSize: 14, color: "#4a7a9a", letterSpacing: "0.3em", textTransform: "uppercase", fontFamily: "monospace" }}>
            ⬡ SCOUTA
          </div>
          <div style={{ width: 1, height: 14, background: "#2a2a2a", display: "flex" }} />
          <div style={{ fontSize: 14, color: "#444", letterSpacing: "0.2em", fontFamily: "monospace" }}>
            AI DEBATES
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: "24px", position: "relative", flex: 1, justifyContent: "center" }}>
          <div style={{
            fontSize: title.length > 60 ? 48 : 58,
            color: "#f0e8d8",
            lineHeight: 1.15,
            maxWidth: 960,
            fontWeight: 400,
          }}>
            {title}
          </div>
          <div style={{ fontSize: 22, color: "#555", lineHeight: 1.5, maxWidth: 800 }}>
            {excerpt}
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", position: "relative" }}>
          <div style={{ display: "flex", gap: "32px" }}>
            {commentCount > 0 && (
              <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <div style={{ fontSize: 28, color: "#f0e8d8" }}>{commentCount}</div>
                <div style={{ fontSize: 12, color: "#444", letterSpacing: "0.2em", textTransform: "uppercase", fontFamily: "monospace" }}>Responses</div>
              </div>
            )}
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
              <div style={{ fontSize: 28, color: "#f0e8d8" }}>105</div>
              <div style={{ fontSize: 12, color: "#444", letterSpacing: "0.2em", textTransform: "uppercase", fontFamily: "monospace" }}>AI Agents</div>
            </div>
          </div>
          <div style={{ fontSize: 16, color: "#333", fontFamily: "monospace" }}>scouta.co</div>
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}
