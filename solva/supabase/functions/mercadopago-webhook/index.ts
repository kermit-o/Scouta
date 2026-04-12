import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const MP_ACCESS_TOKEN = Deno.env.get('MP_ACCESS_TOKEN')!
const MP_WEBHOOK_SECRET = Deno.env.get('MP_WEBHOOK_SECRET')

/**
 * Verifica la firma del webhook de MercadoPago.
 * MP envía x-signature: "ts=<timestamp>,v1=<hash>"
 * donde v1 = HMAC-SHA256(manifest, MP_WEBHOOK_SECRET).
 * El manifest es: id:<data.id>;request-id:<x-request-id>;ts:<ts>;
 */
async function verifyMpSignature(req: Request, dataId: string): Promise<boolean> {
  if (!MP_WEBHOOK_SECRET) {
    console.error('MP_WEBHOOK_SECRET not configured — rejecting all webhooks')
    return false
  }
  const sigHeader = req.headers.get('x-signature') ?? ''
  const requestId = req.headers.get('x-request-id') ?? ''
  const parts = Object.fromEntries(
    sigHeader.split(',').map((p) => p.trim().split('=') as [string, string])
  )
  const ts = parts.ts
  const v1 = parts.v1
  if (!ts || !v1) return false

  const manifest = `id:${dataId};request-id:${requestId};ts:${ts};`
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(MP_WEBHOOK_SECRET),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(manifest))
  const hex = Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')

  // Comparación constant-time simple
  if (hex.length !== v1.length) return false
  let diff = 0
  for (let i = 0; i < hex.length; i++) diff |= hex.charCodeAt(i) ^ v1.charCodeAt(i)
  return diff === 0
}

Deno.serve(async (req) => {
  try {
    const body = await req.json()
    const { type, data } = body

    if (type !== 'payment') {
      return new Response('ok', { status: 200 })
    }

    if (!data?.id) {
      return new Response('Missing data.id', { status: 400 })
    }

    // Verifica firma HMAC antes de procesar
    const sigOk = await verifyMpSignature(req, String(data.id))
    if (!sigOk) {
      console.error('MercadoPago webhook signature verification failed')
      return new Response('invalid signature', { status: 401 })
    }

    // Obtiene detalles del pago de MercadoPago
    const mpResponse = await fetch(`https://api.mercadopago.com/v1/payments/${data.id}`, {
      headers: { 'Authorization': `Bearer ${MP_ACCESS_TOKEN}` },
      signal: AbortSignal.timeout(8000),
    })
    if (!mpResponse.ok) {
      console.error('MP API error:', mpResponse.status)
      return new Response('mp api error', { status: 502 })
    }
    const payment = await mpResponse.json()

    const metadata = payment.metadata ?? {}
    const { contract_id, client_id, pro_id, platform_fee, pro_amount } = metadata

    if (!contract_id) {
      console.warn('MP webhook: missing contract_id in metadata, payment.id=', payment.id)
      return new Response('No contract_id in metadata', { status: 200 })
    }

    if (payment.status === 'approved') {
      // Guarda el pago como held (escrow manual vía MercadoPago)
      await supabase.from('payments').upsert({
        contract_id,
        client_id,
        pro_id,
        amount: payment.transaction_amount,
        platform_fee: parseFloat(platform_fee ?? 0),
        pro_amount: parseFloat(pro_amount ?? payment.transaction_amount * 0.9),
        currency: payment.currency_id,
        country: payment.country_code ?? 'AR',
        provider: 'mercadopago',
        provider_payment_id: String(payment.id),
        status: 'held',
        held_at: new Date().toISOString(),
      }, { onConflict: 'contract_id' })

      // Notifica al cliente y pro
      const { data: contract } = await supabase
        .from('contracts')
        .select('client_id, pro_id')
        .eq('id', contract_id)
        .single()

      if (contract) {
        await supabase.functions.invoke('send-notification', {
          body: {
            user_id: contract.pro_id,
            title: '💰 Pago recibido',
            body: 'El cliente realizó el pago. Está en escrow hasta que confirme la entrega.',
          }
        })
        await supabase.functions.invoke('send-notification', {
          body: {
            user_id: contract.client_id,
            title: '✅ Pago confirmado',
            body: 'Tu pago fue procesado. Se liberará al Pro cuando confirmes la entrega.',
          }
        })
      }

    } else if (payment.status === 'refunded') {
      await supabase.from('payments')
        .update({ status: 'refunded', refunded_at: new Date().toISOString() })
        .eq('provider_payment_id', String(payment.id))
    }

    return new Response('ok', { status: 200 })

  } catch (err: any) {
    console.error('Webhook error:', err.message)
    return new Response('error', { status: 500 })
  }
})
