import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/" },
    sitemap: "https://serene-eagerness-production.up.railway.app/sitemap.xml",
  };
}
