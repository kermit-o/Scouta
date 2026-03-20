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

    // Verificar firma de Stripe si hay webhook secret configurado
    let event: any
    if (webhookSecret && sig) {
      // Verificacion manual de firma HMAC
      const encoder = new TextEncoder()
      const parts = sig.split(',')
      const timestamp = parts.find((p: string) => p.startsWith('t='))?.split('=')[1]
      const v1 = parts.find((p: string) => p.startsWith('v1='))?.split('=')[1]

      if (!timestamp || !v1) throw new Error('Firma Stripe invalida')

      const signedPayload = `${timestamp}.${body}`
      const key = await crypto.subtle.importKey(
        'raw', encoder.encode(webhookSecret),
        { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
      )
      const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(signedPayload))
      const expectedSig = Array.from(new Uint8Array(signature))
        .map(b => b.toString(16).padStart(2, '0')).join('')

      if (expectedSig !== v1) throw new Error('Firma Stripe no coincide')
      event = JSON.parse(body)
    } else {
      event = JSON.parse(body)
    }

    console.log('Webhook event:', event.type)

    // Manejar eventos
    if (event.type === 'payment_intent.created') {
      const pi = event.data.object
      const contract_id = pi.metadata?.contract_id
      if (!contract_id) return new Response('ok', { headers: CORS })

      // Actualizar payment a held cuando se crea el payment intent
      await supabase.from('payments')
        .update({ status: 'held', provider_payment_id: pi.id })
        .eq('contract_id', contract_id)
        .eq('status', 'pending')

      console.log('Payment held for contract:', contract_id)
    }

    else if (event.type === 'payment_intent.amount_capturable_updated') {
      // Pago autorizado y listo para captura (escrow)
      const pi = event.data.object
      const contract_id = pi.metadata?.contract_id
      if (!contract_id) return new Response('ok', { headers: CORS })

      await supabase.from('payments')
        .update({ status: 'held', provider_payment_id: pi.id })
        .eq('contract_id', contract_id)

      // Notificar al cliente que el pago está retenido
      const { data: payment } = await supabase
        .from('payments')
        .select('client_id, pro_id, amount, currency')
        .eq('contract_id', contract_id)
        .single()

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
      // Pago capturado exitosamente
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

      // Notificar al cliente del fallo
      const { data: payment } = await supabase
        .from('payments')
        .select('client_id')
        .eq('contract_id', contract_id)
        .single()

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
      // Pro completó onboarding de Stripe Connect
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
