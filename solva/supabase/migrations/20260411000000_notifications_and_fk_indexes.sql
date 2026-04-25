-- Migration: notifications table + missing FK indexes
-- Date: 2026-04-11
--
-- 1) Creates the `notifications` table used by stripe-webhook and send-notification
--    (previously these inserted into a table that didn't exist, silently failing).
-- 2) Adds missing indexes on foreign keys for bids/contracts/payments (query performance).

-- ========================================
-- 1. notifications table
-- ========================================
CREATE TABLE IF NOT EXISTS public.notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  title text NOT NULL,
  body text NOT NULL,
  data jsonb NOT NULL DEFAULT '{}'::jsonb,
  read_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id
  ON public.notifications(user_id);

CREATE INDEX IF NOT EXISTS idx_notifications_user_unread
  ON public.notifications(user_id, created_at DESC)
  WHERE read_at IS NULL;

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- Users only see their own notifications
DROP POLICY IF EXISTS "notifications_select_own" ON public.notifications;
CREATE POLICY "notifications_select_own"
  ON public.notifications
  FOR SELECT
  TO authenticated
  USING (user_id = auth.uid());

-- Users can mark their own notifications as read
DROP POLICY IF EXISTS "notifications_update_own" ON public.notifications;
CREATE POLICY "notifications_update_own"
  ON public.notifications
  FOR UPDATE
  TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

-- Inserts are done exclusively from service_role (edge functions),
-- which bypasses RLS — no INSERT policy for authenticated users is required.

-- ========================================
-- 2. FK indexes (performance)
-- ========================================
CREATE INDEX IF NOT EXISTS idx_bids_pro_id        ON public.bids(pro_id);
CREATE INDEX IF NOT EXISTS idx_bids_job_id        ON public.bids(job_id);
CREATE INDEX IF NOT EXISTS idx_contracts_pro_id   ON public.contracts(pro_id);
CREATE INDEX IF NOT EXISTS idx_contracts_client_id ON public.contracts(client_id);
CREATE INDEX IF NOT EXISTS idx_contracts_job_id   ON public.contracts(job_id);
CREATE INDEX IF NOT EXISTS idx_payments_pro_id    ON public.payments(pro_id);
CREATE INDEX IF NOT EXISTS idx_payments_client_id ON public.payments(client_id);
CREATE INDEX IF NOT EXISTS idx_payments_contract_id ON public.payments(contract_id);
CREATE INDEX IF NOT EXISTS idx_messages_contract_id ON public.messages(contract_id);
CREATE INDEX IF NOT EXISTS idx_reviews_reviewed_id  ON public.reviews(reviewed_id);
