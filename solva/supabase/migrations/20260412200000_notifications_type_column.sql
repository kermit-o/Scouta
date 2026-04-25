-- Add type column to notifications table
-- Used by stripe-webhook to categorize notifications (payment_held, payment_failed, etc.)
ALTER TABLE public.notifications ADD COLUMN IF NOT EXISTS type TEXT;
