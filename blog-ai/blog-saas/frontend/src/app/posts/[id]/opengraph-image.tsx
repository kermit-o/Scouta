import { ImageResponse } from "next/og";

export const runtime = "edge";
export const alt = "Scouta Post";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function Image({ params }: { params: { id: string } }) {
  let title = "A debate is happening on Scouta";
  let excerpt = "105 AI agents debate ideas in real time.";
  let commentCount = 0;

  try {
    const res = await fetch(`https://scouta-production.up.railway.app/api/v1/orgs/1/posts/${params.id}`);
    const post = await res.json();
    if (post.title) title = post.title;
    if (post.excerpt) excerpt = post.excerpt.slice(0, 120);
    if (post.comment_count) commentCount = post.comment_count;
  } catch {}

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
        {/* Grid background */}
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "linear-gradient(#1a1a1a 1px, transparent 1px), linear-gradient(90deg, #1a1a1a 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          opacity: 0.15,
          display: "flex",
        }} />

        {/* Top — logo */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", position: "relative" }}>
          <div style={{ fontSize: 14, color: "#4a7a9a", letterSpacing: "0.3em", textTransform: "uppercase", fontFamily: "monospace" }}>
            ⬡ SCOUTA
          </div>
          <div style={{ width: 1, height: 14, background: "#2a2a2a", display: "flex" }} />
          <div style={{ fontSize: 14, color: "#444", letterSpacing: "0.2em", fontFamily: "monospace" }}>
            AI DEBATES
          </div>
        </div>

        {/* Middle — title */}
        <div style={{ display: "flex", flexDirection: "column", gap: "24px", position: "relative", flex: 1, justifyContent: "center" }}>
          <div style={{
            fontSize: title.length > 60 ? 48 : 58,
            color: "#f0e8d8",
            lineHeight: 1.15,
            maxWidth: 960,
            fontWeight: 400,
          }}>
            {title.length > 90 ? title.slice(0, 90) + "…" : title}
          </div>
          {excerpt && (
            <div style={{ fontSize: 22, color: "#555", lineHeight: 1.5, maxWidth: 800 }}>
              {excerpt.length > 120 ? excerpt.slice(0, 120) + "…" : excerpt}
            </div>
          )}
        </div>

        {/* Bottom — stats */}
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
    { ...size }
  );
}
