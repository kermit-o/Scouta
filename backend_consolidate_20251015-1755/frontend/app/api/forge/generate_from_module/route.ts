import { NextRequest, NextResponse } from 'next/server';

const BACKEND_BASE =
  process.env.FORGE_BACKEND_INTERNAL_BASE ?? 'http://127.0.0.1:8000';

export async function POST(req: NextRequest) {
  const target = `${BACKEND_BASE}/api/forge/generate_from_module`;

  try {
    const body = await req.text();

    console.log('[PROXY-GEN-MODULE] Forwarding POST to:', target);
    console.log('[PROXY-GEN-MODULE] Payload length:', body.length);

    const res = await fetch(target, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body,
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
    console.error('[PROXY-GEN-MODULE] Error calling backend:', err);
    return NextResponse.json(
      {
        error: 'Failed to generate from module',
        detail: err?.message ?? String(err),
      },
      { status: 500 },
    );
  }
}
