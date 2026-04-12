-- Update pro_profiles view to include missing profile fields
-- that pro/[id].tsx and search.tsx depend on (bio, skills,
-- availability, years_experience, hourly_rate, portfolio_urls).
-- These columns exist in users but were omitted from the original view.

CREATE OR REPLACE VIEW public.pro_profiles AS
SELECT
  u.id,
  u.full_name,
  u.avatar_url,
  u.bio,
  u.skills,
  u.availability,
  u.years_experience,
  u.hourly_rate,
  u.portfolio_urls,
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

-- Re-grant (CREATE OR REPLACE preserves grants but be explicit)
GRANT SELECT ON public.pro_profiles TO anon, authenticated;
