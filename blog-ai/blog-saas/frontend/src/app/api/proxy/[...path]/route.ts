import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Params = { path: string[] };

async function proxyFetch(req: NextRequest, params: Params, method: string) {
  const path = params.path.join("/");
  const search = req.nextUrl.search;
  // path ya viene como "api/v1/..." desde el cliente
  const fullPath = path.startsWith("api/v1/") ? path : `api/v1/${path}`;
  const url = `${API_BASE}/${fullPath}${search}`;

  const headers: Record<string, string> = {};
  const ct = req.headers.get("content-type");
  if (ct) headers["content-type"] = ct;
  const auth = req.headers.get("authorization");
  if (auth) headers.authorization = auth;

  const init: RequestInit = { method, headers };
  if (method !== "GET" && method !== "HEAD") {
    // arrayBuffer (not text!) so binary payloads survive intact. The
    // previous `await req.text()` was decoding the body as UTF-8, which
    // replaced every non-ASCII byte with U+FFFD (EF BF BD) — that turned
    // every uploaded JPEG into a corrupted blob of replacement chars.
    init.body = await req.arrayBuffer();
  }

  const upstream = await fetch(url, init);

  // Forward the upstream response body and content-type as-is. The previous
  // unconditional `res.json()` + `NextResponse.json(data)` would fail for
  // any non-JSON response (e.g. file downloads, plain text errors) and was
  // double-serializing JSON for no reason.
  const upstreamCt = upstream.headers.get("content-type") ?? "application/octet-stream";
  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: { "content-type": upstreamCt },
  });
}

export async function GET(req: NextRequest, { params }: { params: Promise<Params> }) {
  return proxyFetch(req, await params, "GET");
}
export async function POST(req: NextRequest, { params }: { params: Promise<Params> }) {
  return proxyFetch(req, await params, "POST");
}
export async function PATCH(req: NextRequest, { params }: { params: Promise<Params> }) {
  return proxyFetch(req, await params, "PATCH");
}
export async function DELETE(req: NextRequest, { params }: { params: Promise<Params> }) {
  return proxyFetch(req, await params, "DELETE");
}
