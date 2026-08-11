import { NavLink, Link } from 'react-router-dom'
import Button from './Button'
export default function Header() { return <header className="header"><Link to="/" className="logo">scene<span>log</span></Link><nav><NavLink to="/" end>홈</NavLink><NavLink to="/movies">내 기록</NavLink><NavLink to="/about">소개</NavLink></nav><Link to="/movies/new"><Button>+ 새 기록</Button></Link></header> }
