import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
}

const supabaseUrl = Deno.env.get('SUPABASE_URL')
const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')

function jsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  })
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  if (!supabaseUrl || !supabaseKey) {
    console.error('send-notification: missing SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY')
    return jsonResponse({ error: 'Server not configured' }, 500)
  }

  try {
    const { user_id, title, body, data } = await req.json()
    if (!user_id || !title || !body) {
      return jsonResponse({ error: 'Parametros invalidos' }, 400)
    }

    const admin = createClient(supabaseUrl, supabaseKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    })

    const { data: tokens, error: tokensError } = await admin
      .from('push_tokens')
      .select('token')
      .eq('user_id', user_id)

    if (tokensError) {
      console.error('push_tokens fetch error:', tokensError.message)
      return jsonResponse({ error: 'Failed to fetch tokens' }, 500)
    }
    if (!tokens || tokens.length === 0) {
      return jsonResponse({ success: true, sent: 0 })
    }

    const messages = tokens.map((t: { token: string }) => ({
      to: t.token,
      title,
      body,
      data: data ?? {},
      sound: 'default',
    }))

    const pushRes = await fetch('https://exp.host/--/api/v2/push/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(messages),
      signal: AbortSignal.timeout(8000),
    })

    if (!pushRes.ok) {
      console.error('Expo push HTTP error:', pushRes.status)
      return jsonResponse({ error: 'Push provider error' }, 502)
    }

    const result = await pushRes.json()

    // Persistir notificación en tabla (para historial/inbox del usuario)
    await admin.from('notifications').insert({
      user_id,
      title,
      body,
      data: data ?? {},
    })

    return jsonResponse({ success: true, sent: messages.length, result })
  } catch (err: any) {
    // Nunca exponer el error completo al cliente (puede contener info sensible)
    console.error('send-notification error:', err?.message ?? err)
    return jsonResponse({ error: 'Internal error' }, 500)
  }
})
