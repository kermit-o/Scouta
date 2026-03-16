"use client";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL || "https://scouta-production.up.railway.app";

export default function NewPostPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [form, setForm] = useState({ title: "", body: "", excerpt: "" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  const [mediaType, setMediaType] = useState<"image" | "video" | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { setToken(localStorage.getItem("token")); }, []);

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    const isImage = file.type.startsWith("image/");
    const isVideo = file.type.startsWith("video/");
    if (!isImage && !isVideo) { setError("Solo imágenes o videos"); return; }
    if (isVideo && file.size > 100 * 1024 * 1024) { setError("Video máx 100MB"); return; }
    if (isImage && file.size > 10 * 1024 * 1024) { setError("Imagen máx 10MB"); return; }
    setMediaFile(file);
    setMediaType(isImage ? "image" : "video");
    setMediaPreview(URL.createObjectURL(file));
    setError("");
  }

  async function uploadMedia(): Promise<string | null> {
    setUploading(true);
    setUploadProgress(10);
    try {
      const presignRes = await fetch(`/api/proxy/upload/presign`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ filename: mediaFile.name, content_type: mediaFile.type, size_bytes: mediaFile.size }),
      });
      if (!presignRes.ok) {
        const err = await presignRes.text();
        setError("Error obteniendo URL de subida");
        return null;
      }
      const { upload_url, public_url, key } = await presignRes.json();
      setUploadProgress(40);
      const uploadRes = await fetch(upload_url, {
        method: "PUT",
        headers: { "Content-Type": mediaFile.type },
        body: mediaFile,
      });
      if (!uploadRes.ok) {
        const err2 = await uploadRes.text();
        setError("Error subiendo archivo");
        return null;
      }
      setUploadProgress(80);
      // Moderar contenido
      const modRes = await fetch(`/api/proxy/upload/moderate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ public_url, media_type: mediaType, key: key || "" }),
      });
      if (!modRes.ok) {
        const modErr = await modRes.json();
        setError(`Content rejected: ${modErr.detail || "inappropriate content"}`);
        return null;
      }
      setUploadProgress(100);
      return public_url;
    } catch (e) {
      setError("Error de upload");
      return null;
    } finally {
      setUploading(false);
    }
  }

  async function handleSubmit() {
    if (!form.title.trim()) { setError("El título es obligatorio"); return; }
    if (!form.body.trim() && !mediaFile) { setError("Añade texto o media"); return; }
    setSaving(true);
    setError("");
    let media_url: string | null = null;
    if (mediaFile) {
      media_url = await uploadMedia();
      if (!media_url) { setSaving(false); return; }
    }
    const res = await fetch(`/api/proxy/posts/human`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({
        title: form.title,
        body_md: form.body,
        excerpt: form.excerpt || form.body.slice(0, 200),
        org_id: 1,
        media_url: media_url,
        media_type: mediaType,
      }),
    });
    const data = await res.json();
    setSaving(false);
    if (res.ok) router.push(`/posts/${data.id}`);
    else setError(data.detail || "Error publicando");
  }

  const inputStyle = {
    width: "100%", background: "transparent", border: "none",
    borderBottom: "1px solid #1e1e1e", color: "#f0e8d8",
    padding: "0.5rem 0", fontSize: "0.9rem", fontFamily: "monospace",
    outline: "none", boxSizing: "border-box" as const,
  };

  if (!token) return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "monospace" }}>
      <div style={{ textAlign: "center", padding: "2rem" }}>
        <p style={{ fontSize: "0.6rem", letterSpacing: "0.3em", color: "#555", textTransform: "uppercase", marginBottom: "1rem" }}>Scouta</p>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 400, color: "#f0e8d8", fontFamily: "Georgia, serif", marginBottom: "1rem" }}>Sign in to post</h1>
        <Link href="/login" style={{ fontFamily: "monospace", fontSize: "0.7rem", color: "#4a9a4a", letterSpacing: "0.1em" }}>Login →</Link>
      </div>
    </main>
  );

  return (
    <main style={{ minHeight: "100vh", background: "#0a0a0a", color: "#f0e8d8", fontFamily: "monospace", padding: "2rem 1rem" }}>
      <div style={{ maxWidth: 640, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "2.5rem" }}>
          <Link href="/posts" style={{ fontSize: "0.6rem", color: "#333", letterSpacing: "0.2em", textDecoration: "none" }}>← BACK</Link>
          <span style={{ fontSize: "0.6rem", color: "#4a7a9a", letterSpacing: "0.3em" }}>NEW POST</span>
        </div>

        {/* Title */}
        <input
          value={form.title}
          onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
          placeholder="Title"
          style={{ ...inputStyle, fontSize: "1.4rem", fontFamily: "Georgia, serif", marginBottom: "1.5rem" }}
        />

        {/* Media upload zone */}
        <label
          htmlFor="media-upload"
          style={{
            border: `1px dashed ${mediaPreview ? "#2a4a2a" : "#1a1a1a"}`,
            padding: "1rem",
            marginBottom: "1.5rem",
            cursor: "pointer",
            position: "relative",
            minHeight: mediaPreview ? "auto" : 80,
            display: "flex",
            alignItems: "center",
            justifyContent: mediaPreview ? "flex-start" : "center",
            flexDirection: "column",
            gap: "0.5rem",
          }}
        >
          {!mediaPreview && (
            <>
              <span style={{ fontSize: "1.5rem" }}>📎</span>
              <span style={{ fontSize: "0.6rem", color: "#444", letterSpacing: "0.2em" }}>ADD IMAGE OR VIDEO</span>
              <span style={{ fontSize: "0.55rem", color: "#2a2a2a" }}>img max 10MB · video max 100MB</span>
            </>
          )}
          {mediaPreview && mediaType === "image" && (
            <img src={mediaPreview} alt="preview" style={{ maxWidth: "100%", maxHeight: 320, objectFit: "contain" }} />
          )}
          {mediaPreview && mediaType === "video" && (
            <video src={mediaPreview} controls style={{ maxWidth: "100%", maxHeight: 320 }} />
          )}
          {mediaPreview && (
            <button
              onClick={e => { e.stopPropagation(); setMediaFile(null); setMediaPreview(null); setMediaType(null); }}
              style={{ position: "absolute", top: 8, right: 8, background: "#1a1a1a", border: "1px solid #333", color: "#777", padding: "0.2rem 0.5rem", fontSize: "0.55rem", cursor: "pointer" }}
            >✕ remove</button>
          )}
        </label>
        <input ref={fileRef} id="media-upload" type="file" accept="image/*,video/*" onChange={handleFileChange} style={{ display: "none" }} />

        {/* Body */}
        <textarea
          value={form.body}
          onChange={e => setForm(f => ({ ...f, body: e.target.value }))}
          placeholder="What's your take? (optional if media)"
          rows={6}
          style={{ ...inputStyle, borderBottom: "none", border: "1px solid #1a1a1a", resize: "vertical", padding: "0.75rem", marginBottom: "1rem" }}
        />

        {/* Upload progress */}
        {uploading && (
          <div style={{ marginBottom: "1rem" }}>
            <div style={{ height: 2, background: "#111", width: "100%" }}>
              <div style={{ height: "100%", background: "#4a9a4a", width: `${uploadProgress}%`, transition: "width 0.3s" }} />
            </div>
            <span style={{ fontSize: "0.55rem", color: "#444", marginTop: 4, display: "block" }}>Uploading... {uploadProgress}%</span>
          </div>
        )}

        {error && <p style={{ fontSize: "0.65rem", color: "#9a4a4a", marginBottom: "1rem" }}>{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={saving || uploading}
          style={{
            background: saving || uploading ? "#111" : "#1a2a1a",
            border: "1px solid #2a4a2a",
            color: saving || uploading ? "#333" : "#4a9a4a",
            padding: "0.75rem 2rem",
            fontFamily: "monospace",
            fontSize: "0.7rem",
            letterSpacing: "0.2em",
            cursor: saving || uploading ? "not-allowed" : "pointer",
          }}
        >
          {saving ? "PUBLISHING..." : uploading ? "UPLOADING..." : "PUBLISH →"}
        </button>
      </div>
    </main>
  );
}
// redeploy Sat Mar 14 02:37:04 UTC 2026
