import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, stripe-signature',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    const body = await req.text()
    const sig = req.headers.get('stripe-signature')
    const webhookSecret = Deno.env.get('STRIPE_WEBHOOK_SECRET')

    // Reject if webhook secret is not configured — never accept unverified events
    if (!webhookSecret) {
      console.error('STRIPE_WEBHOOK_SECRET not configured — rejecting webhook')
      return new Response(JSON.stringify({ error: 'Webhook secret not configured' }), {
        status: 500, headers: { ...CORS, 'Content-Type': 'application/json' }
      })
    }
    if (!sig) {
      return new Response(JSON.stringify({ error: 'Missing stripe-signature header' }), {
        status: 401, headers: { ...CORS, 'Content-Type': 'application/json' }
      })
    }

    // Verify HMAC signature with constant-time comparison
    const encoder = new TextEncoder()
    const parts = sig.split(',')
    const timestamp = parts.find((p: string) => p.startsWith('t='))?.split('=')[1]
    const v1 = parts.find((p: string) => p.startsWith('v1='))?.split('=')[1]

    if (!timestamp || !v1) throw new Error('Invalid Stripe signature format')

    const signedPayload = `${timestamp}.${body}`
    const key = await crypto.subtle.importKey(
      'raw', encoder.encode(webhookSecret),
      { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
    )
    const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(signedPayload))
    const expectedSigBytes = new Uint8Array(signature)
    const receivedSigBytes = new Uint8Array(v1.match(/.{2}/g)!.map(b => parseInt(b, 16)))

    if (expectedSigBytes.length !== receivedSigBytes.length) {
      throw new Error('Stripe signature mismatch')
    }
    // Constant-time comparison to prevent timing attacks
    let diff = 0
    for (let i = 0; i < expectedSigBytes.length; i++) {
      diff |= expectedSigBytes[i] ^ receivedSigBytes[i]
    }
    if (diff !== 0) throw new Error('Stripe signature mismatch')

    const event = JSON.parse(body)
    console.log('Webhook event:', event.type)

    if (event.type === 'payment_intent.created') {
      const pi = event.data.object
      const contract_id = pi.metadata?.contract_id
      if (!contract_id) return new Response('ok', { headers: CORS })

      await supabase.from('payments')
        .update({ status: 'held', provider_payment_id: pi.id })
        .eq('contract_id', contract_id)
        .eq('status', 'pending')

      console.log('Payment held for contract:', contract_id)
    }

    else if (event.type === 'payment_intent.amount_capturable_updated') {
      const pi = event.data.object
      const contract_id = pi.metadata?.contract_id
      if (!contract_id) return new Response('ok', { headers: CORS })

      await supabase.from('payments')
        .update({ status: 'held', provider_payment_id: pi.id })
        .eq('contract_id', contract_id)

      const { data: payment } = await supabase
        .from('payments')
        .select('client_id, pro_id, amount, currency')
        .eq('contract_id', contract_id)
        .maybeSingle()

      if (payment) {
        await supabase.from('notifications').insert({
          user_id: payment.client_id,
          type: 'payment_held',
          title: 'Pago en custodia',
          body: `Tu pago de ${payment.amount} ${payment.currency} está retenido de forma segura`,
          data: { contract_id },
        }).maybeSingle()
      }

      console.log('Payment capturable for contract:', contract_id)
    }

    else if (event.type === 'payment_intent.succeeded') {
      const pi = event.data.object
      const contract_id = pi.metadata?.contract_id
      if (!contract_id) return new Response('ok', { headers: CORS })

      await supabase.from('payments')
        .update({ status: 'released' })
        .eq('contract_id', contract_id)
        .eq('provider_payment_id', pi.id)

      console.log('Payment released for contract:', contract_id)
    }

    else if (event.type === 'payment_intent.payment_failed') {
      const pi = event.data.object
      const contract_id = pi.metadata?.contract_id
      if (!contract_id) return new Response('ok', { headers: CORS })

      await supabase.from('payments')
        .update({ status: 'pending' })
        .eq('contract_id', contract_id)
        .eq('provider_payment_id', pi.id)

      const { data: payment } = await supabase
        .from('payments')
        .select('client_id')
        .eq('contract_id', contract_id)
        .maybeSingle()

      if (payment) {
        await supabase.from('notifications').insert({
          user_id: payment.client_id,
          type: 'payment_failed',
          title: 'Pago fallido',
          body: 'Tu pago no pudo procesarse. Por favor intenta de nuevo.',
          data: { contract_id },
        }).maybeSingle()
      }

      console.log('Payment failed for contract:', contract_id)
    }

    else if (event.type === 'account.updated') {
      const account = event.data.object
      if (account.details_submitted && account.charges_enabled) {
        await supabase.from('users')
          .update({ stripe_onboarding_completed: true })
          .eq('stripe_account_id', account.id)
        console.log('Connect onboarding completed for account:', account.id)
      }
    }

    return new Response(JSON.stringify({ received: true }), {
      headers: { ...CORS, 'Content-Type': 'application/json' }
    })

  } catch (err: any) {
    console.error('Webhook error:', err.message)
    return new Response(JSON.stringify({ error: err.message }), {
      status: 400, headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  }
})
