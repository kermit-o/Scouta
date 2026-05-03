"use client";
import { useEffect, useRef, Suspense } from "react";

function AuthCallbackContent() {
  const fired = useRef(false);

  useEffect(() => {
    // Effect runs exactly once. Re-renders triggered by AuthContext state
    // changes would otherwise replay the redirect and cancel the in-flight
    // navigation, leaving the page stuck on "Signing you in...".
    if (fired.current) return;
    fired.current = true;

    if (typeof window === "undefined") return;

    // Read OAuth params from the URL fragment (after `#`), not the query
    // string. The backend now redirects with `#token=...` instead of
    // `?token=...` so the JWT never reaches Railway access logs, CDN logs,
    // or any third-party script reading document.referrer. Fragments stay
    // client-side.
    const hash = window.location.hash.startsWith("#")
      ? window.location.hash.slice(1)
      : window.location.hash;
    const params = hash ? new URLSearchParams(hash) : new URLSearchParams();

    const token = params.get("token");
    if (!token) {
      window.location.replace("/login?error=google_failed");
      return;
    }

    const user_id = params.get("user_id");
    const username = params.get("username");
    const display_name = params.get("display_name");
    const avatar_url = params.get("avatar_url");

    // Persist token + user before the hard navigation so the destination
    // page mounts with localStorage already populated. AuthProvider re-reads
    // localStorage on init, so by the time /posts renders, useAuth() has
    // the token. Using window.location.replace (not router.replace) because
    // a hard nav guarantees AuthProvider re-initializes from localStorage —
    // router.replace was getting cancelled by AuthContext-triggered renders
    // before the navigation could commit.
    localStorage.setItem("token", token);
    if (user_id || username) {
      localStorage.setItem("user", JSON.stringify({
        id: user_id ?? "",
        username: username ?? "",
        display_name: display_name ?? "",
        avatar_url: avatar_url ?? "",
      }));
    }
    document.cookie = `auth_token=${token}; path=/; SameSite=Strict; max-age=604800`;

    window.location.replace("/posts");
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <p style={{ color: "#888" }}>Signing you in...</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: "100vh", background: "#0a0a0a" }} />}>
      <AuthCallbackContent />
    </Suspense>
  );
}
