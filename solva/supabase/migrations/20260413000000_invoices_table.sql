-- Table: invoices
CREATE TABLE IF NOT EXISTS public.invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  payment_id UUID NOT NULL REFERENCES public.payments(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  invoice_number TEXT NOT NULL UNIQUE,
  amount NUMERIC NOT NULL,
  platform_fee NUMERIC NOT NULL,
  pro_amount NUMERIC NOT NULL,
  currency TEXT NOT NULL DEFAULT 'EUR',
  country TEXT NOT NULL DEFAULT 'ES',
  job_title TEXT,
  client_name TEXT,
  pro_name TEXT,
  pdf_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON public.invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_invoices_payment_id ON public.invoices(payment_id);

ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "invoices_select_own" ON public.invoices
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

-- Storage bucket for invoice PDFs (private)
INSERT INTO storage.buckets (id, name, public)
VALUES ('invoices', 'invoices', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "invoices_storage_select" ON storage.objects
  FOR SELECT TO authenticated
  USING (bucket_id = 'invoices' AND (storage.foldername(name))[1] = auth.uid()::text);
