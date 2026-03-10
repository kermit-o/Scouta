import { ScrollView, View, Text, StyleSheet, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import { Ionicons } from '@expo/vector-icons'

export default function TermsScreen() {
  const insets = useSafeAreaInsets()
  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={20} color="#1a1a2e" />
        </TouchableOpacity>
        <Text style={s.headerTitle}>Términos de Servicio</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>
        <Text style={s.meta}>Versión 1.0 — Marzo 2026 | Bélgica</Text>
        {[
          ['1. Aceptación de los Términos', 'Al registrarte en Solva aceptas estos Términos de Servicio. Si no estás de acuerdo, no puedes usar la plataforma. Solva se reserva el derecho a modificar estos términos con 30 días de aviso previo.'],
          ['2. Descripción del Servicio', 'Solva es una plataforma digital que conecta clientes con profesionales de servicios del hogar y otros servicios locales. Solva actúa como intermediario y no es empleador ni contratista de los profesionales.'],
          ['3. Registro y Cuenta', 'Debes tener al menos 18 años para registrarte. Eres responsable de mantener la confidencialidad de tu contraseña y de todas las actividades que ocurran bajo tu cuenta. Debes proporcionar información veraz y actualizada.'],
          ['4. Verificación de Identidad (KYC)', 'Para acceder a todas las funciones de la plataforma, deberás verificar tu identidad mediante un documento oficial. Este proceso es obligatorio para publicar jobs y recibir pagos. Los documentos son tratados conforme al RGPD.'],
          ['5. Jobs y Contratos', 'Los clientes publican jobs con descripción, presupuesto y categoría. Los profesionales envían ofertas. Una vez aceptada una oferta, se genera un contrato digital vinculante para ambas partes. Cualquier modificación requiere acuerdo mutuo.'],
          ['6. Sistema de Pagos (Escrow)', 'Los pagos se realizan a través del sistema de custodia (escrow) de Solva. El cliente deposita el pago antes del inicio del trabajo. El dinero se libera al profesional solo cuando el cliente confirma la finalización satisfactoria o transcurrido el plazo acordado.'],
          ['7. Comisiones', 'Solva cobra una comisión del 10% sobre el valor de cada transacción completada. Esta comisión se detrae automáticamente del pago al profesional. Los precios mostrados a los clientes son finales e incluyen la comisión.'],
          ['8. Cancelaciones y Reembolsos', 'El cliente puede cancelar un job sin coste antes de que sea aceptado. Tras la aceptación, aplica la política de cancelación acordada en el contrato. En caso de disputa, Solva mediará y su decisión será vinculante.'],
          ['9. Valoraciones y Reseñas', 'Ambas partes pueden valorarse mutuamente tras completar un job. Las valoraciones deben ser honestas y basadas en la experiencia real. Solva se reserva el derecho de eliminar valoraciones que incumplan estas normas.'],
          ['10. Conducta Prohibida', 'Está prohibido: proporcionar información falsa, eludir el sistema de pagos de Solva, acosar a otros usuarios, publicar contenido ilegal o inapropiado, crear múltiples cuentas y cualquier actividad fraudulenta.'],
          ['11. Responsabilidad', 'Solva no garantiza la calidad de los servicios prestados por los profesionales. La responsabilidad de Solva se limita al importe de la transacción en disputa. Solva no es responsable de daños indirectos o consecuentes.'],
          ['12. Ley Aplicable', 'Estos términos se rigen por la legislación belga. Cualquier disputa se someterá a los tribunales de Bruselas, Bélgica.'],
          ['13. Contacto', 'Para cualquier consulta sobre estos términos: legal@solva.app'],
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
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 20, paddingVertical: 14, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: 'rgba(0,0,0,0.05)' },
  backBtn: { width: 40, height: 40, borderRadius: 12, backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center' },
  headerTitle: { fontSize: 16, fontWeight: '700', color: '#1a1a2e' },
  scroll: { flex: 1 },
  content: { padding: 20, paddingBottom: 48 },
  meta: { fontSize: 12, color: '#9CA3AF', marginBottom: 16, fontStyle: 'italic' },
  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 15, fontWeight: '800', color: '#2563EB', marginBottom: 8 },
  sectionBody: { fontSize: 14, color: '#374151', lineHeight: 22 },
  footer: { fontSize: 12, color: '#9CA3AF', textAlign: 'center', marginTop: 16, fontStyle: 'italic' },
})
