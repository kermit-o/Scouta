// Sentry is disabled until @sentry/react-native is updated to ~7.11.0
// (compatible with Expo SDK 55). Re-enable when ready.

export function initSentry() {
  // no-op
}

export const Sentry = {
  captureException: (err: any) => console.error('Sentry disabled:', err),
  captureMessage: (msg: string) => console.warn('Sentry disabled:', msg),
}
