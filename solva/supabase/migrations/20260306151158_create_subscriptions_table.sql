-- ============================================
-- SUSCRIPCIONES: planes free vs pro
-- ============================================
CREATE TYPE subscription_plan AS ENUM ('free', 'pro', 'company');
CREATE TYPE subscription_status AS ENUM ('active', 'cancelled', 'expired', 'trialing');

CREATE TABLE public.subscriptions (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  plan                  subscription_plan NOT NULL DEFAULT 'free',
  status                subscription_status NOT NULL DEFAULT 'active',
  stripe_subscription_id TEXT,
  current_period_start  TIMESTAMPTZ,
  current_period_end    TIMESTAMPTZ,
  cancel_at_period_end  BOOLEAN DEFAULT FALSE,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "subscriptions_own"
  ON public.subscriptions FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE TRIGGER subscriptions_updated_at
  BEFORE UPDATE ON public.subscriptions
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Auto-crea suscripción free al registrarse
CREATE OR REPLACE FUNCTION public.handle_new_subscription()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.subscriptions (user_id, plan, status)
  VALUES (NEW.id, 'free', 'active')
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_user_created_subscription
  AFTER INSERT ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_subscription();

-- Límites por plan
CREATE OR REPLACE FUNCTION public.get_bids_this_month(user_id UUID)
RETURNS INT AS $$
  SELECT COUNT(*)::INT
  FROM public.bids
  WHERE pro_id = user_id
    AND created_at >= date_trunc('month', NOW());
$$ LANGUAGE sql STABLE;

-- Vista analytics para pros
CREATE OR REPLACE VIEW public.pro_analytics AS
SELECT
  u.id AS user_id,
  COUNT(DISTINCT b.id) FILTER (WHERE b.status = 'pending')  AS bids_pending,
  COUNT(DISTINCT b.id) FILTER (WHERE b.status = 'accepted') AS bids_accepted,
  COUNT(DISTINCT b.id) FILTER (WHERE b.status = 'rejected') AS bids_rejected,
  COUNT(DISTINCT c.id) FILTER (WHERE c.status = 'completed') AS jobs_completed,
  COUNT(DISTINCT c.id) FILTER (WHERE c.status = 'active')    AS jobs_active,
  COALESCE(SUM(p.pro_amount) FILTER (WHERE p.status = 'released'), 0) AS total_earned,
  COALESCE(SUM(p.pro_amount) FILTER (WHERE p.status = 'held'), 0)     AS pending_payout,
  COALESCE(AVG(r.rating), 0) AS avg_rating,
  COUNT(DISTINCT r.id) AS total_reviews,
  -- Este mes
  COUNT(DISTINCT b.id) FILTER (
    WHERE b.created_at >= date_trunc('month', NOW())
  ) AS bids_this_month,
  COALESCE(SUM(p.pro_amount) FILTER (
    WHERE p.status = 'released'
    AND p.released_at >= date_trunc('month', NOW())
  ), 0) AS earned_this_month
FROM public.users u
LEFT JOIN public.bids b ON b.pro_id = u.id
LEFT JOIN public.contracts c ON c.pro_id = u.id
LEFT JOIN public.payments p ON p.pro_id = u.id
LEFT JOIN public.reviews r ON r.reviewed_id = u.id
WHERE u.role IN ('pro', 'company')
GROUP BY u.id;

GRANT SELECT ON public.pro_analytics TO authenticated;
