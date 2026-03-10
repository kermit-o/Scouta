import { supabase } from './supabase'

export type PlanFeature = 'bid' | 'photo' | 'ai_content' | 'analytics' | 'saved_reply' | 'team_member'

export interface PlanLimitResult {
  allowed: boolean
  limit?: number
  current?: number
  upgrade_required?: boolean
  message?: string
}

export async function checkPlanLimit(
  userId: string,
  feature: PlanFeature
): Promise<PlanLimitResult> {
  const { data, error } = await supabase.rpc('check_plan_limit', {
    p_user_id: userId,
    p_feature: feature,
  })
  if (error) return { allowed: true } // fail open — no bloquear por error técnico
  return data as PlanLimitResult
}

export async function getCommissionPct(userId: string): Promise<number> {
  const { data } = await supabase.rpc('get_commission_pct', { p_user_id: userId })
  return data ?? 10
}

// Mensajes contextuales por feature — usados en PaywallModal
export const PAYWALL_COPY: Record<PlanFeature, {
  title: string
  description: string
  cta: string
  icon: string
  color: string
}> = {
  bid: {
    title: '3 bids activos en Free',
    description: 'Con Pro envías bids ilimitados. Un solo contrato extra al mes cubre la suscripción.',
    cta: 'Activar Pro — 14 días gratis',
    icon: 'flash-outline',
    color: '#2563EB',
  },
  photo: {
    title: 'Más fotos = más contratos',
    description: 'Los pros con 10+ fotos reciben un 40% más de bids. Pro incluye hasta 20 fotos.',
    cta: 'Activar Pro — 14 días gratis',
    icon: 'images-outline',
    color: '#2563EB',
  },
  ai_content: {
    title: 'Descripción profesional con IA',
    description: 'La IA genera tu perfil optimizado para SEO en 30 segundos. Los clientes confían más en perfiles completos.',
    cta: 'Probar Pro gratis 14 días',
    icon: 'sparkles-outline',
    color: '#7C3AED',
  },
  analytics: {
    title: 'Conoce tu rendimiento',
    description: 'Tasa de conversión, posición en búsquedas, ingresos proyectados. Solo en Pro.',
    cta: 'Activar Pro — 14 días gratis',
    icon: 'bar-chart-outline',
    color: '#059669',
  },
  saved_reply: {
    title: 'Respuestas rápidas',
    description: 'Guarda hasta 5 plantillas de respuesta para responder bids en segundos.',
    cta: 'Activar Pro — 14 días gratis',
    icon: 'chatbubble-ellipses-outline',
    color: '#D97706',
  },
  team_member: {
    title: 'Gestión de equipo',
    description: 'Añade hasta 5 miembros de tu empresa. Ideal para negocios con empleados.',
    cta: 'Ver plan Business',
    icon: 'people-outline',
    color: '#7C3AED',
  },
}
