import Stripe from 'https://esm.sh/stripe@14.21.0'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, {
  apiVersion: '2024-04-10',
})

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, content-type',
      }
    })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    const { payment_id, contract_id } = await req.json()

    // Obtiene el payment
    const { data: payment, error } = await supabase
      .from('payments')
      .select('*')
      .eq('id', payment_id)
      .single()

    if (error || !payment) throw new Error('Payment no encontrado')
    if (payment.status !== 'held') throw new Error('El pago no está retenido')

    if (payment.provider === 'stripe') {
      // Captura el pago (libera del escrow)
      await stripe.paymentIntents.capture(payment.provider_payment_id)

      // Actualiza estado en DB
      await supabase.from('payments').update({
        status: 'released',
        released_at: new Date().toISOString(),
      }).eq('id', payment_id)

      // Marca contrato como completado
      await supabase.from('contracts').update({
        status: 'completed',
        completed_at: new Date().toISOString(),
      }).eq('id', contract_id)

      // Marca job como completado
      const { data: contract } = await supabase
        .from('contracts')
        .select('job_id')
        .eq('id', contract_id)
        .single()

      if (contract) {
        await supabase.from('jobs').update({ status: 'completed' }).eq('id', contract.job_id)
      }
    }

    return new Response(JSON.stringify({ success: true }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      }
    })

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
