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
          ['1. Partes del Contrato', 'El presente contrato se establece entre Solva SRL, empresa registrada en Belgica, y el usuario registrado en la plataforma. Al crear una cuenta, el Usuario acepta integramente estos Terminos de Servicio.'],
          ['2. Descripcion del Servicio', 'Solva es una plataforma digital de intermediacion que conecta clientes con profesionales independientes de servicios del hogar. Solva actua exclusivamente como intermediario tecnologico y no es empleador ni contratista de los profesionales registrados.'],
          ['3. Elegibilidad y Registro', 'Para registrarse el Usuario debe: tener al menos 18 anos; capacidad legal para contratar; proporcionar informacion veraz y actualizada; mantener la confidencialidad de sus credenciales. Solva puede suspender cuentas que incumplan estos requisitos.'],
          ['4. Verificacion de Identidad KYC', 'Para acceder a todas las funcionalidades, especialmente publicar trabajos y recibir pagos, el Usuario debera verificar su identidad mediante documento oficial vigente. Los documentos se procesan conforme al RGPD UE 2016/679 y se eliminan tras la verificacion.'],
          ['5. Publicacion de Trabajos y Ofertas', 'Los clientes publican trabajos especificando descripcion, categoria, presupuesto y ubicacion. Los profesionales envian ofertas con precio, plazo y mensaje. El cliente puede aceptar, rechazar o ignorar cualquier oferta.'],
          ['6. Contratos Digitales', 'La aceptacion de una oferta genera automaticamente un contrato digital vinculante entre cliente y profesional. Cualquier modificacion posterior requiere acuerdo expreso de ambas partes a traves de la plataforma.'],
          ['7. Sistema de Pago en Custodia Escrow', 'Los pagos se procesan mediante el sistema de custodia de Solva operado a traves de Stripe (certificado PCI DSS). El cliente deposita el importe antes del inicio; el dinero queda retenido en custodia; al confirmar la finalizacion el cliente libera el pago; el profesional recibe el importe en su cuenta bancaria.'],
          ['8. Comisiones y Tarifas', 'Solva cobra una comision del 10% sobre el valor bruto de cada transaccion completada. Esta comision se deduce automaticamente del pago al profesional. Ejemplo: trabajo de 100 EUR, profesional recibe 90 EUR, Solva retiene 10 EUR. Las tarifas pueden modificarse con 30 dias de preaviso.'],
          ['9. Cancelaciones y Reembolsos', 'Cancelacion antes de aceptacion: sin coste. Cancelacion tras aceptacion: segun politica del contrato. Cancelacion por el profesional: reembolso integro al cliente. En caso de trabajo no realizado, Solva gestionara el reembolso previa investigacion.'],
          ['10. Sistema de Disputas', 'Cualquier parte puede abrir una disputa. Solva mediara y si no hay acuerdo en 7 dias habiles emitira una resolucion vinculante basada en evidencias. La decision de Solva es definitiva en el marco de la plataforma.'],
          ['11. Valoraciones y Resenas', 'Tras completar un trabajo, ambas partes pueden valorarse con puntuacion de 1 a 5 estrellas y comentario. Las valoraciones deben basarse en experiencias reales. Solva puede eliminar valoraciones que incumplan estas normas.'],
          ['12. Conducta Prohibida', 'Queda prohibido: proporcionar informacion falsa; acordar pagos fuera de la plataforma; crear multiples cuentas; acosar o discriminar usuarios; publicar contenido ilegal; comprometer la seguridad de la plataforma. El incumplimiento puede resultar en suspension inmediata.'],
          ['13. Propiedad Intelectual', 'Todos los derechos de propiedad intelectual de Solva son propiedad de Solva SRL. Los usuarios conceden a Solva una licencia no exclusiva para usar el contenido que publiquen con fines operativos.'],
          ['14. Limitacion de Responsabilidad', 'Solva no garantiza la calidad de los servicios de los profesionales. La responsabilidad maxima de Solva se limita al importe de la transaccion en disputa. Solva no sera responsable de danos indirectos o lucro cesante.'],
          ['15. Modificaciones y Terminacion', 'Solva puede modificar estos Terminos con 30 dias de preaviso. El uso continuado implica aceptacion. Solva puede suspender cuentas por incumplimiento, actividad fraudulenta o inactividad prolongada.'],
          ['16. Ley Aplicable y Jurisdiccion', 'Estos Terminos se rigen por la legislacion belga. Las disputas se someteran a los tribunales de Bruselas, sin perjuicio de los derechos del consumidor en su pais de residencia.'],
          ['17. Contacto Legal', 'Para consultas sobre estos Terminos o ejercicio de derechos: legal@getsolva.co | Solva SRL, Bruselas, Belgica.'],
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
