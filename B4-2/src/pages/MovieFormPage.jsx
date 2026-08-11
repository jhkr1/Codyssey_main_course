import { useNavigate, useParams } from 'react-router-dom'
import { useState } from 'react'
import { createMovie, updateMovie } from '../lib/movieApi'
import { useMovie } from '../hooks/useMovie'
import MovieForm from '../components/MovieForm'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
export default function MovieFormPage({ edit = false }) { const { id } = useParams(); const navigate = useNavigate(); const { movie, loading, error, refetch } = useMovie(id, edit); const [submitting, setSubmitting] = useState(false); const [submitError, setSubmitError] = useState(''); const save = async values => { setSubmitting(true); setSubmitError(''); try { const result = edit ? await updateMovie(id, values) : await createMovie(values); navigate(`/movies/${result.id}`) } catch (err) { setSubmitError(err.message || '저장에 실패했습니다. 잠시 후 다시 시도해주세요.') } finally { setSubmitting(false) } }; if (edit && loading) return <Loading />; if (edit && error) return <ErrorState message={error} onRetry={refetch} />; return <section className="form-page"><p className="eyebrow">{edit ? 'REFINE YOUR MEMORY' : 'ADD TO ARCHIVE'}</p><h1>{edit ? '기록 다듬기' : '새 영화 기록'}</h1><p className="page-intro">영화가 끝난 직후의 감정을 놓치지 말고 적어보세요.</p>{submitError && <div className="notice">{submitError}</div>}<MovieForm movie={edit ? movie : null} onSubmit={save} submitting={submitting} /></section> }
