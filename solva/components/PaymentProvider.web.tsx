import { ReactNode } from 'react'

// En web, Stripe Elements se inicializa dentro de StripeCardForm.web.tsx
// por lo que PaymentProvider es un pass-through.
export default function PaymentProvider({ children }: { children: ReactNode }) {
  return <>{children}</>
}
