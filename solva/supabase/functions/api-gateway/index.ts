import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { crypto } from 'https://deno.land/std@0.177.0/crypto/mod.ts'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

async function hashKey(key: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(key)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

const ALLOWED_ORIGINS = (Deno.env.get('API_GATEWAY_ALLOWED_ORIGINS') ??
  'https://www.getsolva.co,https://getsolva.co')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean)

function corsHeaders(origin: string | null) {
  const allow = origin && ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0]
  return {
    'Access-Control-Allow-Origin': allow,
    'Vary': 'Origin',
    'Access-Control-Allow-Headers': 'authorization, x-api-key, content-type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
  }
}

function response(data: any, status = 200, origin: string | null = null) {
  return new Response(JSON.stringify(data), { status, headers: corsHeaders(origin) })
}

async function validateApiKey(apiKey: string): Promise<{ valid: boolean; keyRecord?: any; error?: string }> {
  const hash = await hashKey(apiKey)
  const { data: keyRecord, error } = await supabase
    .from('api_keys')
    .select('*')
    .eq('key_hash', hash)
    .eq('is_active', true)
    .single()

  if (error || !keyRecord) return { valid: false, error: 'API key invalida' }
  if (keyRecord.requests_today >= keyRecord.rate_limit) {
    return { valid: false, error: `Rate limit alcanzado: ${keyRecord.rate_limit} requests/dia` }
  }

  // Incrementa contador
  await supabase.from('api_keys').update({
    requests_today: keyRecord.requests_today + 1,
    requests_total: keyRecord.requests_total + 1,
    last_used_at: new Date().toISOString(),
  }).eq('id', keyRecord.id)

  return { valid: true, keyRecord }
}

function hasScope(keyRecord: any, scope: string): boolean {
  return keyRecord.scopes?.includes(scope) || keyRecord.scopes?.includes('*')
}

Deno.serve(async (req) => {
  const origin = req.headers.get('origin')
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders(origin) })

  const url = new URL(req.url)
  const path = url.pathname.replace('/functions/v1/api-gateway', '')
  const apiKey = req.headers.get('x-api-key')

  if (!apiKey) return response({ error: 'Falta x-api-key header' }, 401, origin)

  const { valid, keyRecord, error } = await validateApiKey(apiKey)
  if (!valid) return response({ error }, 401, origin)

  // ============================================
  // GET /jobs — Lista jobs abiertos
  // ============================================
  if (path === '/jobs' && req.method === 'GET') {
    if (!hasScope(keyRecord, 'jobs:read')) return response({ error: 'Sin permisos: jobs:read' }, 403)

    const country = url.searchParams.get('country')
    const category = url.searchParams.get('category')
    const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') ?? '20') || 20, 1), 100)
    const page = Math.max(parseInt(url.searchParams.get('page') ?? '0') || 0, 0)

    let query = supabase
      .from('jobs')
      .select('id, title, description, category, status, budget_min, budget_max, currency, country, city, is_remote, created_at')
      .eq('status', 'open')
      .order('created_at', { ascending: false })
      .range(page * limit, (page + 1) * limit - 1)

    if (country) query = query.eq('country', country.toUpperCase())
    if (category) query = query.eq('category', category)

    const { data, error: dbError, count } = await query
    if (dbError) return response({ error: dbError.message }, 500)

    return response({
      data,
      meta: { page, limit, total: count ?? 0 },
    })
  }

  // ============================================
  // GET /jobs/:id — Detalle de job
  // ============================================
  if (path.match(/^\/jobs\/[^/]+$/) && req.method === 'GET') {
    if (!hasScope(keyRecord, 'jobs:read')) return response({ error: 'Sin permisos: jobs:read' }, 403)
    const jobId = path.split('/')[2]
    const { data, error: dbError } = await supabase
      .from('jobs')
      .select('id, title, description, category, status, budget_min, budget_max, currency, country, city, is_remote, created_at')
      .eq('id', jobId)
      .single()
    if (dbError) return response({ error: 'Job no encontrado' }, 404)
    return response({ data })
  }

  // ============================================
  // GET /pros — Lista pros verificados
  // ============================================
  if (path === '/pros' && req.method === 'GET') {
    if (!hasScope(keyRecord, 'pros:read')) return response({ error: 'Sin permisos: pros:read' }, 403)

    const country = url.searchParams.get('country')
    const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') ?? '20') || 20, 1), 100)
    const page = Math.max(parseInt(url.searchParams.get('page') ?? '0') || 0, 0)

    let query = supabase
      .from('pro_profiles')
      .select('id, full_name, role, country, is_verified, score, total_reviews, total_jobs_done, created_at')
      .order('score', { ascending: false })
      .range(page * limit, (page + 1) * limit - 1)

    if (country) query = query.eq('country', country.toUpperCase())

    const { data, error: dbError } = await query
    if (dbError) return response({ error: dbError.message }, 500)
    return response({ data, meta: { page, limit } })
  }

  // ============================================
  // GET /pros/:id — Perfil de pro
  // ============================================
  if (path.match(/^\/pros\/[^/]+$/) && req.method === 'GET') {
    if (!hasScope(keyRecord, 'pros:read')) return response({ error: 'Sin permisos: pros:read' }, 403)
    const proId = path.split('/')[2]
    const { data, error: dbError } = await supabase
      .from('pro_profiles')
      .select('*')
      .eq('id', proId)
      .single()
    if (dbError) return response({ error: 'Pro no encontrado' }, 404)
    return response({ data })
  }

  // ============================================
  // POST /jobs — Crea un job (scope: jobs:write)
  // ============================================
  if (path === '/jobs' && req.method === 'POST') {
    if (!hasScope(keyRecord, 'jobs:write')) return response({ error: 'Sin permisos: jobs:write' }, 403)

    const body = await req.json()
    const required = ['title', 'description', 'category', 'country']
    for (const field of required) {
      if (!body[field]) return response({ error: `Campo requerido: ${field}` }, 400)
    }

    const { data, error: dbError } = await supabase.from('jobs').insert({
      client_id: keyRecord.user_id,
      title: body.title,
      description: body.description,
      category: body.category,
      country: body.country,
      currency: body.currency ?? 'EUR',
      city: body.city ?? null,
      budget_min: body.budget_min ?? null,
      budget_max: body.budget_max ?? null,
      is_remote: body.is_remote ?? false,
      status: 'open',
    }).select().single()

    if (dbError) return response({ error: dbError.message }, 500)
    return response({ data }, 201)
  }

  // ============================================
  // GET /stats — Stats de la cuenta
  // ============================================
  if (path === '/stats' && req.method === 'GET') {
    if (!hasScope(keyRecord, 'stats:read')) return response({ error: 'Sin permisos: stats:read' }, 403)

    const { data } = await supabase
      .from('pro_analytics')
      .select('*')
      .eq('user_id', keyRecord.user_id)
      .single()

    return response({ data })
  }

  return response({ error: `Endpoint no encontrado: ${path}`, available: [
    'GET /jobs', 'GET /jobs/:id', 'POST /jobs',
    'GET /pros', 'GET /pros/:id', 'GET /stats'
  ]}, 404)
})
