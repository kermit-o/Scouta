ALTER TABLE public.reviews
  ADD COLUMN IF NOT EXISTS photos_verified      BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS photos_verify_result JSONB,
  ADD COLUMN IF NOT EXISTS photos_verified_at   TIMESTAMPTZ;
