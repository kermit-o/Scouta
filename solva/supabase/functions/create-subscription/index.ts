import Stripe from 'https://esm.sh/stripe@14.21.0'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, { apiVersion: '2024-04-10' })
const supabase = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!)

// Precio mensual por país (en centavos)
const PRICES: Record<string, { pro: number; company: number; currency: string }> = {
  ES: { pro: 1499, company: 3999, currency: 'eur' },
  FR: { pro: 1499, company: 3999, currency: 'eur' },
  MX: { pro: 29900, company: 79900, currency: 'mxn' },
  CO: { pro: 5990000, company: 15990000, currency: 'cop' },
  AR: { pro: 299900, company: 799900, currency: 'ars' },
  BR: { pro: 7990, company: 21990, currency: 'brl' },
  CL: { pro: 12990, company: 34990, currency: 'clp' },
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, content-type' } })
  }
  try {
    const { user_id, plan, country, email } = await req.json()
    const pricing = PRICES[country] ?? PRICES['ES']
    const amount = plan === 'company' ? pricing.company : pricing.pro

    // Crea o recupera customer de Stripe
    const { data: sub } = await supabase
      .from('subscriptions')
      .select('stripe_subscription_id')
      .eq('user_id', user_id)
      .single()

    let customerId: string
    const customers = await stripe.customers.list({ email, limit: 1 })
    if (customers.data.length > 0) {
      customerId = customers.data[0].id
    } else {
      const customer = await stripe.customers.create({ email, metadata: { user_id } })
      customerId = customer.id
    }

    // Crea precio dinámico y suscripción
    const price = await stripe.prices.create({
      unit_amount: amount,
      currency: pricing.currency,
      recurring: { interval: 'month' },
      product_data: { name: `Solva ${plan.charAt(0).toUpperCase() + plan.slice(1)}` },
    })

    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [{ price: price.id }],
      payment_behavior: 'default_incomplete',
      expand: ['latest_invoice.payment_intent'],
      trial_period_days: 14,
    })

    const invoice = subscription.latest_invoice as any
    const clientSecret = invoice?.payment_intent?.client_secret

    // Actualiza DB
    await supabase.from('subscriptions').upsert({
      user_id,
      plan,
      status: 'trialing',
      stripe_subscription_id: subscription.id,
      current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
      current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
    }, { onConflict: 'user_id' })

    return new Response(JSON.stringify({
      subscription_id: subscription.id,
      client_secret: clientSecret,
      trial_end: subscription.trial_end,
      amount: amount / 100,
      currency: pricing.currency.toUpperCase(),
    }), { headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } })

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
