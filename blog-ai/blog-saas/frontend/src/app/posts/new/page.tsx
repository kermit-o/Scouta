"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import Link from "next/link";
import { getPosts, Post, getApiBase } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

// --- Utilidades ---
function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h`;
  return `${Math.floor(h / 24)}d`;
}

// --- Componente de Item de Post ---
function PostItem({ post }: { post: Post }) {
  return (
    <Link href={`/posts/${post.id}`} style={{ textDecoration: "none", display: "block", marginBottom: "2.5rem" }}>
      <article>
        <p style={{ fontSize: "0.65rem", color: "#444", textTransform: "uppercase", letterSpacing: "0.2em", marginBottom: "0.5rem", fontFamily: "monospace" }}>
          {new Date(post.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
        </p>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif", marginBottom: "0.5rem", lineHeight: 1.2 }}>
          {post.title}
        </h2>
        {post.excerpt && (
          <p style={{ fontSize: "0.95rem", color: "#888", lineHeight: 1.6, fontFamily: "Georgia, serif" }}>
            {post.excerpt}
          </p>
        )}
      </article>
    </Link>
  );
}

// --- Componente Principal ---
export default function PostsPage() {
  const { token } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const sentinelRef = useRef<HTMLDivElement>(null);

  // 1. Carga Inicial [cite: 77, 80]
  const loadInitialPosts = useCallback(async () => {
    setLoading(true);
    try {
      // Cargamos los primeros 15 posts [cite: 77]
      const data = await getPosts(1, 15, 0); 
      const postsList = data.posts || [];
      setPosts(postsList);
      setOffset(postsList.length);
      
      // Sincronizar si hay más páginas [cite: 78]
      const total = data.total ?? 0;
      setHasMore(postsList.length < total && total > 0);
    } catch (err) {
      console.error("❌ Error al cargar posts iniciales:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadInitialPosts(); }, [loadInitialPosts]);

  // 2. Carga de más posts (Paginación) [cite: 81, 90]
  const loadMorePosts = useCallback(async (limit = 15) => {
    if (loadingMore || !hasMore) return;
    
    setLoadingMore(true);
    const API = getApiBase();
    try {
      const res = await fetch(`${API}/api/v1/orgs/1/posts?limit=${limit}&offset=${offset}`, {
        headers: { "Content-Type": "application/json" }
      });
      
      if (!res.ok) throw new Error("Failed to fetch more posts");
      
      const data = await res.json();
      const batch = data.posts || [];
      
      if (batch.length === 0) {
        setHasMore(false);
        return;
      }

      // Evitar duplicados [cite: 85, 86]
      setPosts((prev) => {
        const seen = new Set(prev.map(p => p.id));
        const filtered = batch.filter((p: Post) => !seen.has(p.id));
        return [...prev, ...filtered];
      });

      const nextOffset = offset + batch.length;
      setOffset(nextOffset);
      
      // Actualizar si hay más [cite: 88]
      if (data.total !== undefined) {
        setHasMore(nextOffset < data.total);
      } else {
        setHasMore(batch.length === limit);
      }
    } catch (err) {
      console.error("❌ Error al cargar más posts:", err);
    } finally {
      setLoadingMore(false);
    }
  }, [offset, hasMore, loadingMore]);

  // 3. Observer para Scroll Infinito [cite: 91, 96]
  useEffect(() => {
    if (loading || !hasMore) return;

    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !loadingMore) {
        loadMorePosts(15); // Carga el siguiente bloque 
      }
    }, { root: null, rootMargin: "200px", threshold: 0.1 });

    const currentSentinel = sentinelRef.current;
    if (currentSentinel) observer.observe(currentSentinel);

    return () => observer.disconnect();
  }, [hasMore, loadingMore, loadMorePosts, loading]);

  // --- Renderizado ---
  if (loading) return (
    <main style={{ background: "#0a0a0a", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <p style={{ color: "#333", fontFamily: "monospace", fontSize: "0.75rem" }}>Loading feed...</p>
    </main>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#e8e0d0" }}>
      <div style={{ maxWidth: "640px", margin: "0 auto", padding: "3rem 1.5rem" }}>
        <header style={{ marginBottom: "4rem" }}>
          <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", marginBottom: "1rem" }}>
            Scouta Feed
          </p>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif" }}>
            Latest Perspectives
          </h1>
        </header>

        <section>
          {posts.length === 0 ? (
            <p style={{ color: "#444", fontFamily: "monospace" }}>No posts found.</p>
          ) : (
            posts.map(post => <PostItem key={post.id} post={post} />)
          )}
        </section>

        {/* Sentinel para scroll [cite: 116, 121] */}
        <div 
          ref={sentinelRef} 
          style={{ 
            height: "60px", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center",
            opacity: hasMore ? 1 : 0.5 
          }}
        >
          {hasMore ? (
            <span style={{ color: "#4a9a4a", fontSize: "0.7rem", fontFamily: "monospace" }}>
              ⏳ Loading more...
            </span>
          ) : (
            <span style={{ color: "#444", fontSize: "0.7rem", fontFamily: "monospace" }}>
              📄 End of the feed
            </span>
          )}
        </div>
      </div>
    </main>
  );
}