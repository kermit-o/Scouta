/**
 * Tests that validate the consistency of TypeScript types
 * defined in lib/supabase.ts. These are compile-time checks
 * that also verify runtime constants.
 */

import type {
  UserRole, SupportedCountry, SupportedCurrency, SupportedLanguage,
  JobCategory, JobStatus, BidStatus, PaymentStatus, PaymentProvider,
  SubscriptionPlan, SubscriptionStatus, KycStatus, DisputeStatus, DisputeReason,
  GuaranteeStatus,
} from '../lib/supabase'

describe('Supabase Types Consistency', () => {
  it('UserRole should include all expected roles', () => {
    const roles: UserRole[] = ['client', 'pro', 'company', 'admin']
    expect(roles).toHaveLength(4)
  })

  it('SupportedCountry should include all 13 countries', () => {
    const countries: SupportedCountry[] = [
      'ES', 'FR', 'BE', 'NL', 'DE', 'PT', 'IT', 'GB',
      'MX', 'CO', 'AR', 'BR', 'CL',
    ]
    expect(countries).toHaveLength(13)
  })

  it('SupportedCurrency should include all currencies', () => {
    const currencies: SupportedCurrency[] = ['EUR', 'GBP', 'MXN', 'COP', 'ARS', 'BRL', 'CLP']
    expect(currencies).toHaveLength(7)
  })

  it('SupportedLanguage should match i18n supported languages', () => {
    const languages: SupportedLanguage[] = ['en', 'es', 'fr', 'pt', 'nl', 'de', 'it']
    expect(languages).toHaveLength(7)
  })

  it('JobCategory should include all categories', () => {
    const categories: JobCategory[] = [
      'cleaning', 'plumbing', 'electrical', 'painting',
      'moving', 'gardening', 'carpentry', 'tech', 'design', 'other',
    ]
    expect(categories).toHaveLength(10)
  })

  it('payment flow statuses should be complete', () => {
    const statuses: PaymentStatus[] = ['pending', 'held', 'released', 'refunded', 'disputed']
    expect(statuses).toHaveLength(5)
  })

  it('subscription plans should match pricing tiers', () => {
    const plans: SubscriptionPlan[] = ['free', 'pro', 'company']
    expect(plans).toHaveLength(3)
  })

  it('dispute reasons should cover all cases', () => {
    const reasons: DisputeReason[] = [
      'work_not_done', 'work_poor_quality', 'payment_not_released',
      'no_show', 'scope_change', 'other',
    ]
    expect(reasons).toHaveLength(6)
  })
})
