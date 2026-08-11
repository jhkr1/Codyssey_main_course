export default function Loading({ message = '기록을 불러오는 중이에요' }) { return <div className="status"><i className="spinner" /><p>{message}</p></div> }
