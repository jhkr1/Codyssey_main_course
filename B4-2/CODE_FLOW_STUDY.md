# SceneLog 코드 흐름 학습 노트

이 문서는 SceneLog의 현재 코드를 읽으면서 React SPA가 실제로 어떻게 움직이는지 설명하는 학습 자료다. 일반 이론보다 `MoviesPage`, `useMovies`, `MovieForm`, `movieApi`가 연결되는 실제 흐름을 우선한다.

## 1. 이 프로젝트를 한 문장으로 이해하기

SceneLog는 영화 제목, 감독, 장르, 평점, 감상을 기록하는 React SPA다. 사용자가 화면에서 행동하면 Page와 Component가 이벤트를 받고, Hook 또는 `movieApi`가 Supabase와 통신하고, 결과가 state에 저장된 뒤 React가 화면을 다시 그린다.

```text
사용자
  ↓
Page
  ↓
Component / Custom Hook
  ↓
movieApi
  ↓
Supabase
  ↓
데이터 반환
  ↓
State 변경
  ↓
React re-render
  ↓
화면 변경
```

- 사용자는 링크, 필터, 입력창, 저장·삭제 버튼을 누른다.
- Page는 URL에 맞는 큰 화면을 만들고 필요한 data와 이동을 연결한다.
- Component와 Hook은 반복되는 UI, data 요청, 상태 처리를 맡는다.
- `movieApi`는 Supabase의 `movies` 테이블에 어떤 요청을 보낼지 결정한다.
- state가 바뀌면 React가 JSX를 다시 계산해 화면에 반영한다.

## 2. 먼저 알아둘 React 핵심 개념

### Component

Component는 화면의 한 조각을 만드는 함수다. `MoviesPage`는 주소 하나에 대응하는 큰 화면, `MovieCard`는 영화 한 편을 보여 주는 작은 UI, `Button`은 여러 화면에서 쓰는 공통 버튼이다.

- **Page Component**: `MoviesPage`, `MovieDetailPage`, `MovieFormPage`처럼 route에 직접 연결된다. 화면 구성, API 연결, 이동을 담당한다.
- **재사용 Component**: `Button`, `Input`, `Loading`, `ErrorState`, `EmptyState`처럼 여러 화면에서 같은 규칙을 쓴다.
- **Feature Component**: `MovieList`, `MovieCard`, `MovieForm`처럼 영화 기능에 가까운 UI를 맡는다.

`MoviesPage` 안에 카드 HTML을 전부 적지 않고 `MovieList`를 쓰는 이유는 화면이 “어떤 상태에서 무엇을 보여 줄지”에 집중하게 하기 위해서다. 카드의 모양은 `MovieCard` 한 곳에서 관리한다.

### Props

props는 부모 Component가 자식 Component에 건네는 값이다. 자식은 받은 props를 읽어 화면을 만들지만 직접 바꾸지 않는다.

```text
MoviesPage → MovieList에 movies 전달
MovieList → MovieCard에 movie 전달
```

실제 `MovieList`는 `movies` props를 순회하며 각 원소를 `MovieCard`의 `movie` props로 전달한다. `MovieCard`는 `movie.title`, `movie.genre`, `movie.rating`을 표시하고 `movie.id`로 상세 링크를 만든다. `Button`도 `loading`, `variant`, `children` props를 받아 모양과 비활성 상태를 결정한다.

### State

state는 입력값이나 요청 결과처럼 시간이 지나며 바뀌는 값을 Component가 기억하는 방법이다. 일반 지역 변수와 달리 `useState` setter가 호출되면 React가 다시 렌더한다.

- `MoviesPage`의 `genre`: 사용자가 고른 장르
- `MovieForm`의 `values`: 입력 중인 폼 값
- `MovieFormPage`의 `submitting`: 저장 요청 진행 여부
- `MovieDetailPage`의 `deleting`: 삭제 요청 진행 여부

### Event

이벤트는 사용자의 행동을 코드가 받는 통로다. `onClick`은 필터·별점·삭제 버튼, `onChange`는 input/select, `onSubmit`은 form 저장에 사용된다.

예를 들어 장르 버튼의 `onClick={() => setGenre(item)}`이 `genre` state를 바꾸면 `filtered` 목록이 다시 계산된다. React는 새 목록에 맞게 `MovieList`를 다시 렌더한다.

### useEffect

`useEffect`는 화면을 처음 보여 준 뒤 목록을 요청하는 것처럼 렌더와 별도로 해야 하는 일을 실행한다. SceneLog에서는 `useMovies`와 `useMovie`가 Supabase 읽기 요청을 시작할 때 사용한다.

`useMovies`의 `useEffect(() => { fetchMovies() }, [])`에서 `[]`는 Hook을 쓰는 화면이 처음 나타날 때 한 번 요청한다는 뜻이다. `useMovie`는 `[id, enabled]`를 쓰므로 상세 대상 id가 바뀌면 그 영화도 다시 가져온다.

### Custom Hook

Custom Hook은 여러 화면에 필요한 state와 로직을 `useMovies()`처럼 묶은 함수다. `HomePage`와 `MoviesPage`가 목록 요청, loading, error 로직을 각각 복사하지 않고 같은 `useMovies()`를 사용할 수 있다.

## 3. 폴더를 역할로 읽기

```text
src/
├─ pages/       주소 하나에 대응하는 화면
├─ components/  재사용 UI와 영화 기능 UI
├─ hooks/       data 요청과 관련 state 묶음
├─ lib/         Supabase 연결과 CRUD 함수
├─ App.jsx      route와 Page 연결
└─ main.jsx     React 시작점
```

| 위치 | 현재 예시 | 맡은 일 |
|---|---|---|
| `pages/` | `MoviesPage.jsx`, `MovieDetailPage.jsx` | 화면 구성, route 상태 연결 |
| `components/` | `MovieCard.jsx`, `MovieForm.jsx`, `Button.jsx` | 반복 UI 표시와 입력 |
| `hooks/` | `useMovies.js`, `useMovie.js` | data, loading, error, retry 관리 |
| `lib/` | `supabase.js`, `movieApi.js` | Supabase client와 CRUD 요청 |
| `App.jsx` | `Routes`, `Route` | URL에 맞는 Page 선택 |
| `main.jsx` | `BrowserRouter`, `App` | React 앱 시작 |

`MoviesPage`에서 Supabase를 바로 호출하지 않는 이유는 화면 코드에 DB 요청과 오류 처리가 섞이지 않게 하기 위해서다. Page는 Hook이 돌려준 상태를 보고 어떤 UI를 보여 줄지만 결정한다.

## 4. 앱을 실행하면 처음 일어나는 일

```text
index.html → main.jsx → App.jsx → BrowserRouter / Routes → Layout → 현재 URL의 Page
```

1. `index.html`에는 React가 붙을 root 요소가 있다.
2. `main.jsx`가 `ReactDOM.createRoot(...).render(...)`로 React 앱을 시작한다.
3. `main.jsx`는 `App`을 `BrowserRouter`로 감싼다. 앱 안에서 URL을 읽고 `Link`로 이동할 수 있는 이유다.
4. `App.jsx`의 `Routes`가 현재 주소와 맞는 `Route`를 찾는다.
5. 모든 route는 `Layout` 아래에 있어 `Header`는 공통으로 보이고, `Outlet` 위치에 선택된 Page가 들어간다.

## 5. Route 흐름

| URL | Component | 역할 |
|---|---|---|
| `/` | `HomePage` | 최근 영화와 시작 화면 |
| `/movies` | `MoviesPage` | 전체 목록과 장르 필터 |
| `/movies/new` | `MovieFormPage` | 새 영화 등록 |
| `/movies/:id` | `MovieDetailPage` | 영화 한 편 상세와 삭제 |
| `/movies/:id/edit` | `MovieFormPage` with `edit` | 기존 영화 수정 |
| `/about` | `AboutPage` | 서비스 소개 |
| `*` | `NotFoundPage` | 없는 주소 처리 |

`/movies/123`으로 들어가면 `/movies/:id` route가 `MovieDetailPage`를 선택한다. `MovieDetailPage`의 `useParams()`는 URL에서 `id`를 읽고, 그 id가 `useMovie(id)`와 `getMovie(id)`에 전달되어 특정 영화 한 편을 가져온다.

## 6. 가장 중요한 흐름: 영화 목록 조회

`/movies`를 열었을 때의 실제 흐름이다.

1. 사용자가 `/movies`로 이동한다.
2. `App.jsx`가 `MoviesPage`를 렌더한다.
3. `MoviesPage`는 `useMovies()`를 호출해 `movies`, `genres`, `loading`, `error`, `refetch`를 받는다.
4. `useMovies`는 처음 `movies = []`, `loading = true`, `error = ''`로 시작한다.
5. `useEffect(..., [])`가 `fetchMovies()`를 호출한다.
6. `fetchMovies()`는 `setLoading(true)`와 `setError('')`로 요청을 준비한다.
7. `getMovies()`가 `requireSupabase().from('movies').select('*').order(...)`를 실행한다.
8. Supabase가 `movies` 테이블의 행을 `created_at` 내림차순으로 반환한다.
9. 성공하면 `setMovies(data)`, 실패하면 `setError(...)`가 실행된다.
10. `finally`에서 `setLoading(false)`가 실행된다.
11. state가 바뀌었으므로 React가 `MoviesPage`를 다시 렌더한다.
12. 데이터가 있으면 `MovieList`, 없으면 `EmptyState`, 오류면 `ErrorState`가 보인다.

### 요청 중

`loading === true`일 때 `MoviesPage`는 `<Loading />`을 보여 준다. 아직 결과가 없다는 뜻이므로 빈 목록을 데이터 없음으로 오해하지 않는다.

### 요청 성공

`loading`이 false이고 `error`가 없고 `filtered.length`가 있으면 `<MovieList movies={filtered} />`가 렌더된다. `MovieList`는 영화마다 `MovieCard`를 하나씩 만든다.

### 요청 실패

Supabase 오류나 설정 오류가 throw되면 `fetchMovies()`의 `catch`가 `error` state에 메시지를 넣는다. `MoviesPage`는 `<ErrorState message={error} onRetry={refetch} />`를 보여 주고, 재시도 버튼은 `fetchMovies`를 다시 실행한다.

### 성공했지만 데이터가 0개

`movies`가 빈 배열이면 `filtered.length`도 0이다. 이때 `MoviesPage`는 공통 `<EmptyState />`를 보여 준다. `HomePage`도 `movies.length`를 확인해 같은 방식으로 빈 상태를 처리한다.

## 7. 영화 상세 조회 흐름

```text
MovieCard 클릭 → /movies/:id → MovieDetailPage → useParams() → useMovie(id) → getMovie(id) → Supabase SELECT → movie state → 상세 화면
```

`MovieCard`는 `to={`/movies/${movie.id}`}` 형태의 `Link`다. 카드를 누르면 React Router가 주소를 바꾸고 `MovieDetailPage`를 렌더한다.

`useMovie(id)`는 목록용 `useMovies()`와 비슷하지만 배열 대신 한 편의 `movie` state를 관리한다. `getMovie(id)`는 `.eq('id', id).single()`을 사용하므로 URL id와 일치하는 한 행을 기대한다.

목록 조회는 `movies` 배열과 `MovieList`를 만들고, 상세 조회는 `movie` 한 객체와 제목·감상·평점이 있는 상세 화면을 만든다는 점이 다르다. 둘 다 loading/error 처리와 Supabase SELECT를 공유한다.

## 8. 영화 등록 흐름

```text
/movies/new → MovieFormPage → MovieForm → 사용자 입력 → onChange → values state → submit → createMovie → Supabase INSERT → navigate → 상세 페이지
```

`/movies/new`에서는 `MovieFormPage`가 `MovieForm`에 `movie={null}`, `onSubmit={save}`, `submitting`을 전달한다. `MovieForm`의 새 등록 초기값은 `initial`이다.

제목 input은 `value={values.title}`을 사용하고, `onChange`는 `setValues`로 해당 필드를 바꾼다. 이것이 controlled input이다. 브라우저가 값을 따로 관리하는 것이 아니라 React의 `values.title`이 화면의 값이 된다.

저장하면 `submit`이 제목·감독·감상이 비었는지 검사해 `errors` state를 만든다. 문제가 없으면 `onSubmit`에 `year`를 숫자 또는 null로 바꾼 값을 전달한다. `MovieFormPage.save`는 `submitting`을 true로 바꾸고 `createMovie(values)`를 호출한다.

`createMovie`는 `movies` 테이블에 `insert(values).select().single()`을 실행한다. 성공 응답의 id로 `navigate(`/movies/${result.id}`)`를 호출하므로 사용자는 방금 만든 영화의 상세 화면으로 이동한다. 실패하면 `submitError`가 표시되고 `finally`에서 `submitting`은 false가 된다.

## 9. 영화 수정 흐름

등록과 수정이 모두 `MovieForm`을 쓰는 이유는 제목·감독·연도·장르·평점·감상 입력 UI와 검증 규칙이 같기 때문이다. 두 폼을 따로 만들면 같은 input과 validation을 두 곳에서 고쳐야 한다.

```text
수정 버튼 → /movies/:id/edit → MovieFormPage edit → useMovie → 기존 movie → MovieForm 초기값 → 사용자 수정 → updateMovie → Supabase UPDATE → navigate
```

`App.jsx`는 `/movies/:id/edit`에서 `<MovieFormPage edit />`를 전달한다. `MovieFormPage`는 `useMovie(id, edit)`를 호출하므로 edit가 true일 때만 기존 영화를 읽는다. 가져오는 동안 Loading, 실패하면 ErrorState를 보여 준 뒤에 form을 렌더한다.

`MovieForm`은 기존 movie 전체를 복사하지 않고 `title`, `director`, `year`, `genre`, `rating`, `note`만 초기 state로 사용한다. 따라서 input에는 기존 값이 보이지만 `id`, `created_at`은 form state에 들어가지 않는다.

`MovieFormPage.save`는 edit일 때 `updateMovie(id, values)`를 호출한다. `updateMovie`도 허용한 여섯 필드만 `updates` 객체로 만들어 `.update(updates).eq('id', id)`에 전달한다. DB 메타데이터를 실수로 수정하지 않도록 form과 API 양쪽에서 막은 것이다.

## 10. 영화 삭제 흐름

```text
삭제 클릭 → remove handler → deleting = true → 버튼 disabled → deleteMovie(id) → Supabase DELETE → 성공: /movies 이동 / 실패: deleteError 표시
```

`MovieDetailPage`의 삭제 버튼은 `onClick={remove}`을 사용한다. `remove`는 먼저 confirm으로 정말 삭제할지 확인한 뒤 `setDeleting(true)`를 호출한다.

state setter가 호출되면 React가 `MovieDetailPage`를 다시 렌더한다. `deleting`이 `Button`의 `loading` props가 되고, `Button`은 `disabled={loading || props.disabled}`를 적용한다. 그래서 DELETE 요청이 끝나기 전 중복 클릭을 막을 수 있다.

성공하면 `deleteMovie(id)`가 `.delete().eq('id', id)`를 마치고 `navigate('/movies')`로 목록에 돌아간다. 실패하면 `deleteError` state가 바뀌고, 상세 내용을 없애지 않은 채 `notice` 영역에 오류가 표시된다.

## 11. 장르 필터 흐름

`MoviesPage`의 `genre`는 서버에 저장할 필요가 없는, 현재 화면에서만 필요한 state다. 처음에는 `'All'`이고 장르 버튼을 누르면 `setGenre(item)`이 실행된다.

```text
장르 버튼 클릭 → setGenre(...) → genre state 변경 → MoviesPage re-render → filtered 재계산 → MovieList 내용 변경
```

`filtered`는 별도 state가 아니라 현재 `movies`와 `genre`로 매 렌더마다 계산한다. 이렇게 하면 목록 data와 필터 결과가 어긋날 위험이 줄어든다. state가 중요한 이유는 `genre`처럼 사용자의 선택을 기억하고 값이 바뀌었을 때 React가 UI를 다시 계산하게 하기 때문이다.

## 12. Loading / Success / Error / Empty는 서로 다른 상태다

한 번의 목록 요청도 화면에서는 네 가지 결과가 될 수 있다.

```text
처음: loading = true
성공 + 데이터: loading = false, movies = [...]
실패: loading = false, error = '...'
성공 + 데이터 없음: loading = false, movies = []
```

| 상태 | `MoviesPage`가 보여 주는 것 | 의미 |
|---|---|---|
| loading | `Loading` | 아직 기다리는 중 |
| success | `MovieList` | 받은 영화를 보여 줌 |
| error | `ErrorState` | 요청이 실패했고 재시도 가능 |
| empty | `EmptyState` | 요청은 성공했지만 영화가 없음 |

이 네 상태를 구분하지 않으면 요청 중인 빈 배열과 실제로 영화가 없는 빈 배열이 같은 화면으로 보인다. SceneLog는 `Loading`, `ErrorState`, `EmptyState`를 공통 Component로 분리해 각 Page가 같은 방식으로 처리한다.

## 13. SceneLog에서 Props와 State 구분하기

| 값 | Props / State | 위치 | 이유 |
|---|---|---|---|
| `genre` | State | `MoviesPage` | 사용자가 버튼으로 바꿈 |
| `movies` | State | `useMovies` | API 응답으로 바뀜 |
| `movie` | State | `useMovie` | 상세 API 응답으로 바뀜 |
| `movie` | Props | `MovieCard` | 부모가 카드에 표시할 data 전달 |
| `movies` | Props | `MovieList` | 부모가 목록에 표시할 배열 전달 |
| `values` | State | `MovieForm` | 입력할 때마다 바뀜 |
| `submitting` | State | `MovieFormPage` | 저장 요청 중인지 기억 |
| `submitting` | Props | `MovieForm` | 부모의 저장 상태를 버튼 UI에 전달 |
| `deleting` | State | `MovieDetailPage` | 삭제 요청 중인지 기억 |
| `loading` | Props | `Button` | Button이 disabled 여부를 판단 |

같은 이름이라도 어디에 있느냐에 따라 의미가 다를 수 있다. 예를 들어 `submitting`은 `MovieFormPage`가 가진 state지만, `MovieForm` 입장에서는 부모가 준 props다.

## 14. Page와 Component를 나눈 이유

`MovieFormPage`는 route parameter, `useNavigate`, `useMovie`, 저장 API, `submitting`, `submitError`를 연결한다. 반면 `MovieForm`은 input 표시, 입력 이벤트, validation, 별점 선택처럼 사용자가 form을 채우는 경험을 담당한다.

둘을 하나로 합치면 입력 UI를 고치는 일이 API 이동 로직과 섞이고 등록/수정에서 같은 form을 재사용하기도 어려워진다. 현재처럼 나누면 `MovieForm`은 `movie`, `onSubmit`, `submitting` props만 알면 되고, Page는 어떤 저장 API를 쓸지 결정하면 된다.

## 15. Custom Hook을 만든 이유

Custom Hook이 없다고 생각하면 `HomePage`와 `MoviesPage`가 각자 `useState`, `useEffect`, `getMovies`, try/catch/finally, retry를 모두 작성해야 한다. 그러면 같은 목록 요청 로직이 두 곳에 생기고 오류 메시지나 loading 처리가 달라질 수 있다.

`useMovies()`는 `movies`, `genres`, `loading`, `error`, `refetch`를 한 묶음으로 반환한다. Page는 `const { movies, loading, error, refetch } = useMovies()`처럼 읽기만 하면 된다. `useMovie(id)`도 같은 원리로 상세 한 건의 요청 상태를 묶는다.

## 16. Supabase와 React의 역할

React는 화면과 state를 담당하고, Supabase는 실제 영화 데이터를 보관하고 돌려주는 곳이다. React가 DB를 대신하는 것이 아니며, Supabase가 React 화면을 그리는 것도 아니다.

| 기능 | SceneLog 함수 | DB 동작 |
|---|---|---|
| 등록 | `createMovie` | INSERT |
| 목록 | `getMovies` | SELECT 여러 행 |
| 상세 | `getMovie` | SELECT 한 행 |
| 수정 | `updateMovie` | UPDATE |
| 삭제 | `deleteMovie` | DELETE |

`supabase.js`의 `requireSupabase()`는 환경변수가 없는 상태에서 조용히 demo data로 넘어가지 않게 한다. 실제 요청 또는 설정 오류는 Hook/Page의 기존 error UI로 전달된다.

## 17. 면접 직전: 네 가지 전체 흐름

### 목록 조회

1. `/movies` 진입
2. `MoviesPage` 렌더
3. `useMovies()` 실행
4. `useEffect`가 `fetchMovies()` 호출
5. `getMovies()`가 Supabase SELECT
6. `setMovies(data)` 또는 `setError(...)`
7. `setLoading(false)`
8. React re-render
9. `MovieList`, `ErrorState`, `EmptyState` 중 하나 표시

### 등록

1. `/movies/new` 진입
2. `MovieFormPage`가 `MovieForm` 렌더
3. `onChange`가 `values` state 변경
4. React가 input/별점 UI 재렌더
5. `onSubmit`이 validation
6. `setSubmitting(true)`
7. `createMovie()`가 INSERT
8. 성공 id로 상세 route 이동

### 수정

1. 수정 링크로 `/movies/:id/edit` 이동
2. `useParams()`가 id를 읽음
3. `useMovie(id, true)`가 기존 영화 조회
4. `MovieForm`이 기존 여섯 필드로 초기화
5. 입력과 validation
6. `updateMovie(id, values)` 호출
7. 허용 필드만 UPDATE
8. 성공한 영화의 상세 route 이동

### 삭제

1. 상세 페이지에서 삭제 확인
2. `setDeleting(true)`
3. 버튼이 disabled 상태로 재렌더
4. `deleteMovie(id)` 호출
5. Supabase DELETE
6. 성공하면 `/movies` 이동
7. 실패하면 `deleteError` 변경
8. 상세 화면에 오류 notice 표시

## 18. 예상 질문과 답변

### Q1. 왜 React에서 Component를 나누나요?

SceneLog에서는 목록 화면, 카드, 버튼, 입력창이 각자 다른 일을 한다. `MoviesPage`에 카드와 버튼 코드를 전부 넣으면 화면 구성과 작은 UI 규칙이 섞인다. `MovieCard`와 `Button`으로 나누면 같은 UI를 다시 쓸 수 있고, 고칠 장소도 분명해진다.

### Q2. props와 state의 차이는 무엇인가요?

props는 부모가 자식에게 주는 읽기용 값이고, state는 Component가 변화하는 값을 기억하는 공간이다. `MovieCard`의 `movie`는 부모가 전달한 props다. `MoviesPage`의 `genre`는 사용자가 바꾸므로 state다.

### Q3. 이 프로젝트의 state는 어디에 있나요?

필터는 `MoviesPage`, form 입력값은 `MovieForm`, 저장 진행 상태는 `MovieFormPage`, 삭제 진행 상태는 `MovieDetailPage`에 둔다. 목록과 상세처럼 요청 결과와 여러 UI가 함께 쓰는 값은 `useMovies`, `useMovie` 안에 둔다. 필요한 화면에 가장 가까운 위치에 둔 구조다.

### Q4. useEffect는 왜 쓰나요?

목록 화면이 나타난 뒤 Supabase에서 영화를 읽어야 하기 때문이다. `useMovies`의 effect가 `fetchMovies()`를 시작하고 응답을 `movies` state에 저장한다. 렌더 과정에서 바로 요청을 반복하지 않도록 effect로 분리했다.

### Q5. dependency array `[]`는 무슨 뜻인가요?

`useMovies`의 `[]`는 목록 요청을 화면이 처음 나타날 때 한 번 시작한다는 뜻이다. 사용자가 재시도 버튼을 누르면 effect가 아니라 `refetch`로 같은 요청을 다시 시작한다. 목록 data가 매 렌더마다 다시 요청되지 않게 한다.

### Q6. useMovie에서는 왜 id가 dependency인가요?

`/movies/1`에서 `/movies/2`로 바뀌면 다른 영화를 읽어야 한다. 그래서 `useMovie`는 `[id, enabled]`가 바뀔 때 `fetchMovie()`를 다시 실행한다. id를 넣지 않으면 이전 영화가 남는 문제가 생길 수 있다.

### Q7. state가 바뀌면 화면은 왜 바뀌나요?

React는 `setGenre`, `setMovies`, `setDeleting` 같은 setter가 호출되면 해당 Component의 JSX를 다시 계산한다. 예를 들어 `setDeleting(true)` 뒤에는 `Button`이 받은 `loading` props가 true가 된다. Button의 disabled 조건도 true가 되어 중복 삭제를 막는다.

### Q8. controlled input이 무엇인가요?

`MovieForm`의 제목 input은 `value={values.title}`이고 입력 이벤트는 `setValues`를 호출한다. 즉 input에 보이는 값의 기준은 React state다. 저장할 값, validation할 값, 화면에 보일 값이 모두 `values`에 모여 있어 예측하기 쉽다.

### Q9. Custom Hook을 왜 만드나요?

HomePage와 MoviesPage는 모두 영화 목록·loading·error·재시도가 필요하다. `useMovies()`로 묶으면 두 Page가 같은 비동기 흐름을 공유한다. UI가 아니라 상태와 요청 로직을 재사용하는 방법이다.

### Q10. API 요청 중 loading state가 왜 필요한가요?

요청이 끝나기 전 `movies`는 빈 배열일 수 있다. loading이 없으면 사용자는 데이터가 정말 없는지 아직 기다리는 중인지 구분하기 어렵다. `Loading` UI는 현재 앱이 요청을 처리 중임을 알려 준다.

### Q11. MovieFormPage와 MovieForm은 왜 나뉘나요?

MovieFormPage는 저장 API와 route 이동을 맡고, MovieForm은 입력·검증·버튼 UI를 맡는다. 이 구분 덕분에 등록과 수정이 같은 form UI를 공유한다. form의 모양과 서버 통신 책임도 섞이지 않는다.

### Q12. Supabase와 React는 각각 무슨 역할인가요?

Supabase는 `movies` 데이터를 실제로 저장하고 SELECT/INSERT/UPDATE/DELETE에 응답한다. React는 그 응답을 state에 넣고 어떤 화면을 보여 줄지 결정한다. `movieApi`가 두 역할 사이의 얇은 연결 지점이다.

### Q13. 등록 버튼을 누르면 어떤 순서로 실행되나요?

MovieForm의 `submit`이 validation을 먼저 수행한다. 통과하면 MovieFormPage의 `save`가 `submitting`을 true로 하고 `createMovie`를 호출한다. INSERT 성공 후 새 id로 상세 페이지로 이동하고, 실패하면 저장 오류 메시지가 보인다.

### Q14. 삭제 버튼을 누르면 왜 바로 비활성화되나요?

`remove`이 `setDeleting(true)`를 호출하기 때문이다. state 변경으로 MovieDetailPage가 다시 렌더되고 Button의 `loading` props가 true가 된다. Button은 loading일 때 disabled를 적용하므로 요청 중 두 번 누를 수 없다.

### Q15. 장르 필터를 누르면 목록은 왜 바뀌나요?

버튼의 `onClick`이 `setGenre`를 실행해 선택 장르를 바꾼다. MoviesPage가 다시 렌더될 때 `filtered`가 새 genre 기준으로 계산된다. MovieList가 새 배열을 받으므로 카드 내용도 바뀐다.

## 19. 직접 코드를 읽는 추천 순서

목록 흐름은 아래 순서로 읽으면 좋다.

```text
1. App.jsx
2. MoviesPage.jsx
3. useMovies.js
4. movieApi.js
5. MovieList.jsx
6. MovieCard.jsx
```

그 다음 등록은 `MovieFormPage.jsx → MovieForm.jsx → movieApi.js` 순서로 읽는다. 수정은 여기에 `useMovie.js`와 `MovieDetailPage.jsx`의 수정 링크를 더해 읽으면 된다. 삭제는 `MovieDetailPage.jsx → movieApi.js → Button.jsx` 순서로 보면 `deleting` state가 UI를 바꾸는 이유를 확인하기 쉽다.

## 20. 과제 직전 5분 복습

- **Component**: `MovieCard`처럼 UI를 역할별로 나눈 함수다.
- **Props**: `MovieList`가 `MovieCard`에 넘기는 `movie`처럼 부모가 주는 값이다.
- **State**: `genre`, `values`, `submitting`, `deleting`처럼 바뀌면 화면도 다시 계산되는 값이다.
- **Event**: `onClick`, `onChange`, `onSubmit`이 사용자 행동을 state 변경 또는 API 요청으로 연결한다.
- **useEffect**: `useMovies`, `useMovie`에서 화면이 나타난 뒤 목록·상세 요청을 시작한다.
- **Custom Hook**: data, loading, error, retry를 Page에서 분리해 재사용한다.
- **CRUD**: `movieApi.js`의 다섯 함수가 Supabase의 INSERT, SELECT, UPDATE, DELETE를 담당한다.
- **Re-render**: state가 바뀌면 React가 JSX를 다시 계산해 로딩, 카드, 오류, 버튼 상태를 화면에 반영한다.

전체 흐름은 항상 다음과 같이 기억하면 된다.

```text
사용자 이벤트
  ↓
event handler
  ↓
state 변경 또는 API 요청
  ↓
Supabase 결과 반환
  ↓
state 변경
  ↓
React re-render
  ↓
화면 변경
```
