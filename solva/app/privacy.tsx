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
          ['1. Responsable del Tratamiento', 'Solva SRL, empresa registrada en Bélgica, es la responsable del tratamiento de sus datos personales. Contacto del Delegado de Protección de Datos: privacy@getsolva.co'],
          ['2. Datos que Recopilamos', 'Recopilamos: (a) Datos de registro: nombre completo, email, número de teléfono, fecha de nacimiento, país; (b) Datos de verificación KYC: copia de documento de identidad, selfie con documento; (c) Datos de actividad: trabajos publicados, ofertas, contratos, mensajes, valoraciones; (d) Datos de pago: información de tarjeta procesada por Stripe (nunca almacenamos datos de tarjeta directamente); (e) Datos técnicos: dirección IP, dispositivo, sistema operativo, logs de acceso; (f) Datos de ubicación: coordenadas GPS para servicios geolocalizados (solo con consentimiento explícito).'],
          ['3. Finalidad del Tratamiento', 'Tratamos sus datos para: (a) Gestionar su cuenta y autenticación; (b) Facilitar la conexión entre clientes y profesionales; (c) Procesar pagos y gestionar el sistema de custodia; (d) Verificar identidades y prevenir fraude; (e) Enviar comunicaciones transaccionales (confirmaciones, notificaciones de pago, recordatorios); (f) Mejorar la plataforma mediante análisis agregados y anónimos; (g) Cumplir obligaciones legales y fiscales.'],
          ['4. Base Legal del Tratamiento', 'El tratamiento de sus datos se basa en: (a) Ejecución del contrato: datos necesarios para prestar el servicio; (b) Obligación legal: verificación KYC, cumplimiento fiscal, prevención de blanqueo; (c) Interés legítimo: seguridad de la plataforma, prevención de fraude; (d) Consentimiento: comunicaciones de marketing, geolocalización. Puede retirar su consentimiento en cualquier momento sin que ello afecte a la licitud del tratamiento previo.'],
          ['5. Conservación de Datos', 'Conservamos sus datos durante el tiempo necesario para los fines descritos: (a) Datos de cuenta: mientras mantenga su cuenta activa + 3 años tras la cancelación; (b) Documentos KYC: se eliminan tras la verificación exitosa, conservando solo el resultado; (c) Datos de transacciones: 7 años por obligaciones fiscales y legales; (d) Mensajes y contratos: 5 años desde la finalización del contrato; (e) Logs técnicos: 12 meses.'],
          ['6. Compartición de Datos', 'Compartimos sus datos únicamente con: (a) Stripe Inc.: procesamiento de pagos (certificado PCI DSS nivel 1); (b) Resend Inc.: envío de emails transaccionales; (c) Supabase Inc.: infraestructura de base de datos (servidores en la UE); (d) Autoridades competentes: cuando lo exija la ley o una orden judicial. No vendemos ni cedemos sus datos personales a terceros con fines comerciales.'],
          ['7. Transferencias Internacionales', 'Algunos de nuestros proveedores técnicos tienen sede en EE.UU. (Stripe, Supabase). Estas transferencias están amparadas por las Cláusulas Contractuales Tipo aprobadas por la Comisión Europea o por el marco EU-US Data Privacy Framework, garantizando un nivel de protección equivalente al europeo.'],
          ['8. Sus Derechos (RGPD)', 'Como titular de los datos, tiene derecho a: (a) Acceso: obtener confirmación y copia de sus datos; (b) Rectificación: corregir datos inexactos o incompletos; (c) Supresión ("derecho al olvido"): solicitar la eliminación de sus datos; (d) Limitación: restringir el tratamiento en determinadas circunstancias; (e) Portabilidad: recibir sus datos en formato estructurado; (f) Oposición: oponerse al tratamiento basado en interés legítimo; (g) Decisiones automatizadas: no ser objeto de decisiones basadas únicamente en tratamiento automatizado. Para ejercer estos derechos: privacy@getsolva.co'],
          ['9. Datos de Menores', 'Solva no está dirigida a menores de 18 años. No recopilamos conscientemente datos de menores. Si detectamos que un menor ha proporcionado datos sin consentimiento parental, los eliminaremos inmediatamente.'],
          ['10. Cookies y Tecnologías Similares', 'La versión web de Solva utiliza cookies técnicas esenciales para el funcionamiento de la autenticación y la sesión. No utilizamos cookies de seguimiento publicitario ni compartimos datos con redes publicitarias. La aplicación móvil no utiliza cookies.'],
          ['11. Seguridad', 'Implementamos medidas técnicas y organizativas para proteger sus datos: cifrado en tránsito (TLS 1.3), cifrado en reposo, autenticación de dos factores, acceso restringido por roles, auditorías de seguridad periódicas y políticas de respuesta ante incidentes. En caso de brecha de seguridad que afecte a sus datos, le notificaremos en un plazo máximo de 72 horas conforme al RGPD.'],
          ['12. Reclamaciones', 'Si considera que el tratamiento de sus datos vulnera la normativa, puede presentar reclamación ante la Autoridad de Protección de Datos de Bélgica (APD): www.autoriteprotectiondonnees.be | Rue de la Presse 35, 1000 Bruselas. También puede dirigirse a la autoridad de protección de datos de su país de residencia.'],
          ['13. Cambios en esta Política', 'Podemos actualizar esta Política de Privacidad. Le notificaremos los cambios significativos por email con al menos 30 días de antelación. La fecha de última actualización aparece al pie de este documento.'],
          ['14. Contacto', 'Para cualquier consulta sobre privacidad y protección de datos: privacy@getsolva.co | Solva SRL, Bruselas, Bélgica.']
        ]].map(([title, body], i) => (
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
