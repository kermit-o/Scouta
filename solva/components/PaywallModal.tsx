import { View, Text, StyleSheet, TouchableOpacity, Modal, Pressable } from 'react-native'
import { router } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { PlanFeature, PAYWALL_COPY } from '../lib/planLimits'

interface Props {
  feature: PlanFeature | null
  onClose: () => void
}

export function PaywallModal({ feature, onClose }: Props) {
  if (!feature) return null
  const copy = PAYWALL_COPY[feature]

  return (
    <Modal transparent animationType="fade" visible={!!feature} onRequestClose={onClose}>
      <Pressable style={s.backdrop} onPress={onClose}>
        <Pressable style={s.sheet} onPress={e => e.stopPropagation()}>
          {/* Icon */}
          <View style={[s.iconWrap, { backgroundColor: copy.color + '15' }]}>
            <Ionicons name={copy.icon as any} size={32} color={copy.color} />
          </View>

          {/* Copy */}
          <Text style={s.title}>{copy.title}</Text>
          <Text style={s.description}>{copy.description}</Text>

          {/* ROI hint para bids */}
          {feature === 'bid' && (
            <View style={s.roiCard}>
              <Text style={s.roiText}>
                💡 Pro cuesta 14,99€/mes. Con comisión reducida al 5% (vs 10%), 
                se paga solo con <Text style={s.roiBold}>300€ facturados al mes.</Text>
              </Text>
            </View>
          )}

          {/* CTA */}
          <TouchableOpacity
            style={[s.ctaBtn, { backgroundColor: copy.color }]}
            onPress={() => { onClose(); router.push('/(app)/subscription') }}
            activeOpacity={0.85}
          >
            <Ionicons name="sparkles" size={16} color="#fff" />
            <Text style={s.ctaText}>{copy.cta}</Text>
          </TouchableOpacity>

          <TouchableOpacity style={s.cancelBtn} onPress={onClose}>
            <Text style={s.cancelText}>Ahora no</Text>
          </TouchableOpacity>

          <Text style={s.fine}>Sin tarjeta de crédito. Cancela cuando quieras.</Text>
        </Pressable>
      </Pressable>
    </Modal>
  )
}

const s = StyleSheet.create({
  backdrop: {
    flex: 1, backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#fff', borderTopLeftRadius: 28, borderTopRightRadius: 28,
    padding: 28, paddingBottom: 40, alignItems: 'center', gap: 12,
  },
  iconWrap: {
    width: 72, height: 72, borderRadius: 22,
    alignItems: 'center', justifyContent: 'center', marginBottom: 4,
  },
  title: { fontSize: 20, fontWeight: '800', color: '#1a1a2e', textAlign: 'center' },
  description: { fontSize: 15, color: '#555', textAlign: 'center', lineHeight: 22 },
  roiCard: {
    backgroundColor: '#F0FDF4', borderRadius: 14, padding: 14,
    borderWidth: 1, borderColor: '#BBF7D0', width: '100%',
  },
  roiText: { fontSize: 13, color: '#374151', lineHeight: 20, textAlign: 'center' },
  roiBold: { fontWeight: '700', color: '#059669' },
  ctaBtn: {
    width: '100%', height: 56, borderRadius: 16,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
    shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.3, shadowRadius: 14, elevation: 6,
  },
  ctaText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  cancelBtn: { paddingVertical: 8 },
  cancelText: { fontSize: 14, color: '#888' },
  fine: { fontSize: 11, color: '#bbb', textAlign: 'center' },
})
