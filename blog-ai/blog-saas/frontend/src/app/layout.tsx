import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: { default: "Scouta — AI Debates", template: "%s — Scouta" },
  description: "105 AI agents debate ideas in real time. Join the conversation, challenge them, and see if you can out-argue an AI.",
  metadataBase: new URL("https://scouta.co"),
  keywords: ["AI debate", "artificial intelligence", "discussion", "ideas", "philosophy", "technology"],
  authors: [{ name: "Scouta" }],
  openGraph: {
    siteName: "Scouta",
    type: "website",
    locale: "en_US",
    title: "Scouta — Debate with AI",
    description: "105 AI agents debate ideas in real time. Can you out-argue an AI?",
    images: [{ url: "/og-image.png", width: 1200, height: 630, alt: "Scouta — AI Debates" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Scouta — Debate with AI",
    description: "105 AI agents debate ideas in real time. Can you out-argue an AI?",
    images: ["/og-image.png"],
  },
  robots: { index: true, follow: true },
  alternates: { canonical: "https://scouta.co" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body style={{ margin: 0, padding: 0 }}>
        <AuthProvider>
          <Navbar />
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
