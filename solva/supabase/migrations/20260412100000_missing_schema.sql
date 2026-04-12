-- Migration: add missing columns, tables, and storage bucket
-- These elements are used by the frontend but were never captured in migrations
-- (likely added manually via Supabase dashboard).
-- Uses IF NOT EXISTS / ADD COLUMN IF NOT EXISTS so it's safe to run on
-- a DB that already has some of these.

-- ========================================
-- 1. Missing columns on public.users
-- ========================================
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS skills TEXT[];
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS availability TEXT DEFAULT 'available';
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS years_experience INTEGER;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS hourly_rate NUMERIC;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS portfolio_urls TEXT[];
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS certifications JSONB;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS languages_spoken TEXT[];
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS service_radius_km NUMERIC;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS city TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS stripe_account_id TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS stripe_onboarding_completed BOOLEAN DEFAULT false;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS referral_code TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS referred_by UUID REFERENCES public.users(id);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION;

-- Index for referral lookups
CREATE INDEX IF NOT EXISTS idx_users_referral_code ON public.users(referral_code) WHERE referral_code IS NOT NULL;

-- ========================================
-- 2. Table: referrals
-- Used by register.tsx and referrals.tsx
-- ========================================
CREATE TABLE IF NOT EXISTS public.referrals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  referrer_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  referred_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'rewarded')),
  reward_amount NUMERIC DEFAULT 0,
  reward_currency TEXT DEFAULT 'EUR',
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(referrer_id, referred_id)
);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON public.referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referred ON public.referrals(referred_id);

ALTER TABLE public.referrals ENABLE ROW LEVEL SECURITY;

-- Users can see referrals where they are the referrer
CREATE POLICY "referrals_select_own" ON public.referrals
  FOR SELECT TO authenticated
  USING (referrer_id = auth.uid() OR referred_id = auth.uid());

-- Inserts happen from the auth trigger / backend, not directly from client
-- But allow insert for the referrer to track signups
CREATE POLICY "referrals_insert" ON public.referrals
  FOR INSERT TO authenticated
  WITH CHECK (referrer_id = auth.uid());

-- ========================================
-- 3. Table: pro_services
-- Used by pro-services.tsx (full CRUD)
-- ========================================
CREATE TABLE IF NOT EXISTS public.pro_services (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pro_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  price_from NUMERIC,
  price_to NUMERIC,
  price_type TEXT NOT NULL DEFAULT 'quote' CHECK (price_type IN ('fixed', 'from', 'hourly', 'quote')),
  category TEXT,
  duration_hours NUMERIC,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pro_services_pro_id ON public.pro_services(pro_id);

ALTER TABLE public.pro_services ENABLE ROW LEVEL SECURITY;

-- Anyone authenticated can see active services
CREATE POLICY "pro_services_select" ON public.pro_services
  FOR SELECT TO authenticated
  USING (is_active = true OR pro_id = auth.uid());

-- Only the pro can manage their own services
CREATE POLICY "pro_services_insert" ON public.pro_services
  FOR INSERT TO authenticated
  WITH CHECK (pro_id = auth.uid());

CREATE POLICY "pro_services_update" ON public.pro_services
  FOR UPDATE TO authenticated
  USING (pro_id = auth.uid())
  WITH CHECK (pro_id = auth.uid());

CREATE POLICY "pro_services_delete" ON public.pro_services
  FOR DELETE TO authenticated
  USING (pro_id = auth.uid());

-- ========================================
-- 4. Storage bucket: avatars
-- Used by profile.tsx for avatar upload
-- ========================================
INSERT INTO storage.buckets (id, name, public)
VALUES ('avatars', 'avatars', true)
ON CONFLICT (id) DO NOTHING;

-- Anyone can view avatars (public bucket)
CREATE POLICY "avatars_select" ON storage.objects
  FOR SELECT TO public
  USING (bucket_id = 'avatars');

-- Users can upload/update their own avatar (path starts with their user id)
CREATE POLICY "avatars_insert" ON storage.objects
  FOR INSERT TO authenticated
  WITH CHECK (bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text);

CREATE POLICY "avatars_update" ON storage.objects
  FOR UPDATE TO authenticated
  USING (bucket_id = 'avatars' AND (storage.foldername(name))[1] = auth.uid()::text);
