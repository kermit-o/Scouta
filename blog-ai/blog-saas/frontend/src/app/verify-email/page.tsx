"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

function VerifyEmailContent() {
  const params = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const token = params.get("token");
    if (!token) {
      setStatus("error");
      setMessage("Invalid verification link.");
      return;
    }
    fetch(`/api/proxy/auth/verify?token=${token}`)
      .then(res => res.json())
      .then(data => {
        if (data.access_token) {
          localStorage.setItem("token", data.access_token);
          localStorage.setItem("user", JSON.stringify({
            id: data.user_id,
            username: data.username,
            display_name: data.display_name,
            avatar_url: data.avatar_url,
          }));
          setStatus("success");
          setMessage(`Welcome, ${data.display_name}! Your account is verified.`);
          setTimeout(() => router.push("/posts"), 2000);
        } else {
          setStatus("error");
          setMessage(data.detail || "Verification failed.");
        }
      })
      .catch(() => {
        setStatus("error");
        setMessage("Something went wrong. Please try again.");
      });
  }, [params, router]);

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <div style={{ textAlign: "center", color: "#e0e0e0" }}>
        {status === "loading" && <p style={{ color: "#888" }}>Verifying your email...</p>}
        {status === "success" && (
          <>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>✅</div>
            <p style={{ color: "#4caf50" }}>{message}</p>
            <p style={{ color: "#444", fontSize: "0.8rem" }}>Redirecting to feed...</p>
          </>
        )}
        {status === "error" && (
          <>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>❌</div>
            <p style={{ color: "#f44336" }}>{message}</p>
            <a href="/register" style={{ color: "#888", fontSize: "0.8rem" }}>Back to register</a>
          </>
        )}
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div style={{ minHeight: "100vh", background: "#0a0a0a" }} />}>
      <VerifyEmailContent />
    </Suspense>
  );
}
