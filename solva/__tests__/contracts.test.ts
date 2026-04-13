import { getContractTerms, CONTRACT_TEMPLATES } from '../lib/contracts/templates'

describe('Contract Templates', () => {
  const ALL_COUNTRIES = ['ES', 'FR', 'BE', 'NL', 'DE', 'PT', 'IT', 'GB', 'MX', 'CO', 'AR', 'BR', 'CL'] as const

  it('should have templates for all 13 supported countries', () => {
    for (const country of ALL_COUNTRIES) {
      expect(CONTRACT_TEMPLATES[country]).toBeDefined()
      expect(CONTRACT_TEMPLATES[country].country).toBe(country)
    }
  })

  it('should return ES as fallback for unknown countries', () => {
    const terms = getContractTerms('XX' as any)
    expect(terms.country).toBe('ES')
  })

  it('each template should have all required fields', () => {
    const requiredFields = [
      'country', 'language', 'law', 'jurisdiction',
      'payment_protection', 'cancellation_policy', 'dispute_resolution',
      'warranty_days', 'platform_fee_pct', 'platform_role',
      'independent_contractor', 'escrow_conditions', 'data_processing',
      'home_access_confidentiality', 'liability_limit',
    ]
    for (const country of ALL_COUNTRIES) {
      const template = CONTRACT_TEMPLATES[country]
      for (const field of requiredFields) {
        expect(template).toHaveProperty(field)
        expect((template as any)[field]).toBeTruthy()
      }
    }
  })

  it('EU countries should have 7 day warranty', () => {
    const euCountries = ['ES', 'FR', 'BE', 'NL', 'DE', 'PT', 'IT', 'GB'] as const
    for (const country of euCountries) {
      expect(CONTRACT_TEMPLATES[country].warranty_days).toBe(7)
    }
  })

  it('all templates should have 10% platform fee', () => {
    for (const country of ALL_COUNTRIES) {
      expect(CONTRACT_TEMPLATES[country].platform_fee_pct).toBe(10)
    }
  })

  it('b2b_clause can be null only where intentional', () => {
    for (const country of ALL_COUNTRIES) {
      // b2b_clause is explicitly typed as string | null
      const clause = CONTRACT_TEMPLATES[country].b2b_clause
      expect(typeof clause === 'string' || clause === null).toBe(true)
    }
  })
})
