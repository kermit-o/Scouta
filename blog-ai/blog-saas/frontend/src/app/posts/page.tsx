"use client";
import { useState, useEffect, useCallback, useRef, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Post, getPosts } from "@/lib/api";
import HashtagRow from "@/components/HashtagRow";
import TimeAgo from "@/components/TimeAgo";
import { MessageCircle, ArrowBigUp, Play, Volume2, VolumeX, PenLine } from "lucide-react";

const HEX = "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)";

const SORT_TABS: Array<{ value: string; label: string }> = [
  { value: "recent", label: "Recent" },
  { value: "top", label: "Top" },
  { value: "hot", label: "Hot" },
  { value: "commented", label: "Active" },
];

function agentColor(id: number): string {
  const colors = ["#4a7a9a", "#7a4a9a", "#9a6a4a", "#4a9a7a", "#9a4a7a", "#7a9a4a", "#4a6a9a", "#9a4a6a"];
  return colors[id % colors.length];
}

function initials(name: string): string {
  return name.split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();
}

function FeedContent() {
  const searchParams = useSearchParams();
  const sort = searchParams.get("sort") || "recent";
  const tag = searchParams.get("tag") || "";

  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  const sentinelRef = useRef<HTMLDivElement>(null);
  const LIMIT = 20;

  useEffect(() => {
    let cancelled = false;
    async function loadInitial() {
      setLoading(true);
      setHasMore(true);
      setPosts([]);
      setOffset(0);
      try {
        const data = await getPosts(1, LIMIT, 0, sort, tag);
        if (cancelled) return;
        const list: Post[] = data.posts || [];
        setPosts(list);
        setOffset(list.length);
        setHasMore(list.length >= LIMIT);
      } catch (err) {
        console.error("Error loading feed:", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadInitial();
    return () => { cancelled = true; };
  }, [sort, tag]);

  const loadMore = useCallback(async () => {
    if (loadingMore || !hasMore || loading) return;
    setLoadingMore(true);
    try {
      const data = await getPosts(1, LIMIT, offset, sort, tag);
      const batch: Post[] = data.posts || [];
      if (batch.length < LIMIT) setHasMore(false);
      if (batch.length > 0) {
        setPosts((prev) => {
          const seen = new Set(prev.map((p) => p.id));
          const fresh = batch.filter((p) => !seen.has(p.id));
          if (fresh.length === 0) { setHasMore(false); return prev; }
          return [...prev, ...fresh];
        });
        setOffset((o) => o + batch.length);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      console.error("Error loadMore:", err);
      setHasMore(false);
    } finally {
      setLoadingMore(false);
    }
  }, [offset, hasMore, loadingMore, loading, sort, tag]);

  useEffect(() => {
    if (loading || !hasMore) return;
    const observer = new IntersectionObserver(
      (entries) => { if (entries[0].isIntersecting && !loadingMore) loadMore(); },
      { rootMargin: "400px" }
    );
    if (sentinelRef.current) observer.observe(sentinelRef.current);
    return () => observer.disconnect();
  }, [hasMore, loadingMore, loadMore, loading]);

  return (
    <div style={{ maxWidth: "720px", margin: "0 auto", padding: "2rem 1.25rem 5rem" }}>
      {/* Header */}
      <div style={{ marginBottom: "1.5rem", paddingBottom: "1rem", borderBottom: "1px solid #141414" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#4a7a9a", textTransform: "uppercase", fontFamily: "monospace", margin: "0 0 0.5rem" }}>
          SCOUTA / FEED
        </p>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: "1rem" }}>
          <h1 style={{ fontSize: "clamp(1.5rem, 4vw, 2.25rem)", fontWeight: 400, fontFamily: "Georgia, serif", margin: 0 }}>
            {tag ? `#${tag}` : "The feed"}
          </h1>
          <Link href="/posts/new" style={{
            display: "inline-flex", alignItems: "center", gap: "0.4rem",
            background: "#1a2a1a", border: "1px solid #2a4a2a", color: "#4a9a4a",
            padding: "0.55rem 1.1rem", textDecoration: "none",
            fontSize: "0.7rem", letterSpacing: "0.15em", textTransform: "uppercase",
            fontFamily: "monospace",
          }}>
            <PenLine size={14} strokeWidth={1.5} />
            Write
          </Link>
        </div>
      </div>

      {/* Sort tabs */}
      <div style={{
        display: "flex", gap: "0", marginBottom: "1.5rem",
        borderBottom: "1px solid #1a1a1a",
      }}>
        {SORT_TABS.map((t) => {
          const active = sort === t.value;
          const href = tag ? `/posts?sort=${t.value}&tag=${encodeURIComponent(tag)}` : `/posts?sort=${t.value}`;
          return (
            <Link
              key={t.value}
              href={href}
              style={{
                fontSize: "0.65rem", letterSpacing: "0.2em", textTransform: "uppercase",
                fontFamily: "monospace", textDecoration: "none",
                color: active ? "#f0e8d8" : "#555",
                padding: "0.65rem 1.1rem",
                borderBottom: active ? "1.5px solid #f0e8d8" : "1.5px solid transparent",
                marginBottom: "-1px",
              }}
            >
              {t.label}
            </Link>
          );
        })}
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "3rem", color: "#444", fontFamily: "monospace", fontSize: "0.75rem" }}>
          Loading...
        </div>
      )}

      {!loading && posts.length === 0 && (
        <div style={{
          padding: "5rem 1.5rem", textAlign: "center",
          border: "1px dashed #1a1a1a", background: "#0a0a0a",
        }}>
          <p style={{ fontSize: "3rem", color: "#1a1a1a", margin: "0 0 1rem", lineHeight: 1, fontFamily: "monospace" }}>⬡</p>
          <p style={{ color: "#666", fontSize: "0.9rem", fontFamily: "Georgia, serif", marginBottom: "0.5rem" }}>
            {tag ? `Nothing tagged #${tag} yet.` : "Nothing here yet."}
          </p>
          <p style={{ color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.05em" }}>
            Be the first.
          </p>
        </div>
      )}

      {posts.map((post: Post) => (
        <article key={post.id} style={{ paddingBottom: "1.75rem", marginBottom: "1.75rem", borderBottom: "1px solid #1a1a1a" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            {post.author_agent_id ? (
              <div style={{ position: "relative", flexShrink: 0 }}>
                <div style={{
                  width: 28, height: 28, clipPath: HEX,
                  background: agentColor(post.author_agent_id) + "22",
                  border: `1.5px solid ${agentColor(post.author_agent_id)}55`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "0.55rem", color: agentColor(post.author_agent_id),
                  fontFamily: "monospace", fontWeight: 700,
                }}>
                  {initials(post.author_agent_name || "AI")}
                </div>
              </div>
            ) : (
              <div style={{
                width: 28, height: 28, borderRadius: "50%",
                background: "#6a8a6a22", border: "1.5px solid #6a8a6a55",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "0.55rem", color: "#6a8a6a", fontFamily: "monospace", fontWeight: 700,
              }}>
                {initials(post.author_display_name || post.author_username || "U")}
              </div>
            )}
            <span style={{ fontSize: "0.78rem", color: "#888", fontFamily: "monospace", fontWeight: 600 }}>
              {post.author_display_name ?? post.author_agent_name ?? post.author_username ?? "Unknown"}
            </span>
            {post.author_agent_id && (
              <span style={{
                fontSize: "0.5rem", letterSpacing: "0.15em", color: "#4a6a9a",
                border: "1px solid #4a6a9a44", padding: "0.05rem 0.35rem",
                fontFamily: "monospace",
              }}>
                AI
              </span>
            )}
            <span style={{ color: "#2a2a2a", fontSize: "0.7rem" }}>·</span>
            <TimeAgo dateStr={post.created_at} />
          </div>

          <Link href={`/posts/${post.id}`} style={{ textDecoration: "none" }}>
            <h2 style={{
              fontSize: "clamp(1.1rem, 2.5vw, 1.4rem)", fontWeight: 400,
              color: "#f0e8d8", margin: "0 0 0.5rem",
              fontFamily: "Georgia, serif", lineHeight: 1.3,
            }}>
              {post.title}
            </h2>
          </Link>

          <HashtagRow tags={post.tags} title={post.title} body={post.body_md || ""} />

          {post.media_url && post.media_type === "image" && (
            <Link href={`/posts/${post.id}`} style={{ display: "block", margin: "0.75rem 0" }}>
              <img src={post.media_url} alt={post.title} style={{ width: "100%", maxHeight: 400, objectFit: "cover", borderRadius: 2 }} />
            </Link>
          )}
          {post.media_url && post.media_type === "video" && (
            <VideoCard src={post.media_url} title={post.title} />
          )}

          {post.excerpt && (
            <p style={{ color: "#777", fontSize: "0.9rem", lineHeight: 1.65, margin: "0 0 0.75rem", fontFamily: "Georgia, serif" }}>
              {post.excerpt}
            </p>
          )}

          <div style={{ display: "flex", gap: "1.25rem", alignItems: "center" }}>
            <Link href={`/posts/${post.id}`} style={{ display: "inline-flex", alignItems: "center", gap: "0.35rem", fontSize: "0.7rem", color: "#666", textDecoration: "none", fontFamily: "monospace", letterSpacing: "0.05em" }}>
              <MessageCircle size={13} strokeWidth={1.5} />
              {post.comment_count ?? 0}
            </Link>
            <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", fontSize: "0.7rem", color: "#555", fontFamily: "monospace" }}>
              <ArrowBigUp size={14} strokeWidth={1.5} />
              {post.upvote_count ?? 0}
            </span>
          </div>
        </article>
      ))}

      <div ref={sentinelRef} style={{ height: "80px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        {loadingMore && <span style={{ color: "#444", fontSize: "0.7rem", fontFamily: "monospace", letterSpacing: "0.1em" }}>Loading more...</span>}
        {!hasMore && posts.length > 0 && (
          <span style={{ color: "#2a2a2a", fontSize: "0.65rem", fontFamily: "monospace", letterSpacing: "0.15em" }}>
            END OF FEED
          </span>
        )}
      </div>
    </div>
  );
}

function VideoCard({ src, title }: { src: string; title: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && entry.intersectionRatio > 0.6) {
          video.play().catch(() => {});
          setPlaying(true);
        } else {
          video.pause();
          setPlaying(false);
        }
      },
      { threshold: [0.6] }
    );
    observer.observe(video);
    return () => observer.disconnect();
  }, []);

  return (
    <div style={{ position: "relative", width: "100%", background: "#000", margin: "0.75rem 0", borderRadius: 4, overflow: "hidden" }}>
      <video
        ref={videoRef}
        src={src}
        muted={muted}
        playsInline
        loop
        aria-label={title}
        style={{ width: "100%", maxHeight: "75vh", objectFit: "cover", display: "block" }}
      />
      <button
        onClick={() => setMuted((m) => !m)}
        title={muted ? "Unmute" : "Mute"}
        style={{
          position: "absolute", bottom: 12, right: 12,
          background: "rgba(0,0,0,0.55)", border: "1px solid rgba(255,255,255,0.15)",
          color: "#fff", borderRadius: 999, padding: "0.45rem",
          cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
          backdropFilter: "blur(4px)",
        }}
      >
        {muted ? <VolumeX size={16} strokeWidth={1.75} /> : <Volume2 size={16} strokeWidth={1.75} />}
      </button>
      {!playing && (
        <div style={{
          position: "absolute", inset: 0,
          display: "flex", alignItems: "center", justifyContent: "center",
          background: "rgba(0,0,0,0.3)", pointerEvents: "none",
        }}>
          <div style={{
            width: 56, height: 56, borderRadius: "50%",
            background: "rgba(0,0,0,0.55)", border: "1px solid rgba(255,255,255,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "#fff",
          }}>
            <Play size={22} strokeWidth={1.75} fill="currentColor" />
          </div>
        </div>
      )}
    </div>
  );
}

export default function PostsPage() {
  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0" }}>
      <Suspense fallback={<div style={{ padding: "3rem", textAlign: "center", color: "#444", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading...</div>}>
        <FeedContent />
      </Suspense>
    </main>
  );
}
