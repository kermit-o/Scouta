import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const ANTHROPIC_API_KEY = Deno.env.get('ANTHROPIC_API_KEY')!

const CATEGORY_MAP: Record<string, string> = {
  limpieza: 'cleaning', limpiar: 'cleaning', aseo: 'cleaning',
  fontaneria: 'plumbing', fontanero: 'plumbing', agua: 'plumbing', tubo: 'plumbing', cañeria: 'plumbing',
  electricidad: 'electrical', electricista: 'electrical', luz: 'electrical', enchufe: 'electrical',
  pintura: 'painting', pintar: 'painting', pintor: 'painting',
  mudanza: 'moving', mover: 'moving', transporte: 'moving',
  jardineria: 'gardening', jardin: 'gardening', plantas: 'gardening', cesped: 'gardening',
  carpinteria: 'carpentry', madera: 'carpentry', muebles: 'carpentry', carpintero: 'carpentry',
  tecnologia: 'tech', informatica: 'tech', ordenador: 'tech', computadora: 'tech', wifi: 'tech',
  diseño: 'design', logo: 'design', grafico: 'design', web: 'design',
}

async function parseQueryWithClaude(query: string, country: string, currency: string): Promise<any> {
  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 400,
      system: `Eres un asistente de busqueda para Solva, una app de servicios del hogar.
Analiza la consulta del usuario y extrae informacion estructurada.
Responde SOLO con JSON valido, sin texto adicional, sin markdown.

Categorias validas: cleaning, plumbing, electrical, painting, moving, gardening, carpentry, tech, design, other
Pais del usuario: ${country}
Moneda: ${currency}`,
      messages: [{
        role: 'user',
        content: `Consulta: "${query}"

Extrae y responde con este JSON exacto:
{
  "category": "categoria_detectada_o_null",
  "keywords": ["palabra1", "palabra2"],
  "budget_max": numero_o_null,
  "is_remote": true_o_false_o_null,
  "urgency": "urgent|normal|flexible|null",
  "summary": "resumen en 1 frase de lo que busca",
  "suggestions": ["sugerencia1 para mejorar busqueda", "sugerencia2"]
}`
      }]
    })
  })

  const data = await response.json()
  const text = data.content?.[0]?.text ?? '{}'
  try {
    return JSON.parse(text)
  } catch {
    return {}
  }
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, content-type' }
    })
  }

  try {
    const { query, country, currency, lat, lng } = await req.json()

    if (!query?.trim()) {
      return new Response(JSON.stringify({ error: 'Query vacia' }), { status: 400 })
    }

    // 1. Analiza la query con Claude
    const parsed = await parseQueryWithClaude(query, country ?? 'ES', currency ?? 'EUR')

    // 2. Construye filtros para Supabase
    let dbQuery = supabase
      .from('jobs')
      .select('*, client:client_id(profile_quality_score, subscriptions(plan, status))')
      .eq('status', 'open')
      .eq('country', country ?? 'ES')
      .order('created_at', { ascending: false })
      .limit(20)

    // Filtro por categoría detectada
    if (parsed.category && parsed.category !== 'other') {
      dbQuery = dbQuery.eq('category', parsed.category)
    }

    // Filtro por presupuesto máximo
    if (parsed.budget_max) {
      dbQuery = dbQuery.lte('budget_max', parsed.budget_max * 1.3) // margen 30%
    }

    // Filtro remoto
    if (parsed.is_remote === true) {
      dbQuery = dbQuery.eq('is_remote', true)
    }

    // Búsqueda por keywords en título y descripción
    if (parsed.keywords?.length > 0) {
      const keywordFilter = parsed.keywords
        .map((k: string) => `title.ilike.%${k}%,description.ilike.%${k}%`)
        .join(',')
      dbQuery = dbQuery.or(keywordFilter)
    }

    let { data: jobs, error } = await dbQuery

    // 3. Si hay ubicación y pocos resultados, busca por proximidad
    if (lat && lng && (!jobs || jobs.length < 5)) {
      const { data: nearbyJobs } = await supabase.rpc('jobs_nearby', {
        lat, lng,
        radius_km: 50,
        max_results: 20,
      })
      if (nearbyJobs?.length) {
        // Combina sin duplicados
        const existingIds = new Set((jobs ?? []).map((j: any) => j.id))
        const extra = nearbyJobs.filter((j: any) => !existingIds.has(j.id))
        jobs = [...(jobs ?? []), ...extra]
      }
    }

    // 4. Score de relevancia con Claude (ordena resultados)
    if (jobs && jobs.length > 1) {
      const jobsWithScore = jobs.map((job: any) => {
        let score = 0
        const titleLower = job.title.toLowerCase()
        const descLower = job.description.toLowerCase()
        const queryLower = query.toLowerCase()

        // Keyword match en título (más peso)
        parsed.keywords?.forEach((k: string) => {
          if (titleLower.includes(k.toLowerCase())) score += 3
          if (descLower.includes(k.toLowerCase())) score += 1
        })

        // Categoría exacta
        if (job.category === parsed.category) score += 5

        // Urgencia implícita (jobs recientes = urgentes)
        const hoursOld = (Date.now() - new Date(job.created_at).getTime()) / 3600000
        if (parsed.urgency === 'urgent' && hoursOld < 24) score += 2

        // Presupuesto compatible
        if (parsed.budget_max && job.budget_max && job.budget_max <= parsed.budget_max) score += 2

        // Boost por plan del cliente del job (pro/company aparecen antes)
        if (job.client_plan === 'pro')     score += 3
        if (job.client_plan === 'company') score += 5

        // Boost por quality score del job (descripción IA)
        if (job.client_quality_score) score += Math.floor(job.client_quality_score / 20)

        return { ...job, _relevance: score }
      })

      jobs = jobsWithScore.sort((a: any, b: any) => b._relevance - a._relevance)
    }

    // Añadir client_plan y client_quality_score como campos planos
    const enriched = (jobs ?? []).map((j: any) => {
      const sub = j.client?.subscriptions?.[0]
      return {
        ...j,
        client_plan: sub?.status === 'active' || sub?.status === 'trialing' ? sub?.plan : 'free',
        client_quality_score: j.client?.profile_quality_score ?? 0,
        client: undefined, // no exponer datos del cliente
      }
    })

    return new Response(JSON.stringify({
      jobs: enriched,
      parsed,
      total: enriched.length,
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
