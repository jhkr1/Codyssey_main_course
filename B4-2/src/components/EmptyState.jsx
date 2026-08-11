import { Link } from 'react-router-dom'
export default function EmptyState({ title = '아직 기록이 없어요', description = '첫 번째 영화를 남겨보세요.', action = true }) { return <div className="status"><span className="empty-icon">✦</span><strong>{title}</strong><p>{description}</p>{action && <Link className="button button--primary" to="/movies/new">기록 시작하기</Link>}</div> }
