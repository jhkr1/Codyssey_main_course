export default function Input({ label, error, as = 'input', ...props }) {
  const Field = as
  return <label className="field"><span>{label}</span><Field className={error ? 'field__control is-error' : 'field__control'} {...props} />{error && <small className="field__error">{error}</small>}</label>
}
