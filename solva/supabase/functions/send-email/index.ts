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
  review_request: (d) => ({
    subject: `⭐ ¿Cómo fue el trabajo? Deja tu reseña — "${d.jobTitle}"`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#F59E0B">¿Cómo fue la experiencia?</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>El trabajo <b>"${d.jobTitle}"</b> ha sido completado. Tu opinión es muy importante para la comunidad de Solva.</p>
        <p>Solo te tomará 1 minuto — puntúa la experiencia y ayuda a otros usuarios.</p>
        <a href="https://www.getsolva.co/(app)/jobs/${d.jobId}/review" style="display:inline-block;margin-top:16px;background:#F59E0B;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Dejar reseña ⭐</a>
        <p style="color:#aaa;font-size:12px;margin-top:24px">Este enlace es válido durante 7 días.</p>
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
  dispute_opened: (d) => ({
    subject: `⚠️ Disputa abierta — "${d.jobTitle}"`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#DC2626">Se ha abierto una disputa</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Se ha abierto una disputa para el trabajo <b>"${d.jobTitle}"</b>.</p>
        <p><b>Motivo:</b> ${d.reason}</p>
        <p style="color:#555">El pago queda bloqueado hasta que se resuelva. Nuestro equipo revisará el caso en 48-72h hábiles.</p>
        <a href="https://www.getsolva.co/(app)/jobs/${d.jobId}/dispute" style="display:inline-block;margin-top:16px;background:#DC2626;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver disputa →</a>
      </div>`,
  }),
  welcome: (d) => ({
    subject: `🎉 Bienvenido a Solva, ${d.userName}`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#2563EB">¡Bienvenido a Solva!</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Gracias por unirte a Solva, la plataforma que conecta clientes con profesionales verificados para servicios del hogar.</p>
        <p>Esto es lo que puedes hacer ahora:</p>
        <ul style="color:#555;line-height:24px">
          <li>🔍 <b>Buscar profesionales</b> cerca de ti</li>
          <li>📝 <b>Publicar un trabajo</b> y recibir ofertas</li>
          <li>🛡️ <b>Pagar con escrow</b> — tu dinero está protegido</li>
        </ul>
        <a href="https://www.getsolva.co" style="display:inline-block;margin-top:16px;background:#2563EB;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Empezar →</a>
        <p style="color:#aaa;font-size:12px;margin-top:24px">¿Necesitas ayuda? Responde a este email o visita nuestro centro de ayuda.</p>
      </div>`,
  }),
  job_posted: (d) => ({
    subject: `📝 Tu trabajo "${d.jobTitle}" ha sido publicado`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#2563EB">Trabajo publicado</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Tu trabajo <b>"${d.jobTitle}"</b> ya está visible para los profesionales de tu zona.</p>
        <p style="color:#555">Normalmente recibirás las primeras ofertas en menos de 24 horas. Te notificaremos por email y push cada vez que un profesional envíe una propuesta.</p>
        <a href="https://www.getsolva.co/(app)/jobs/${d.jobId}" style="display:inline-block;margin-top:16px;background:#2563EB;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver mi trabajo →</a>
      </div>`,
  }),
  payment_held: (d) => ({
    subject: `🔒 Pago retenido en escrow — ${d.amount} ${d.currency}`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#2563EB">Pago en escrow</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Tu pago de <b>${d.amount} ${d.currency}</b> para el trabajo <b>"${d.jobTitle}"</b> ha sido procesado y está retenido de forma segura.</p>
        <p style="color:#555">El dinero se liberará al profesional cuando confirmes que el trabajo está completado.</p>
        <a href="https://www.getsolva.co/(app)/jobs/${d.jobId}/payment" style="display:inline-block;margin-top:16px;background:#2563EB;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver estado del pago →</a>
      </div>`,
  }),
  kyc_approved: (d) => ({
    subject: `✅ Identidad verificada — ya eres un profesional de confianza`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#059669">¡Verificación completada!</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Tu identidad ha sido verificada correctamente. Ahora tienes el badge de verificado en tu perfil.</p>
        <p style="color:#555">Los profesionales verificados reciben hasta un 40% más de contratos. ¡Enhorabuena!</p>
        <a href="https://www.getsolva.co/(app)/profile" style="display:inline-block;margin-top:16px;background:#059669;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Ver mi perfil →</a>
      </div>`,
  }),
  kyc_rejected: (d) => ({
    subject: `❌ Verificación rechazada — acción requerida`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#DC2626">Verificación rechazada</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Tu verificación de identidad ha sido rechazada.</p>
        ${d.reason ? `<p><b>Motivo:</b> ${d.reason}</p>` : ''}
        <p style="color:#555">Puedes volver a intentarlo con documentos más claros. Asegúrate de que las fotos sean legibles y la selfie coincida con el documento.</p>
        <a href="https://www.getsolva.co/(app)/kyc" style="display:inline-block;margin-top:16px;background:#DC2626;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Reintentar verificación →</a>
      </div>`,
  }),
  trial_expiring: (d) => ({
    subject: `⏰ Tu prueba Pro expira en ${d.daysLeft} día${d.daysLeft === 1 ? '' : 's'}`,
    html: `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:32px">
        <h1 style="color:#D97706">Tu prueba Pro está por terminar</h1>
        <p>Hola <b>${d.userName}</b>,</p>
        <p>Tu período de prueba de <b>Solva Pro</b> expira en <b>${d.daysLeft} día${d.daysLeft === 1 ? '' : 's'}</b>.</p>
        <p style="color:#555">Con Pro tienes bids ilimitados, comisión reducida al 5%, y posición preferente en búsquedas. Un solo contrato extra al mes cubre la suscripción.</p>
        <a href="https://www.getsolva.co/(app)/subscription" style="display:inline-block;margin-top:16px;background:#2563EB;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:700">Activar Pro →</a>
        <p style="color:#aaa;font-size:12px;margin-top:24px">Si no activas Pro, volverás automáticamente al plan gratuito.</p>
      </div>`,
  }),
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')
  if (!RESEND_API_KEY) {
    console.error('send-email: RESEND_API_KEY not configured')
    return new Response(JSON.stringify({ error: 'Email provider not configured' }), {
      status: 500,
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })
  }

  try {
    const { to, template, data } = await req.json()
    if (!to || !template || !TEMPLATES[template]) {
      return new Response(JSON.stringify({ error: 'Parámetros inválidos' }), {
        status: 400,
        headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }
    const { subject, html } = TEMPLATES[template](data)
    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Solva <noreply@scouta.co>',
        to,
        subject,
        html,
      }),
      signal: AbortSignal.timeout(8000),
    })
    const result = await res.json()
    if (!res.ok) throw new Error(result.message ?? 'Error enviando email')
    return new Response(JSON.stringify({ success: true, id: result.id }), {
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })
  } catch (err: any) {
    console.error('send-email error:', err?.message ?? err)
    return new Response(JSON.stringify({ error: 'Failed to send email' }), {
      status: 500,
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })
  }
})
