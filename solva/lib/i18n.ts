import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import * as Localization from 'expo-localization'
import AsyncStorage from '@react-native-async-storage/async-storage'

import en from './locales/en.json'
import es from './locales/es.json'
import fr from './locales/fr.json'
import pt from './locales/pt.json'
import nl from './locales/nl.json'
import de from './locales/de.json'
import it from './locales/it.json'

export const LANGUAGES = [
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'pt', label: 'Português', flag: '🇵🇹' },
  { code: 'nl', label: 'Nederlands', flag: '🇳🇱' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', label: 'Italiano', flag: '🇮🇹' },
]

const LANGUAGE_KEY = '@solva_language'

export async function getStoredLanguage(): Promise<string | null> {
  try { return await AsyncStorage.getItem(LANGUAGE_KEY) } catch { return null }
}

export async function setStoredLanguage(lang: string) {
  try { await AsyncStorage.setItem(LANGUAGE_KEY, lang) } catch {}
}

export async function changeLanguage(lang: string) {
  await setStoredLanguage(lang)
  await i18n.changeLanguage(lang)
}

function getDeviceLanguage(): string {
  const locale = Localization.getLocales()[0]?.languageCode ?? 'en'
  const supported = ['en', 'es', 'fr', 'pt', 'nl', 'de', 'it']
  return supported.includes(locale) ? locale : 'en'
}

// Init síncrono para evitar hooks error
i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, es: { translation: es }, fr: { translation: fr },
               pt: { translation: pt }, nl: { translation: nl }, de: { translation: de },
               it: { translation: it } },
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export async function initI18n() {
  const stored = await getStoredLanguage()
  const lng = stored ?? getDeviceLanguage()

  await i18n.changeLanguage(lng)
}

export default i18n
