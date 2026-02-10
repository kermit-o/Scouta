import { NextRequest, NextResponse } from 'next/server';

const BACKEND_BASE =
  process.env.FORGE_BACKEND_INTERNAL_BASE ?? 'http://127.0.0.1:8000';

export async function GET(_req: NextRequest) {
  const target = `${BACKEND_BASE}/api/forge/module_resources`;
  try {
    console.log('[PROXY-MODULE-RES] Forwarding GET to:', target);

    const res = await fetch(target, {
      method: 'GET',
    });

    const text = await res.text();

    return new NextResponse(text, {
      status: res.status,
      headers: {
        'Content-Type':
          res.headers.get('content-type') ?? 'application/json',
      },
    });
  } catch (err: any) {
    console.error('[PROXY-MODULE-RES] Error calling backend:', err);
    return NextResponse.json(
      {
        error: 'Failed to fetch module resources from backend',
        detail: err?.message ?? String(err),
      },
      { status: 500 },
    );
  }
}
