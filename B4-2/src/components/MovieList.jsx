import MovieCard from './MovieCard'
export default function MovieList({ movies }) { return <section className="movie-grid">{movies.map(movie => <MovieCard key={movie.id} movie={movie} />)}</section> }
