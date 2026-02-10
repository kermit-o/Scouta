import { BACKEND_BASE } from '@/lib/config';

export async function GET(
  req: Request,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;

  const target = `${BACKEND_BASE}/api/forge/projects/${slug}/download`;
  console.log('[PROXY-DOWNLOAD] Forwarding GET to:', target);

  const res = await fetch(target);

  if (!res.ok) {
    return new Response('Not found', { status: res.status });
  }

  // Proxy directo del ZIP
  const body = res.body;

  return new Response(body, {
    status: res.status,
    headers: {
      'Content-Type': res.headers.get('content-type') ?? 'application/zip',
      'Content-Disposition':
        res.headers.get('content-disposition') ??
        `attachment; filename="${slug}.zip"`,
    },
  });
}
