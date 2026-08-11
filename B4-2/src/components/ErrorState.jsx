import Button from './Button'
export default function ErrorState({ message = '요청에 실패했습니다.', onRetry }) { return <div className="status status--error"><strong>잠시 문제가 생겼어요</strong><p>{message}</p>{onRetry && <Button variant="ghost" onClick={onRetry}>다시 시도</Button>}</div> }
