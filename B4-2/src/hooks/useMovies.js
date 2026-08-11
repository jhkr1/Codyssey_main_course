import { useEffect, useState } from 'react'
import { getMovies } from '../lib/movieApi'

export function useMovies() {
  const [movies, setMovies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  async function fetchMovies() {
    setLoading(true); setError('')
    try { setMovies(await getMovies()) } catch (err) { setError(err.message || '목록을 불러오지 못했습니다.') } finally { setLoading(false) }
  }
  useEffect(() => { fetchMovies() }, [])
  const genres = [...new Set(movies.map(movie => movie.genre))]
  return { movies, genres, loading, error, refetch: fetchMovies }
}
