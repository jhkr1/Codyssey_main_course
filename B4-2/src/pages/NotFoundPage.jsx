import { Link } from 'react-router-dom'
export default function NotFoundPage() { return <div className="status"><span className="empty-icon">404</span><strong>이 장면은 찾을 수 없어요</strong><p>주소를 다시 확인해주세요.</p><Link className="button button--primary" to="/">홈으로 돌아가기</Link></div> }
