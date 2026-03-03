import { MetadataRoute } from "next";
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/admin", "/billing", "/api/"] },
    sitemap: "https://scouta.co/sitemap.xml",
  };
}
