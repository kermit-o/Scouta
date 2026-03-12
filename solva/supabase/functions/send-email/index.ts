const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
}

const TEMPLATES: Record<string, (data: any) => { subject: string; html: string }> = {
  bid_received: (d) => ({
    subject: `💼 Nueva oferta para "${d.jobTitle}"`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#1a1a2e">Nueva oferta recibida</h1>
        <p>Hola <b>${d.clientName}</b>,</p>
        <p><b>${d.proName}</b> ha enviado una oferta de <b>${d.amount} ${d.currency}</b> para tu trabajo <b>"${d.jobTitle}"</b>.</p>
        <p style="color:#555">"${d.message}"</p>
        <a href="https://www.getsolva.co" style="display:inline-block;margin-top:16px;background:#2563EB;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver oferta →</a>
      </div>`,
  }),
  bid_accepted: (d) => ({
    subject: `✅ Tu oferta fue aceptada — "${d.jobTitle}"`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#059669">¡Oferta aceptada!</h1>
        <p>Hola <b>${d.proName}</b>,</p>
        <p>Tu oferta de <b>${d.amount} ${d.currency}</b> para <b>"${d.jobTitle}"</b> ha sido aceptada.</p>
        <p>El contrato está listo. El pago quedará en escrow hasta que completes el trabajo.</p>
        <a href="https://www.getsolva.co" style="display:inline-block;margin-top:16px;background:#059669;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver contrato →</a>
      </div>`,
  }),
  payment_released: (d) => ({
    subject: `💰 Pago liberado — ${d.amount} ${d.currency}`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#2563EB">¡Pago recibido!</h1>
        <p>Hola <b>${d.proName}</b>,</p>
        <p>El cliente ha confirmado la entrega. Has recibido <b>${d.proAmount} ${d.currency}</b> por el trabajo <b>"${d.jobTitle}"</b>.</p>
        <p style="color:#888;font-size:13px">Comisión Solva (10%): -${d.fee} ${d.currency}</p>
        <a href="https://www.getsolva.co" style="display:inline-block;margin-top:16px;background:#2563EB;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver historial →</a>
      </div>`,
  }),
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })
  try {
    const { to, template, data } = await req.json()
    if (!to || !template || !TEMPLATES[template]) {
      return new Response(JSON.stringify({ error: 'Parámetros inválidos' }), { status: 400, headers: { ...CORS, 'Content-Type': 'application/json' } })
    }
    const { subject, html } = TEMPLATES[template](data)
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('RESEND_API_KEY')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Solva <onboarding@resend.dev>',
        to,
        subject,
        html,
      }),
    })
    const result = await res.json()
    if (!res.ok) throw new Error(result.message ?? 'Error enviando email')
    return new Response(JSON.stringify({ success: true, id: result.id }), {
      headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  }
})
