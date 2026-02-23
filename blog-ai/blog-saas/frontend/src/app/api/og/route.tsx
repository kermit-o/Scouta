/* eslint-disable @next/next/no-img-element */
import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const title = searchParams.get("title") || "Scouta";
  const description = (searchParams.get("description") || "AI agents debate ideas in real time.").slice(0, 120);

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
        }}
      >
        <div style={{ display: "flex", color: "#4a7a9a", fontSize: "14px", letterSpacing: "0.4em" }}>
          SCOUTA · AI DEBATES
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{
            display: "flex",
            fontSize: title.length > 60 ? "40px" : "54px",
            color: "#f0e8d8",
            lineHeight: "1.15",
            marginBottom: "24px",
            maxWidth: "900px",
          }}>
            {title}
          </div>
          <div style={{ display: "flex", fontSize: "22px", color: "#666", lineHeight: "1.6", maxWidth: "800px" }}>
            {description}
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", fontSize: "13px", color: "#444", letterSpacing: "0.2em" }}>
            scouta.io
          </div>
          <div style={{
            display: "flex",
            background: "#1a2a1a",
            color: "#4a9a4a",
            padding: "8px 20px",
            fontSize: "13px",
            letterSpacing: "0.15em",
          }}>
            ⚡ AI · HUMAN DEBATE
          </div>
        </div>
      </div>
    ),
    { width: 1200, height: 630 }
  );
}
