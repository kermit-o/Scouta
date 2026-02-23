import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const title = searchParams.get("title") || "Scouta";
  const description = searchParams.get("description") || "AI agents debate ideas in real time.";
  const shortDesc = description.length > 120 ? description.slice(0, 120) + "..." : description;

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
          {
            type: "div",
            props: {
              style: { fontSize: "14px", letterSpacing: "0.4em", color: "#4a7a9a", display: "flex" },
              children: "SCOUTA · AI DEBATES",
            },
          },
          {
            type: "div",
            props: {
              style: { display: "flex", flexDirection: "column", gap: "24px" },
              children: [
                {
                  type: "div",
                  props: {
                    style: {
                      fontSize: title.length > 60 ? "42px" : "54px",
                      color: "#f0e8d8", lineHeight: "1.15", letterSpacing: "-0.02em",
                      maxWidth: "900px", display: "flex",
                    },
                    children: title,
                  },
                },
                {
                  type: "div",
                  props: {
                    style: { fontSize: "22px", color: "#666", lineHeight: "1.6", maxWidth: "800px", display: "flex" },
                    children: shortDesc,
                  },
                },
              ],
            },
          },
          {
            type: "div",
            props: {
              style: { display: "flex", justifyContent: "space-between", alignItems: "center" },
              children: [
                {
                  type: "div",
                  props: {
                    style: { fontSize: "13px", color: "#333", letterSpacing: "0.2em", display: "flex" },
                    children: "scouta.io",
                  },
                },
                {
                  type: "div",
                  props: {
                    style: {
                      background: "#1a2a1a", border: "1px solid #2a4a2a",
                      color: "#4a9a4a", padding: "8px 20px",
                      fontSize: "13px", letterSpacing: "0.15em", display: "flex",
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
