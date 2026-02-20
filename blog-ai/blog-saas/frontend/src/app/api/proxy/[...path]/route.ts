import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type Params = { path: string[] };

async function proxyFetch(req: NextRequest, params: Params, method: string) {
  const path = params.path.join("/");
  const search = req.nextUrl.search;
  // path ya viene como "api/v1/..." desde el cliente
  const fullPath = path.startsWith("api/v1/") ? path : `api/v1/${path}`;
  const url = `${API_BASE}/${fullPath}${search}`;
  const headers: Record<string, string> = {
    "content-type": req.headers.get("content-type") ?? "application/json",
    authorization: req.headers.get("authorization") ?? "",
  };
  const init: RequestInit = { method, headers };
  if (method !== "GET") init.body = await req.text();
  const res = await fetch(url, init);
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
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
