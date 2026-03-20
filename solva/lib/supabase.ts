import AsyncStorage from '@react-native-async-storage/async-storage'
import { createClient } from '@supabase/supabase-js'
import { Platform } from 'react-native'

const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: Platform.OS === 'web' ? undefined : AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: Platform.OS === 'web',
  },
})

// Tipos del perfil de usuario
export type UserRole = 'client' | 'pro' | 'company' | 'admin'
export type SupportedCountry = 'ES' | 'FR' | 'BE' | 'NL' | 'DE' | 'PT' | 'IT' | 'GB' | 'MX' | 'CO' | 'AR' | 'BR' | 'CL'
export type SupportedCurrency = 'EUR' | 'GBP' | 'MXN' | 'COP' | 'ARS' | 'BRL' | 'CLP'
export type SupportedLanguage = 'es' | 'es-ES' | 'pt-BR'

export interface UserProfile {
  id: string
  email: string
  full_name: string | null
  avatar_url: string | null
  phone: string | null
  role: UserRole
  country: SupportedCountry
  currency: SupportedCurrency
  language: SupportedLanguage
  is_verified: boolean
  onboarding_completed: boolean
  onboarding_step: number
  bio: string | null
  skills: string[] | null
  city: string | null
  ai_keywords: string[] | null
  created_at: string
  updated_at: string
}

export type JobStatus = 'open' | 'in_progress' | 'completed' | 'cancelled'
export type JobCategory = 'cleaning' | 'plumbing' | 'electrical' | 'painting' | 'moving' | 'gardening' | 'carpentry' | 'tech' | 'design' | 'other'

export interface Job {
  id: string
  client_id: string
  title: string
  description: string
  category: JobCategory
  status: JobStatus
  budget_min: number | null
  budget_max: number | null
  currency: SupportedCurrency
  country: SupportedCountry
  city: string | null
  address: string | null
  is_remote: boolean
  photos: string[]
  created_at: string
  updated_at: string
}

export type BidStatus = 'pending' | 'accepted' | 'rejected' | 'withdrawn'

export interface Bid {
  id: string
  job_id: string
  pro_id: string
  amount: number
  currency: SupportedCurrency
  message: string
  delivery_days: number | null
  status: BidStatus
  created_at: string
  updated_at: string
  // join
  users?: { full_name: string; avatar_url: string | null; is_verified: boolean }
}

export type PaymentStatus = 'pending' | 'held' | 'released' | 'refunded' | 'disputed'
export type PaymentProvider = 'stripe' | 'mercadopago'

export interface Payment {
  id: string
  contract_id: string
  client_id: string
  pro_id: string
  amount: number
  platform_fee: number
  pro_amount: number
  currency: SupportedCurrency
  country: SupportedCountry
  provider: PaymentProvider
  provider_payment_id: string | null
  status: PaymentStatus
  held_at: string | null
  released_at: string | null
  created_at: string
  updated_at: string
}

export interface Review {
  id: string
  contract_id: string
  job_id: string
  reviewer_id: string
  reviewed_id: string
  rating: number
  comment: string
  photos_before: string[]
  photos_after: string[]
  created_at: string
  users?: { full_name: string; avatar_url: string | null }
}

export interface Message {
  id: string
  contract_id: string
  sender_id: string
  content: string
  read_at: string | null
  created_at: string
  users?: { full_name: string; avatar_url: string | null }
}

export type KycStatus = 'pending' | 'submitted' | 'approved' | 'rejected'
export type KycDocType = 'dni' | 'passport' | 'residence_permit' | 'drivers_license'

export interface KycVerification {
  id: string
  user_id: string
  status: KycStatus
  doc_type: KycDocType | null
  doc_front_url: string | null
  doc_back_url: string | null
  selfie_url: string | null
  rejection_reason: string | null
  submitted_at: string | null
  created_at: string
}

export type DisputeStatus = 'open' | 'under_review' | 'resolved_client' | 'resolved_pro' | 'resolved_split' | 'closed'
export type DisputeReason = 'work_not_done' | 'work_poor_quality' | 'payment_not_released' | 'no_show' | 'scope_change' | 'other'

export interface Dispute {
  id: string
  contract_id: string
  payment_id: string | null
  opened_by: string
  against: string
  reason: DisputeReason
  description: string
  evidence_urls: string[]
  status: DisputeStatus
  resolution_note: string | null
  refund_pct: number
  resolved_at: string | null
  created_at: string
}

export type SubscriptionPlan = 'free' | 'pro' | 'company'
export type SubscriptionStatus = 'active' | 'cancelled' | 'expired' | 'trialing'

export interface Subscription {
  id: string
  user_id: string
  plan: SubscriptionPlan
  status: SubscriptionStatus
  stripe_subscription_id: string | null
  current_period_end: string | null
  cancel_at_period_end: boolean
  created_at: string
}

export interface ProAnalytics {
  user_id: string
  bids_pending: number
  bids_accepted: number
  bids_rejected: number
  jobs_completed: number
  jobs_active: number
  total_earned: number
  pending_payout: number
  avg_rating: number
  total_reviews: number
  bids_this_month: number
  earned_this_month: number
}

export type GuaranteeStatus = 'active' | 'claimed' | 'approved' | 'rejected' | 'expired'

export interface Guarantee {
  id: string
  contract_id: string
  client_id: string
  status: GuaranteeStatus
  max_coverage: number
  currency: SupportedCurrency
  country: SupportedCountry
  claim_reason: string | null
  claim_evidence: string[]
  approved_amount: number | null
  resolution_note: string | null
  claimed_at: string | null
  resolved_at: string | null
  expires_at: string
  created_at: string
}
