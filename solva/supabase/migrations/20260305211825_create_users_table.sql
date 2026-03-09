CREATE TYPE user_role AS ENUM ('client', 'pro', 'company');

CREATE TYPE supported_country AS ENUM (
  'ES', 'FR', 'MX', 'CO', 'AR', 'BR', 'CL'
);

CREATE TYPE supported_currency AS ENUM (
  'EUR', 'MXN', 'COP', 'ARS', 'BRL', 'CLP'
);

CREATE TYPE supported_language AS ENUM (
  'es', 'es-ES', 'pt-BR'
);

CREATE TABLE public.users (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT NOT NULL UNIQUE,
  full_name   TEXT,
  avatar_url  TEXT,
  phone       TEXT,
  role        user_role NOT NULL DEFAULT 'client',
  country     supported_country NOT NULL,
  currency    supported_currency NOT NULL,
  language    supported_language NOT NULL DEFAULT 'es',
  is_verified BOOLEAN DEFAULT FALSE,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_select_own"
  ON public.users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "user_update_own"
  ON public.users FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "user_insert_own"
  ON public.users FOR INSERT
  WITH CHECK (auth.uid() = id);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, role, country, currency, language)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE((NEW.raw_user_meta_data->>'role')::user_role, 'client'),
    COALESCE((NEW.raw_user_meta_data->>'country')::supported_country, 'ES'),
    COALESCE((NEW.raw_user_meta_data->>'currency')::supported_currency, 'EUR'),
    COALESCE((NEW.raw_user_meta_data->>'language')::supported_language, 'es')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
