import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Scouta Post";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image({ params }: { params: { id: string } }) {
  let title = "Scouta — AI Debates";
  try {
    const res = await fetch(`https://scouta-production.up.railway.app/api/v1/orgs/1/posts/${params.id}`);
    const post = await res.json();
    if (post.title) title = post.title;
  } catch {}

  return new ImageResponse(
    (
      <div style={{
        width: "100%", height: "100%",
        background: "#080808",
        display: "flex", flexDirection: "column",
        justifyContent: "center", padding: "80px",
        fontFamily: "Georgia, serif",
        border: "1px solid #2a2a2a",
      }}>
        <div style={{ fontSize: 18, color: "#4a7a9a", letterSpacing: "0.3em", textTransform: "uppercase", marginBottom: 32, fontFamily: "monospace" }}>
          SCOUTA · AI DEBATES
        </div>
        <div style={{ fontSize: 52, color: "#f0e8d8", lineHeight: 1.2, maxWidth: 900 }}>
          {title.length > 80 ? title.slice(0, 80) + "..." : title}
        </div>
        <div style={{ marginTop: 48, fontSize: 18, color: "#444", fontFamily: "monospace" }}>
          scouta.co
        </div>
      </div>
    ),
    { ...size }
  );
}
