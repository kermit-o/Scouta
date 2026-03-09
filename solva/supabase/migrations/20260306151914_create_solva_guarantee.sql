-- ============================================
-- GARANTÍA SOLVA: cobertura por trabajo
-- ============================================
CREATE TYPE guarantee_status AS ENUM (
  'active', 'claimed', 'approved', 'rejected', 'expired'
);

CREATE TABLE public.guarantees (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id     UUID NOT NULL REFERENCES public.contracts(id) ON DELETE CASCADE,
  client_id       UUID NOT NULL REFERENCES public.users(id),
  status          guarantee_status NOT NULL DEFAULT 'active',
  max_coverage    NUMERIC(10,2) NOT NULL,
  currency        supported_currency NOT NULL,
  country         supported_country NOT NULL,
  claim_reason    TEXT,
  claim_evidence  TEXT[] DEFAULT '{}',
  approved_amount NUMERIC(10,2),
  resolution_note TEXT,
  claimed_at      TIMESTAMPTZ,
  resolved_at     TIMESTAMPTZ,
  expires_at      TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(contract_id)
);

ALTER TABLE public.guarantees ENABLE ROW LEVEL SECURITY;

CREATE POLICY "guarantees_select"
  ON public.guarantees FOR SELECT
  USING (auth.uid() = client_id);

CREATE POLICY "guarantees_insert"
  ON public.guarantees FOR INSERT
  WITH CHECK (auth.uid() = client_id);

CREATE POLICY "guarantees_update"
  ON public.guarantees FOR UPDATE
  USING (auth.uid() = client_id);

CREATE TRIGGER guarantees_updated_at
  BEFORE UPDATE ON public.guarantees
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Cobertura máxima por país
CREATE OR REPLACE FUNCTION public.get_guarantee_coverage(country supported_country, amount NUMERIC)
RETURNS NUMERIC AS $$
  SELECT LEAST(amount, CASE country
    WHEN 'ES' THEN 500
    WHEN 'FR' THEN 500
    WHEN 'MX' THEN 5000
    WHEN 'CO' THEN 500000
    WHEN 'AR' THEN 50000
    WHEN 'BR' THEN 1000
    WHEN 'CL' THEN 150000
    ELSE 500
  END);
$$ LANGUAGE sql IMMUTABLE;
