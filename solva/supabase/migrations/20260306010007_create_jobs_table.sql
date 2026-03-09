-- ============================================
-- TABLA: jobs (publicaciones de trabajo)
-- ============================================
CREATE TYPE job_status AS ENUM ('open', 'in_progress', 'completed', 'cancelled');
CREATE TYPE job_category AS ENUM (
  'cleaning', 'plumbing', 'electrical', 'painting', 'moving',
  'gardening', 'carpentry', 'tech', 'design', 'other'
);

CREATE TABLE public.jobs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  description   TEXT NOT NULL,
  category      job_category NOT NULL DEFAULT 'other',
  status        job_status NOT NULL DEFAULT 'open',
  budget_min    NUMERIC(10,2),
  budget_max    NUMERIC(10,2),
  currency      supported_currency NOT NULL,
  country       supported_country NOT NULL,
  city          TEXT,
  address       TEXT,
  is_remote     BOOLEAN DEFAULT FALSE,
  photos        TEXT[] DEFAULT '{}',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- RLS
-- ============================================
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Todos los usuarios autenticados pueden ver jobs abiertos
CREATE POLICY "jobs_select_open"
  ON public.jobs FOR SELECT
  USING (auth.role() = 'authenticated');

-- Solo el cliente dueño puede crear jobs
CREATE POLICY "jobs_insert_own"
  ON public.jobs FOR INSERT
  WITH CHECK (auth.uid() = client_id);

-- Solo el cliente dueño puede editar sus jobs
CREATE POLICY "jobs_update_own"
  ON public.jobs FOR UPDATE
  USING (auth.uid() = client_id);

-- Solo el cliente dueño puede eliminar sus jobs
CREATE POLICY "jobs_delete_own"
  ON public.jobs FOR DELETE
  USING (auth.uid() = client_id);

-- ============================================
-- AUTO-UPDATE: updated_at
-- ============================================
CREATE TRIGGER jobs_updated_at
  BEFORE UPDATE ON public.jobs
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
