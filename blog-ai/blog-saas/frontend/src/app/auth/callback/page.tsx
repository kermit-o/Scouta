"use client";
import { useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

function AuthCallbackContent() {
  const params = useSearchParams();
  const router = useRouter();
  const { login } = useAuth();

  useEffect(() => {
    const token = params.get("token");
    const user_id = params.get("user_id");
    const username = params.get("username");
    const display_name = params.get("display_name");
    const avatar_url = params.get("avatar_url");

    if (token) {
      // Push the token through the AuthContext so React state updates
      // synchronously. Previously we wrote localStorage and did a hard
      // window.location.href = "/posts", which made the destination page
      // mount with `useAuth().token === null` for one render — its first
      // fetch fired without Authorization and got 401.
      login(token, {
        id: user_id ?? "",
        username: username ?? "",
        display_name: display_name ?? "",
        avatar_url: avatar_url ?? "",
      });
      // Cookie for SSR-rendered routes that read auth_token.
      document.cookie = `auth_token=${token}; path=/; SameSite=Strict; max-age=604800`;
      router.replace("/posts");
    } else {
      router.replace("/login?error=google_failed");
    }
  }, [params, router, login]);

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
