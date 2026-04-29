import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AuthProvider } from "@/context/AuthContext";
import Navbar from "@/components/Navbar";

const TITLE = "Scouta — Live talk, sharpened";
const DESCRIPTION =
  "The streaming platform for podcasters, debaters, coaches, and anyone who actually talks. AI co-hosts that fact-check, contradict, and keep the conversation honest.";

export const metadata: Metadata = {
  title: { default: TITLE, template: "%s — Scouta" },
  description: DESCRIPTION,
  metadataBase: new URL("https://scouta.co"),
  keywords: [
    "live streaming",
    "live talk",
    "podcasting",
    "debate",
    "AI co-host",
    "creator economy",
    "live shows",
    "audio video",
  ],
  authors: [{ name: "Scouta" }],
  openGraph: {
    siteName: "Scouta",
    type: "website",
    locale: "en_US",
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
    creator: "@scouta",
  },
  robots: { index: true, follow: true },
  alternates: { canonical: "https://scouta.co" },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#080808",
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
