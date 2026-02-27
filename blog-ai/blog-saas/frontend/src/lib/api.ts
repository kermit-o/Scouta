const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getApiBase(): string {
  return process.env.NEXT_PUBLIC_API_BROWSER_URL
      || process.env.NEXT_PUBLIC_API_URL
      || "http://localhost:8000";
}

export interface Post {
  id: number;
  org_id: number;
  title: string;
  slug: string;
  body_md: string;
  tags?: string[];
  upvotes?: number;
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

export async function getPost(org_id = 1, post_id: number): Promise<Post | null> {
  const res = await fetch(
    `${getApiBase()}/api/v1/orgs/${org_id}/posts/${post_id}`,
    { cache: "no-store" }
  );
  if (!res.ok) return null;
  return res.json();
}

export async function getFeed(org_id = 1, limit = 20): Promise<Post[]> {
  const res = await fetch(`${getApiBase()}/api/v1/orgs/${org_id}/posts?limit=${limit}&status=published`, { cache: "no-store" });
  if (!res.ok) return [];
  return res.json();
}

export async function getComments(
  orgId: number,
  postId: number,
  limit = 50,
  offset = 0,
) {
  const res = await fetch(
    `${getApiBase()}/api/v1/orgs/${orgId}/posts/${postId}/comments?limit=${limit}&offset=${offset}`,
    { cache: "no-store" }
  );
  if (!res.ok) return { comments: [], total: 0 };
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
export async function getPosts(orgId: number, limit = 15, offset = 0, sort = "recent", tag = "") {
  const API = getApiBase();
  let url = `${API}/api/v1/orgs/${orgId}/posts?limit=${limit}&offset=${offset}&status=published`;
  if (sort && sort !== "recent") url += `&sort=${sort}`;
  if (tag) url += `&tag=${encodeURIComponent(tag)}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) return { posts: [], total: 0 };
  const data = await res.json();
  if (Array.isArray(data)) return { posts: data, total: data.length };
  return data;
}