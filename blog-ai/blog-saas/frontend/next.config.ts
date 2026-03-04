import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com https://accounts.google.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://challenges.cloudflare.com",
              "font-src 'self' https://fonts.gstatic.com",
              "frame-src https://challenges.cloudflare.com https://accounts.google.com",
              "connect-src 'self' https://scouta-production.up.railway.app https://challenges.cloudflare.com",
              "img-src 'self' data: https: blob:",
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
