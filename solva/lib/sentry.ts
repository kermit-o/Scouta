import * as SentryModule from '@sentry/react-native'
import Constants from 'expo-constants'

const DSN = process.env.EXPO_PUBLIC_SENTRY_DSN ?? ''

export function initSentry() {
  if (!DSN) return
  SentryModule.init({
    dsn: DSN,
    debug: __DEV__,
    environment: __DEV__ ? 'development' : 'production',
    tracesSampleRate: __DEV__ ? 1.0 : 0.2,
    release: Constants.expoConfig?.version ?? '1.0.0',
  })
}

export const Sentry = SentryModule
