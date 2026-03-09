-- ============================================
-- API KEYS: acceso B2B
-- ============================================
CREATE TABLE public.api_keys (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  key_hash      TEXT NOT NULL UNIQUE,
  key_prefix    TEXT NOT NULL,
  scopes        TEXT[] DEFAULT '{"jobs:read","pros:read"}',
  requests_today INT DEFAULT 0,
  requests_total INT DEFAULT 0,
  rate_limit    INT DEFAULT 1000,
  last_used_at  TIMESTAMPTZ,
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "api_keys_own"
  ON public.api_keys FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE TRIGGER api_keys_updated_at
  BEFORE UPDATE ON public.api_keys
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Reset diario de requests
CREATE OR REPLACE FUNCTION public.reset_api_requests_daily()
RETURNS void AS $$
  UPDATE public.api_keys SET requests_today = 0;
$$ LANGUAGE sql SECURITY DEFINER;
