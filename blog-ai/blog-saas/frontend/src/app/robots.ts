import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        disallow: ["/admin", "/api/", "/profile/edit"],
      },
    ],
    sitemap: "https://scouta.co/sitemap.xml",
  };
}
