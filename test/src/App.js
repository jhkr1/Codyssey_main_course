import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ItemList } from './pages/ItemList';
import { ItemForm } from './pages/ItemForm';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <a href="/items">목록</a> | <a href="/items/new">등록</a>
      </nav>
      <Routes>
        <Route path="/items" element={<ItemList />} />
        <Route path="/items/new" element={<ItemForm />} />
        <Route path="*" element={<div>404 Not Found</div>} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;