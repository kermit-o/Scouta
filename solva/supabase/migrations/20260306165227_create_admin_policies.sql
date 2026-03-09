-- Admin puede ver TODO
CREATE POLICY "admin_select_all_users"
  ON public.users FOR SELECT
  USING ((SELECT role FROM public.users WHERE id = auth.uid()) = 'admin' OR auth.uid() = id);

CREATE POLICY "admin_select_all_kyc"
  ON public.kyc_verifications FOR SELECT
  USING ((SELECT role FROM public.users WHERE id = auth.uid()) = 'admin' OR auth.uid() = user_id);

CREATE POLICY "admin_update_kyc"
  ON public.kyc_verifications FOR UPDATE
  USING ((SELECT role FROM public.users WHERE id = auth.uid()) = 'admin' OR auth.uid() = user_id);

CREATE POLICY "admin_select_all_disputes"
  ON public.disputes FOR SELECT
  USING (
    (SELECT role FROM public.users WHERE id = auth.uid()) = 'admin'
    OR auth.uid() = opened_by OR auth.uid() = against
  );

CREATE POLICY "admin_update_disputes"
  ON public.disputes FOR UPDATE
  USING (
    (SELECT role FROM public.users WHERE id = auth.uid()) = 'admin'
    OR auth.uid() = opened_by OR auth.uid() = against
  );

CREATE POLICY "admin_select_all_guarantees"
  ON public.guarantees FOR SELECT
  USING ((SELECT role FROM public.users WHERE id = auth.uid()) = 'admin' OR auth.uid() = client_id);

CREATE POLICY "admin_update_guarantees"
  ON public.guarantees FOR UPDATE
  USING ((SELECT role FROM public.users WHERE id = auth.uid()) = 'admin' OR auth.uid() = client_id);

CREATE POLICY "admin_select_all_payments"
  ON public.payments FOR SELECT
  USING (
    (SELECT role FROM public.users WHERE id = auth.uid()) = 'admin'
    OR auth.uid() = client_id OR auth.uid() = pro_id
  );
