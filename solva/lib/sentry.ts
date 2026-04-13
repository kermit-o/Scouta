import * as Sentry from '@sentry/react-native'
import Constants from 'expo-constants'

const SENTRY_DSN = process.env.EXPO_PUBLIC_SENTRY_DSN

export function initSentry() {
  if (!SENTRY_DSN) {
    console.warn('Sentry DSN not configured — error tracking disabled')
    return
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment: __DEV__ ? 'development' : 'production',
    release: Constants.expoConfig?.version ?? '1.0.0',
    dist: Constants.expoConfig?.android?.versionCode?.toString() ?? '1',
    tracesSampleRate: __DEV__ ? 1.0 : 0.2,
    enableAutoSessionTracking: true,
    attachScreenshot: true,
    // Don't send in dev unless explicitly configured
    enabled: !__DEV__ || !!SENTRY_DSN,
  })
}

export { Sentry }
