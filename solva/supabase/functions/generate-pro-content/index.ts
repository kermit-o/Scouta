import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)
const DEEPSEEK_API_KEY = Deno.env.get('DEEPSEEK_API_KEY')!

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
      is_onboarding = false,
    } = await req.json()

    if (!user_id || !category) {
      return new Response(JSON.stringify({ error: 'Faltan parámetros' }), { status: 400, headers: cors })
    }

    // Verificar plan Pro (skip si es onboarding)
    const { data: limit } = await supabase.rpc('check_plan_limit', {
      p_user_id: user_id,
      p_feature: 'ai_content',
    })
    const isOnboarding = !limit?.allowed && limit?.upgrade_required
    if (!limit?.allowed && !isOnboarding) {
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
- Precio por hora: ${avg_price ? `${avg_price} ${currency ?? 'EUR'}/h` : 'no especificado'}

GENERA EXACTAMENTE este JSON (sin markdown, sin texto extra):
{
  "profile_title": "Título del perfil (max 60 chars, impactante, con especialidad y ciudad si aplica)",
  "short_description": "Frase de marketing impactante (max 140 chars, beneficio principal para el cliente, tono confiado y profesional)",
  "long_description": "Bio de marketing profesional (250-350 chars): empieza con gancho, menciona experiencia y especialidad, añade propuesta de valor única y termina con llamada a la acción. Tono cercano pero experto, escrita en primera persona)",
  "keywords": ["5 palabras clave SEO relevantes para búsquedas en la app"],
  "bid_template": "Plantilla de respuesta para bids (100-150 chars, personalizable, profesional, incluye {{job_title}} como placeholder)",
  "usp": "Propuesta única de valor en 10 palabras máximo",
  "quality_tips": ["3 consejos específicos para mejorar el perfil de este profesional"]
}`

    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DEEPSEEK_API_KEY}`,
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      }),
    })

    const aiData = await response.json()
    if (!response.ok || aiData.error) {
      return new Response(JSON.stringify({ debug_error: aiData }), { status: 200, headers: { ...cors, 'Content-Type': 'application/json' } })
    }
    const rawText = aiData.choices?.[0]?.message?.content ?? '{}'

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
      bio: generated.long_description ?? generated.short_description ?? null,
      skills: generated.keywords ?? [],
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
