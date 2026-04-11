import { useState } from 'react'
import { View, Text, TouchableOpacity, ActivityIndicator, StyleSheet } from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import { CardField, useConfirmPayment, CardFieldInput } from '@stripe/stripe-react-native'
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

export default function StripeCardForm(props: StripeCardFormProps) {
  const { clientSecret, paymentData, contract, onSuccess, onError, processing, setProcessing, t } = props
  const { confirmPayment } = useConfirmPayment()
  const [cardComplete, setCardComplete] = useState(false)

  async function handleSubmit() {
    if (!clientSecret || !paymentData || !contract) {
      onError('Datos de pago incompletos')
      return
    }
    if (!cardComplete) {
      onError('Introduce los datos completos de la tarjeta')
      return
    }
    setProcessing(true)
    try {
      const { error, paymentIntent } = await confirmPayment(clientSecret, {
        paymentMethodType: 'Card',
      })
      if (error) throw new Error(error.message)
      if (!paymentIntent) throw new Error('No se pudo confirmar el pago')

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
      <Text style={styles.label}>
        {t('payment.cardNumber') ?? 'Número de tarjeta'}
      </Text>
      <CardField
        postalCodeEnabled={false}
        placeholders={{ number: '4242 4242 4242 4242' }}
        cardStyle={{
          backgroundColor: '#F9FAFB',
          textColor: '#1a1a2e',
          placeholderColor: '#9CA3AF',
          borderRadius: 12,
        }}
        style={styles.cardField}
        onCardChange={(details: CardFieldInput.Details) => setCardComplete(details.complete)}
      />
      <View style={styles.secureRow}>
        <Ionicons name="lock-closed-outline" size={14} color="#059669" />
        <Text style={styles.secureText}>
          {t('payment.securedByStripe') ?? 'Pago seguro con Stripe'}
        </Text>
      </View>
      <TouchableOpacity
        style={[styles.button, (processing || !cardComplete) && styles.buttonDisabled]}
        onPress={handleSubmit}
        disabled={processing || !cardComplete}
      >
        {processing
          ? <ActivityIndicator color="#fff" />
          : <Text style={styles.buttonText}>
              {t('payment.confirmPay') ?? 'Confirmar pago'}
            </Text>}
      </TouchableOpacity>
    </View>
  )
}

const styles = StyleSheet.create({
  label: { fontSize: 13, fontWeight: '600', color: '#555', marginBottom: 8 },
  cardField: { height: 50, marginBottom: 20 },
  secureRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 16 },
  secureText: { fontSize: 12, color: '#059669', fontWeight: '600' },
  button: {
    backgroundColor: '#2563EB',
    borderRadius: 14,
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { fontSize: 16, fontWeight: '700', color: '#fff' },
})
