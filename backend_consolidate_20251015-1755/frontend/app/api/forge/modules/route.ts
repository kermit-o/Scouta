import { NextRequest, NextResponse } from 'next/server';

const BACKEND_BASE =
  process.env.FORGE_BACKEND_INTERNAL_BASE ?? 'http://127.0.0.1:8000';

export async function GET(_req: NextRequest) {
  const target = `${BACKEND_BASE}/api/forge/modules`;
  try {
    console.log('[PROXY-MODULES] Forwarding GET to:', target);

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
    console.error('[PROXY-MODULES] Error calling backend:', err);
    return NextResponse.json(
      {
        error: 'Failed to fetch modules from backend',
        detail: err?.message ?? String(err),
      },
      { status: 500 },
    );
  }
}
