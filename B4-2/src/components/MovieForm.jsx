import { useState } from 'react'
import Button from './Button'
import Input from './Input'
import Rating from './Rating'

const initial = { title: '', director: '', year: '', genre: 'Drama', rating: 3, note: '' }

export default function MovieForm({ movie, onSubmit, submitting }) {
  const [values, setValues] = useState(movie ? {
    title: movie.title,
    director: movie.director,
    year: movie.year || '',
    genre: movie.genre,
    rating: movie.rating,
    note: movie.note
  } : initial)
  const [errors, setErrors] = useState({})

  const change = event => setValues(prev => ({ ...prev, [event.target.name]: event.target.value }))

  const submit = async event => {
    event.preventDefault()
    const next = {}
    if (!values.title.trim()) next.title = '제목을 입력해주세요.'
    if (!values.director.trim()) next.director = '감독을 입력해주세요.'
    if (!values.note.trim()) next.note = '한 줄 감상을 입력해주세요.'
    setErrors(next)
    if (Object.keys(next).length) return

    await onSubmit({ ...values, year: values.year ? Number(values.year) : null })
  }

  return <form className="movie-form" onSubmit={submit}><div className="form-grid"><Input label="영화 제목 *" name="title" value={values.title} onChange={change} error={errors.title} placeholder="예: Past Lives" /><Input label="감독 *" name="director" value={values.director} onChange={change} error={errors.director} placeholder="감독 이름" /><Input label="개봉 연도" name="year" type="number" value={values.year} onChange={change} placeholder="2026" /><label className="field"><span>장르 *</span><select className="field__control" name="genre" value={values.genre} onChange={change}><option>Drama</option><option>Romance</option><option>Comedy</option><option>Action</option><option>Sci-Fi</option><option>Documentary</option></select></label></div><label className="field"><span>나의 평점</span><Rating interactive value={Number(values.rating)} onChange={rating => setValues(prev => ({ ...prev, rating }))} /></label><Input label="한 줄 감상 *" name="note" as="textarea" rows="5" value={values.note} onChange={change} error={errors.note} placeholder="이 영화가 남긴 장면과 감정을 적어보세요." /><div className="form-actions"><Button type="submit" loading={submitting}>{movie ? '수정 완료' : '기록 저장'}</Button></div></form>
}
