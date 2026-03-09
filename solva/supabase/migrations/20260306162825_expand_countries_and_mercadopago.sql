-- ============================================
-- EXPANSIÓN: nuevos países Europa + LatAm
-- ============================================

-- Agrega nuevos valores a ENUMs existentes
ALTER TYPE supported_country ADD VALUE IF NOT EXISTS 'BE';
ALTER TYPE supported_country ADD VALUE IF NOT EXISTS 'NL';
ALTER TYPE supported_country ADD VALUE IF NOT EXISTS 'DE';
ALTER TYPE supported_country ADD VALUE IF NOT EXISTS 'PT';
ALTER TYPE supported_country ADD VALUE IF NOT EXISTS 'IT';
ALTER TYPE supported_country ADD VALUE IF NOT EXISTS 'GB';

ALTER TYPE supported_currency ADD VALUE IF NOT EXISTS 'GBP';

-- MercadoPago: tabla de cuentas conectadas de pros
CREATE TABLE public.mercadopago_accounts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  mp_user_id      TEXT NOT NULL,
  mp_access_token TEXT NOT NULL,
  mp_public_key   TEXT,
  country         supported_country NOT NULL,
  is_active       BOOLEAN DEFAULT TRUE,
  connected_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

ALTER TABLE public.mercadopago_accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "mp_accounts_own"
  ON public.mercadopago_accounts FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE TRIGGER mp_accounts_updated_at
  BEFORE UPDATE ON public.mercadopago_accounts
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
