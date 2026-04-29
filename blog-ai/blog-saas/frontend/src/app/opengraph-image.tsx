import { ImageResponse } from "next/og";

// Default OG image for the homepage and any route that doesn't override it.
// Next.js renders this on demand at /opengraph-image and references it
// automatically for og:image and twitter:image tags.

export const runtime = "edge";
export const alt = "Scouta — Live talk, sharpened.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function OGImage() {
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
            opacity: 0.25,
            display: "flex",
          }}
        />

        {/* Header / brand */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "16px",
            position: "relative",
            zIndex: 1,
          }}
        >
          <div
            style={{
              fontSize: 28,
              color: "#f0e8d8",
              fontFamily: "monospace",
            }}
          >
            ⬡
          </div>
          <div
            style={{
              fontSize: 20,
              letterSpacing: 8,
              color: "#f0e8d8",
              fontFamily: "monospace",
              textTransform: "uppercase",
            }}
          >
            Scouta
          </div>
        </div>

        {/* Eyebrow */}
        <div
          style={{
            marginTop: 80,
            fontSize: 18,
            letterSpacing: 6,
            color: "#4a7a9a",
            fontFamily: "monospace",
            textTransform: "uppercase",
            display: "flex",
          }}
        >
          For people who actually talk
        </div>

        {/* H1 */}
        <div
          style={{
            marginTop: 24,
            fontSize: 128,
            lineHeight: 1.05,
            color: "#f0e8d8",
            fontFamily: "Georgia, serif",
            letterSpacing: -2,
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div>Live talk,</div>
          <div style={{ color: "#888", fontStyle: "italic" }}>sharpened.</div>
        </div>

        {/* Glow accent */}
        <div
          style={{
            position: "absolute",
            bottom: -100,
            right: -100,
            width: 500,
            height: 500,
            background:
              "radial-gradient(circle, rgba(74,122,154,0.15) 0%, transparent 70%)",
            display: "flex",
          }}
        />

        {/* Tagline bottom */}
        <div
          style={{
            position: "absolute",
            bottom: 64,
            left: 80,
            right: 80,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: 18,
            color: "#666",
            fontFamily: "monospace",
            letterSpacing: 1.5,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div
              style={{
                width: 10,
                height: 10,
                borderRadius: 999,
                background: "#e44",
                display: "flex",
              }}
            />
            <div>Live debates · AI co-hosts · 80% to creators</div>
          </div>
          <div style={{ display: "flex", color: "#444" }}>scouta.co</div>
        </div>
      </div>
    ),
    size
  );
}
