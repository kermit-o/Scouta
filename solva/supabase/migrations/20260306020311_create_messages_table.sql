-- ============================================
-- TABLA: messages (chat realtime por contrato)
-- ============================================
CREATE TABLE public.messages (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id UUID NOT NULL REFERENCES public.contracts(id) ON DELETE CASCADE,
  sender_id   UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  content     TEXT NOT NULL,
  read_at     TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Solo las partes del contrato pueden ver mensajes
CREATE POLICY "messages_select"
  ON public.messages FOR SELECT
  USING (
    auth.uid() IN (
      SELECT client_id FROM public.contracts WHERE id = contract_id
      UNION
      SELECT pro_id FROM public.contracts WHERE id = contract_id
    )
  );

-- Solo las partes pueden enviar mensajes
CREATE POLICY "messages_insert"
  ON public.messages FOR INSERT
  WITH CHECK (
    auth.uid() = sender_id
    AND auth.uid() IN (
      SELECT client_id FROM public.contracts WHERE id = contract_id
      UNION
      SELECT pro_id FROM public.contracts WHERE id = contract_id
    )
  );

-- Habilita Realtime en la tabla
ALTER PUBLICATION supabase_realtime ADD TABLE public.messages;
