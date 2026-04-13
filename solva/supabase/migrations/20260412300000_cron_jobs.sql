-- Enable pg_cron extension (available on Supabase by default)
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Grant usage to postgres role
GRANT USAGE ON SCHEMA cron TO postgres;

-- ========================================
-- 1. Reset API key daily request counters
-- Runs at midnight UTC every day
-- ========================================
SELECT cron.schedule(
  'reset-api-requests-daily',
  '0 0 * * *',
  $$UPDATE public.api_keys SET requests_today = 0 WHERE requests_today > 0$$
);

-- ========================================
-- 2. Expire trials that have ended
-- Runs every hour — checks trial_ends_at
-- ========================================
SELECT cron.schedule(
  'expire-trials-hourly',
  '0 * * * *',
  $$UPDATE public.subscriptions
    SET status = 'expired', cancel_at_period_end = true
    WHERE status = 'trialing'
    AND trial_ends_at IS NOT NULL
    AND trial_ends_at < NOW()$$
);

-- ========================================
-- 3. Clean up expired push tokens
-- Runs weekly on Sunday at 3 AM UTC
-- Removes tokens older than 90 days (likely stale)
-- ========================================
SELECT cron.schedule(
  'cleanup-push-tokens-weekly',
  '0 3 * * 0',
  $$DELETE FROM public.push_tokens
    WHERE created_at < NOW() - INTERVAL '90 days'$$
);

-- ========================================
-- 4. Auto-close stale disputes
-- Runs daily at 6 AM UTC
-- Disputes open for more than 30 days without resolution
-- get marked as closed with a note
-- ========================================
SELECT cron.schedule(
  'close-stale-disputes-daily',
  '0 6 * * *',
  $$UPDATE public.disputes
    SET status = 'closed',
        resolution_note = 'Cerrada automáticamente por inactividad tras 30 días.',
        resolved_at = NOW()
    WHERE status IN ('open', 'under_review')
    AND created_at < NOW() - INTERVAL '30 days'$$
);
