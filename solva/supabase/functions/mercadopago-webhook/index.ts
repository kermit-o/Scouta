import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const MP_ACCESS_TOKEN = Deno.env.get('MP_ACCESS_TOKEN')!

Deno.serve(async (req) => {
  try {
    const body = await req.json()
    const { type, data } = body

    if (type !== 'payment') {
      return new Response('ok', { status: 200 })
    }

    // Obtiene detalles del pago de MercadoPago
    const mpResponse = await fetch(`https://api.mercadopago.com/v1/payments/${data.id}`, {
      headers: { 'Authorization': `Bearer ${MP_ACCESS_TOKEN}` }
    })
    const payment = await mpResponse.json()

    const { contract_id, client_id, pro_id, platform_fee, pro_amount } = payment.metadata ?? {}

    if (!contract_id) {
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
