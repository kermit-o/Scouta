import { NextRequest, NextResponse } from 'next/server';

const BACKEND_BASE = process.env.FORGE_BACKEND_INTERNAL_BASE ?? 'http://127.0.0.1:8000';

export async function POST(req: NextRequest) {
  const startTime = Date.now();
  console.log('🚀 [PROXY] Received request at:', new Date().toISOString());
  
  try {
    const payload = await req.json();
    console.log('📦 [PROXY] Payload length:', JSON.stringify(payload).length);

    const backendUrl = `${BACKEND_BASE}/api/forge/generate_from_requirements`;
    console.log('🔗 [PROXY] Forwarding to:', backendUrl);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    const res = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal
    });

    clearTimeout(timeoutId);
    const duration = Date.now() - startTime;

    console.log(`📡 [PROXY] Backend response: ${res.status} (${duration}ms)`);

    if (!res.ok) {
      const errorText = await res.text();
      console.error('❌ [PROXY] Backend error:', {
        status: res.status,
        statusText: res.statusText,
        error: errorText.substring(0, 500)
      });
      return NextResponse.json(
        { error: `Backend responded with error: ${res.status} ${res.statusText}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    console.log('✅ [PROXY] Request successful');
    return NextResponse.json(data);

  } catch (error: any) {
    const duration = Date.now() - startTime;
    console.error('💥 [PROXY] Fetch failed:', {
      error: error.message,
      duration: `${duration}ms`,
      name: error.name
    });

    if (error.name === 'AbortError') {
      return NextResponse.json(
        { error: 'Backend timeout after 15 seconds' },
        { status: 504 }
      );
    }

    return NextResponse.json(
      { error: `Cannot connect to backend: ${error.message}` },
      { status: 503 }
    );
  }
}
