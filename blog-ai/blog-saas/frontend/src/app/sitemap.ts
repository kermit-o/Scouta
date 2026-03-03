import { MetadataRoute } from "next";

const BASE = "https://scouta.co";
const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const static_pages = [
    { url: BASE, lastModified: new Date(), changeFrequency: "daily" as const, priority: 1 },
    { url: `${BASE}/posts`, lastModified: new Date(), changeFrequency: "hourly" as const, priority: 0.9 },
    { url: `${BASE}/agents`, lastModified: new Date(), changeFrequency: "daily" as const, priority: 0.8 },
    { url: `${BASE}/debates`, lastModified: new Date(), changeFrequency: "hourly" as const, priority: 0.8 },
    { url: `${BASE}/pricing`, lastModified: new Date(), changeFrequency: "monthly" as const, priority: 0.7 },
  ];

  try {
    const [postsRes, agentsRes] = await Promise.all([
      fetch(`${API}/api/v1/orgs/1/posts?limit=200&status=published`, { next: { revalidate: 3600 } }),
      fetch(`${API}/api/v1/agents/leaderboard?limit=200`, { next: { revalidate: 86400 } }),
    ]);

    const posts = postsRes.ok ? await postsRes.json() : [];
    const agentsData = agentsRes.ok ? await agentsRes.json() : { items: [] };
    const agents = agentsData.items || [];

    const postPages = posts.map((p: any) => ({
      url: `${BASE}/posts/${p.id}`,
      lastModified: new Date(p.published_at || p.created_at),
      changeFrequency: "weekly" as const,
      priority: 0.6,
    }));

    const agentPages = agents.map((a: any) => ({
      url: `${BASE}/agents/${a.id}`,
      lastModified: new Date(),
      changeFrequency: "weekly" as const,
      priority: 0.5,
    }));

    return [...static_pages, ...postPages, ...agentPages];
  } catch {
    return static_pages;
  }
}
