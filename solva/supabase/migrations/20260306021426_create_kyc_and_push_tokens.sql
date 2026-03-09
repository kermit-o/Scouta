-- ============================================
-- KYC: verificación de identidad
-- ============================================
CREATE TYPE kyc_status AS ENUM ('pending', 'submitted', 'approved', 'rejected');
CREATE TYPE kyc_doc_type AS ENUM ('dni', 'passport', 'residence_permit', 'drivers_license');

CREATE TABLE public.kyc_verifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  status          kyc_status NOT NULL DEFAULT 'pending',
  doc_type        kyc_doc_type,
  doc_front_url   TEXT,
  doc_back_url    TEXT,
  selfie_url      TEXT,
  rejection_reason TEXT,
  submitted_at    TIMESTAMPTZ,
  reviewed_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

ALTER TABLE public.kyc_verifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "kyc_select_own"
  ON public.kyc_verifications FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "kyc_insert_own"
  ON public.kyc_verifications FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "kyc_update_own"
  ON public.kyc_verifications FOR UPDATE
  USING (auth.uid() = user_id);

CREATE TRIGGER kyc_updated_at
  BEFORE UPDATE ON public.kyc_verifications
  FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Storage bucket para documentos KYC (privado)
INSERT INTO storage.buckets (id, name, public)
VALUES ('kyc-docs', 'kyc-docs', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "kyc_docs_owner_only"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'kyc-docs' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "kyc_docs_upload"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'kyc-docs' AND auth.uid()::text = (storage.foldername(name))[1]);

-- ============================================
-- PUSH TOKENS: notificaciones
-- ============================================
CREATE TABLE public.push_tokens (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  token       TEXT NOT NULL,
  platform    TEXT NOT NULL DEFAULT 'expo',
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, token)
);

ALTER TABLE public.push_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "push_tokens_own"
  ON public.push_tokens FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
