import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMovies } from '../hooks/useMovies'
import MovieList from '../components/MovieList'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'
export default function MoviesPage() { const { movies, genres, loading, error, refetch } = useMovies(); const [genre, setGenre] = useState('All'); const filtered = genre === 'All' ? movies : movies.filter(movie => movie.genre === genre); return <><div className="page-heading"><div><p className="eyebrow">MY CINEMA ARCHIVE</p><h1>영화 기록</h1><p>마음에 남은 순간들을 다시 꺼내보세요.</p></div><Link className="button button--primary" to="/movies/new">+ 새 기록</Link></div><div className="filters"><button className={genre === 'All' ? 'selected' : ''} onClick={() => setGenre('All')}>전체 <b>{movies.length}</b></button>{genres.map(item => <button key={item} className={genre === item ? 'selected' : ''} onClick={() => setGenre(item)}>{item}</button>)}</div>{loading ? <Loading /> : error ? <ErrorState message={error} onRetry={refetch} /> : filtered.length ? <MovieList movies={filtered} /> : <EmptyState title="이 장르의 기록은 없어요" description="다른 필터를 선택하거나 새 영화를 기록해보세요." action={false} />}</> }
