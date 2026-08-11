import { Link } from 'react-router-dom'
import Button from '../components/Button'
import EmptyState from '../components/EmptyState'
import ErrorState from '../components/ErrorState'
import Loading from '../components/Loading'
import MovieList from '../components/MovieList'
import { useMovies } from '../hooks/useMovies'

export default function HomePage() {
  const { movies, loading, error, refetch } = useMovies()

  return <><section className="hero"><p className="eyebrow">YOUR PERSONAL CINEMA ARCHIVE</p><h1>좋았던 장면은<br /><em>오래 기록될수록</em> 선명해져요.</h1><p className="hero__copy">그때의 영화와 감정을 나만의 언어로 모아보세요.</p><Link to="/movies/new"><Button>오늘의 영화 기록하기 →</Button></Link></section><section className="section"><div className="section-title"><div><p className="eyebrow">RECENTLY WATCHED</p><h2>최근 기록</h2></div><Link to="/movies">모두 보기 →</Link></div>{loading ? <Loading /> : error ? <ErrorState message={error} onRetry={refetch} /> : movies.length ? <MovieList movies={movies.slice(0, 3)} /> : <EmptyState title="아직 기록한 영화가 없어요" description="첫 번째 영화와 그때의 감상을 남겨보세요." />}</section></>
}
