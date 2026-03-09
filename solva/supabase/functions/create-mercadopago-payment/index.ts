import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const MP_ACCESS_TOKEN = Deno.env.get('MP_ACCESS_TOKEN')!

// Moneda por país LatAm
const MP_CURRENCY: Record<string, string> = {
  AR: 'ARS', BR: 'BRL', CL: 'CLP', MX: 'MXN', CO: 'COP'
}

const PLATFORM_FEE_PCT = 0.10

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', {
      headers: { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, content-type' }
    })
  }

  try {
    const { contract_id, amount, country, client_id, pro_id, client_email } = await req.json()

    const platformFee = Math.round(amount * PLATFORM_FEE_PCT * 100) / 100
    const proAmount = Math.round((amount - platformFee) * 100) / 100
    const currency = MP_CURRENCY[country] ?? 'ARS'

    // Obtiene token del pro en MercadoPago si existe
    const { data: mpAccount } = await supabase
      .from('mercadopago_accounts')
      .select('mp_access_token, mp_user_id')
      .eq('user_id', pro_id)
      .maybeSingle()

    // Crea preferencia de pago en MercadoPago
    const preferenceBody = {
      items: [{
        title: `Servicio Solva - Contrato ${contract_id.slice(0, 8).toUpperCase()}`,
        quantity: 1,
        unit_price: amount,
        currency_id: currency,
      }],
      payer: { email: client_email },
      metadata: {
        contract_id,
        client_id,
        pro_id,
        platform_fee: platformFee,
        pro_amount: proAmount,
      },
      notification_url: `${Deno.env.get('SUPABASE_URL')}/functions/v1/mercadopago-webhook`,
      // Marketplace split si el pro tiene cuenta conectada
      ...(mpAccount ? {
        marketplace_fee: Math.round(platformFee * 100),
      } : {}),
    }

    const mpResponse = await fetch('https://api.mercadopago.com/checkout/preferences', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${mpAccount?.mp_access_token ?? MP_ACCESS_TOKEN}`,
      },
      body: JSON.stringify(preferenceBody),
    })

    const preference = await mpResponse.json()

    if (!preference.id) {
      throw new Error(preference.message ?? 'Error creando preferencia MercadoPago')
    }

    return new Response(JSON.stringify({
      provider: 'mercadopago',
      preference_id: preference.id,
      init_point: preference.init_point,
      sandbox_init_point: preference.sandbox_init_point,
      platform_fee: platformFee,
      pro_amount: proAmount,
      currency,
    }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    })

  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500 })
  }
})
