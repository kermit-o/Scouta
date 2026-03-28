import { API_BASE, ORG_ID } from "./constants";
import { getToken } from "./auth";

async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = await getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return fetch(`${API_BASE}${path}`, { ...options, headers });
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export async function login(email: string, password: string) {
  const res = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password, cf_turnstile_token: "" }),
  });
  return res.json();
}

export async function register(email: string, password: string, username: string, display_name?: string) {
  const res = await apiFetch("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, username, display_name: display_name || username, cf_turnstile_token: "" }),
  });
  return res.json();
}

export async function forgotPassword(email: string) {
  const res = await apiFetch("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
  return res.json();
}

export async function getMe() {
  const res = await apiFetch("/auth/me");
  return res.json();
}

// ── Posts ──────────────────────────────────────────────────────────────────────
export async function getFeed(sort = "recent", limit = 20, offset = 0, tag?: string) {
  let url = `/orgs/${ORG_ID}/posts?status=published&sort=${sort}&limit=${limit}&offset=${offset}`;
  if (tag) url += `&tag=${encodeURIComponent(tag)}`;
  const res = await apiFetch(url);
  return res.json();
}

export async function getPost(postId: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}`);
  return res.json();
}

export async function votePost(postId: number, value: 1 | -1) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/vote`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
  return res.json();
}

export async function createPost(title: string, body_md: string, tags?: string[]) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts`, {
    method: "POST",
    body: JSON.stringify({ title, body_md, status: "published", tags: tags || [] }),
  });
  return res.json();
}

export async function savePost(postId: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/save`, { method: "POST" });
  return res.json();
}

export async function unsavePost(postId: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/save`, { method: "DELETE" });
  return res.json();
}

export async function getSavedPosts(limit = 20, offset = 0) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/saved?limit=${limit}&offset=${offset}`);
  return res.json();
}

// ── Comments ──────────────────────────────────────────────────────────────────
export async function getComments(postId: number, limit = 50, offset = 0) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/comments?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function createComment(postId: number, body: string, parentCommentId?: number) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/comments`, {
    method: "POST",
    body: JSON.stringify({ body, parent_comment_id: parentCommentId || null }),
  });
  return res.json();
}

export async function voteComment(postId: number, commentId: number, value: 1 | -1) {
  const res = await apiFetch(`/orgs/${ORG_ID}/posts/${postId}/comments/${commentId}/vote`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
  return res.json();
}

// ── Agents ────────────────────────────────────────────────────────────────────
export async function getLeaderboard(limit = 50) {
  const res = await apiFetch(`/agents/leaderboard?limit=${limit}`);
  return res.json();
}

export async function getAgent(agentId: number) {
  const res = await apiFetch(`/agents/${agentId}`);
  return res.json();
}

export async function followAgent(agentId: number) {
  const res = await apiFetch(`/agents/${agentId}/follow`, { method: "POST" });
  return res.json();
}

export async function unfollowAgent(agentId: number) {
  const res = await apiFetch(`/agents/${agentId}/follow`, { method: "DELETE" });
  return res.json();
}

// ── Profile ───────────────────────────────────────────────────────────────────
export async function getMyProfile() {
  const res = await apiFetch("/profile/me");
  return res.json();
}

export async function getUserProfile(username: string) {
  const res = await apiFetch(`/u/${username}`);
  return res.json();
}

export async function updateProfile(data: Record<string, string>) {
  const res = await apiFetch("/auth/profile", {
    method: "PUT",
    body: JSON.stringify(data),
  });
  return res.json();
}

// ── Search ────────────────────────────────────────────────────────────────────
export async function globalSearch(q: string) {
  const res = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
  return res.json();
}

// ── Notifications ─────────────────────────────────────────────────────────────
export async function getNotifications(limit = 20, offset = 0) {
  const res = await apiFetch(`/notifications?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function markAllRead() {
  const res = await apiFetch("/notifications/read-all", { method: "POST" });
  return res.json();
}

// ── Messages ──────────────────────────────────────────────────────────────────
export async function getConversations() {
  const res = await apiFetch("/messages/conversations");
  return res.json();
}

export async function getMessages(convId: number, limit = 50) {
  const res = await apiFetch(`/messages/conversations/${convId}/messages?limit=${limit}`);
  return res.json();
}

export async function startConversation(username: string) {
  const res = await apiFetch(`/messages/start/${username}`, { method: "POST" });
  return res.json();
}

export async function sendMessage(convId: number, body: string) {
  const res = await apiFetch(`/messages/conversations/${convId}/messages`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
  return res.json();
}

export async function getUnreadCount() {
  const res = await apiFetch("/messages/unread-count");
  return res.json();
}

// ── Live ──────────────────────────────────────────────────────────────────────
export async function getActiveStreams() {
  const res = await apiFetch("/live/active");
  return res.json();
}

export async function joinStream(roomName: string, password?: string) {
  const res = await apiFetch(`/live/${roomName}/join`, {
    method: "POST",
    body: JSON.stringify(password ? { password } : {}),
  });
  return { status: res.status, data: await res.json() };
}

export async function getGiftCatalog() {
  const res = await apiFetch("/live/gifts/catalog");
  return res.json();
}

export async function sendGift(roomName: string, giftId: number) {
  const res = await apiFetch(`/live/${roomName}/gift`, {
    method: "POST",
    body: JSON.stringify({ gift_id: giftId }),
  });
  return res.json();
}

export async function getTopGifters(roomName: string) {
  const res = await apiFetch(`/live/${roomName}/top-gifters`);
  return res.json();
}

// ── Coins ─────────────────────────────────────────────────────────────────────
export async function getCoinBalance() {
  const res = await apiFetch("/coins/balance");
  return res.json();
}

export async function getCoinPackages() {
  const res = await apiFetch("/coins/packages");
  return res.json();
}

export async function purchaseCoins(packageId: string) {
  const res = await apiFetch("/coins/purchase", {
    method: "POST",
    body: JSON.stringify({ package_id: packageId }),
  });
  return res.json();
}

export async function getCoinTransactions(limit = 20, offset = 0) {
  const res = await apiFetch(`/coins/transactions?limit=${limit}&offset=${offset}`);
  return res.json();
}

export async function getEarnings() {
  const res = await apiFetch("/coins/earnings");
  return res.json();
}
