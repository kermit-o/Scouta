const ANTHROPIC_API_KEY = Deno.env.get('ANTHROPIC_API_KEY')

interface VerifyResult {
  is_valid: boolean
  is_relevant: boolean
  before_detected: boolean
  after_detected: boolean
  improvement_visible: boolean
  confidence: number
  issues: string[]
  summary: string
}

const MAX_IMAGE_BYTES = 5 * 1024 * 1024 // 5 MB

async function fetchImageAsBase64(url: string): Promise<{ data: string; mediaType: string }> {
  const response = await fetch(url, { signal: AbortSignal.timeout(6000) })
  if (!response.ok) {
    throw new Error(`Image fetch failed: ${response.status}`)
  }
  const contentType = response.headers.get('content-type') || 'image/jpeg'
  if (!contentType.startsWith('image/')) {
    throw new Error(`Invalid content-type: ${contentType}`)
  }
  const contentLength = parseInt(response.headers.get('content-length') ?? '0', 10)
  if (contentLength > MAX_IMAGE_BYTES) {
    throw new Error(`Image too large: ${contentLength} bytes`)
  }
  const buffer = await response.arrayBuffer()
  if (buffer.byteLength > MAX_IMAGE_BYTES) {
    throw new Error(`Image too large: ${buffer.byteLength} bytes`)
  }
  const bytes = new Uint8Array(buffer)
  const binary = bytes.reduce((acc, byte) => acc + String.fromCharCode(byte), '')
  const base64 = btoa(binary)
  return { data: base64, mediaType: contentType.split(';')[0] }
}

async function verifyPhotosWithClaude(
  photosBefore: string[],
  photosAfter: string[],
  jobCategory: string,
  jobTitle: string,
): Promise<VerifyResult> {

  const imageBlocks: any[] = []

  // Agrega fotos antes
  for (const url of photosBefore.slice(0, 2)) {
    try {
      const { data, mediaType } = await fetchImageAsBase64(url)
      imageBlocks.push({
        type: 'text',
        text: '--- FOTO ANTES DEL TRABAJO ---'
      })
      imageBlocks.push({
        type: 'image',
        source: { type: 'base64', media_type: mediaType, data }
      })
    } catch { /* skip */ }
  }

  // Agrega fotos después
  for (const url of photosAfter.slice(0, 2)) {
    try {
      const { data, mediaType } = await fetchImageAsBase64(url)
      imageBlocks.push({
        type: 'text',
        text: '--- FOTO DESPUES DEL TRABAJO ---'
      })
      imageBlocks.push({
        type: 'image',
        source: { type: 'base64', media_type: mediaType, data }
      })
    } catch { /* skip */ }
  }

  if (imageBlocks.length === 0) {
    return {
      is_valid: false,
      is_relevant: false,
      before_detected: false,
      after_detected: false,
      improvement_visible: false,
      confidence: 0,
      issues: ['No se pudieron cargar las imagenes'],
      summary: 'No se pudieron verificar las fotos',
    }
  }

  imageBlocks.push({
    type: 'text',
    text: `
Tipo de trabajo: ${jobCategory}
Titulo del trabajo: ${jobTitle}

Analiza estas fotos de antes y despues de un trabajo de servicios del hogar/profesional.

Responde SOLO con JSON valido sin markdown:
{
  "is_valid": boolean (las fotos son reales, no memes ni imagenes de internet),
  "is_relevant": boolean (las fotos son relevantes al tipo de trabajo ${jobCategory}),
  "before_detected": boolean (se detecta una foto de antes/estado inicial),
  "after_detected": boolean (se detecta una foto de despues/resultado final),
  "improvement_visible": boolean (hay mejora visible entre antes y despues),
  "confidence": numero entre 0 y 1,
  "issues": ["lista de problemas encontrados, vacia si todo ok"],
  "summary": "descripcion breve en 1 frase de lo que se ve en las fotos"
}`
  })

  if (!ANTHROPIC_API_KEY) {
    throw new Error('ANTHROPIC_API_KEY not configured')
  }

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': ANTHROPIC_API_KEY,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 500,
      messages: [{ role: 'user', content: imageBlocks }]
    }),
    signal: AbortSignal.timeout(30000),
  })

  if (!response.ok) {
    throw new Error(`Anthropic API error: ${response.status}`)
  }

  const data = await response.json()
  const text = data.content?.[0]?.text ?? '{}'

  try {
    return JSON.parse(text)
  } catch {
    return {
      is_valid: true,
      is_relevant: true,
      before_detected: photosBefore.length > 0,
      after_detected: photosAfter.length > 0,
      improvement_visible: false,
      confidence: 0.5,
      issues: ['No se pudo analizar completamente'],
      summary: 'Verificacion parcial',
    }
  }
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, content-type' }
    })
  }

  try {
    const { photos_before, photos_after, job_category, job_title, review_id } = await req.json()

    if (!photos_before?.length && !photos_after?.length) {
      return new Response(JSON.stringify({
        verified: false,
        result: null,
        message: 'No hay fotos para verificar'
      }), { headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } })
    }

    const result = await verifyPhotosWithClaude(
      photos_before ?? [],
      photos_after ?? [],
      job_category ?? 'other',
      job_title ?? 'Servicio',
    )

    const verified = result.is_valid && result.is_relevant && result.confidence >= 0.6

    return new Response(JSON.stringify({ verified, result, review_id }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
