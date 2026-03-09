-- ============================================
-- ADMIN: tabla de acciones y permisos
-- ============================================
CREATE TABLE public.admin_actions (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id    UUID NOT NULL REFERENCES public.users(id),
  action_type TEXT NOT NULL,
  target_id   UUID,
  target_type TEXT,
  notes       TEXT,
  metadata    JSONB DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.admin_actions ENABLE ROW LEVEL SECURITY;

-- Ahora el enum 'admin' ya existe en la DB, se puede usar
CREATE POLICY "admin_actions_admin_only"
  ON public.admin_actions FOR ALL
  USING ((SELECT role FROM public.users WHERE id = auth.uid()) = 'admin');

-- Vista admin: stats globales
CREATE OR REPLACE VIEW public.admin_stats AS
SELECT
  (SELECT COUNT(*) FROM public.users)::INT                                    AS total_users,
  (SELECT COUNT(*) FROM public.users WHERE role = 'pro')::INT                 AS total_pros,
  (SELECT COUNT(*) FROM public.users WHERE role = 'client')::INT              AS total_clients,
  (SELECT COUNT(*) FROM public.jobs WHERE status = 'open')::INT               AS jobs_open,
  (SELECT COUNT(*) FROM public.jobs WHERE status = 'completed')::INT          AS jobs_completed,
  (SELECT COUNT(*) FROM public.contracts WHERE status = 'active')::INT        AS contracts_active,
  (SELECT COUNT(*) FROM public.disputes WHERE status = 'open')::INT           AS disputes_open,
  (SELECT COUNT(*) FROM public.kyc_verifications WHERE status = 'submitted')::INT AS kyc_pending,
  (SELECT COUNT(*) FROM public.guarantees WHERE status = 'claimed')::INT      AS guarantees_claimed,
  (SELECT COALESCE(SUM(pro_amount), 0) FROM public.payments WHERE status = 'released') AS total_volume,
  (SELECT COALESCE(SUM(platform_fee), 0) FROM public.payments WHERE status = 'released') AS total_revenue;

GRANT SELECT ON public.admin_stats TO authenticated;
