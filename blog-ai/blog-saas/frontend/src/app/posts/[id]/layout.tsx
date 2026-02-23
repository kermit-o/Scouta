import type { Metadata } from "next";

const API = "https://scouta-production.up.railway.app";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  try {
    const { id } = await params;
    const res = await fetch(`${API}/api/v1/orgs/1/posts/${id}`, {
      next: { revalidate: 3600 }
    });
    if (!res.ok) return { title: "Scouta" };
    const post = await res.json();
    const title = post.title || "Scouta";
    const description = post.excerpt || (post.body_md || "").slice(0, 160) || "AI-powered debates";
    const url = `https://serene-eagerness-production.up.railway.app/posts/${id}`;

    return {
      title,
      description,
      openGraph: {
        title,
        description,
        url,
        siteName: "Scouta",
        type: "article",
      },
      twitter: {
        card: "summary_large_image",
        title,
        description,
      },
    };
  } catch {
    return { title: "Scouta" };
  }
}

export default function PostLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
