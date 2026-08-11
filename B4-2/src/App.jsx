import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import MoviesPage from './pages/MoviesPage'
import MovieDetailPage from './pages/MovieDetailPage'
import MovieFormPage from './pages/MovieFormPage'
import AboutPage from './pages/AboutPage'
import NotFoundPage from './pages/NotFoundPage'
export default function App() { return <Routes><Route element={<Layout />}><Route path="/" element={<HomePage />} /><Route path="/movies" element={<MoviesPage />} /><Route path="/movies/new" element={<MovieFormPage />} /><Route path="/movies/:id" element={<MovieDetailPage />} /><Route path="/movies/:id/edit" element={<MovieFormPage edit />} /><Route path="/about" element={<AboutPage />} /><Route path="*" element={<NotFoundPage />} /></Route></Routes> }
