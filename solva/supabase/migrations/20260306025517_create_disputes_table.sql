-- ============================================
-- TABLA: disputes (sistema de mediación)
-- ============================================
CREATE TYPE dispute_status AS ENUM (
  'open', 'under_review', 'resolved_client', 'resolved_pro', 'resolved_split', 'closed'
);
CREATE TYPE dispute_reason AS ENUM (
  'work_not_done', 'work_poor_quality', 'payment_not_released',
  'no_show', 'scope_change', 'other'
);

CREATE TABLE public.disputes (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id     UUID NOT NULL REFERENCES public.contracts(id) ON DELETE CASCADE,
  payment_id      UUID REFERENCES public.payments(id),
  opened_by       UUID NOT NULL REFERENCES public.users(id),
  against         UUID NOT NULL REFERENCES public.users(id),
  reason          dispute_reason NOT NULL,
  description     TEXT NOT NULL,
  evidence_urls   TEXT[] DEFAULT '{}',
  status          dispute_status NOT NULL DEFAULT 'open',
  resolution_note TEXT,
  refund_pct      SMALLINT DEFAULT 0 CHECK (refund_pct >= 0 AND refund_pct <= 100),
  resolved_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(contract_id)
);

ALTER TABLE public.disputes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "disputes_select_parties"
  ON public.disputes FOR SELECT
  USING (auth.uid() = opened_by OR auth.uid() = against);

CREATE POLICY "disputes_insert"
  ON public.disputes FOR INSERT
  WITH CHECK (
    auth.uid() = opened_by
    AND auth.uid() IN (
      SELECT client_id FROM public.contracts WHERE id = contract_id
      UNION
      SELECT pro_id FROM public.contracts WHERE id = contract_id
    )
  );

CREATE POLICY "disputes_update_parties"
  ON public.disputes FOR UPDATE
  USING (auth.uid() = opened_by OR auth.uid() = against);

CREATE TRIGGER disputes_updated_at
  BEFORE UPDATE ON public.disputes
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Tabla de mensajes de disputa (evidencias y comunicación)
CREATE TABLE public.dispute_messages (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dispute_id  UUID NOT NULL REFERENCES public.disputes(id) ON DELETE CASCADE,
  sender_id   UUID NOT NULL REFERENCES public.users(id),
  content     TEXT NOT NULL,
  attachments TEXT[] DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.dispute_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dispute_messages_select"
  ON public.dispute_messages FOR SELECT
  USING (
    auth.uid() IN (
      SELECT opened_by FROM public.disputes WHERE id = dispute_id
      UNION
      SELECT against FROM public.disputes WHERE id = dispute_id
    )
  );

CREATE POLICY "dispute_messages_insert"
  ON public.dispute_messages FOR INSERT
  WITH CHECK (
    auth.uid() = sender_id
    AND auth.uid() IN (
      SELECT opened_by FROM public.disputes WHERE id = dispute_id
      UNION
      SELECT against FROM public.disputes WHERE id = dispute_id
    )
  );

-- Storage para evidencias de disputa
INSERT INTO storage.buckets (id, name, public)
VALUES ('dispute-evidence', 'dispute-evidence', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "dispute_evidence_parties"
  ON storage.objects FOR ALL
  USING (bucket_id = 'dispute-evidence' AND auth.uid()::text = (storage.foldername(name))[1])
  WITH CHECK (bucket_id = 'dispute-evidence' AND auth.uid()::text = (storage.foldername(name))[1]);
