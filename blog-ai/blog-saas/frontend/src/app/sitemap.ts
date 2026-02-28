import { MetadataRoute } from "next";

const BASE = "https://scouta.co";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Static pages
  const static_pages = [
    { url: BASE, lastModified: new Date(), changeFrequency: "daily" as const, priority: 1 },
    { url: `${BASE}/posts`, lastModified: new Date(), changeFrequency: "hourly" as const, priority: 0.9 },
    { url: `${BASE}/about`, lastModified: new Date(), changeFrequency: "monthly" as const, priority: 0.5 },
    { url: `${BASE}/privacy`, lastModified: new Date(), changeFrequency: "monthly" as const, priority: 0.3 },
  ];

  // Dynamic posts
  let post_pages: MetadataRoute.Sitemap = [];
  try {
    const res = await fetch(`https://scouta-production.up.railway.app/api/v1/orgs/1/posts?limit=200&status=published`, { next: { revalidate: 3600 } });
    const data = await res.json();
    const posts = Array.isArray(data) ? data : data.posts || [];
    post_pages = posts.map((p: any) => ({
      url: `${BASE}/posts/${p.id}`,
      lastModified: new Date(p.created_at),
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));
  } catch {}

  return [...static_pages, ...post_pages];
}
