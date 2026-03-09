-- ============================================
-- TABLA: reviews (obligatorias al completar)
-- ============================================
CREATE TABLE public.reviews (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id     UUID NOT NULL REFERENCES public.contracts(id) ON DELETE CASCADE,
  job_id          UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
  reviewer_id     UUID NOT NULL REFERENCES public.users(id),
  reviewed_id     UUID NOT NULL REFERENCES public.users(id),
  rating          SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
  comment         TEXT NOT NULL,
  photos_before   TEXT[] DEFAULT '{}',
  photos_after    TEXT[] DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW(),

  -- Una review por contrato por reviewer
  UNIQUE(contract_id, reviewer_id)
);

ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;

-- Todos los autenticados pueden ver reviews
CREATE POLICY "reviews_select"
  ON public.reviews FOR SELECT
  USING (auth.role() = 'authenticated');

-- Solo las partes del contrato pueden crear reviews
CREATE POLICY "reviews_insert"
  ON public.reviews FOR INSERT
  WITH CHECK (
    auth.uid() = reviewer_id
    AND auth.uid() IN (
      SELECT client_id FROM public.contracts WHERE id = contract_id
      UNION
      SELECT pro_id FROM public.contracts WHERE id = contract_id
    )
  );

-- ============================================
-- FUNCIÓN: score promedio por usuario
-- ============================================
CREATE OR REPLACE FUNCTION public.get_user_score(user_id UUID)
RETURNS NUMERIC AS $$
  SELECT ROUND(AVG(rating)::numeric, 2)
  FROM public.reviews
  WHERE reviewed_id = user_id;
$$ LANGUAGE sql STABLE;

-- ============================================
-- Storage bucket para fotos de reviews
-- ============================================
INSERT INTO storage.buckets (id, name, public)
VALUES ('reviews', 'reviews', true)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "reviews_photos_read"
  ON storage.objects FOR SELECT
  USING (bucket_id = 'reviews');

CREATE POLICY "reviews_photos_upload"
  ON storage.objects FOR INSERT
  WITH CHECK (bucket_id = 'reviews' AND auth.uid()::text = (storage.foldername(name))[1]);
