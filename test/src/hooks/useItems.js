import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';

export const useItems = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchItems = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase.from('items').select('*');
      if (error) throw error;
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchItems(); }, []);
  return { items, loading, error, refetch: fetchItems };
};