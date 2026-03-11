-- Trigger más defensivo — captura excepciones y nunca bloquea el registro
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  v_role      user_role        := 'client';
  v_country   supported_country := 'ES';
  v_currency  supported_currency := 'EUR';
  v_language  supported_language := 'es';
BEGIN
  -- Cast seguro de role
  BEGIN
    v_role := (NEW.raw_user_meta_data->>'role')::user_role;
  EXCEPTION WHEN OTHERS THEN
    v_role := 'client';
  END;

  -- Cast seguro de country
  BEGIN
    v_country := (NEW.raw_user_meta_data->>'country')::supported_country;
  EXCEPTION WHEN OTHERS THEN
    v_country := 'ES';
  END;

  -- Cast seguro de currency
  BEGIN
    v_currency := (NEW.raw_user_meta_data->>'currency')::supported_currency;
  EXCEPTION WHEN OTHERS THEN
    v_currency := 'EUR';
  END;

  -- Cast seguro de language
  BEGIN
    v_language := (NEW.raw_user_meta_data->>'language')::supported_language;
  EXCEPTION WHEN OTHERS THEN
    v_language := 'es';
  END;

  INSERT INTO public.users (
    id, email, full_name, avatar_url,
    role, country, currency, language,
    profile_quality_score, ai_description_generated, ai_keywords,
    saved_replies, portfolio_photos
  )
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(
      NEW.raw_user_meta_data->>'full_name',
      NEW.raw_user_meta_data->>'name',
      split_part(NEW.email, '@', 1)
    ),
    COALESCE(
      NEW.raw_user_meta_data->>'avatar_url',
      NEW.raw_user_meta_data->>'picture'
    ),
    v_role, v_country, v_currency, v_language,
    0, false, '{}', '[]', '{}'
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name  = COALESCE(EXCLUDED.full_name, public.users.full_name),
    avatar_url = COALESCE(EXCLUDED.avatar_url, public.users.avatar_url),
    updated_at = NOW();

  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  -- Nunca bloquear el registro por error en el trigger
  RAISE WARNING 'handle_new_user error: %', SQLERRM;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Handle new subscription también defensivo
CREATE OR REPLACE FUNCTION public.handle_new_subscription()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.subscriptions (user_id, plan, status)
  VALUES (NEW.id, 'free', 'active')
  ON CONFLICT (user_id) DO NOTHING;
  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  RAISE WARNING 'handle_new_subscription error: %', SQLERRM;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
