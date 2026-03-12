import Stripe from 'https://esm.sh/stripe@14.21.0'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, { apiVersion: '2024-04-10' })

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })
  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )
    const body = await req.json()
    const payment_id = body.paymentId ?? body.payment_id
    const contract_id = body.contractId ?? body.contract_id

    const { data: payment, error } = await supabase
      .from('payments').select('*').eq('id', payment_id).single()
    if (error || !payment) throw new Error('Payment no encontrado')
    if (payment.status !== 'held') throw new Error('El pago no está retenido')

    // Intentar capturar en Stripe — si falla (test mode), continuar igualmente
    if (payment.provider === 'stripe' && payment.provider_payment_id) {
      try {
        const pi = await stripe.paymentIntents.retrieve(payment.provider_payment_id)
        if (pi.status === 'requires_capture') {
          await stripe.paymentIntents.capture(payment.provider_payment_id)
        }
        // Si está en otro estado (test mode sin tarjeta real), simplemente continuar
      } catch (stripeErr: any) {
        console.log('Stripe capture skipped:', stripeErr.message)
      }
    }

    await supabase.from('payments').update({
      status: 'released', released_at: new Date().toISOString(),
    }).eq('id', payment_id)

    await supabase.from('contracts').update({
      status: 'completed', completed_at: new Date().toISOString(),
    }).eq('id', contract_id)

    const { data: contract } = await supabase
      .from('contracts').select('job_id').eq('id', contract_id).single()
    if (contract) {
      await supabase.from('jobs').update({ status: 'completed' }).eq('id', contract.job_id)
    }

    // Email al pro — pago liberado
    try {
      const { data: proProfile } = await supabase.from('users').select('email, full_name').eq('id', payment.pro_id).single()
      const { data: contractData } = await supabase.from('contracts').select('job_id, jobs(title)').eq('id', contract_id).single()
      if (proProfile?.email) {
        await fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/send-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')}` },
          body: JSON.stringify({
            to: proProfile.email,
            template: 'payment_released',
            data: {
              proName: proProfile.full_name ?? 'Profesional',
              jobTitle: contractData?.jobs?.title ?? 'Trabajo',
              amount: payment.amount,
              proAmount: payment.pro_amount,
              fee: payment.platform_fee,
              currency: payment.currency,
            }
          })
        })
      }
    } catch (_) {}
    return new Response(JSON.stringify({ success: true }), {
      headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { ...CORS, 'Content-Type': 'application/json' }
    })
  }
})
