import { useEffect, useState, useCallback } from 'react'
import { supabase, Subscription } from '../lib/supabase'
import { useAuth } from '../lib/AuthContext'
import { checkPlanLimit, PlanFeature, PlanLimitResult } from '../lib/planLimits'

export function useSubscription() {
  const { session } = useAuth()
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    if (!session?.user.id) {
      setSubscription(null)
      setLoading(false)
      return
    }
    setLoading(true)
    supabase
      .from('subscriptions')
      .select('*')
      .eq('user_id', session.user.id)
      .maybeSingle()
      .then(({ data, error }) => {
        if (cancelled) return
        if (error) {
          console.warn('useSubscription fetch error:', error.message)
          setSubscription(null)
        } else {
          setSubscription((data as Subscription | null) ?? null)
        }
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [session?.user.id])

  const isPro =
    subscription != null &&
    subscription.plan !== 'free' &&
    subscription.status !== 'expired' &&
    subscription.status !== 'cancelled'
  const isTrialing = subscription?.status === 'trialing'
  const isBusiness = subscription?.plan === 'company'

  // Días restantes de trial
  const trialDaysLeft = (() => {
    if (!isTrialing || !subscription?.trial_ends_at) return null
    const ms = new Date(subscription.trial_ends_at).getTime() - Date.now()
    return Math.max(0, Math.ceil(ms / 86400000))
  })()

  // Función principal — verificar cualquier límite
  const canUse = useCallback(async (feature: PlanFeature): Promise<PlanLimitResult> => {
    if (!session?.user.id) return { allowed: false, message: 'No autenticado' }
    return checkPlanLimit(session.user.id, feature)
  }, [session?.user.id])

  // Activar trial
  async function startTrial(plan: 'pro' | 'company'): Promise<{ success: boolean; error?: string }> {
    if (!session?.user.id) return { success: false, error: 'No autenticado' }

    // Verificar que no haya tenido trial antes
    if (subscription?.trial_converted) {
      return { success: false, error: 'Ya usaste tu trial anteriormente.' }
    }

    const trialEnds = new Date(Date.now() + 14 * 86400000).toISOString()
    const { error } = await supabase
      .from('subscriptions')
      .update({
        plan,
        status: 'trialing',
        trial_started_at: new Date().toISOString(),
        trial_ends_at: trialEnds,
      })
      .eq('user_id', session.user.id)

    if (error) return { success: false, error: error.message }
    setSubscription(prev =>
      prev
        ? { ...prev, plan, status: 'trialing', trial_ends_at: trialEnds }
        : null
    )
    return { success: true }
  }

  // Pausar suscripción (retención antes de cancelar)
  async function pauseSubscription(reason: string): Promise<boolean> {
    if (!session?.user.id) return false
    const { error } = await supabase
      .from('subscriptions')
      .update({ paused_at: new Date().toISOString(), pause_reason: reason })
      .eq('user_id', session.user.id)
    return !error
  }

  return {
    subscription,
    loading,
    isPro,
    isTrialing,
    isBusiness,
    trialDaysLeft,
    canUse,
    startTrial,
    pauseSubscription,
  }
}
