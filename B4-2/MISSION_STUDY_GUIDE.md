# React SPA 미션 학습서

> 주제: 버튼을 누르면 화면이 바뀌는 웹사이트는 어떤 원리로 움직일까?
>
> 범위: React 컴포넌트, 상태, 이벤트, 라우팅, 비동기 데이터, Supabase CRUD, 폼 UX. 보너스 과제인 전역 상태·성능 최적화·인증은 다루지 않는다.

---

## 0. 이 미션을 한 문장으로 이해하기

이 미션은 **사용자 행동이 상태를 바꾸고, React가 바뀐 상태를 기준으로 화면을 다시 그리는 SPA**를 만드는 과제다.

SceneLog를 예로 들면 사용자가 `새 기록` 버튼을 누르고 제목을 입력한 뒤 저장할 때, 화면에서 일어나는 일은 아래와 같다.

```text
클릭 / 입력 / 제출
  → 이벤트 핸들러 실행
  → state 변경 또는 Supabase 요청
  → React re-render
  → 바뀐 화면 표시 또는 다음 주소로 이동
```

React 개발에서 가장 중요한 질문은 늘 두 가지다.

1. **이 값은 누가 바꿀 수 있는가?** → state가 있어야 할 위치를 정한다.
2. **값이 바뀌면 어느 화면이 바뀌어야 하는가?** → 컴포넌트와 props의 흐름을 정한다.

---

## 1. SPA와 React의 역할

### 1.1 SPA란 무엇인가

SPA(Single Page Application)는 페이지를 옮길 때 서버에서 HTML 문서 전체를 다시 받는 대신, 처음 받은 JavaScript가 필요한 화면 부분만 교체하는 웹 애플리케이션이다.

`/movies`에서 영화 카드를 누르면 브라우저 주소는 `/movies/1`로 바뀐다. 하지만 일반적으로 문서 전체를 새로고침하지 않는다. React Router가 주소를 보고 `MovieDetailPage` 컴포넌트를 렌더링한다.

```text
주소 변경 → React Router가 라우트 확인 → 해당 Page 컴포넌트 렌더링
```

SPA라고 해서 서버가 필요 없다는 뜻은 아니다. 화면을 만드는 일은 React가, 영화 데이터를 저장하고 가져오는 일은 Supabase가 담당한다.

### 1.2 React가 필요한 이유

순수 JavaScript로 화면을 만들면 다음을 직접 관리해야 한다.

- 입력창 값이 바뀌면 어떤 DOM을 바꿀지
- 목록 데이터가 달라지면 카드를 어떻게 추가/제거할지
- 로딩 중일 때 기존 화면을 무엇으로 바꿀지

React는 이 과정을 선언적으로 바꾼다. 개발자는 “현재 데이터가 이렇다면 화면은 이렇게 보인다”라고 JSX로 작성한다. 데이터(state)가 바뀌면 React가 이전 화면과 비교해 필요한 DOM만 갱신한다.

```jsx
// movies 값이 바뀌면 이 목록도 자동으로 다시 계산되어 화면에 반영된다.
{movies.map((movie) => <MovieCard key={movie.id} movie={movie} />)}
```

### 1.3 컴포넌트란 무엇인가

컴포넌트는 UI와 그 UI에 필요한 동작을 한 덩어리로 묶은 함수다. 대문자로 시작하며 JSX를 반환한다.

```jsx
function Greeting({ name }) {
  return <p>{name}님, 반가워요.</p>
}
```

`Greeting`은 `name`이라는 props를 받아 다른 문구를 표시할 수 있다. 이렇게 한 번 만든 컴포넌트를 여러 화면에서 재사용한다.

---

## 2. 컴포넌트를 나누는 기준

### 2.1 Page와 UI 컴포넌트의 차이

이 프로젝트는 역할별로 폴더를 나눈다.

```text
src/
 ├─ pages/       주소 하나에 대응하는 큰 화면
 ├─ components/  여러 화면에서 조합해 쓰는 UI
 ├─ hooks/       데이터 요청과 상태 로직 재사용
 └─ lib/         Supabase 연결, API 함수 등 UI와 무관한 코드
```

| 종류 | 책임 | 예시 |
| --- | --- | --- |
| Page | 라우트 단위 화면 구성, 페이지 수준 상태 연결 | `MoviesPage`, `MovieDetailPage` |
| UI 컴포넌트 | 반복되는 UI와 작은 상호작용 | `Button`, `Input`, `MovieCard` |
| Custom Hook | 데이터 요청·로딩·오류 같은 상태 로직 | `useMovies`, `useMovie` |
| lib | 원격 DB와 통신하는 함수 | `getMovies`, `createMovie` |

### 2.2 언제 분리하는가

다음 중 하나에 해당하면 컴포넌트로 분리할 좋은 신호다.

- 같은 UI 패턴을 2곳 이상에서 쓴다. (`Loading`, `ErrorState`)
- 한 부분을 props만 바꿔 재사용할 수 있다. (`Button`의 `variant`, `loading`)
- 이름을 붙이면 역할이 명확해진다. (`MovieForm`, `MovieList`)
- Page 코드가 데이터 요청, 폼, 카드 마크업 때문에 너무 길어진다.

반대로 한 페이지에서 단 한 번만 쓰고 너무 단순한 마크업이라면 분리하지 않아도 된다. “파일 개수”가 목적이 아니라 **읽기 쉬운 책임 분리**가 목적이다.

### 2.3 이 프로젝트의 재사용 컴포넌트

| 컴포넌트 | 받는 props 예시 | 재사용 이유 |
| --- | --- | --- |
| `Button` | `variant`, `loading`, `children` | 버튼 스타일과 진행 상태 통일 |
| `Input` | `label`, `error`, `as` | 입력창/오류 표시 패턴 통일 |
| `Loading` | `message` | 모든 로딩 화면의 일관성 |
| `ErrorState` | `message`, `onRetry` | 실패 화면과 재시도 동작 통일 |
| `EmptyState` | `title`, `description`, `action` | 빈 목록 화면 통일 |
| `Rating` | `value`, `interactive`, `onChange` | 별점 표시와 선택 재사용 |
| `MovieCard` | `movie` | 목록의 영화 한 건 표현 |
| `MovieList` | `movies` | 카드 배열 렌더링 |
| `MovieForm` | `movie`, `onSubmit`, `submitting` | 등록·수정 폼 공유 |
| `Layout` / `Header` | `Outlet` | 공통 헤더와 페이지 틀 |

---

## 3. props와 state: 가장 자주 묻는 개념

### 3.1 props는 부모가 전달하는 읽기 전용 값

props(properties)는 부모 컴포넌트가 자식에게 전달하는 값이다. 자식은 받은 props를 직접 바꾸면 안 된다.

```jsx
// 부모
<MovieCard movie={movie} />

// 자식
function MovieCard({ movie }) {
  return <h3>{movie.title}</h3>
}
```

`MovieCard`가 제목을 표시할 수는 있지만 `movie.title = '새 제목'`처럼 props를 변경해서는 안 된다. 데이터 변경의 책임은 부모 또는 데이터 관리 계층에 있다.

### 3.2 state는 컴포넌트가 기억하는 값

state는 사용자의 입력, 선택된 필터, 요청 진행 여부처럼 시간이 지나며 바뀌는 값이다. `useState`로 만든다.

```jsx
const [genre, setGenre] = useState('All')
```

첫 번째 값 `genre`는 현재 상태, 두 번째 값 `setGenre`는 그 상태를 바꾸는 함수다. `setGenre('Drama')`를 호출하면 React는 해당 컴포넌트를 다시 렌더링한다.

### 3.3 state는 어디에 두는가

state는 **그 값을 필요로 하는 컴포넌트들의 가장 가까운 공통 부모**에 둔다.

| 상태 | 위치 | 이유 |
| --- | --- | --- |
| 장르 필터 `genre` | `MoviesPage` | 목록 필터 버튼과 필터된 리스트가 함께 사용 |
| 폼 입력값 `values` | `MovieForm` | 폼 내부 입력창만 사용 |
| 삭제 진행 `deleting` | `MovieDetailPage` | 상세 페이지의 삭제 버튼만 사용 |
| 목록/로딩/오류 | `useMovies` | 여러 목록 화면에서 같은 요청 흐름을 재사용 |

상태를 너무 상위에 두면 관계없는 컴포넌트도 다시 렌더링될 수 있고 코드 흐름이 복잡해진다. 너무 아래에 두면 필요한 형제 컴포넌트끼리 값을 공유할 수 없다.

### 3.4 단방향 데이터 흐름

React의 기본 데이터 흐름은 아래 방향이다.

```text
부모 state → props → 자식 UI
자식 이벤트 → 부모가 전달한 함수 호출 → 부모 state 변경
```

예를 들어 `MovieForm`은 저장할 데이터를 직접 DB에 저장하지 않고 `onSubmit` props를 호출한다. `MovieFormPage`가 그 데이터를 받아 `createMovie` 또는 `updateMovie`를 호출하고, 성공하면 이동한다. 이 구조 덕분에 폼은 화면 입력에, 페이지는 저장 후 흐름에 집중한다.

---

## 4. 이벤트에서 렌더링까지

React UI 변화는 대체로 다음 3단계다.

```text
1) 사용자 이벤트 발생
2) 이벤트 핸들러에서 state 변경
3) React가 컴포넌트를 다시 실행(re-render)하고 JSX 결과를 화면에 반영
```

### 4.1 사례 1: 장르 필터

```jsx
<button onClick={() => setGenre('Drama')}>Drama</button>
```

1. 사용자가 `Drama` 버튼을 클릭한다.
2. `setGenre('Drama')`가 호출된다.
3. `MoviesPage`가 다시 렌더링된다.
4. 현재 `genre` 값으로 `Drama`만 남긴 `filtered`가 계산된다.
5. `MovieList`가 달라진 영화 배열을 받아 새 카드 목록을 표시한다.

### 4.2 사례 2: controlled input

```jsx
<input name="title" value={values.title} onChange={change} />
```

입력창의 실제 값은 브라우저 DOM이 아니라 React state `values.title`이 기준이다. 사용자가 글자를 입력하면 `onChange`가 실행되어 state를 갱신하고, 갱신된 state가 다시 `value` prop으로 내려온다. 이를 **controlled input**이라고 한다.

```jsx
const change = (event) => {
  setValues((previous) => ({
    ...previous,
    [event.target.name]: event.target.value,
  }))
}
```

장점은 유효성 검사, 오류 메시지, 제출 시 전체 값 사용을 React 방식으로 일관되게 처리한다는 점이다.

### 4.3 사례 3: 저장 버튼

```text
폼 제출 → submitting: true → 버튼 비활성화 및 “처리 중…” 표시
       → Supabase 저장 성공 → 상세 주소로 navigate
       → 상세 페이지가 새 데이터 요청 후 렌더링
```

비동기 요청 도중에는 같은 버튼을 여러 번 눌러 중복 저장될 수 있다. 그래서 `submitting` 상태를 `true`로 두고 버튼을 비활성화한다. 완료 여부와 관계없이 `finally`에서 다시 `false`로 돌린다.

---

## 5. re-render를 정확히 이해하기

### 5.1 언제 re-render되는가

대표적으로 다음 상황에서 컴포넌트 함수가 다시 실행된다.

- 그 컴포넌트의 state가 변경될 때
- 부모가 다시 렌더링되어 새 props를 받을 때
- 사용하는 Context 값이 변경될 때 (이 미션의 필수 범위는 아님)

re-render는 “브라우저 전체를 새로고침한다”는 뜻이 아니다. React는 새로운 JSX를 만든 뒤 이전 결과와 비교하고, 실제 DOM에서 바뀐 부분을 갱신한다.

### 5.2 state를 직접 바꾸면 안 되는 이유

```jsx
// 잘못된 예: React는 변경을 감지하지 못할 수 있다.
values.title = '새 제목'

// 올바른 예: setter를 통해 새 객체를 전달한다.
setValues((previous) => ({ ...previous, title: '새 제목' }))
```

state는 setter로 바꾸고, 객체/배열은 기존 값을 변경하지 않는 방식(불변성)으로 새 값을 만들어 전달한다. 그래야 React가 변화 여부를 안정적으로 판단한다.

---

## 6. 라우팅: 주소와 Page를 연결하기

`react-router-dom`은 현재 URL에 맞는 Page 컴포넌트를 보여준다.

```jsx
<Routes>
  <Route path="/movies" element={<MoviesPage />} />
  <Route path="/movies/:id" element={<MovieDetailPage />} />
  <Route path="*" element={<NotFoundPage />} />
</Routes>
```

### 6.1 동적 라우트

`/movies/:id`의 `:id`는 바뀌는 부분이다.

```jsx
const { id } = useParams()
```

주소가 `/movies/abc-123`이면 `id`는 `abc-123`이다. 이 id를 사용해 Supabase에서 특정 영화 한 건을 조회한다.

### 6.2 Link와 navigate

- `<Link to="/movies">`는 사용자가 클릭해 주소를 옮기는 링크다.
- `navigate('/movies')`는 저장/삭제 성공처럼 JavaScript 코드에서 주소를 옮길 때 쓴다.

`<a href>`도 주소를 바꾸지만 문서를 다시 요청할 수 있다. SPA 내부 화면 전환에는 `Link`를 사용한다.

### 6.3 공통 레이아웃과 Outlet

```jsx
function Layout() {
  return <><Header /><main><Outlet /></main></>
}
```

`Layout`은 모든 주요 페이지에 Header를 공통으로 붙인다. `Outlet` 자리에 현재 라우트의 Page가 들어간다. Header를 페이지마다 복사하지 않아도 된다.

---

## 7. useEffect와 비동기 데이터 요청

### 7.1 useEffect는 언제 쓰는가

렌더링 결과를 만드는 일 외에 해야 하는 작업을 **side effect**라고 한다. 데이터 요청, 타이머, 구독 등이 대표적이다. `useEffect`는 렌더링 뒤에 그러한 작업을 실행한다.

```jsx
useEffect(() => {
  fetchMovies()
}, [fetchMovies])
```

이 코드는 컴포넌트가 처음 화면에 나타났을 때, 그리고 `fetchMovies` 참조가 바뀔 때 목록을 요청한다.

### 7.2 의존성 배열

| 코드 | 실행 시점 |
| --- | --- |
| `useEffect(fn)` | 모든 렌더링 후 |
| `useEffect(fn, [])` | 처음 마운트된 뒤 한 번 |
| `useEffect(fn, [id])` | 처음 + `id`가 달라질 때 |

상세 페이지는 주소의 id가 달라지면 다른 데이터를 요청해야 하므로 `id`에 의존한다. 의존성을 빼면 이전 id의 데이터를 계속 보여주는 버그가 날 수 있다.

### 7.3 왜 커스텀 훅으로 분리하는가

`useMovies`는 목록 데이터, `loading`, `error`, 재시도 함수까지 한 덩어리로 반환한다.

```jsx
const { movies, loading, error, refetch } = useMovies()
```

이점은 두 가지다.

1. `HomePage`, `MoviesPage`가 같은 비동기 패턴을 중복 작성하지 않는다.
2. Page 컴포넌트가 “어떤 화면을 보여줄지”에 집중한다.

Hook 이름은 `use`로 시작해야 하며, Hook은 컴포넌트 최상위에서만 호출해야 한다. 조건문·반복문 안에서 호출하면 안 된다.

---

## 8. 비동기 UI의 네 가지 상태

원격 데이터 화면은 성공 화면만 만들면 불완전하다. 최소한 아래 상태를 구분한다.

```text
요청 전/진행 중  → loading
요청 성공 + 데이터 있음 → 목록/상세 UI
요청 성공 + 데이터 없음 → EmptyState
요청 실패 → ErrorState
```

```jsx
if (loading) return <Loading />
if (error) return <ErrorState message={error} onRetry={refetch} />
if (movies.length === 0) return <EmptyState />
return <MovieList movies={movies} />
```

### 8.1 try / catch / finally

```jsx
setLoading(true)
setError('')
try {
  const result = await getMovies()
  setMovies(result)
} catch (err) {
  setError(err.message || '목록을 불러오지 못했습니다.')
} finally {
  setLoading(false)
}
```

- `try`: 정상 요청
- `catch`: 네트워크·권한·서버 오류 처리
- `finally`: 성공/실패와 관계없이 반드시 실행. 로딩 종료에 적합

오류를 콘솔에만 남기면 사용자는 아무것도 할 수 없다. 화면에 실패 사실과 재시도 버튼을 보여주는 것이 필수 UX다.

---

## 9. Supabase와 CRUD

### 9.1 역할 구분

```text
Page / Hook → lib/movieApi.js → Supabase Client → Supabase Database
```

UI 컴포넌트에서 Supabase 코드를 직접 호출하지 않고, `lib/movieApi.js`의 함수로 감싼다. 나중에 DB 또는 요청 형식이 바뀌어도 UI 전체가 영향을 받지 않는다.

### 9.2 CRUD의 뜻

| 약어 | 뜻 | SceneLog 함수 |
| --- | --- | --- |
| Create | 새 데이터 생성 | `createMovie(values)` |
| Read | 데이터 조회 | `getMovies()`, `getMovie(id)` |
| Update | 기존 데이터 수정 | `updateMovie(id, values)` |
| Delete | 데이터 삭제 | `deleteMovie(id)` |

### 9.3 Supabase 요청 예시

```jsx
// 목록 조회
supabase.from('movies').select('*').order('created_at', { ascending: false })

// 특정 한 건 조회
supabase.from('movies').select('*').eq('id', id).single()

// 생성 후 생성된 행 받기
supabase.from('movies').insert(values).select().single()
```

Supabase는 보통 `{ data, error }`를 반환한다. `error`가 있으면 `throw error`로 catch 흐름에 보내어 오류 UI를 표시한다.

### 9.4 등록/수정/삭제 뒤의 흐름

- 등록: 성공 응답의 id로 `/movies/:id` 이동
- 수정: 성공 응답의 id로 `/movies/:id` 이동
- 삭제: 성공 후 더는 상세 데이터가 없으므로 `/movies` 이동

이렇게 요청 성공 뒤에 이동 또는 목록 재조회가 있어야 사용자가 최신 데이터를 볼 수 있다.

---

## 10. 폼 UX와 유효성 검사

### 10.1 유효성 검사는 왜 필요한가

필수 입력이 없는 데이터를 DB에 보내면 오류를 늦게 알게 되고 품질도 낮아진다. 제출 전에 검사하고, 무엇을 고쳐야 하는지 입력창 근처에서 알려준다.

```jsx
const nextErrors = {}
if (!values.title.trim()) nextErrors.title = '제목을 입력해주세요.'
if (!values.note.trim()) nextErrors.note = '한 줄 감상을 입력해주세요.'

setErrors(nextErrors)
if (Object.keys(nextErrors).length) return
```

### 10.2 좋은 제출 경험

제출 시 UI는 다음을 분명히 보여야 한다.

- 비어 있는 필드: 해당 필드 아래 오류 메시지
- 요청 중: 저장 버튼 비활성화 및 `처리 중…`
- 요청 실패: 폼 상단의 실패 알림
- 요청 성공: 상세 페이지 또는 목록으로 이동

검증 오류는 사용자가 입력을 고쳐 해결할 수 있는 오류이고, 네트워크 오류는 사용자가 직접 해결하기 어려운 오류다. 두 오류를 구분해 표시한다.

---

## 11. 배포와 환경변수

### 11.1 환경변수에 넣는 값

```env
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=YOUR_ANON_KEY
```

Vite는 클라이언트 코드에서 사용할 환경변수 이름이 `VITE_`로 시작해야 한다.

`.env`는 실제 값이 들어 있으므로 GitHub에 올리면 안 된다. `.gitignore`에 넣는다. 대신 `.env.example`에는 키 이름만 남겨 다른 사람이 설정 방법을 알 수 있게 한다.

### 11.2 배포 체크리스트

1. Supabase SQL Editor에서 `supabase-schema.sql` 실행
2. 로컬 `.env`에 실제 URL과 anon key 입력
3. `npm run build`가 성공하는지 확인
4. GitHub에는 `.env` 없이 코드만 push
5. Vercel 또는 Netlify의 Environment Variables에 같은 두 값 등록
6. 배포 URL에서 목록, 등록, 수정, 삭제, 새로고침 후 상세 진입까지 직접 확인

환경변수는 로컬에만 있고 배포 대시보드에 없으면, 배포 사이트에서 데이터 기능이 작동하지 않는다.

---

## 12. 평가 대비 설명 답안

### Q. 컴포넌트를 어떤 기준으로 나눴나요?

**답변 예시:** “주소 단위의 큰 화면은 pages에 두고, 여러 화면에서 반복되는 버튼·입력창·상태 UI는 components로 분리했습니다. 특히 로딩, 오류, 빈 상태는 화면마다 따로 작성하지 않고 재사용 컴포넌트로 통일했습니다. 목록 요청 로직은 `useMovies`, 상세 요청 로직은 `useMovie` 커스텀 훅으로 분리해서 페이지가 UI 조합에 집중하도록 했습니다.”

### Q. props와 state의 차이는 무엇인가요?

**답변 예시:** “props는 부모가 자식에게 전달하는 읽기 전용 값이고, state는 컴포넌트가 이벤트에 따라 바꾸며 기억하는 값입니다. 예를 들어 `MovieCard`는 `movie`를 props로 받아 표시하고, `MoviesPage`의 선택 장르나 `MovieForm`의 입력값은 사용자가 바꾸므로 state로 관리했습니다.”

### Q. 상태는 어디에 두었나요?

**답변 예시:** “상태를 사용하는 범위의 가장 가까운 공통 위치에 두었습니다. 필터는 목록 페이지, 폼 입력값은 폼, 삭제 진행 상태는 상세 페이지에 두었습니다. 목록과 상세 요청의 데이터·로딩·오류 상태는 여러 UI 흐름에 필요해서 각각 커스텀 훅 안에 뒀습니다.”

### Q. useEffect는 왜, 언제 실행되나요?

**답변 예시:** “렌더링 자체와 분리된 데이터 요청을 하기 위해 사용했습니다. 목록 hook은 처음 마운트될 때 목록을 요청하고, 상세 hook은 `id`를 의존성으로 두어 주소의 id가 바뀌면 해당 영화를 다시 요청합니다. 의존성 배열이 바뀔 때 effect가 다시 실행됩니다.”

### Q. 로딩/오류/빈 상태를 어떻게 처리했나요?

**답변 예시:** “요청 전에는 `loading`을 true로 두고 Loading 컴포넌트를 보여줍니다. 성공했지만 배열이 비었으면 EmptyState, 요청이 실패하면 error 문자열과 ErrorState를 표시합니다. ErrorState는 `refetch`를 받아 재시도를 제공합니다. 이 패턴을 핵심 목록과 상세 화면에 공통 적용했습니다.”

### Q. 저장 버튼을 누르면 어떤 일이 일어나나요?

**답변 예시:** “submit 이벤트가 폼의 필수값을 먼저 검사합니다. 통과하면 `submitting` state를 true로 바꿔 버튼을 비활성화하고 API 함수를 호출합니다. 성공하면 받은 id의 상세 라우트로 `navigate`하고, 실패하면 오류 상태를 폼 상단에 표시합니다. finally에서 제출 상태를 false로 돌립니다.”

### Q. React에서 상태 변경이 화면 변경으로 이어지는 지점을 말해보세요.

**답변 예시:** “장르 필터 클릭 시 `genre` state가 바뀌고 필터된 목록이 다시 렌더링됩니다. 입력창에 타이핑하면 `values` state가 바뀌고 input value 및 별점 UI가 갱신됩니다. 저장할 때 `submitting`이 바뀌어 버튼 문구와 disabled 상태가 바뀌며, 저장 성공 뒤에는 라우트 변경으로 상세 페이지가 렌더링됩니다.”

---

## 13. 제출 전 최종 점검

- [ ] 최소 5개 이상 라우트와 `NotFoundPage`가 있다.
- [ ] Header의 Link로 주요 화면을 이동할 수 있다.
- [ ] 목록과 상세가 Supabase 원격 데이터로 조회된다.
- [ ] 등록·수정·삭제가 실제 DB에서 동작한다.
- [ ] 등록/수정 폼은 controlled input이고 필수값 오류를 표시한다.
- [ ] 요청 중 버튼이 비활성화된다.
- [ ] 로딩·오류·빈 상태가 공통 컴포넌트로 표시된다.
- [ ] 8개 이상의 재사용 컴포넌트가 props를 받아 동작한다.
- [ ] 데이터 요청 흐름이 적어도 하나의 custom hook으로 분리되어 있다.
- [ ] `.env`는 gitignore에 있고 배포 환경변수를 등록했다.
- [ ] README에 실행법과 기술 스택을 작성했다.

---

## 핵심 암기 문장

> React는 state가 바뀌면 컴포넌트를 다시 렌더링하고, 개발자는 그 state에 따른 UI를 JSX로 선언한다.

> props는 부모가 자식에게 주는 값이고, state는 컴포넌트가 이벤트에 따라 바꾸는 값이다.

> 비동기 화면은 데이터 성공만이 아니라 loading, error, empty까지 함께 설계해야 한다.

> 좋은 컴포넌트 분리는 반복되는 UI와 반복되는 로직을 각자의 책임으로 분리하는 것이다.
