export interface User {
  id: number;
  email: string;
  username: string;
  display_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  is_verified: boolean;
  is_superuser: boolean;
}

export interface Post {
  id: number;
  title: string;
  slug: string;
  body_md: string;
  excerpt: string | null;
  status: string;
  media_url: string | null;
  media_type: string | null;
  author_type: string;
  author_user_id: number | null;
  author_agent_id: number | null;
  author_display_name?: string;
  author_username?: string;
  author_agent_name?: string;
  author_avatar_url?: string;
  upvote_count: number;
  downvote_count: number;
  comment_count: number;
  debate_status: string;
  created_at: string;
  published_at: string | null;
  tags?: string[];
}

export interface Comment {
  id: number;
  body: string;
  author_type: string;
  author_display_name: string | null;
  author_username: string | null;
  author_avatar_url: string | null;
  upvotes: number;
  downvotes: number;
  parent_comment_id: number | null;
  source: string;
  created_at: string;
  replies?: Comment[];
}

export interface Agent {
  id: number;
  display_name: string;
  handle: string;
  bio: string | null;
  topics: string | null;
  style: string | null;
  reputation_score: number;
  is_enabled: boolean;
  total_comments?: number;
  total_upvotes?: number;
  follower_count?: number;
  is_following?: boolean;
}

export interface LiveStream {
  room_name: string;
  title: string;
  viewer_count: number;
  host_username: string;
  host_display_name: string;
  description: string;
  started_at: string;
  is_private: boolean;
  access_type: string;
  entry_coin_cost: number;
}

export interface Gift {
  id: number;
  name: string;
  emoji: string;
  coin_cost: number;
  animation_type: string;
}

export interface CoinPackage {
  id: string;
  coins: number;
  price_cents: number;
}

export interface Conversation {
  id: number;
  other_user: {
    id: number;
    username: string;
    display_name: string;
    avatar_url: string | null;
  };
  last_message_preview: string | null;
  last_message_at: string | null;
  unread: number;
}

export interface Message {
  id: number;
  sender_id: number;
  body: string;
  read: boolean;
  created_at: string;
}

export interface Notification {
  id: number;
  type: string;
  message: string;
  read: boolean;
  post_id: number | null;
  comment_id: number | null;
  created_at: string;
}
