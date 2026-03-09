-- ============================================
-- TABLA: contracts (contrato auto al aceptar bid)
-- ============================================
CREATE TYPE contract_status AS ENUM ('active', 'completed', 'disputed', 'cancelled');

CREATE TABLE public.contracts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id          UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  bid_id          UUID NOT NULL REFERENCES public.bids(id) ON DELETE CASCADE,
  client_id       UUID NOT NULL REFERENCES public.users(id),
  pro_id          UUID NOT NULL REFERENCES public.users(id),
  amount          NUMERIC(10,2) NOT NULL,
  currency        supported_currency NOT NULL,
  country         supported_country NOT NULL,
  status          contract_status NOT NULL DEFAULT 'active',
  terms           JSONB NOT NULL DEFAULT '{}',
  delivery_days   INTEGER,
  due_date        TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),

  UNIQUE(job_id),
  UNIQUE(bid_id)
);

-- ============================================
-- RLS
-- ============================================
ALTER TABLE public.contracts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "contracts_select_parties"
  ON public.contracts FOR SELECT
  USING (auth.uid() = client_id OR auth.uid() = pro_id);

CREATE POLICY "contracts_insert_system"
  ON public.contracts FOR INSERT
  WITH CHECK (auth.uid() = client_id);

CREATE POLICY "contracts_update_parties"
  ON public.contracts FOR UPDATE
  USING (auth.uid() = client_id OR auth.uid() = pro_id);

-- ============================================
-- AUTO-UPDATE: updated_at
-- ============================================
CREATE TRIGGER contracts_updated_at
  BEFORE UPDATE ON public.contracts
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
