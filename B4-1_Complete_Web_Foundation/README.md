# Vanilla Portfolio Mission

순수 HTML, CSS, JavaScript만으로 만든 반응형 포트폴리오 웹사이트입니다.

이 프로젝트의 목적은 단순히 화면을 완성하는 것이 아니라, 브라우저에서 다음 흐름이 어떻게 연결되는지 직접 이해하는 것입니다.

```text
사용자 이벤트
→ JavaScript 상태 변경
→ DOM 업데이트
→ 화면 변화
```

## 최종 결과물

반응형 포트폴리오 웹사이트 1개를 완성합니다.

포함 섹션:
- Hero
- About
- Skills
- Projects
- Contact
- Footer

주요 기능:
- 모바일 햄버거 메뉴
- 다크 모드 토글
- 다크 모드 로컬스토리지 저장
- 부드러운 스크롤
- 스크롤 탑 버튼
- 스크롤 위치에 따른 헤더 스타일 변경
- Intersection Observer 기반 스크롤 애니메이션
- Contact 폼 유효성 검사
- GitHub API 기반 프로젝트 카드 렌더링
- API 로딩, 성공, 에러, 빈 상태 처리

## 프로젝트 구조

```text
.
├── index.html
├── css/
│   └── style.css
├── js/
│   └── main.js
├── images/
│   └── profile.svg
├── docs/
│   └── mission-book.md
└── README.md
```

역할:

- `index.html`: 웹 페이지의 구조와 콘텐츠
- `css/style.css`: 레이아웃, 색상, 반응형, 다크 모드, 애니메이션
- `js/main.js`: 이벤트 처리, 상태 관리, DOM 업데이트, GitHub API 연동
- `images/`: 이미지 자산
- `docs/mission-book.md`: 미션 관련 지식 총집합

## 로컬 실행

이 프로젝트는 정적 웹사이트입니다.

가장 쉬운 방법은 VS Code Live Server를 사용하는 것입니다.

1. VS Code에서 프로젝트 폴더를 연다.
2. `index.html`을 연다.
3. 우측 하단의 `Go Live`를 클릭한다.
4. 브라우저에서 화면과 기능을 확인한다.

Python 서버로 확인할 수도 있습니다.

```bash
python3 -m http.server 8000
```

그 다음 브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:8000
```

## 구현 기준값

- GitHub API 사용자명: `jhkr1`
- GitHub 프로젝트 표시 개수: 최신 업데이트 기준 `6개`
- 스크롤 탑 버튼 표시 기준: `300px`
- 헤더 스타일 변경 기준: `60px`
- Intersection Observer threshold: `0.2`

GitHub 사용자명이 바뀌면 [js/main.js](/Users/wlgjs060614351/Desktop/Codyssey_main_course/B4-1_Complete_Web_Foundation/js/main.js)의 `GITHUB_USERNAME` 값과 [index.html](/Users/wlgjs060614351/Desktop/Codyssey_main_course/B4-1_Complete_Web_Foundation/index.html)의 GitHub 링크를 함께 수정합니다.

## 구현 흐름

### 1. HTML 구조 작성

`index.html`에서 시맨틱 태그를 사용해 전체 구조를 만듭니다.

사용한 주요 태그:

- `header`
- `nav`
- `main`
- `section`
- `article`
- `footer`

각 섹션은 `id`를 가지고 있고, 네비게이션의 앵커 링크가 이 `id`로 이동합니다.

### 2. CSS 레이아웃 작성

`css/style.css`에서 모바일 퍼스트 방식으로 스타일을 작성합니다.

사용한 주요 CSS 개념:

- CSS 변수
- Flexbox
- Grid
- 미디어 쿼리
- hover
- transition
- box-shadow
- `[data-theme="dark"]`

데스크톱에서는 일반 메뉴가 보이고, 모바일에서는 햄버거 버튼으로 메뉴를 열고 닫습니다.

### 3. JavaScript 동작 작성

`js/main.js`에서 DOM 요소를 선택하고 이벤트를 연결합니다.

핵심 흐름:

```text
DOM 요소 선택
→ 이벤트 연결
→ 상태 변경
→ 렌더 함수 실행
→ 화면 업데이트
```

주요 기능:

- `toggleTheme()`: 다크 모드 전환
- `toggleMenu()`: 모바일 메뉴 열기/닫기
- `handleScroll()`: 스크롤 탑 버튼과 헤더 스타일 제어
- `observeSections()`: 스크롤 애니메이션
- `loadProjects()`: GitHub API 호출
- `renderProjects()`: 프로젝트 카드 렌더링
- `validateForm()`: 폼 유효성 검사

## 학습 포인트

이 프로젝트를 공부할 때는 기능을 외우기보다 아래 질문에 답할 수 있어야 합니다.

- HTML은 어떤 구조와 의미를 제공하는가?
- CSS는 어떤 기준으로 레이아웃과 테마를 처리하는가?
- JavaScript는 어떤 DOM 요소를 선택하는가?
- 사용자의 행동은 어떤 이벤트로 감지되는가?
- 이벤트가 발생하면 어떤 상태가 바뀌는가?
- 상태가 바뀐 뒤 어떤 DOM이 업데이트되는가?
- API 요청은 로딩, 성공, 에러, 빈 상태를 어떻게 구분하는가?

자세한 개념 설명은 [미션북](./docs/mission-book.md)에서 확인합니다.

## 배포 전 확인

- 모바일, 태블릿, 데스크톱에서 레이아웃이 깨지지 않는가?
- 햄버거 메뉴가 모바일에서 열리고 닫히는가?
- 다크 모드가 새로고침 후에도 유지되는가?
- 네비게이션 클릭 시 부드럽게 이동하는가?
- 스크롤 탑 버튼이 동작하는가?
- 스크롤 애니메이션이 동작하는가?
- Contact 폼에서 빈 값과 이메일 형식을 검사하는가?
- GitHub API 프로젝트가 정상 표시되는가?
- API 실패 시 에러 메시지와 다시 불러오기 버튼이 보이는가?
- README에 배포 URL과 스크린샷을 추가했는가?

## 배포

GitHub Pages로 배포합니다.

배포 후 README에 아래 항목을 추가합니다.

```text
배포 URL: https://{github-id}.github.io/{repository-name}/
```

스크린샷 권장 목록:

- 데스크톱 화면
- 모바일 화면
- 다크 모드 화면
- Contact 폼 에러 화면

