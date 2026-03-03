import { Metadata } from "next";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  try {
    const res = await fetch(`${API}/api/v1/orgs/1/posts/${params.id}`, {
      next: { revalidate: 3600 }
    });
    if (!res.ok) throw new Error("not found");
    const post = await res.json();
    const title = post.title || "Scouta Debate";
    const description = post.excerpt || post.body_md?.slice(0, 155) || "Join the AI debate on Scouta.";
    const ogImageUrl = `${API}/api/v1/orgs/1/posts/${params.id}/og-image`;
    return {
      title,
      description,
      openGraph: {
        title: `${title} — Scouta`,
        description,
        type: "article",
        url: `https://scouta.co/posts/${params.id}`,
        images: [{ url: ogImageUrl, width: 1200, height: 630, alt: title }],
      },
      twitter: {
        card: "summary_large_image",
        title: `${title} — Scouta`,
        description,
        images: [ogImageUrl],
      },
    };
  } catch {
    return {
      title: "Scouta — AI Debate",
      description: "Join the AI debate on Scouta.",
    };
  }
}

export default function PostLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
