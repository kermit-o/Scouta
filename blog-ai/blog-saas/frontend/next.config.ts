import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [
      // Legacy paths consolidated into the new IA
      { source: "/welcome", destination: "/manifesto", permanent: true },
      { source: "/best-debates", destination: "/posts?sort=top", permanent: true },
      { source: "/debates", destination: "/posts", permanent: true },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com https://static.cloudflareinsights.com https://accounts.google.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "frame-src https://challenges.cloudflare.com https://accounts.google.com",
              "connect-src 'self' wss://scouta-pi70lg8z.livekit.cloud https://scouta-pi70lg8z.livekit.cloud wss://*.livekit.cloud https://*.livekit.cloud https://scouta-production.up.railway.app wss://scouta-production.up.railway.app https://challenges.cloudflare.com https://cloudflareinsights.com https://*.r2.cloudflarestorage.com https://pub-fa5f65f875ac451bb5ddc548aebb08a7.r2.dev",
              "img-src 'self' data: https: blob:",
              "worker-src blob:",
              "media-src 'self' https://*.livekit.cloud blob: https://pub-fa5f65f875ac451bb5ddc548aebb08a7.r2.dev https://*.r2.dev",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
