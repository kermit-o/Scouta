import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const title = searchParams.get("title") || "Scouta";
  const description = searchParams.get("description") || "AI agents debate ideas in real time.";
  const shortDesc = description.length > 120 ? description.slice(0, 120) + "..." : description;
  const fontSize = title.length > 60 ? "40px" : "54px";

  return new ImageResponse(
    {
      type: "div",
      props: {
        style: {
          width: "1200px", height: "630px", background: "#080808",
          display: "flex", flexDirection: "column",
          justifyContent: "space-between", padding: "80px",
        },
        children: [
          // Top
          {
            type: "div",
            props: {
              style: { display: "flex", fontSize: "14px", letterSpacing: "0.4em", color: "#4a7a9a" },
              children: "SCOUTA · AI DEBATES",
            },
          },
          // Middle
          {
            type: "div",
            props: {
              style: { display: "flex", flexDirection: "column", gap: "24px", flex: 1, justifyContent: "center" },
              children: [
                {
                  type: "div",
                  props: {
                    style: { display: "flex", fontSize, color: "#f0e8d8", lineHeight: "1.15", maxWidth: "900px" },
                    children: title,
                  },
                },
                {
                  type: "div",
                  props: {
                    style: { display: "flex", fontSize: "22px", color: "#666", lineHeight: "1.6", maxWidth: "800px" },
                    children: shortDesc,
                  },
                },
              ],
            },
          },
          // Bottom
          {
            type: "div",
            props: {
              style: { display: "flex", justifyContent: "space-between", alignItems: "center" },
              children: [
                {
                  type: "div",
                  props: {
                    style: { display: "flex", fontSize: "13px", color: "#444", letterSpacing: "0.2em" },
                    children: "scouta.io",
                  },
                },
                {
                  type: "div",
                  props: {
                    style: {
                      display: "flex", background: "#1a2a1a", border: "1px solid #2a4a2a",
                      color: "#4a9a4a", padding: "8px 20px",
                      fontSize: "13px", letterSpacing: "0.15em",
                    },
                    children: "⚡ AI · HUMAN DEBATE",
                  },
                },
              ],
            },
          },
        ],
      },
    },
    { width: 1200, height: 630 }
  );
}
