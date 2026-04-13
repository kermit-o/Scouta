import { PAYWALL_COPY, PlanFeature } from '../lib/planLimits'

describe('Plan Limits', () => {
  const ALL_FEATURES: PlanFeature[] = ['bid', 'photo', 'ai_content', 'analytics', 'saved_reply', 'team_member']

  it('PAYWALL_COPY should have entries for all plan features', () => {
    for (const feature of ALL_FEATURES) {
      expect(PAYWALL_COPY[feature]).toBeDefined()
    }
  })

  it('each PAYWALL_COPY entry should have title, description, cta, icon, color', () => {
    for (const feature of ALL_FEATURES) {
      const copy = PAYWALL_COPY[feature]
      expect(copy.title).toBeTruthy()
      expect(copy.description).toBeTruthy()
      expect(copy.cta).toBeTruthy()
      expect(copy.icon).toBeTruthy()
      expect(copy.color).toMatch(/^#[0-9A-Fa-f]{6}$/)
    }
  })
})
