import { supabase } from '../lib/supabase'
import { getContractTerms } from '../lib/contracts/templates'
import { SupportedCountry, SupportedCurrency } from '../lib/supabase'

interface CreateContractParams {
  jobId: string
  bidId: string
  clientId: string
  proId: string
  amount: number
  currency: SupportedCurrency
  country: SupportedCountry
  deliveryDays?: number | null
}

export async function createContract(params: CreateContractParams) {
  const terms = getContractTerms(params.country)
  const dueDate = params.deliveryDays
    ? new Date(Date.now() + params.deliveryDays * 86400000).toISOString()
    : null

  // Calcula cobertura máxima según país
  const { data: coverageData } = await supabase.rpc('get_guarantee_coverage', {
    country: params.country,
    amount: params.amount,
  })
  const maxCoverage = coverageData ?? 0

  const { data, error } = await supabase.from('contracts').insert({
    job_id: params.jobId,
    bid_id: params.bidId,
    client_id: params.clientId,
    pro_id: params.proId,
    amount: params.amount,
    currency: params.currency,
    country: params.country,
    delivery_days: params.deliveryDays ?? null,
    due_date: dueDate,
    terms,
  }).select().single()

  // Crea garantía automáticamente (expira en 7 días tras completar)
  if (data && !error) {
    const expiresAt = new Date(Date.now() + 7 * 86400000).toISOString()
    await supabase.from('guarantees').insert({
      contract_id: data.id,
      client_id: params.clientId,
      status: 'active',
      max_coverage: maxCoverage,
      currency: params.currency,
      country: params.country,
      expires_at: expiresAt,
    })
  }

  return { data, error }
}

export async function getContract(jobId: string) {
  const { data, error } = await supabase
    .from('contracts')
    .select('*')
    .eq('job_id', jobId)
    .single()
  return { data, error }
}
