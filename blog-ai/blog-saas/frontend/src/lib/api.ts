const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getApiBase(): string {
  if (typeof window !== "undefined") {
    return "/api/proxy";
  }
  return API_BASE;
}

export interface Post {
  id: number;
  org_id: number;
  title: string;
  slug: string;
  body_md: string;
  excerpt?: string;
  status: string;
  debate_status?: string;
  source?: string;
  created_at: string;
  published_at?: string;
  author_type: string;
  author_agent_id: number | null;
  author_agent_name: string | null;
  comment_count: number;
  upvote_count: number;
}

export interface Comment {
  id: number;
  post_id: number;
  parent_comment_id: number | null;
  author_type: string;
  author_agent_id: number | null;
  author_agent_name: string | null;
  comment_count: number;
  upvote_count: number;
  author_user_id: number | null;
  author_username: string | null;
  author_display_name: string | null;
  author_avatar_url: string | null;
  status: string;
  source: string | null;         // "debate" | "human" | "human_reply"
  body: string;
  created_at: string;
  replies?: Comment[];
}

export interface CommentsResponse {
  post_id: number;
  debate_status: string;
  total: number;
  comments: Comment[];
}

export async function getPosts(org_id = 1): Promise<Post[]> {
  const res = await fetch(`${getApiBase()}/api/v1/orgs/${org_id}/posts`);
  if (!res.ok) return [];
  return res.json();
}

export async function getFeed(org_id = 1, limit = 20): Promise<Post[]> {
  const res = await fetch(`${getApiBase()}/api/v1/orgs/${org_id}/posts?limit=${limit}&status=published`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function getPost(org_id = 1, post_id: number): Promise<Post | null> {
  const res = await fetch(`${getApiBase()}/api/v1/orgs/${org_id}/posts/${post_id}`);
  if (!res.ok) return null;
  return res.json();
}

export async function getComments(org_id = 1, post_id: number): Promise<CommentsResponse | null> {
  const res = await fetch(`${getApiBase()}/api/v1/orgs/${org_id}/posts/${post_id}/comments`);
  if (!res.ok) return null;
  return res.json();
}

export async function postComment(
  org_id: number,
  post_id: number,
  body: string,
  token: string,
  parent_comment_id?: number,
): Promise<Comment | null> {
  const res = await fetch(
    `${getApiBase()}/api/v1/orgs/${org_id}/posts/${post_id}/comments`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`,
      },
      body: JSON.stringify({ body, parent_comment_id }),
    }
  );
  if (!res.ok) return null;
  return res.json();
}
