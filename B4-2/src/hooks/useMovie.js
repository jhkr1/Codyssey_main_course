import { useEffect, useState } from 'react'
import { getMovie } from '../lib/movieApi'

export function useMovie(id, enabled = true) {
  const [movie, setMovie] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('')
  async function fetchMovie() { setLoading(true); setError(''); try { setMovie(await getMovie(id)) } catch (err) { setError(err.message || '기록을 불러오지 못했습니다.') } finally { setLoading(false) } }
  useEffect(() => { if (enabled) fetchMovie(); else setLoading(false) }, [id, enabled])
  return { movie, loading, error, refetch: fetchMovie }
}
