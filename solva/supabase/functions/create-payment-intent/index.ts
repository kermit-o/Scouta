import Stripe from 'https://esm.sh/stripe@14.21.0'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, {
  apiVersion: '2024-04-10',
})

// Proveedor por país
const PROVIDER_BY_COUNTRY: Record<string, 'stripe' | 'mercadopago'> = {
  // Europa — Stripe
  ES: 'stripe', FR: 'stripe', BE: 'stripe', NL: 'stripe',
  DE: 'stripe', PT: 'stripe', IT: 'stripe', GB: 'stripe',
  // LatAm — MercadoPago
  AR: 'mercadopago', BR: 'mercadopago', CL: 'mercadopago',
  MX: 'mercadopago', CO: 'mercadopago',
}

// Moneda a código Stripe
const STRIPE_CURRENCY: Record<string, string> = {
  EUR: 'eur', GBP: 'gbp',
  MXN: 'mxn', COP: 'cop',
  ARS: 'ars', BRL: 'brl', CLP: 'clp',
}

const PLATFORM_FEE_PCT = 0.10

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
    const { contract_id, amount, currency, country, client_id, pro_id } = await req.json()

    if (!contract_id || !amount || !currency || !country) {
      return new Response(JSON.stringify({ error: 'Faltan parámetros' }), { status: 400 })
    }

    const provider = PROVIDER_BY_COUNTRY[country] ?? 'stripe'
    const platformFee = Math.round(amount * PLATFORM_FEE_PCT * 100) / 100
    const proAmount = Math.round((amount - platformFee) * 100) / 100

    if (provider === 'stripe') {
      const paymentIntent = await stripe.paymentIntents.create({
        amount: Math.round(amount * 100), // en centavos
        currency: STRIPE_CURRENCY[currency] ?? 'eur',
        capture_method: 'manual', // ESCROW: captura manual al liberar
        metadata: {
          contract_id,
          client_id,
          pro_id,
          platform_fee: platformFee.toString(),
          pro_amount: proAmount.toString(),
        },
      })

      return new Response(JSON.stringify({
        provider: 'stripe',
        client_secret: paymentIntent.client_secret,
        payment_intent_id: paymentIntent.id,
        platform_fee: platformFee,
        pro_amount: proAmount,
      }), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        }
      })
    }

    // MercadoPago para LatAm
    if (provider === 'mercadopago') {
      // Delega a la función de MercadoPago
      const supabaseUrl = Deno.env.get('SUPABASE_URL')!
      const mpResponse = await fetch(`${supabaseUrl}/functions/v1/create-mercadopago-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.get('Authorization') ?? '',
        },
        body: JSON.stringify({
          contract_id, amount, country, client_id, pro_id,
          client_email: '',
        })
      })
      const mpData = await mpResponse.json()
      return new Response(JSON.stringify(mpData), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      })
    }

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
