import Stripe from 'https://esm.sh/stripe@14.21.0'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, { apiVersion: '2024-04-10' })

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
}

const PROVIDER_BY_COUNTRY: Record<string, 'stripe' | 'mercadopago'> = {
  ES: 'stripe', FR: 'stripe', BE: 'stripe', NL: 'stripe',
  DE: 'stripe', PT: 'stripe', IT: 'stripe', GB: 'stripe',
  AR: 'mercadopago', BR: 'mercadopago', CL: 'mercadopago',
  MX: 'mercadopago', CO: 'mercadopago',
}

const STRIPE_CURRENCY: Record<string, string> = {
  EUR: 'eur', GBP: 'gbp', MXN: 'mxn', COP: 'cop', ARS: 'ars', BRL: 'brl', CLP: 'clp',
}

const PLATFORM_FEE_PCT = 0.10

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: CORS })
  }
  try {
    const { contract_id, amount, currency, country, client_id, pro_id } = await req.json()
    if (!contract_id || !amount || !currency || !country) {
      return new Response(JSON.stringify({ error: 'Faltan parámetros' }), { status: 400, headers: { ...CORS, 'Content-Type': 'application/json' } })
    }

    const provider = PROVIDER_BY_COUNTRY[country] ?? 'stripe'

    let commissionPct = PLATFORM_FEE_PCT
    if (pro_id) {
      try {
        const supabase = createClient(
          Deno.env.get('SUPABASE_URL')!,
          Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
        )
        const { data: pct } = await supabase.rpc('get_commission_pct', { p_user_id: pro_id })
        if (pct != null) commissionPct = pct / 100
      } catch (_) {}
    }

    const platformFee = Math.round(amount * commissionPct * 100) / 100
    const proAmount = Math.round((amount - platformFee) * 100) / 100

    if (provider === 'stripe') {
      const paymentIntent = await stripe.paymentIntents.create({
        amount: Math.round(amount * 100),
        currency: STRIPE_CURRENCY[currency] ?? 'eur',
        capture_method: 'manual',
        metadata: { contract_id, client_id, pro_id, platform_fee: platformFee.toString(), pro_amount: proAmount.toString() },
      })
      return new Response(JSON.stringify({
        provider: 'stripe',
        client_secret: paymentIntent.client_secret,
        payment_intent_id: paymentIntent.id,
        platform_fee: platformFee,
        pro_amount: proAmount,
      }), { headers: { ...CORS, 'Content-Type': 'application/json' } })
    }

    if (provider === 'mercadopago') {
      const supabaseUrl = Deno.env.get('SUPABASE_URL')!
      const mpResponse = await fetch(`${supabaseUrl}/functions/v1/create-mercadopago-payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': req.headers.get('Authorization') ?? '' },
        body: JSON.stringify({ contract_id, amount, country, client_id, pro_id, client_email: '' })
      })
      const mpData = await mpResponse.json()
      return new Response(JSON.stringify(mpData), { headers: { ...CORS, 'Content-Type': 'application/json' } })
    }

    return new Response(JSON.stringify({ error: 'Provider no soportado' }), { status: 400, headers: { ...CORS, 'Content-Type': 'application/json' } })
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...CORS, 'Content-Type': 'application/json' } })
  }
})
