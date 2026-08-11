export default function Rating({ value, interactive = false, onChange }) { return <div className={interactive ? 'rating rating--interactive' : 'rating'} aria-label={`${value}점`}>
  {[1, 2, 3, 4, 5].map(star => <button key={star} type="button" disabled={!interactive} onClick={() => onChange?.(star)} className={star <= value ? 'active' : ''}>★</button>)}
</div> }
