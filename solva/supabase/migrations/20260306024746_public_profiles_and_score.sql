-- ============================================
-- Perfil público: pros visibles sin login
-- ============================================

-- Permite ver perfiles de pros públicamente
CREATE POLICY "users_select_public"
  ON public.users FOR SELECT
  USING (
    role IN ('pro', 'company')
    OR auth.uid() = id
  );

-- Reviews públicas (visibles para todos)
CREATE POLICY "reviews_select_public"
  ON public.reviews FOR SELECT
  USING (true);

-- Vista pública de pros con score
CREATE OR REPLACE VIEW public.pro_profiles AS
SELECT
  u.id,
  u.full_name,
  u.avatar_url,
  u.role,
  u.country,
  u.currency,
  u.language,
  u.is_verified,
  u.created_at,
  COALESCE(public.get_user_score(u.id), 0) AS score,
  COUNT(DISTINCT r.id)::INT AS total_reviews,
  COUNT(DISTINCT c.id)::INT AS total_jobs_done
FROM public.users u
LEFT JOIN public.reviews r ON r.reviewed_id = u.id
LEFT JOIN public.contracts c ON c.pro_id = u.id AND c.status = 'completed'
WHERE u.role IN ('pro', 'company')
GROUP BY u.id;

-- Acceso público a la vista
GRANT SELECT ON public.pro_profiles TO anon, authenticated;
