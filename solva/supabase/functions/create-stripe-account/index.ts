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

Deno.serve(async (req) => {
  const cors = corsHeaders(req)
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors })
  try {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Missing Authorization header' }), {
        status: 401, headers: { ...cors, 'Content-Type': 'application/json' },
      })
    }
    const jwt = authHeader.replace('Bearer ', '')

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )
    const { data: { user }, error: authError } = await supabase.auth.getUser(jwt)
    if (authError || !user) {
      return new Response(JSON.stringify({ error: 'No autenticado' }), {
        status: 401, headers: { ...cors, 'Content-Type': 'application/json' },
      })
    }

    const { data: profile } = await supabase
      .from('users')
      .select('stripe_account_id, email, full_name, country, role')
      .eq('id', user.id)
      .single()

    if (!profile || !['pro', 'company'].includes(profile.role)) {
      return new Response(JSON.stringify({ error: 'Only pro/company users can create Stripe accounts' }), {
        status: 403, headers: { ...cors, 'Content-Type': 'application/json' },
      })
    }

    let accountId = profile.stripe_account_id

    // Crear cuenta Connect si no existe
    if (!accountId) {
      const account = await stripe.accounts.create({
        type: 'express',
        email: profile?.email ?? user.email,
        capabilities: {
          card_payments: { requested: true },
          transfers: { requested: true },
        },
        business_type: 'individual',
        metadata: { user_id: user.id },
      })
      accountId = account.id
      await supabase.from('users')
        .update({ stripe_account_id: accountId })
        .eq('id', user.id)
    }

    // Crear link de onboarding
    const accountLink = await stripe.accountLinks.create({
      account: accountId,
      refresh_url: 'https://www.getsolva.co/(app)/profile',
      return_url: 'https://www.getsolva.co/(app)/profile?stripe=success',
      type: 'account_onboarding',
    })

    return new Response(JSON.stringify({ url: accountLink.url, account_id: accountId }), {
      headers: { ...cors, 'Content-Type': 'application/json' }
    })
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { ...cors, 'Content-Type': 'application/json' }
    })
  }
})
