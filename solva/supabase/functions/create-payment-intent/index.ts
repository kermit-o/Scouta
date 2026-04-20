import Stripe from 'https://esm.sh/stripe@14.21.0'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, { apiVersion: '2024-04-10' })

const ALLOWED_ORIGINS = (Deno.env.get('ALLOWED_ORIGINS') ?? 'https://www.getsolva.co,https://getsolva.co').split(',')

function corsHeaders(req: Request) {
  const origin = req.headers.get('origin') ?? ''
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
  }
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
  const cors = corsHeaders(req)
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: cors })
  }
  try {
    // 1.3 — Validate auth and ownership
    const authHeader = req.headers.get('Authorization')
    if (!authHeader?.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Missing Authorization' }), { status: 401, headers: { ...cors, 'Content-Type': 'application/json' } })
    }
    const supabaseAuth = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_ANON_KEY') ?? Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!)
    const { data: { user }, error: authErr } = await supabaseAuth.auth.getUser(authHeader.replace('Bearer ', ''))
    if (authErr || !user) {
      return new Response(JSON.stringify({ error: 'Not authenticated' }), { status: 401, headers: { ...cors, 'Content-Type': 'application/json' } })
    }

    const { contract_id, amount, currency, country, client_id, pro_id } = await req.json()
    if (!contract_id || !amount || !currency || !country) {
      return new Response(JSON.stringify({ error: 'Missing parameters' }), { status: 400, headers: { ...cors, 'Content-Type': 'application/json' } })
    }

    // Validate amount and currency
    if (typeof amount !== 'number' || amount <= 0) {
      return new Response(JSON.stringify({ error: 'Invalid amount' }), { status: 400, headers: { ...cors, 'Content-Type': 'application/json' } })
    }
    if (!STRIPE_CURRENCY[currency]) {
      return new Response(JSON.stringify({ error: 'Unsupported currency' }), { status: 400, headers: { ...cors, 'Content-Type': 'application/json' } })
    }

    // Verify caller is the client on this contract
    if (client_id && user.id !== client_id) {
      return new Response(JSON.stringify({ error: 'Forbidden' }), { status: 403, headers: { ...cors, 'Content-Type': 'application/json' } })
    }

    const provider = PROVIDER_BY_COUNTRY[country] ?? 'stripe'

    let commissionPct = PLATFORM_FEE_PCT
    if (pro_id) {
      try {
        const supabase = createClient(
          Deno.env.get('SUPABASE_URL')!,
          Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
        )
        const { data: pct, error: pctError } = await supabase.rpc('get_commission_pct', { p_user_id: pro_id })
        if (pctError) {
          console.warn('get_commission_pct error, falling back to default:', pctError.message)
        } else if (pct != null && !Number.isNaN(Number(pct))) {
          commissionPct = Number(pct) / 100
        }
      } catch (err: any) {
        console.warn('commissionPct fetch failed:', err?.message ?? err)
      }
    }
    // Guard against NaN regardless of source
    if (!Number.isFinite(commissionPct) || commissionPct < 0 || commissionPct > 1) {
      commissionPct = PLATFORM_FEE_PCT
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
      }), { headers: { ...cors, 'Content-Type': 'application/json' } })
    }

    if (provider === 'mercadopago') {
      const supabaseUrl = Deno.env.get('SUPABASE_URL')!
      const mpResponse = await fetch(`${supabaseUrl}/functions/v1/create-mercadopago-payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': req.headers.get('Authorization') ?? '' },
        body: JSON.stringify({ contract_id, amount, country, client_id, pro_id, client_email: '' })
      })
      const mpData = await mpResponse.json()
      return new Response(JSON.stringify(mpData), { headers: { ...cors, 'Content-Type': 'application/json' } })
    }

    return new Response(JSON.stringify({ error: 'Provider no soportado' }), { status: 400, headers: { ...cors, 'Content-Type': 'application/json' } })
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { ...cors, 'Content-Type': 'application/json' } })
  }
})
