import { Link, useNavigate, useParams } from 'react-router-dom'
import { useState } from 'react'
import { deleteMovie } from '../lib/movieApi'
import { useMovie } from '../hooks/useMovie'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
import Rating from '../components/Rating'
import Button from '../components/Button'

export default function MovieDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { movie, loading, error, refetch } = useMovie(id)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')

  const remove = async () => {
    if (!confirm('이 기록을 삭제할까요?')) return

    setDeleting(true)
    setDeleteError('')
    try {
      await deleteMovie(id)
      navigate('/movies')
    } catch (err) {
      setDeleteError(err.message || '삭제에 실패했습니다. 잠시 후 다시 시도해주세요.')
    } finally {
      setDeleting(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} onRetry={refetch} />

  return <article className="detail"><Link className="back-link" to="/movies">← 기록 목록</Link><div className="detail__hero"><div className="detail__poster">{movie.title.slice(0, 1)}</div><div><p className="eyebrow">{movie.genre} · {movie.year || 'YEAR UNKNOWN'}</p><h1>{movie.title}</h1><p className="director">directed by {movie.director}</p><Rating value={movie.rating} /></div></div><div className="detail__note"><span>MY NOTE</span><p>“{movie.note}”</p></div>{deleteError && <div className="notice" role="alert">{deleteError}</div>}<div className="detail__actions"><Link to={`/movies/${id}/edit`}><Button variant="ghost">수정하기</Button></Link><Button variant="danger" loading={deleting} onClick={remove}>삭제하기</Button></div></article>
}
