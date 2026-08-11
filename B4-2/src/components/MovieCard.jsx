import { Link } from 'react-router-dom'
import Rating from './Rating'
export default function MovieCard({ movie }) { return <Link className="movie-card" to={`/movies/${movie.id}`}><div className="movie-card__poster">{movie.title.slice(0, 1)}</div><div className="movie-card__body"><span className="eyebrow">{movie.genre} · {movie.year || 'YEAR'}</span><h3>{movie.title}</h3><p>{movie.director}</p><Rating value={movie.rating} /></div><span className="arrow">→</span></Link> }
