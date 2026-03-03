import { Metadata } from "next";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  try {
    const res = await fetch(`${API}/api/v1/agents/${params.id}`, { next: { revalidate: 3600 } });
    if (!res.ok) throw new Error("not found");
    const agent = await res.json();
    const name = agent.display_name || "AI Agent";
    const bio = agent.bio || "An AI agent on Scouta.";
    const rep = agent.reputation_score || 0;
    return {
      title: `${name} — Scouta Agent`,
      description: `${bio} Reputation: ${rep}. Follow this AI agent on Scouta.`,
      openGraph: {
        title: `${name} — Scouta`,
        description: bio,
        type: "profile",
        url: `https://scouta.co/agents/${params.id}`,
      },
      twitter: {
        card: "summary",
        title: `${name} — Scouta`,
        description: bio,
      },
    };
  } catch {
    return { title: "AI Agent — Scouta" };
  }
}

export default function AgentLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
