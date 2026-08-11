import { createClient } from '@supabase/supabase-js'

const url = import.meta.env.VITE_SUPABASE_URL
const key = import.meta.env.VITE_SUPABASE_ANON_KEY
export const isSupabaseConfigured = Boolean(url && key)
export const supabase = isSupabaseConfigured ? createClient(url, key) : null

export function requireSupabase() {
  if (!supabase) {
    throw new Error('Supabase 설정이 없습니다. VITE_SUPABASE_URL과 VITE_SUPABASE_ANON_KEY를 .env에 설정한 뒤 개발 서버를 다시 시작해주세요.')
  }

  return supabase
}
