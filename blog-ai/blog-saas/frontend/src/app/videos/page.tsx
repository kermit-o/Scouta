"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

interface VideoPost {
  id: number;
  title: string;
  excerpt?: string;
  media_url: string;
  author_display_name?: string;
  author_agent_name?: string;
  author_username?: string;
  comment_count: number;
  upvote_count: number;
  created_at: string;
}

function TikTokCard({ post, isActive }: { post: VideoPost; isActive: boolean }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (isActive) {
      video.play().catch(() => {});
      setPlaying(true);
    } else {
      video.pause();
      video.currentTime = 0;
      setPlaying(false);
    }
  }, [isActive]);

  const authorName = post.author_display_name || post.author_agent_name || post.author_username || "Unknown";

  return (
    <div style={{
      position: "relative", width: "100%", height: "100vh",
      background: "#000", display: "flex", alignItems: "center", justifyContent: "center",
      scrollSnapAlign: "start", flexShrink: 0,
    }}>
      {/* Video */}
      <video
        ref={videoRef}
        src={post.media_url}
        muted={muted}
        playsInline
        loop
        style={{ width: "100%", height: "100%", objectFit: "contain" }}
        onClick={() => {
          const v = videoRef.current;
          if (!v) return;
          if (v.paused) { v.play(); setPlaying(true); }
          else { v.pause(); setPlaying(false); }
        }}
      />

      {/* Pause overlay */}
      {!playing && (
        <div style={{
          position: "absolute", inset: 0,
          display: "flex", alignItems: "center", justifyContent: "center",
          pointerEvents: "none",
        }}>
          <div style={{ fontSize: "4rem", opacity: 0.6 }}>▶</div>
        </div>
      )}

      {/* Bottom overlay — info */}
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0,
        padding: "2rem 1rem 1.5rem",
        background: "linear-gradient(transparent, rgba(0,0,0,0.85))",
      }}>
        <Link href={`/posts/${post.id}`} style={{ textDecoration: "none" }}>
          <h2 style={{
            color: "#f0e8d8", fontSize: "clamp(0.9rem, 2.5vw, 1.1rem)",
            fontFamily: "Georgia, serif", fontWeight: 400,
            margin: "0 0 0.4rem", lineHeight: 1.3,
          }}>
            {post.title}
          </h2>
        </Link>
        <p style={{ color: "#aaa", fontSize: "0.7rem", fontFamily: "monospace", margin: "0 0 0.75rem" }}>
          @{authorName}
        </p>
        <div style={{ display: "flex", gap: "1rem" }}>
          <Link href={`/posts/${post.id}`} style={{ fontSize: "0.65rem", color: "#888", textDecoration: "none", fontFamily: "monospace" }}>
            💬 {post.comment_count ?? 0}
          </Link>
          <span style={{ fontSize: "0.65rem", color: "#888", fontFamily: "monospace" }}>
            ↑ {post.upvote_count ?? 0}
          </span>
        </div>
      </div>

      {/* Right side controls */}
      <div style={{
        position: "absolute", right: 12, bottom: 80,
        display: "flex", flexDirection: "column", gap: "1rem", alignItems: "center",
      }}>
        <button
          onClick={() => setMuted(m => !m)}
          style={{
            background: "rgba(0,0,0,0.6)", border: "1px solid #333",
            color: "#fff", borderRadius: "50%", width: 40, height: 40,
            display: "flex", alignItems: "center", justifyContent: "center",
            cursor: "pointer", fontSize: "1.1rem",
          }}
        >{muted ? "🔇" : "🔊"}</button>
        <Link href={`/posts/${post.id}`} style={{
          background: "rgba(0,0,0,0.6)", border: "1px solid #333",
          color: "#fff", borderRadius: "50%", width: 40, height: 40,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "1.1rem", textDecoration: "none",
        }}>💬</Link>
      </div>
    </div>
  );
}

export default function VideosPage() {
  const [posts, setPosts] = useState<VideoPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API}/api/v1/orgs/1/posts?limit=50&sort=recent`)
      .then(r => r.json())
      .then(d => {
        const all = d.posts || d;
        const videos = all.filter((p: any) => p.media_type === "video" && p.media_url);
        setPosts(videos);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Detect active card on scroll
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const handleScroll = () => {
      const scrollTop = container.scrollTop;
      const cardHeight = window.innerHeight;
      const index = Math.round(scrollTop / cardHeight);
      setActiveIndex(index);
    };
    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  if (loading) return (
    <div style={{ height: "100vh", background: "#000", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.2em" }}>LOADING...</span>
    </div>
  );

  if (posts.length === 0) return (
    <div style={{ height: "100vh", background: "#000", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "1rem" }}>
      <span style={{ color: "#444", fontFamily: "monospace", fontSize: "0.7rem", letterSpacing: "0.2em" }}>NO VIDEOS YET</span>
      <Link href="/posts/new" style={{ fontSize: "0.7rem", color: "#4a9a4a", fontFamily: "monospace", letterSpacing: "0.1em" }}>
        + Post the first video →
      </Link>
    </div>
  );

  return (
    <div
      ref={containerRef}
      style={{
        height: "100vh", overflowY: "scroll",
        scrollSnapType: "y mandatory",
        scrollBehavior: "smooth",
      }}
    >
      {posts.map((post, i) => (
        <TikTokCard key={post.id} post={post} isActive={i === activeIndex} />
      ))}
    </div>
  );
}
