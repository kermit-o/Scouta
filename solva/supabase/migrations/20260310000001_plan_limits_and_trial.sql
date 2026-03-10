-- ============================================
-- PLAN LIMITS: límites por plan
-- ============================================
CREATE TABLE public.plan_limits (
  plan                subscription_plan PRIMARY KEY,
  max_active_bids     INT NOT NULL DEFAULT 3,
  max_portfolio_photos INT NOT NULL DEFAULT 3,
  commission_pct      NUMERIC(4,2) NOT NULL DEFAULT 10.00,
  ai_content_uses_month INT NOT NULL DEFAULT 0,  -- 0 = bloqueado
  max_saved_replies   INT NOT NULL DEFAULT 0,
  max_team_members    INT NOT NULL DEFAULT 1,
  can_see_analytics   BOOLEAN NOT NULL DEFAULT FALSE,
  can_boost_profile   BOOLEAN NOT NULL DEFAULT FALSE,
  has_priority_support BOOLEAN NOT NULL DEFAULT FALSE,
  has_auto_invoice    BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO public.plan_limits VALUES
-- plan, bids, fotos, comision, ai_uses, replies, team, analytics, boost, support, invoice
('free',    3,  3,  10.00,  0,  0, 1, FALSE, FALSE, FALSE, FALSE),
('pro',    -1, 20,   5.00, 20,  5, 1,  TRUE,  TRUE,  TRUE, FALSE),
('company',-1, 50,   3.00, -1, -1, 5,  TRUE,  TRUE,  TRUE,  TRUE);
-- -1 = ilimitado

-- ============================================
-- TRIAL: campos en subscriptions
-- ============================================
ALTER TABLE public.subscriptions
  ADD COLUMN IF NOT EXISTS trial_started_at  TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS trial_ends_at     TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS trial_converted   BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS paused_at         TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS pause_reason      TEXT;

-- ============================================
-- PROFILE QUALITY SCORE
-- ============================================
ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS profile_quality_score INT DEFAULT 0,
  ADD COLUMN IF NOT EXISTS ai_description_generated BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS ai_keywords             TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS saved_replies           JSONB DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS portfolio_photos        TEXT[] DEFAULT '{}';

-- ============================================
-- FUNCIÓN: calcular quality score
-- ============================================
CREATE OR REPLACE FUNCTION public.calculate_profile_quality(uid UUID)
RETURNS INT AS $$
DECLARE
  score INT := 0;
  u public.users%ROWTYPE;
  review_count INT;
  avg_response_hours NUMERIC;
BEGIN
  SELECT * INTO u FROM public.users WHERE id = uid;

  IF u.avatar_url IS NOT NULL AND u.avatar_url != '' THEN score := score + 10; END IF;
  IF u.ai_description_generated THEN score := score + 20; END IF;
  IF u.is_verified THEN score := score + 20; END IF;

  SELECT COUNT(*) INTO review_count FROM public.reviews WHERE reviewed_id = uid;
  IF review_count >= 1  THEN score := score + 5;  END IF;
  IF review_count >= 5  THEN score := score + 5;  END IF;
  IF review_count >= 10 THEN score := score + 5;  END IF;

  -- Plan bonus
  IF EXISTS (
    SELECT 1 FROM public.subscriptions
    WHERE user_id = uid AND plan != 'free' AND status IN ('active','trialing')
  ) THEN score := score + 20; END IF;

  -- Portfolio photos
  IF array_length(u.portfolio_photos, 1) >= 3  THEN score := score + 5;  END IF;
  IF array_length(u.portfolio_photos, 1) >= 10 THEN score := score + 10; END IF;

  RETURN LEAST(score, 100);
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================
-- FUNCIÓN: check_plan_limit (RPC central)
-- ============================================
CREATE OR REPLACE FUNCTION public.check_plan_limit(
  p_user_id UUID,
  p_feature TEXT  -- 'bid', 'photo', 'ai_content', 'saved_reply', 'team_member'
)
RETURNS JSONB AS $$
DECLARE
  sub   public.subscriptions%ROWTYPE;
  lim   public.plan_limits%ROWTYPE;
  cur   INT := 0;
  max_v INT;
  res   JSONB;
BEGIN
  -- Obtiene suscripción activa
  SELECT * INTO sub FROM public.subscriptions
  WHERE user_id = p_user_id
  LIMIT 1;

  IF NOT FOUND THEN
    RETURN jsonb_build_object('allowed', false, 'reason', 'Sin suscripción');
  END IF;

  -- Si expiró trial, trata como free
  IF sub.status = 'trialing' AND sub.trial_ends_at < NOW() THEN
    UPDATE public.subscriptions SET status = 'expired', plan = 'free' WHERE user_id = p_user_id;
    sub.plan := 'free';
  END IF;

  SELECT * INTO lim FROM public.plan_limits WHERE plan = sub.plan;

  -- Evalúa según feature
  IF p_feature = 'bid' THEN
    max_v := lim.max_active_bids;
    IF max_v = -1 THEN RETURN jsonb_build_object('allowed', true, 'limit', -1, 'current', 0); END IF;
    SELECT COUNT(*)::INT INTO cur FROM public.bids
      WHERE pro_id = p_user_id AND status = 'pending';
    res := jsonb_build_object(
      'allowed', cur < max_v,
      'limit', max_v, 'current', cur,
      'upgrade_required', cur >= max_v,
      'message', CASE WHEN cur >= max_v
        THEN 'Has alcanzado el límite de ' || max_v || ' bids activos en el plan gratuito. Actualiza a Pro para enviar bids ilimitados.'
        ELSE NULL END
    );

  ELSIF p_feature = 'photo' THEN
    max_v := lim.max_portfolio_photos;
    IF max_v = -1 THEN RETURN jsonb_build_object('allowed', true, 'limit', -1, 'current', 0); END IF;
    SELECT COALESCE(array_length(portfolio_photos, 1), 0) INTO cur
      FROM public.users WHERE id = p_user_id;
    res := jsonb_build_object(
      'allowed', cur < max_v,
      'limit', max_v, 'current', cur,
      'upgrade_required', cur >= max_v,
      'message', CASE WHEN cur >= max_v
        THEN 'Límite de ' || max_v || ' fotos en tu plan. Actualiza a Pro para subir hasta 20 fotos.'
        ELSE NULL END
    );

  ELSIF p_feature = 'ai_content' THEN
    max_v := lim.ai_content_uses_month;
    IF max_v = 0 THEN
      RETURN jsonb_build_object(
        'allowed', false, 'limit', 0, 'current', 0,
        'upgrade_required', true,
        'message', 'La generación de contenido con IA es exclusiva del plan Pro. Pruébalo 14 días gratis.'
      );
    END IF;
    IF max_v = -1 THEN RETURN jsonb_build_object('allowed', true, 'limit', -1, 'current', 0); END IF;
    -- Contar usos este mes (simplificado — se puede añadir tabla de logs después)
    res := jsonb_build_object('allowed', true, 'limit', max_v, 'current', 0);

  ELSIF p_feature = 'analytics' THEN
    res := jsonb_build_object(
      'allowed', lim.can_see_analytics,
      'upgrade_required', NOT lim.can_see_analytics,
      'message', CASE WHEN NOT lim.can_see_analytics
        THEN 'Las estadísticas avanzadas son exclusivas de Pro. Conoce tu tasa de conversión y posición en búsquedas.'
        ELSE NULL END
    );

  ELSE
    res := jsonb_build_object('allowed', true);
  END IF;

  RETURN res;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.check_plan_limit TO authenticated;
GRANT SELECT ON public.plan_limits TO authenticated;

-- ============================================
-- FUNCIÓN: get_commission_pct (para pagos)
-- ============================================
CREATE OR REPLACE FUNCTION public.get_commission_pct(p_user_id UUID)
RETURNS NUMERIC AS $$
  SELECT lim.commission_pct
  FROM public.subscriptions sub
  JOIN public.plan_limits lim ON lim.plan = sub.plan
  WHERE sub.user_id = p_user_id
    AND sub.status IN ('active', 'trialing')
  LIMIT 1;
$$ LANGUAGE sql STABLE SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.get_commission_pct TO authenticated;
