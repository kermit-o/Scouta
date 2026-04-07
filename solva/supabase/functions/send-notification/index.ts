const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })
  try {
    const { user_id, title, body, data } = await req.json()
    if (!user_id || !title || !body) {
      return new Response(JSON.stringify({ error: 'Parametros invalidos' }), { status: 400, headers: { ...CORS, 'Content-Type': 'application/json' } })
    }
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const tokensRes = await fetch(`${supabaseUrl}/rest/v1/push_tokens?user_id=eq.${user_id}&select=token`, {
      headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
    })
    const tokens = await tokensRes.json()
    if (!tokens.length) {
      return new Response(JSON.stringify({ success: true, sent: 0 }), { headers: { ...CORS, 'Content-Type': 'application/json' } })
    }
    const messages = tokens.map((t: any) => ({
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
    })
    const result = await pushRes.json()
    return new Response(JSON.stringify({ success: true, sent: messages.length, result }), {
      headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  }
})
