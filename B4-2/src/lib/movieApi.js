import { requireSupabase } from './supabase'

export async function getMovies() {
  const { data, error } = await requireSupabase().from('movies').select('*').order('created_at', { ascending: false })
  if (error) throw error
  return data
}

export async function getMovie(id) {
  const { data, error } = await requireSupabase().from('movies').select('*').eq('id', id).single()
  if (error) throw error
  return data
}

export async function createMovie(values) {
  const { data, error } = await requireSupabase().from('movies').insert(values).select().single()
  if (error) throw error
  return data
}

export async function updateMovie(id, values) {
  const { title, director, year, genre, rating, note } = values
  const updates = { title, director, year, genre, rating, note }
  const { data, error } = await requireSupabase().from('movies').update(updates).eq('id', id).select().single()
  if (error) throw error
  return data
}

export async function deleteMovie(id) {
  const { error } = await requireSupabase().from('movies').delete().eq('id', id)
  if (error) throw error
}
