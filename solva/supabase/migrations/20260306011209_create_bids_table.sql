-- ============================================
-- TABLA: bids (ofertas de pros a jobs)
-- ============================================
CREATE TYPE bid_status AS ENUM ('pending', 'accepted', 'rejected', 'withdrawn');

CREATE TABLE public.bids (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id        UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  pro_id        UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  amount        NUMERIC(10,2) NOT NULL,
  currency      supported_currency NOT NULL,
  message       TEXT NOT NULL,
  delivery_days INTEGER,
  status        bid_status NOT NULL DEFAULT 'pending',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),

  -- Un pro solo puede hacer una oferta por job
  UNIQUE(job_id, pro_id)
);

-- ============================================
-- RLS
-- ============================================
ALTER TABLE public.bids ENABLE ROW LEVEL SECURITY;

-- El cliente del job y el pro que hizo la oferta pueden verla
CREATE POLICY "bids_select"
  ON public.bids FOR SELECT
  USING (
    auth.uid() = pro_id
    OR auth.uid() = (SELECT client_id FROM public.jobs WHERE id = job_id)
  );

-- Solo pros pueden crear bids (no en sus propios jobs)
CREATE POLICY "bids_insert_pro"
  ON public.bids FOR INSERT
  WITH CHECK (
    auth.uid() = pro_id
    AND (SELECT role FROM public.users WHERE id = auth.uid()) IN ('pro', 'company')
    AND auth.uid() != (SELECT client_id FROM public.jobs WHERE id = job_id)
  );

-- Solo el pro puede editar/retirar su propia oferta
CREATE POLICY "bids_update_own"
  ON public.bids FOR UPDATE
  USING (auth.uid() = pro_id);

-- El cliente puede actualizar el status (aceptar/rechazar)
CREATE POLICY "bids_update_client"
  ON public.bids FOR UPDATE
  USING (auth.uid() = (SELECT client_id FROM public.jobs WHERE id = job_id));

-- ============================================
-- AUTO-UPDATE: updated_at
-- ============================================
CREATE TRIGGER bids_updated_at
  BEFORE UPDATE ON public.bids
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
