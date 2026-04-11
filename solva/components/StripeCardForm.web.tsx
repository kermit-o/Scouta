import { useEffect, useState } from 'react'
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { loadStripe, Stripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { supabase } from '../lib/supabase'

type TFn = (key: string) => string

interface PaymentIntentData {
  payment_intent_id: string
  platform_fee: number
  pro_amount: number
}

interface ContractLike {
  id: string
  client_id: string
  pro_id: string
  amount: number
  currency: string
  country: string
}

export interface StripeCardFormProps {
  clientSecret: string | null
  paymentData: PaymentIntentData | null
  contract: ContractLike | null
  onSuccess: () => void
  onError: (msg: string) => void
  processing: boolean
  setProcessing: (v: boolean) => void
  t: TFn
}

const STRIPE_PK = process.env.EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY

let stripePromise: Promise<Stripe | null> | null = null
function getStripePromise() {
  if (!STRIPE_PK) {
    console.error('Missing EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY')
    return null
  }
  if (!stripePromise) stripePromise = loadStripe(STRIPE_PK)
  return stripePromise
}

function InnerForm(props: StripeCardFormProps) {
  const { clientSecret, paymentData, contract, onSuccess, onError, processing, setProcessing, t } = props
  const stripe = useStripe()
  const elements = useElements()

  async function handleSubmit() {
    if (!stripe || !elements) {
      onError('Stripe no está listo. Espera un momento.')
      return
    }
    if (!clientSecret || !paymentData || !contract) {
      onError('Datos de pago incompletos')
      return
    }
    const card = elements.getElement(CardElement)
    if (!card) {
      onError('No se encontró el campo de tarjeta.')
      return
    }
    setProcessing(true)
    try {
      const { error } = await stripe.confirmCardPayment(clientSecret, {
        payment_method: { card },
      })
      if (error) throw new Error(error.message)

      const { error: dbError } = await supabase.from('payments').insert({
        contract_id: contract.id,
        client_id: contract.client_id,
        pro_id: contract.pro_id,
        amount: contract.amount,
        platform_fee: paymentData.platform_fee,
        pro_amount: paymentData.pro_amount,
        currency: contract.currency,
        country: contract.country,
        provider: 'stripe',
        provider_payment_id: paymentData.payment_intent_id,
        status: 'held',
        held_at: new Date().toISOString(),
      })
      if (dbError) throw new Error(dbError.message)
      onSuccess()
    } catch (err: any) {
      onError(err?.message ?? 'Error al confirmar el pago')
    } finally {
      setProcessing(false)
    }
  }

  return (
    <View>
      <Text style={{ fontSize: 13, fontWeight: '600', color: '#555', marginBottom: 8 }}>
        {t('payment.cardNumber') ?? 'Número de tarjeta'}
      </Text>
      <View style={{
        backgroundColor: '#F9FAFB',
        borderRadius: 12,
        borderWidth: 1,
        borderColor: '#E5E7EB',
        padding: 14,
        marginBottom: 20,
      }}>
        {/* @ts-expect-error – CardElement es un componente DOM, en web renderiza como div */}
        <CardElement options={{
          style: {
            base: {
              fontSize: '16px',
              color: '#1a1a2e',
              fontFamily: 'system-ui, sans-serif',
              '::placeholder': { color: '#9CA3AF' },
            },
            invalid: { color: '#EF4444' },
          },
          hidePostalCode: true,
        }} />
      </View>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 16 }}>
        <Ionicons name="lock-closed-outline" size={14} color="#059669" />
        <Text style={{ fontSize: 12, color: '#059669', fontWeight: '600' }}>
          {t('payment.securedByStripe') ?? 'Pago seguro con Stripe'}
        </Text>
      </View>
      <TouchableOpacity
        style={{
          backgroundColor: '#2563EB',
          borderRadius: 14,
          height: 52,
          alignItems: 'center',
          justifyContent: 'center',
          opacity: processing || !stripe ? 0.6 : 1,
        }}
        onPress={handleSubmit}
        disabled={processing || !stripe}
      >
        {processing
          ? <ActivityIndicator color="#fff" />
          : <Text style={{ fontSize: 16, fontWeight: '700', color: '#fff' }}>
              {t('payment.confirmPay') ?? 'Confirmar pago'}
            </Text>}
      </TouchableOpacity>
    </View>
  )
}

export default function StripeCardForm(props: StripeCardFormProps) {
  const [stripeReady, setStripeReady] = useState(false)
  useEffect(() => {
    const p = getStripePromise()
    if (p) p.then(() => setStripeReady(true))
    else props.onError('Stripe no está configurado (falta EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY)')
  }, [])

  if (!stripeReady) {
    return (
      <View style={{ padding: 20, alignItems: 'center' }}>
        <ActivityIndicator color="#2563EB" />
      </View>
    )
  }

  return (
    <Elements stripe={getStripePromise()}>
      <InnerForm {...props} />
    </Elements>
  )
}
