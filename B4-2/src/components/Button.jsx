export default function Button({ children, variant = 'primary', loading = false, className = '', ...props }) {
  return <button className={`button button--${variant} ${className}`} disabled={loading || props.disabled} {...props}>{loading ? '처리 중…' : children}</button>
}
