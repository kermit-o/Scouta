-- ============================================
-- TABLA: payments (escrow Stripe/MercadoPago)
-- ============================================
CREATE TYPE payment_status AS ENUM (
  'pending', 'held', 'released', 'refunded', 'disputed'
);
CREATE TYPE payment_provider AS ENUM (
  'stripe', 'mercadopago'
);

CREATE TABLE public.payments (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id           UUID NOT NULL REFERENCES public.contracts(id) ON DELETE CASCADE,
  client_id             UUID NOT NULL REFERENCES public.users(id),
  pro_id                UUID NOT NULL REFERENCES public.users(id),
  amount                NUMERIC(10,2) NOT NULL,
  platform_fee          NUMERIC(10,2) NOT NULL,
  pro_amount            NUMERIC(10,2) NOT NULL,
  currency              supported_currency NOT NULL,
  country               supported_country NOT NULL,
  provider              payment_provider NOT NULL,
  provider_payment_id   TEXT,
  provider_transfer_id  TEXT,
  status                payment_status NOT NULL DEFAULT 'pending',
  held_at               TIMESTAMPTZ,
  released_at           TIMESTAMPTZ,
  refunded_at           TIMESTAMPTZ,
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(contract_id)
);

ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "payments_select_parties"
  ON public.payments FOR SELECT
  USING (auth.uid() = client_id OR auth.uid() = pro_id);

CREATE POLICY "payments_insert_client"
  ON public.payments FOR INSERT
  WITH CHECK (auth.uid() = client_id);

CREATE POLICY "payments_update_parties"
  ON public.payments FOR UPDATE
  USING (auth.uid() = client_id OR auth.uid() = pro_id);

CREATE TRIGGER payments_updated_at
  BEFORE UPDATE ON public.payments
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
