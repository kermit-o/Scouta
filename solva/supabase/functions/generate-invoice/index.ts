import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, content-type, x-client-info, apikey',
}

function generateInvoiceNumber(country: string, date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const rand = Math.random().toString(36).substring(2, 8).toUpperCase()
  return `SLV-${country}-${year}${month}-${rand}`
}

function formatDate(date: string, country: string): string {
  const d = new Date(date)
  const locale = country === 'GB' ? 'en-GB' : country === 'DE' ? 'de-DE' :
    country === 'FR' || country === 'BE' ? 'fr-FR' : country === 'NL' ? 'nl-NL' :
    country === 'IT' ? 'it-IT' : country === 'PT' ? 'pt-PT' : 'es-ES'
  return d.toLocaleDateString(locale, { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatCurrency(amount: number, currency: string): string {
  const symbol: Record<string, string> = {
    EUR: '€', GBP: '£', MXN: 'MX$', COP: 'COP$', ARS: 'AR$', BRL: 'R$', CLP: 'CLP$',
  }
  return `${(symbol[currency] ?? currency)} ${amount.toFixed(2)}`
}

function generateInvoiceHTML(data: {
  invoiceNumber: string
  date: string
  clientName: string
  clientEmail: string
  proName: string
  jobTitle: string
  amount: number
  platformFee: number
  proAmount: number
  currency: string
  country: string
  paymentId: string
}): string {
  const { invoiceNumber, date, clientName, clientEmail, proName, jobTitle,
    amount, platformFee, proAmount, currency, country, paymentId } = data

  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Factura ${invoiceNumber}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a1a2e; padding: 40px; max-width: 800px; margin: 0 auto; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; }
    .logo { font-size: 28px; font-weight: 800; color: #2563EB; }
    .logo-sub { font-size: 12px; color: #888; margin-top: 4px; }
    .invoice-meta { text-align: right; }
    .invoice-meta h2 { font-size: 22px; color: #1a1a2e; margin-bottom: 8px; }
    .invoice-meta p { font-size: 13px; color: #666; line-height: 1.6; }
    .parties { display: flex; gap: 40px; margin-bottom: 32px; }
    .party { flex: 1; }
    .party-label { font-size: 11px; font-weight: 700; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .party-name { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
    .party-detail { font-size: 13px; color: #666; }
    .table { width: 100%; border-collapse: collapse; margin-bottom: 24px; }
    .table th { background: #F6F7FB; padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 700; color: #666; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #E5E7EB; }
    .table td { padding: 14px 16px; font-size: 14px; border-bottom: 1px solid #F3F4F6; }
    .table .amount { text-align: right; font-weight: 600; }
    .totals { margin-left: auto; width: 300px; }
    .total-row { display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; }
    .total-row.final { border-top: 2px solid #1a1a2e; padding-top: 12px; margin-top: 8px; font-size: 18px; font-weight: 800; }
    .footer { margin-top: 48px; padding-top: 24px; border-top: 1px solid #E5E7EB; text-align: center; }
    .footer p { font-size: 11px; color: #aaa; line-height: 1.6; }
    .badge { display: inline-block; background: #D1FAE5; color: #059669; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }
    @media print { body { padding: 20px; } }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="logo">Solva</div>
      <div class="logo-sub">Marketplace de servicios del hogar</div>
      <div class="logo-sub">www.getsolva.co</div>
    </div>
    <div class="invoice-meta">
      <h2>Factura</h2>
      <p><strong>${invoiceNumber}</strong></p>
      <p>Fecha: ${formatDate(date, country)}</p>
      <p><span class="badge">Pagado</span></p>
    </div>
  </div>

  <div class="parties">
    <div class="party">
      <div class="party-label">Cliente</div>
      <div class="party-name">${clientName}</div>
      <div class="party-detail">${clientEmail}</div>
    </div>
    <div class="party">
      <div class="party-label">Profesional</div>
      <div class="party-name">${proName}</div>
    </div>
  </div>

  <table class="table">
    <thead>
      <tr>
        <th>Concepto</th>
        <th>Referencia</th>
        <th class="amount">Importe</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>${jobTitle}</strong></td>
        <td style="font-size:12px;color:#888">${paymentId.substring(0, 8)}...</td>
        <td class="amount">${formatCurrency(amount, currency)}</td>
      </tr>
    </tbody>
  </table>

  <div class="totals">
    <div class="total-row">
      <span>Subtotal</span>
      <span>${formatCurrency(amount, currency)}</span>
    </div>
    <div class="total-row">
      <span>Comisión Solva (10%)</span>
      <span>-${formatCurrency(platformFee, currency)}</span>
    </div>
    <div class="total-row">
      <span>Profesional recibe</span>
      <span>${formatCurrency(proAmount, currency)}</span>
    </div>
    <div class="total-row final">
      <span>Total pagado</span>
      <span>${formatCurrency(amount, currency)}</span>
    </div>
  </div>

  <div class="footer">
    <p>Solva SRL — Plataforma intermediaria de servicios</p>
    <p>Este documento es un comprobante de pago generado automáticamente.</p>
    <p>Para cualquier consulta: soporte@getsolva.co</p>
  </div>
</body>
</html>`
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: CORS })

  try {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader?.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Not authenticated' }), {
        status: 401, headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    const { data: { user }, error: authError } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    )
    if (authError || !user) {
      return new Response(JSON.stringify({ error: 'Not authenticated' }), {
        status: 401, headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }

    const { payment_id } = await req.json()
    if (!payment_id) {
      return new Response(JSON.stringify({ error: 'payment_id required' }), {
        status: 400, headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }

    // Check if invoice already exists
    const { data: existing } = await supabase
      .from('invoices')
      .select('*')
      .eq('payment_id', payment_id)
      .eq('user_id', user.id)
      .maybeSingle()

    if (existing?.pdf_url) {
      return new Response(JSON.stringify({ invoice: existing }), {
        headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }

    // Fetch payment with contract and user details
    const { data: payment, error: payError } = await supabase
      .from('payments')
      .select('*, contracts(job_id, jobs(title))')
      .eq('id', payment_id)
      .single()

    if (payError || !payment) {
      return new Response(JSON.stringify({ error: 'Payment not found' }), {
        status: 404, headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }

    // Verify the user is part of this payment
    if (payment.client_id !== user.id && payment.pro_id !== user.id) {
      return new Response(JSON.stringify({ error: 'Not authorized' }), {
        status: 403, headers: { ...CORS, 'Content-Type': 'application/json' },
      })
    }

    const { data: client } = await supabase
      .from('users').select('full_name, email').eq('id', payment.client_id).single()
    const { data: pro } = await supabase
      .from('users').select('full_name').eq('id', payment.pro_id).single()

    const now = new Date()
    const invoiceNumber = generateInvoiceNumber(payment.country ?? 'ES', now)

    const html = generateInvoiceHTML({
      invoiceNumber,
      date: payment.released_at ?? payment.held_at ?? now.toISOString(),
      clientName: client?.full_name ?? 'Cliente',
      clientEmail: client?.email ?? '',
      proName: pro?.full_name ?? 'Profesional',
      jobTitle: (payment.contracts as any)?.jobs?.title ?? 'Servicio',
      amount: payment.amount,
      platformFee: payment.platform_fee,
      proAmount: payment.pro_amount,
      currency: payment.currency,
      country: payment.country ?? 'ES',
      paymentId: payment.id,
    })

    // Store HTML as file in storage
    const fileName = `${user.id}/${invoiceNumber}.html`
    const { error: uploadError } = await supabase.storage
      .from('invoices')
      .upload(fileName, new Blob([html], { type: 'text/html' }), {
        upsert: true, contentType: 'text/html',
      })

    let pdfUrl: string | null = null
    if (!uploadError) {
      const { data: urlData } = await supabase.storage
        .from('invoices')
        .createSignedUrl(fileName, 60 * 60 * 24 * 7) // 7 days
      pdfUrl = urlData?.signedUrl ?? null
    }

    // Save invoice record
    const { data: invoice, error: insertError } = await supabase.from('invoices').upsert({
      payment_id,
      user_id: user.id,
      invoice_number: invoiceNumber,
      amount: payment.amount,
      platform_fee: payment.platform_fee,
      pro_amount: payment.pro_amount,
      currency: payment.currency,
      country: payment.country ?? 'ES',
      job_title: (payment.contracts as any)?.jobs?.title ?? 'Servicio',
      client_name: client?.full_name,
      pro_name: pro?.full_name,
      pdf_url: pdfUrl,
    }, { onConflict: 'payment_id' }).select().single()

    if (insertError) {
      console.error('Invoice insert error:', insertError.message)
    }

    // Return HTML directly if requested, or invoice metadata
    const wantHtml = req.headers.get('Accept')?.includes('text/html')
    if (wantHtml) {
      return new Response(html, {
        headers: { ...CORS, 'Content-Type': 'text/html; charset=utf-8' },
      })
    }

    return new Response(JSON.stringify({ invoice: invoice ?? { invoice_number: invoiceNumber, pdf_url: pdfUrl } }), {
      headers: { ...CORS, 'Content-Type': 'application/json' },
    })
  } catch (err: any) {
    console.error('generate-invoice error:', err?.message ?? err)
    return new Response(JSON.stringify({ error: 'Internal error' }), {
      status: 500, headers: { ...CORS, 'Content-Type': 'application/json' },
    })
  }
})
