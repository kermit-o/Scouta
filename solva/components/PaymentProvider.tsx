import { ReactNode } from 'react'
import { StripeProvider } from '@stripe/stripe-react-native'

const STRIPE_PK = process.env.EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY

export default function PaymentProvider({ children }: { children: ReactNode }) {
  if (!STRIPE_PK) {
    console.warn('PaymentProvider: EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY not set')
    return <>{children}</>
  }
  return (
    <StripeProvider publishableKey={STRIPE_PK} merchantIdentifier="merchant.com.solva.app">
      {children}
    </StripeProvider>
  )
}
