import { SupportedCountry } from '../supabase'

export interface ContractTerms {
  country: SupportedCountry
  language: string
  law: string
  jurisdiction: string
  payment_protection: string
  cancellation_policy: string
  dispute_resolution: string
  warranty_days: number
  platform_fee_pct: number
}

export const CONTRACT_TEMPLATES: Record<SupportedCountry, ContractTerms> = {
  ES: {
    country: 'ES',
    language: 'es-ES',
    law: 'Ley Orgánica 3/2018 (LOPD) y legislación civil española',
    jurisdiction: 'España',
    payment_protection: 'El pago queda retenido en escrow hasta confirmación de entrega',
    cancellation_policy: 'Cancelación gratuita hasta 24h antes del inicio del servicio',
    dispute_resolution: 'Mediación a través de Solva. En caso de no resolución: arbitraje según normativa española',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  FR: {
    country: 'FR',
    language: 'es',
    law: 'Code Civil français et RGPD',
    jurisdiction: 'France',
    payment_protection: 'Paiement conservé en séquestre jusqu\'à confirmation de livraison',
    cancellation_policy: 'Annulation gratuite jusqu\'à 24h avant le début du service',
    dispute_resolution: 'Médiation via Solva. En cas de non-résolution: arbitrage selon droit français',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  MX: {
    country: 'MX',
    language: 'es',
    law: 'Código Civil Federal mexicano y Ley Federal de Protección de Datos',
    jurisdiction: 'México',
    payment_protection: 'El pago queda retenido en escrow hasta confirmación de entrega',
    cancellation_policy: 'Cancelación gratuita hasta 24h antes del inicio del servicio',
    dispute_resolution: 'Mediación a través de Solva. En caso de no resolución: PROFECO o arbitraje civil',
    warranty_days: 5,
    platform_fee_pct: 10,
  },
  CO: {
    country: 'CO',
    language: 'es',
    law: 'Código Civil colombiano y Ley 1581 de 2012',
    jurisdiction: 'Colombia',
    payment_protection: 'El pago queda retenido en escrow hasta confirmación de entrega',
    cancellation_policy: 'Cancelación gratuita hasta 24h antes del inicio del servicio',
    dispute_resolution: 'Mediación a través de Solva. En caso de no resolución: SIC o arbitraje civil',
    warranty_days: 5,
    platform_fee_pct: 10,
  },
  AR: {
    country: 'AR',
    language: 'es',
    law: 'Código Civil y Comercial argentino y Ley 25.326',
    jurisdiction: 'Argentina',
    payment_protection: 'El pago queda retenido en escrow hasta confirmación de entrega',
    cancellation_policy: 'Cancelación gratuita hasta 24h antes del inicio del servicio',
    dispute_resolution: 'Mediación a través de Solva. En caso de no resolución: arbitraje según normativa argentina',
    warranty_days: 5,
    platform_fee_pct: 10,
  },
  BR: {
    country: 'BR',
    language: 'pt-BR',
    law: 'Código Civil brasileiro, CDC e LGPD',
    jurisdiction: 'Brasil',
    payment_protection: 'O pagamento fica retido em escrow até confirmação de entrega',
    cancellation_policy: 'Cancelamento gratuito até 24h antes do início do serviço',
    dispute_resolution: 'Mediação via Solva. Em caso de não resolução: arbitragem conforme lei brasileira',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  BE: {
    country: 'BE',
    language: 'es',
    law: 'Code civil belge et RGPD',
    jurisdiction: 'Belgique',
    payment_protection: "Le paiement est conservé en séquestre jusqu'à confirmation de livraison",
    cancellation_policy: "Annulation gratuite jusqu'à 24h avant le début du service",
    dispute_resolution: "Médiation via Solva. En cas de non-résolution: arbitrage selon droit belge",
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  NL: {
    country: 'NL',
    language: 'es',
    law: 'Burgerlijk Wetboek en AVG/GDPR',
    jurisdiction: 'Nederland',
    payment_protection: 'Betaling wordt in escrow gehouden tot bevestiging van levering',
    cancellation_policy: 'Gratis annulering tot 24 uur voor aanvang van de dienst',
    dispute_resolution: 'Bemiddeling via Solva. Bij geen oplossing: arbitrage volgens Nederlands recht',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  DE: {
    country: 'DE',
    language: 'es',
    law: 'Bürgerliches Gesetzbuch (BGB) und DSGVO',
    jurisdiction: 'Deutschland',
    payment_protection: 'Zahlung wird im Treuhandkonto bis zur Lieferungsbestätigung gehalten',
    cancellation_policy: 'Kostenlose Stornierung bis 24h vor Dienstleistungsbeginn',
    dispute_resolution: 'Mediation über Solva. Bei Nichtlösung: Schiedsverfahren nach deutschem Recht',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  PT: {
    country: 'PT',
    language: 'es',
    law: 'Código Civil português e RGPD',
    jurisdiction: 'Portugal',
    payment_protection: 'O pagamento fica retido em escrow até confirmação de entrega',
    cancellation_policy: 'Cancelamento gratuito até 24h antes do início do serviço',
    dispute_resolution: 'Mediação via Solva. Em caso de não resolução: arbitragem segundo direito português',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  IT: {
    country: 'IT',
    language: 'es',
    law: 'Codice Civile italiano e GDPR',
    jurisdiction: 'Italia',
    payment_protection: 'Il pagamento è trattenuto in escrow fino alla conferma di consegna',
    cancellation_policy: "Cancellazione gratuita fino a 24 ore prima dell'inizio del servizio",
    dispute_resolution: "Mediazione tramite Solva. In caso di mancata risoluzione: arbitrato secondo diritto italiano",
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  GB: {
    country: 'GB',
    language: 'es',
    law: 'UK Contract Law and UK GDPR',
    jurisdiction: 'United Kingdom',
    payment_protection: 'Payment is held in escrow until delivery confirmation',
    cancellation_policy: 'Free cancellation up to 24h before service start',
    dispute_resolution: 'Mediation via Solva. If unresolved: arbitration under UK law',
    warranty_days: 7,
    platform_fee_pct: 10,
  },
  CL: {
    country: 'CL',
    language: 'es',
    law: 'Código Civil chileno y Ley 19.628',
    jurisdiction: 'Chile',
    payment_protection: 'El pago queda retenido en escrow hasta confirmación de entrega',
    cancellation_policy: 'Cancelación gratuita hasta 24h antes del inicio del servicio',
    dispute_resolution: 'Mediación a través de Solva. En caso de no resolución: arbitraje según normativa chilena',
    warranty_days: 5,
    platform_fee_pct: 10,
  },
}

export function getContractTerms(country: SupportedCountry): ContractTerms {
  return CONTRACT_TEMPLATES[country] ?? CONTRACT_TEMPLATES['ES']
}
