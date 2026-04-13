import en from '../lib/locales/en.json'
import es from '../lib/locales/es.json'
import fr from '../lib/locales/fr.json'
import pt from '../lib/locales/pt.json'
import nl from '../lib/locales/nl.json'
import de from '../lib/locales/de.json'
import it from '../lib/locales/it.json'

function flattenKeys(obj: Record<string, any>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      return flattenKeys(value, fullKey)
    }
    return [fullKey]
  })
}

describe('i18n locale files', () => {
  const locales = { en, es, fr, pt, nl, de, it }
  const localeNames = Object.keys(locales) as (keyof typeof locales)[]
  const referenceKeys = flattenKeys(es).sort()

  it('all locales should have the same number of keys', () => {
    for (const name of localeNames) {
      const keys = flattenKeys(locales[name])
      expect(keys.length).toBe(referenceKeys.length)
    }
  })

  it('all locales should have exactly the same keys as es.json', () => {
    for (const name of localeNames) {
      const keys = flattenKeys(locales[name]).sort()
      const missingInLocale = referenceKeys.filter(k => !keys.includes(k))
      const extraInLocale = keys.filter(k => !referenceKeys.includes(k))

      if (missingInLocale.length > 0) {
        fail(`${name}.json is missing keys: ${missingInLocale.join(', ')}`)
      }
      if (extraInLocale.length > 0) {
        fail(`${name}.json has extra keys: ${extraInLocale.join(', ')}`)
      }
    }
  })

  it('no translation value should be empty string', () => {
    for (const name of localeNames) {
      const keys = flattenKeys(locales[name])
      for (const key of keys) {
        const parts = key.split('.')
        let value: any = locales[name]
        for (const part of parts) value = value?.[part]
        expect(value).not.toBe('')
      }
    }
  })
})
