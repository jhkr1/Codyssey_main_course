import { useItems } from '../hooks/useItems';
import { Link } from 'react-router-dom';

export const ItemList = () => {
  const { items, loading, error } = useItems();

  if (loading) return <div>로딩 중...</div>;
  if (error) return <div>에러 발생: {error}</div>;
  if (items.length === 0) return <div>표시할 데이터가 없습니다.</div>;

  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>
          <Link to={`/items/${item.id}`}>{item.title}</Link>
        </li>
      ))}
    </ul>
  );
};