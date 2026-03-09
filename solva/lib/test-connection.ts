import { supabase } from './supabase'

export async function testConnection() {
  const { data, error } = await supabase
    .from('users')
    .select('id')
    .limit(1)

  if (error) {
    console.log('❌ Error:', error.message)
    return false
  }

  console.log('✅ Conexión exitosa con Supabase')
  return true
}
