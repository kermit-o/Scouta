import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

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
    if (!authHeader?.startsWith('Bearer ')) {
      return new Response(JSON.stringify({ error: 'Missing Authorization' }), {
        status: 401, headers: { ...cors, 'Content-Type': 'application/json' },
      })
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    const { data: { user }, error: authErr } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    )
    if (authErr || !user) {
      return new Response(JSON.stringify({ error: 'Not authenticated' }), {
        status: 401, headers: { ...cors, 'Content-Type': 'application/json' },
      })
    }

    const userId = user.id
    console.log('Deleting account for user:', userId)

    // Cancel active subscriptions
    await supabase.from('subscriptions')
      .update({ status: 'cancelled', cancelled_at: new Date().toISOString() })
      .eq('user_id', userId)
      .in('status', ['active', 'trialing'])

    // Anonymize reviews (keep rating data but remove personal info)
    await supabase.from('reviews')
      .update({ comment: '[deleted]' })
      .eq('reviewer_id', userId)

    // Delete push tokens
    await supabase.from('push_tokens').delete().eq('user_id', userId)

    // Delete notifications
    await supabase.from('notifications').delete().eq('user_id', userId)

    // Delete messages
    const { data: contracts } = await supabase
      .from('contracts')
      .select('id')
      .or(`client_id.eq.${userId},pro_id.eq.${userId}`)
    if (contracts?.length) {
      const contractIds = contracts.map(c => c.id)
      await supabase.from('messages').delete().in('contract_id', contractIds)
    }

    // Anonymize user profile (keep row for FK integrity but remove personal data)
    await supabase.from('users').update({
      full_name: 'Deleted User',
      email: `deleted_${userId}@solva.app`,
      avatar_url: null,
      phone: null,
      bio: null,
      skills: null,
      portfolio_urls: null,
      stripe_account_id: null,
    }).eq('id', userId)

    // Delete auth user (this invalidates all sessions)
    const { error: deleteErr } = await supabase.auth.admin.deleteUser(userId)
    if (deleteErr) {
      console.error('Failed to delete auth user:', deleteErr.message)
      return new Response(JSON.stringify({ error: 'Failed to delete account' }), {
        status: 500, headers: { ...cors, 'Content-Type': 'application/json' },
      })
    }

    console.log('Account deleted successfully:', userId)
    return new Response(JSON.stringify({ success: true }), {
      headers: { ...cors, 'Content-Type': 'application/json' },
    })
  } catch (err: any) {
    console.error('delete-account error:', err.message)
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500, headers: { ...cors, 'Content-Type': 'application/json' },
    })
  }
})
