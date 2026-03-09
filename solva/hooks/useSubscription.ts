import { useEffect, useState } from 'react'
import { supabase, Subscription, SubscriptionPlan } from '../lib/supabase'
import { useAuth } from '../lib/AuthContext'

const FREE_BID_LIMIT = 3

export function useSubscription() {
  const { session } = useAuth()
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!session?.user.id) return
    supabase
      .from('subscriptions')
      .select('*')
      .eq('user_id', session.user.id)
      .single()
      .then(({ data }) => {
        setSubscription(data as Subscription)
        setLoading(false)
      })
  }, [session?.user.id])

  const isPro = subscription?.plan !== 'free' && subscription?.status !== 'expired'
  const isTrialing = subscription?.status === 'trialing'

  async function canSendBid(): Promise<{ allowed: boolean; reason?: string }> {
    if (isPro) return { allowed: true }
    const { data } = await supabase.rpc('get_bids_this_month', { user_id: session!.user.id })
    const count = data ?? 0
    if (count >= FREE_BID_LIMIT) {
      return { allowed: false, reason: `Plan gratuito: ${count}/${FREE_BID_LIMIT} bids este mes. Actualiza a Pro para enviar ilimitados.` }
    }
    return { allowed: true }
  }

  return { subscription, loading, isPro, isTrialing, canSendBid }
}
