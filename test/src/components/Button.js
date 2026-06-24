export const Button = ({ children, onClick, disabled, type = "button" }) => (
  <button type={type} onClick={onClick} disabled={disabled} className="btn">
    {disabled ? '처리 중...' : children}
  </button>
);