import { ScrollView, View, Text, StyleSheet, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import Svg, { Path } from 'react-native-svg'

export default function TermsScreen() {
  const insets = useSafeAreaInsets()
  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <Path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="#1a1a2e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </Svg>
        </TouchableOpacity>
        <Text style={s.headerTitle}>Términos y Condiciones</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>
        <Text style={s.meta}>Versión 1.0 — Marzo 2026 | Ley belga aplicable</Text>

        {[
          ['1. Partes del Contrato', 'Estos Términos constituyen un acuerdo vinculante entre el usuario y Solva Platform (en constitución), operador de la plataforma Solva. Al crear una cuenta, aceptas expresamente estos Términos en su totalidad.'],
          ['2. Descripción del Servicio', 'Solva es una plataforma digital de intermediación que conecta a clientes (personas que publican trabajos) con profesionales (autónomos o empresas que ofrecen servicios). Solva actúa como intermediario y no es parte del contrato de prestación de servicios entre cliente y profesional.'],
          ['3. Registro y Cuenta', 'Debes tener al menos 18 años para crear una cuenta. Debes proporcionar información veraz, completa y actualizada. Eres responsable de mantener la confidencialidad de tu contraseña. Cada persona puede tener únicamente una cuenta activa.'],
          ['4. Publicación de Trabajos y Ofertas', 'Clientes: puedes publicar trabajos de forma gratuita en el plan básico. Los trabajos deben ser lícitos y descritos con precisión.\n\nProfesionales: el plan gratuito permite hasta 3 ofertas (bids) por mes. Los planes Pro y Company ofrecen ofertas ilimitadas.'],
          ['5. Contratos y Pagos', 'Cuando un cliente acepta una oferta, se genera automáticamente un contrato digital sujeto al derecho belga. Los pagos quedan retenidos en escrow y se liberan al profesional cuando el cliente confirma la finalización satisfactoria. Solva aplica una comisión del 10% sobre cada transacción.'],
          ['6. Garantía Solva', 'La Garantía Solva protege a los clientes en casos de trabajo no completado, calidad notoriamente inferior a la descrita, daños causados durante la ejecución (con evidencia fotográfica) o cobros indebidos.\n\nNo están cubiertos: cambios de opinión del cliente, disputas por preferencias estéticas subjetivas, o trabajos acordados fuera de la plataforma.'],
          ['7. Sistema de Disputas', 'Cualquier disputa debe iniciarse a través de la plataforma dentro de los 7 días siguientes a la fecha de finalización del trabajo. El proceso incluye notificación a ambas partes, período de negociación de 48h y mediación por el equipo Solva con resolución en 5 días hábiles.'],
          ['8. Verificación KYC', 'Para poder recibir pagos, los profesionales deben completar la verificación KYC (Know Your Customer), obligatoria conforme a la Ley belga de 18 de septiembre de 2017 contra el blanqueo de capitales.'],
          ['9. Suscripciones', 'Plan Básico (gratuito): 3 bids/mes, perfil básico.\nPlan Pro: bids ilimitados, badge verificado, analytics, prioridad en búsquedas.\nPlan Company: todo Pro + dashboard multi-empleado + facturación automática.\n\nLas suscripciones se renuevan automáticamente. Puedes cancelar en cualquier momento. Se ofrecen 14 días de prueba gratuita.'],
          ['10. Prohibiciones', 'Queda prohibido: publicar servicios ilegales, realizar transacciones fuera de la plataforma, crear reseñas falsas, usar la plataforma para actividades de blanqueo de capitales, compartir datos de contacto antes de aceptar un contrato, o hacer scraping a la infraestructura de Solva.'],
          ['11. Limitación de Responsabilidad', 'Solva actúa como intermediario y no garantiza la calidad de los servicios ofrecidos por los profesionales, la solvencia económica de las partes, ni la disponibilidad ininterrumpida de la plataforma. La responsabilidad máxima de Solva está limitada al importe de las comisiones recibidas en los últimos 12 meses.'],
          ['12. Ley Aplicable y Jurisdicción', 'Estos Términos se rigen por el derecho belga. Para cualquier litigio serán competentes los tribunales de Bruselas. Los consumidores belgas también pueden acudir a la plataforma europea ODR: ec.europa.eu/consumers/odr'],
          ['13. Contacto', 'Para consultas legales: legal@solva.app\nDelegado de Protección de Datos: dpo@solva.app'],
        ].map(([title, body], i) => (
          <View key={i} style={s.section}>
            <Text style={s.sectionTitle}>{title}</Text>
            <Text style={s.sectionBody}>{body}</Text>
          </View>
        ))}

        <Text style={s.footer}>Última actualización: Marzo 2026</Text>
      </ScrollView>
    </View>
  )
}

const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: '#F6F7FB' },
  header: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 20, paddingVertical: 14,
    backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.05)',
  },
  backBtn: {
    width: 40, height: 40, borderRadius: 12,
    backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center',
  },
  headerTitle: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  scroll: { flex: 1 },
  content: { padding: 20, gap: 4, paddingBottom: 48 },
  meta: { fontSize: 12, color: '#9CA3AF', marginBottom: 16, fontStyle: 'italic' },
  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 15, fontWeight: '800', color: '#2563EB', marginBottom: 8 },
  sectionBody: { fontSize: 14, color: '#374151', lineHeight: 22 },
  footer: { fontSize: 12, color: '#9CA3AF', textAlign: 'center', marginTop: 16, fontStyle: 'italic' },
})
