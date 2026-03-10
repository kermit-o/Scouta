CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name, avatar_url, role, country, currency, language)
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
    COALESCE((NEW.raw_user_meta_data->>'role')::user_role, 'client'),
    COALESCE((NEW.raw_user_meta_data->>'country')::supported_country, 'ES'),
    COALESCE((NEW.raw_user_meta_data->>'currency')::supported_currency, 'EUR'),
    COALESCE((NEW.raw_user_meta_data->>'language')::supported_language, 'es')
  )
  ON CONFLICT (id) DO UPDATE SET
    full_name = COALESCE(
      EXCLUDED.full_name,
      public.users.full_name,
      split_part(NEW.email, '@', 1)
    ),
    avatar_url = COALESCE(EXCLUDED.avatar_url, public.users.avatar_url),
    updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
