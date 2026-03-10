import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)
const ANTHROPIC_API_KEY = Deno.env.get('ANTHROPIC_API_KEY')!

const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors })

  try {
    const {
      user_id,
      category,        // 'cleaning' | 'plumbing' | etc
      years_experience,
      specialty,       // texto libre: "baños y cocinas"
      city,
      avg_price,
      currency,
      language = 'es', // 'es' | 'fr' | 'pt' | 'en'
    } = await req.json()

    if (!user_id || !category) {
      return new Response(JSON.stringify({ error: 'Faltan parámetros' }), { status: 400, headers: cors })
    }

    // Verificar plan Pro
    const { data: limit } = await supabase.rpc('check_plan_limit', {
      p_user_id: user_id,
      p_feature: 'ai_content',
    })
    if (!limit?.allowed) {
      return new Response(JSON.stringify({ error: 'Plan Pro requerido', upgrade_required: true }), { status: 403, headers: cors })
    }

    const CATEGORY_LABELS: Record<string, Record<string, string>> = {
      es: { cleaning: 'limpieza', plumbing: 'fontanería', electrical: 'electricidad', painting: 'pintura', moving: 'mudanzas', gardening: 'jardinería', carpentry: 'carpintería', tech: 'informática y tecnología', design: 'diseño', other: 'servicios del hogar' },
      fr: { cleaning: 'nettoyage', plumbing: 'plomberie', electrical: 'électricité', painting: 'peinture', moving: 'déménagement', gardening: 'jardinage', carpentry: 'menuiserie', tech: 'informatique', design: 'design', other: 'services à domicile' },
      pt: { cleaning: 'limpeza', plumbing: 'canalizações', electrical: 'eletricidade', painting: 'pintura', moving: 'mudanças', gardening: 'jardinagem', carpentry: 'carpintaria', tech: 'tecnologia', design: 'design', other: 'serviços domésticos' },
      en: { cleaning: 'cleaning', plumbing: 'plumbing', electrical: 'electrical', painting: 'painting', moving: 'moving', gardening: 'gardening', carpentry: 'carpentry', tech: 'tech support', design: 'design', other: 'home services' },
    }

    const catLabel = CATEGORY_LABELS[language]?.[category] ?? category
    const langInstruction: Record<string, string> = {
      es: 'Responde en español.',
      fr: 'Réponds en français.',
      pt: 'Responde em português.',
      en: 'Respond in English.',
    }

    const prompt = `Eres un experto en marketing para profesionales autónomos. ${langInstruction[language] ?? ''}

Genera contenido optimizado para el perfil de un profesional en una app de servicios del hogar llamada Solva.

DATOS DEL PROFESIONAL:
- Categoría: ${catLabel}
- Especialidad: ${specialty ?? 'general'}
- Años de experiencia: ${years_experience ?? 1}
- Ciudad: ${city ?? 'no especificada'}
- Precio medio: ${avg_price ? `${avg_price} ${currency ?? 'EUR'}` : 'no especificado'}

GENERA EXACTAMENTE este JSON (sin markdown, sin texto extra):
{
  "profile_title": "Título del perfil (max 60 chars, impactante, con especialidad y ciudad si aplica)",
  "short_description": "Descripción corta para cards de búsqueda (max 140 chars, beneficio principal del cliente, primera persona)",
  "long_description": "Descripción completa del perfil (250-350 chars, experiencia + especialidad + propuesta de valor + llamada a la acción)",
  "keywords": ["5 palabras clave SEO relevantes para búsquedas en la app"],
  "bid_template": "Plantilla de respuesta para bids (100-150 chars, personalizable, profesional, incluye {{job_title}} como placeholder)",
  "usp": "Propuesta única de valor en 10 palabras máximo",
  "quality_tips": ["3 consejos específicos para mejorar el perfil de este profesional"]
}`

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      }),
    })

    const aiData = await response.json()
    const rawText = aiData.content?.[0]?.text ?? '{}'

    let generated: any
    try {
      generated = JSON.parse(rawText)
    } catch {
      const match = rawText.match(/\{[\s\S]*\}/)
      generated = match ? JSON.parse(match[0]) : {}
    }

    // Guardar en DB
    await supabase.from('users').update({
      ai_description_generated: true,
      ai_keywords: generated.keywords ?? [],
    }).eq('id', user_id)

    // Recalcular quality score
    const { data: newScore } = await supabase.rpc('calculate_profile_quality', { uid: user_id })
    await supabase.from('users').update({ profile_quality_score: newScore ?? 0 }).eq('id', user_id)

    return new Response(JSON.stringify({
      ...generated,
      quality_score: newScore ?? 0,
    }), {
      headers: { ...cors, 'Content-Type': 'application/json' }
    })

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: cors })
  }
})
