import { ScrollView, View, Text, StyleSheet, TouchableOpacity } from 'react-native'
import { router } from 'expo-router'
import { useSafeAreaInsets } from 'react-native-safe-area-context'
import Svg, { Path } from 'react-native-svg'

export default function PrivacyScreen() {
  const insets = useSafeAreaInsets()
  return (
    <View style={[s.screen, { paddingTop: insets.top }]}>
      <View style={s.header}>
        <TouchableOpacity style={s.backBtn} onPress={() => router.back()}>
          <Svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <Path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="#1a1a2e" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </Svg>
        </TouchableOpacity>
        <Text style={s.headerTitle}>Política de Privacidad</Text>
        <View style={{ width: 40 }} />
      </View>
      <ScrollView style={s.scroll} contentContainerStyle={s.content} showsVerticalScrollIndicator={false}>
        <Text style={s.meta}>Versión 1.0 — Marzo 2026 | Conforme al RGPD (UE) 2016/679</Text>

        {[
          ['1. Responsable del Tratamiento', 'Solva Platform (en constitución), Bélgica.\nContacto: legal@solva.app\nDelegado de Protección de Datos: dpo@solva.app'],
          ['2. Datos que Recopilamos', 'Datos de registro: nombre, email, país, rol, fecha de registro.\n\nDatos de uso: publicaciones, ofertas, contratos, mensajes, reseñas con fotos antes/después, historial de transacciones, geolocalización aproximada.\n\nDatos KYC: documento de identidad, selfie con documento, comprobante de domicilio. Almacenados con encriptación.\n\nDatos de pago: procesados por Stripe. Solva no almacena datos bancarios completos.'],
          ['3. Base Legal del Tratamiento', 'Ejecución de contrato (Art. 6.1.b RGPD): gestión de cuenta, contratos y pagos.\nInterés legítimo (Art. 6.1.f RGPD): seguridad y prevención del fraude.\nObligación legal (Art. 6.1.c RGPD): normativa fiscal y AML belga.\nConsentimiento (Art. 6.1.a RGPD): comunicaciones de marketing.'],
          ['4. Finalidades', 'Crear y gestionar tu cuenta, facilitar la contratación de servicios, procesar pagos en escrow, verificar identidad (KYC), gestionar disputas, enviar notificaciones de transacciones y cumplir obligaciones legales en Bélgica y la UE.'],
          ['5. Destinatarios', 'Stripe Inc. — procesamiento de pagos (PCI-DSS).\nSupabase Inc. — infraestructura de base de datos (servidores en EU).\nAutoridades competentes belgas — cuando sea requerido por ley.\nEl otro usuario del contrato activo — solo nombre y mensajes del contrato.\n\nNo vendemos ni cedemos tus datos a terceros con fines publicitarios.'],
          ['6. Plazos de Retención', 'Datos de cuenta activa: durante la vigencia.\nTransacciones y contratos: 7 años (obligación fiscal belga).\nDocumentos KYC: 5 años tras el cierre de cuenta (Ley AML belga).\nMensajes de chat: 2 años tras finalización del contrato.\nMarketing: hasta retirada del consentimiento.'],
          ['7. Tus Derechos (RGPD)', 'Tienes derecho a: acceso, rectificación, supresión ("derecho al olvido"), limitación del tratamiento, portabilidad de datos, oposición al tratamiento, y retirar el consentimiento en cualquier momento.\n\nPara ejercer tus derechos: legal@solva.app\nRespondemos en máximo 30 días (Art. 12 RGPD).\n\nSi consideras que tu solicitud no fue atendida: Autoridad de Protección de Datos belga (APD/GBA) — autoriteprotectiondonnees.be'],
          ['8. Cookies', 'Esenciales (sin consentimiento): sesión de usuario, preferencias de idioma.\nAnalíticas (con consentimiento): análisis de uso anonimizado.\n\nPuedes gestionar tus preferencias desde la configuración de tu cuenta.'],
          ['9. Seguridad', 'Encriptación TLS 1.3 en todas las comunicaciones, AES-256 para datos sensibles en reposo, control de acceso por roles (RLS), auditorías de seguridad periódicas y monitorización 24/7.'],
          ['10. Menores de Edad', 'Solva no está dirigida a menores de 18 años. Si detectamos que un menor ha creado una cuenta, eliminaremos sus datos inmediatamente. Contáctanos en legal@solva.app si tienes conocimiento de ello.'],
          ['11. Cambios en esta Política', 'Notificaremos cualquier cambio material con al menos 30 días de antelación por correo electrónico. El uso continuado de la plataforma implica la aceptación de los cambios.'],
          ['12. Contacto', 'Consultas de privacidad: legal@solva.app\nDelegado de Protección de Datos: dpo@solva.app\nAutoridad de supervisión belga: APD/GBA — autoriteprotectiondonnees.be'],
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
