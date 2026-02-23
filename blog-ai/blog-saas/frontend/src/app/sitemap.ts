import type { MetadataRoute } from "next";

const BASE = "https://serene-eagerness-production.up.railway.app";
const API = "https://scouta-production.up.railway.app";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticPages = [
    { url: BASE, lastModified: new Date(), changeFrequency: "daily" as const, priority: 1 },
    { url: `${BASE}/posts`, lastModified: new Date(), changeFrequency: "hourly" as const, priority: 0.9 },
    { url: `${BASE}/about`, lastModified: new Date(), changeFrequency: "monthly" as const, priority: 0.5 },
    { url: `${BASE}/privacy`, lastModified: new Date(), changeFrequency: "monthly" as const, priority: 0.3 },
  ];

  try {
    const res = await fetch(`${API}/api/v1/orgs/1/posts?limit=200&status=published`, {
      next: { revalidate: 3600 }
    });
    const data = await res.json();
    const posts = Array.isArray(data) ? data : data.posts || [];
    const postPages = posts.map((p: any) => ({
      url: `${BASE}/posts/${p.id}`,
      lastModified: new Date(p.created_at || Date.now()),
      changeFrequency: "weekly" as const,
      priority: 0.7,
    }));
    return [...staticPages, ...postPages];
  } catch {
    return staticPages;
  }
}
