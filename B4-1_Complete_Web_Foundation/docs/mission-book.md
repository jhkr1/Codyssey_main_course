# Vanilla Portfolio Mission Book

HTML, CSS, JavaScript로 포트폴리오 웹사이트를 만들기 위해 필요한 지식을 한 권의 책처럼 정리한 문서입니다.

이 문서는 체크리스트가 아닙니다. 미션을 진행하며 알아야 할 개념, 왜 필요한지, 현재 프로젝트에서 어떻게 쓰이는지를 순서대로 설명합니다.

## 이 책을 읽는 방법

이 미션은 단순히 웹 페이지를 만드는 과제가 아닙니다. 브라우저가 HTML, CSS, JavaScript를 어떻게 해석하고, 사용자의 행동이 어떻게 화면 변화로 이어지는지를 직접 경험하는 과제입니다.

따라서 이 책은 다음 흐름으로 읽으면 좋습니다.

1. 웹 페이지가 무엇으로 구성되는지 이해한다.
2. 포트폴리오 페이지의 각 섹션이 어떤 역할인지 이해한다.
3. CSS로 레이아웃과 반응형을 만드는 방법을 이해한다.
4. JavaScript가 DOM을 선택하고 이벤트를 연결하는 방법을 이해한다.
5. 사용자 이벤트, 상태, 렌더링이 어떻게 연결되는지 이해한다.
6. GitHub API를 통해 외부 데이터를 가져오는 과정을 이해한다.
7. 폼 유효성 검사와 배포까지 하나의 완성 흐름으로 이해한다.

## 1장. 웹 페이지의 세 가지 언어

웹 브라우저가 직접 이해하는 핵심 언어는 HTML, CSS, JavaScript입니다.

React, Vue, Angular 같은 프레임워크도 결국 브라우저에서 실행될 때는 HTML, CSS, JavaScript로 변환됩니다. 그래서 이 미션은 프레임워크를 배우기 전에 반드시 필요한 기본기를 다지는 과정입니다.

### HTML

HTML은 웹 페이지의 구조와 의미를 담당합니다.

제목, 문단, 이미지, 링크, 버튼, 폼, 섹션 같은 콘텐츠를 만들 때 HTML을 사용합니다.

HTML을 잘 작성한다는 것은 단순히 화면에 보이게 만드는 것이 아닙니다. 브라우저, 검색 엔진, 스크린 리더가 페이지의 의미를 이해할 수 있도록 구조를 명확히 작성하는 것입니다.

예시:

```html
<section id="about">
  <h2>About</h2>
  <p>자기소개를 작성합니다.</p>
</section>
```

이 코드는 About이라는 의미 있는 섹션을 만들고, 그 안에 제목과 설명을 배치합니다.

### CSS

CSS는 HTML로 만든 구조를 시각적으로 표현하는 언어입니다.

색상, 글자 크기, 여백, 정렬, 반응형, 다크 모드, 애니메이션 같은 화면 표현을 담당합니다.

예시:

```css
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
```

이 코드는 프로젝트 카드를 화면 크기에 맞춰 자동으로 배치합니다.

### JavaScript

JavaScript는 웹 페이지의 동작을 담당합니다.

사용자가 버튼을 클릭하거나, 메뉴를 열거나, 폼을 제출하거나, 스크롤할 때 JavaScript가 그 행동을 감지하고 화면을 변경합니다.

예시:

```js
button.addEventListener('click', () => {
  console.log('버튼이 클릭되었습니다.');
});
```

JavaScript는 사용자의 행동과 화면 변화를 연결하는 역할을 합니다.

## 2장. 브라우저와 DOM

브라우저는 HTML, CSS, JavaScript를 읽고 웹 페이지를 화면에 보여주는 프로그램입니다.

Chrome, Safari, Edge, Firefox가 모두 브라우저입니다.

브라우저가 하는 일은 다음과 같습니다.

- HTML을 읽어 문서 구조를 만든다.
- CSS를 읽어 스타일을 계산한다.
- JavaScript를 실행한다.
- 사용자 이벤트를 감지한다.
- 변경된 내용을 화면에 다시 그린다.

### DOM

DOM은 Document Object Model의 줄임말입니다.

브라우저가 HTML 문서를 JavaScript로 다룰 수 있는 객체 구조로 바꾼 것입니다.

HTML 문서에 다음 코드가 있다고 가정합니다.

```html
<h1>안녕하세요</h1>
```

JavaScript는 DOM을 통해 이 요소를 선택하고 수정할 수 있습니다.

```js
const title = document.querySelector('h1');
title.textContent = '반갑습니다';
```

이때 JavaScript가 HTML 파일 자체를 직접 고치는 것은 아닙니다. 브라우저가 만든 DOM을 수정하고, 브라우저가 그 변경을 화면에 반영합니다.

## 3장. 포트폴리오 페이지의 구조

이 미션의 최종 결과물은 반응형 포트폴리오 웹사이트입니다.

포트폴리오는 방문자가 짧은 시간 안에 나를 이해할 수 있도록 구성되어야 합니다. 그래서 각 섹션은 역할이 분명해야 합니다.

### Header

Header는 페이지 상단 영역입니다.

보통 로고, 사이트 이름, 네비게이션, 다크 모드 버튼 같은 전역 UI가 들어갑니다.

현재 프로젝트에서 Header는 다음 역할을 합니다.

- 사이트 이름 표시
- 주요 섹션으로 이동하는 메뉴 제공
- 모바일 햄버거 메뉴 제공
- 다크 모드 토글 제공

### Navigation

Navigation은 사용자가 페이지 안에서 원하는 위치로 이동할 수 있도록 돕는 메뉴입니다.

HTML에서는 `nav` 태그로 표현합니다.

```html
<nav aria-label="주요 메뉴">
  <a href="#about">About</a>
  <a href="#projects">Projects</a>
</nav>
```

`href="#about"`은 `id="about"`을 가진 요소로 이동하겠다는 의미입니다.

### Main

Main은 페이지의 핵심 콘텐츠 영역입니다.

Header와 Footer는 사이트의 공통 영역에 가깝고, Main은 이 페이지에서 가장 중요한 내용을 담습니다.

```html
<main>
  <section id="hero">...</section>
  <section id="about">...</section>
</main>
```

### Hero

Hero는 방문자가 페이지에 들어왔을 때 가장 먼저 보는 대표 영역입니다.

포트폴리오의 Hero는 보통 다음 요소를 포함합니다.

- 짧은 인사말
- 나를 설명하는 핵심 문장
- Projects나 Contact로 이동하는 버튼

Hero는 첫인상을 담당합니다. 너무 많은 정보를 넣기보다, 방문자가 “이 사람이 어떤 방향의 개발자인가”를 빠르게 파악하게 만드는 것이 좋습니다.

### CTA

CTA는 Call To Action의 줄임말입니다.

사용자에게 특정 행동을 유도하는 버튼이나 링크를 뜻합니다.

예시:

- 프로젝트 보기
- 문의하기
- GitHub 방문
- 이력서 다운로드

현재 프로젝트의 Hero에는 Projects와 Contact로 이동하는 CTA가 있습니다.

### About

About은 자기소개 섹션입니다.

이 섹션에서는 단순히 이름만 적는 것이 아니라, 어떤 기술을 공부하고 있고, 어떤 방식으로 성장하고 있는지 설명합니다.

포함할 수 있는 내용:

- 현재 학습 중인 분야
- 관심 있는 기술
- 프로젝트를 통해 배우고 싶은 것
- 프로필 이미지 또는 상징 이미지

### Skills

Skills는 기술 스택을 보여주는 섹션입니다.

중요한 점은 기술 이름만 나열하는 것이 아니라, 이 프로젝트에서 그 기술을 어떻게 사용했는지 설명하는 것입니다.

예를 들어 JavaScript를 썼다고만 적는 것보다 “DOM 선택, 이벤트 처리, 상태 변경, API 렌더링에 사용했다”고 적는 편이 더 좋습니다.

### Projects

Projects는 내가 만든 프로젝트 또는 GitHub 저장소를 보여주는 섹션입니다.

현재 프로젝트에서는 GitHub API에서 저장소 목록을 가져와 카드 형태로 보여줍니다.

프로젝트 카드에는 보통 다음 정보가 들어갑니다.

- 저장소 이름
- 설명
- 사용 언어
- 스타 수
- GitHub 링크
- 배포 링크

현재 구현에서는 저장소가 너무 많이 보이지 않도록 최신 업데이트 기준 6개만 표시합니다.

### Contact

Contact는 방문자가 나에게 연락할 수 있도록 만든 섹션입니다.

현재 프로젝트에서는 이름, 이메일, 메시지를 입력하는 폼을 제공합니다.

Contact 섹션의 핵심은 단순히 입력창을 보여주는 것이 아니라, 사용자가 잘못 입력했을 때 명확한 피드백을 제공하는 것입니다.

### Footer

Footer는 페이지 하단 영역입니다.

보통 다음 정보를 포함합니다.

- 저작권 문구
- GitHub 링크
- 이메일 또는 소셜 링크

Header가 페이지의 시작이라면 Footer는 페이지의 마무리입니다.

## 4장. 시맨틱 HTML

시맨틱 HTML은 의미가 있는 태그를 사용해서 문서 구조를 작성하는 방식입니다.

모든 영역을 `div`로 만들 수도 있지만, 그렇게 하면 브라우저나 스크린 리더가 각 영역의 역할을 이해하기 어렵습니다.

예를 들어 메뉴 영역은 `div`보다 `nav`가 적절합니다.

```html
<nav>
  <a href="#about">About</a>
</nav>
```

본문의 독립적인 영역은 `section`이 적절합니다.

```html
<section id="skills">
  <h2>Skills</h2>
</section>
```

반복되는 카드나 독립적으로 읽을 수 있는 콘텐츠는 `article`을 사용할 수 있습니다.

```html
<article class="project-card">
  <h3>Portfolio</h3>
  <p>개인 포트폴리오 프로젝트입니다.</p>
</article>
```

시맨틱 태그를 사용하면 구조가 명확해지고, 접근성과 유지보수성이 좋아집니다.

## 5장. 접근성의 기본

접근성은 다양한 사용자가 웹 페이지를 사용할 수 있도록 만드는 것입니다.

이 미션에서 특히 중요한 접근성 요소는 이미지의 `alt`, 폼의 `label`, 버튼의 `aria-label`입니다.

### alt

`alt`는 이미지가 보이지 않거나 스크린 리더가 이미지를 설명해야 할 때 사용하는 대체 텍스트입니다.

```html
<img src="./images/profile.svg" alt="HTML, CSS, JavaScript 구조를 표현한 이미지" />
```

의미 없는 장식 이미지라면 빈 `alt=""`를 쓸 수도 있지만, 현재 프로젝트의 이미지는 내용을 전달하므로 의미 있는 설명을 넣습니다.

### label

폼 입력 요소는 `label`과 연결되어야 합니다.

```html
<label for="email">이메일</label>
<input id="email" name="email" type="email" />
```

`label`의 `for`와 `input`의 `id`가 같으면 두 요소가 연결됩니다.

이렇게 하면 사용자가 라벨을 클릭했을 때 입력창에 포커스가 가고, 스크린 리더도 입력창의 의미를 이해할 수 있습니다.

### aria-label

아이콘 버튼처럼 텍스트만으로 의미가 드러나지 않는 요소에는 `aria-label`을 사용할 수 있습니다.

```html
<button aria-label="메뉴 열기"></button>
```

현재 프로젝트의 햄버거 메뉴 버튼과 스크롤 탑 버튼은 `aria-label`을 사용합니다.

## 6장. CSS 레이아웃

CSS 레이아웃은 HTML 요소를 화면에 배치하는 방법입니다.

이 미션에서 중요한 레이아웃 개념은 Flexbox, Grid, 반응형, 모바일 퍼스트입니다.

### Flexbox

Flexbox는 한 방향 정렬에 강합니다.

가로 또는 세로 한 줄 안에서 요소를 정렬할 때 좋습니다.

사용하기 좋은 곳:

- 로고와 메뉴를 양쪽으로 배치하는 Header
- 버튼 두 개를 나란히 배치하는 Hero
- 푸터 링크 정렬

예시:

```css
.site-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
```

### Grid

Grid는 행과 열을 함께 다루는 2차원 레이아웃에 강합니다.

사용하기 좋은 곳:

- Skills 카드 목록
- Projects 카드 목록
- 반응형 카드 레이아웃

예시:

```css
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
```

### auto-fit과 minmax

`auto-fit`과 `minmax`를 함께 사용하면 화면 크기에 따라 카드 개수가 자동으로 바뀝니다.

```css
grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
```

의미:

- 각 카드는 최소 240px을 유지한다.
- 남는 공간은 `1fr`로 나누어 가진다.
- 화면이 넓으면 여러 열이 된다.
- 화면이 좁으면 한 열로 줄어든다.

### 모바일 퍼스트

모바일 퍼스트는 모바일 화면 스타일을 먼저 작성하고, 화면이 넓어질 때 태블릿과 데스크톱 스타일을 추가하는 방식입니다.

현재 미션의 브레이크포인트:

```css
@media (min-width: 768px) {
  /* tablet */
}

@media (min-width: 1024px) {
  /* desktop */
}
```

모바일 퍼스트를 사용하면 작은 화면에서도 기본 사용성이 무너지지 않습니다.

## 7장. CSS 변수와 다크 모드

CSS 변수는 반복해서 사용하는 값을 이름으로 저장하는 기능입니다.

```css
:root {
  --color-bg: #f8faf9;
  --color-text: #1f2933;
}
```

사용할 때는 `var()`를 씁니다.

```css
body {
  background: var(--color-bg);
  color: var(--color-text);
}
```

### 다크 모드

다크 모드는 밝은 색상 테마와 어두운 색상 테마를 전환하는 기능입니다.

현재 프로젝트에서는 `html` 태그에 `data-theme="dark"`를 붙이면 다크 모드 변수가 적용됩니다.

```css
[data-theme="dark"] {
  --color-bg: #101418;
  --color-text: #f3f4f6;
}
```

JavaScript는 사용자가 버튼을 클릭했을 때 `data-theme` 값을 바꿉니다.

```js
elements.root.dataset.theme = state.theme;
```

이 방식의 장점은 JavaScript가 모든 요소의 색상을 직접 바꾸지 않아도 된다는 것입니다. JavaScript는 테마 상태만 바꾸고, 실제 색상 변경은 CSS 변수가 처리합니다.

## 8장. JavaScript와 DOM 선택

JavaScript가 화면을 바꾸려면 먼저 바꿀 대상을 찾아야 합니다.

이때 사용하는 대표 메서드가 `querySelector`와 `querySelectorAll`입니다.

### querySelector

`querySelector`는 조건에 맞는 첫 번째 요소 하나를 선택합니다.

```js
const themeButton = document.querySelector('[data-theme-toggle]');
```

### querySelectorAll

`querySelectorAll`은 조건에 맞는 여러 요소를 선택합니다.

```js
const navLinks = document.querySelectorAll('.nav-link');
```

선택한 여러 요소에는 `forEach`로 이벤트를 연결할 수 있습니다.

```js
navLinks.forEach((link) => {
  link.addEventListener('click', closeMenu);
});
```

### data-* 속성

현재 프로젝트는 JavaScript가 요소를 찾기 쉽도록 `data-*` 속성을 사용합니다.

```html
<button data-theme-toggle>Dark</button>
```

```js
const themeToggle = document.querySelector('[data-theme-toggle]');
```

클래스는 CSS 스타일링에 사용하고, `data-*` 속성은 JavaScript 연결 지점으로 사용하면 역할이 깔끔하게 나뉩니다.

## 9장. 이벤트

이벤트는 사용자 행동이나 브라우저 변화입니다.

대표 이벤트:

- `click`: 클릭했을 때
- `submit`: 폼 제출 시
- `scroll`: 페이지 스크롤 시
- `input`: 입력값 변경 시

이벤트를 연결할 때는 `addEventListener`를 사용합니다.

```js
button.addEventListener('click', handleClick);
```

HTML에 `onclick`을 직접 쓰지 않는 이유는 구조와 동작을 분리하기 위해서입니다.

HTML은 구조를 담당하고, JavaScript는 동작을 담당합니다.

## 10장. 상태와 렌더링

상태는 현재 화면을 결정하는 데이터입니다.

현재 프로젝트의 상태 예시:

```js
const state = {
  theme: 'light',
  isMenuOpen: false,
  projects: [],
  projectStatus: 'idle',
  selectedLanguage: 'all',
  formErrors: {},
};
```

상태가 중요한 이유는 화면을 예측 가능하게 만들기 때문입니다.

상태와 렌더링의 기본 흐름:

```text
사용자 이벤트 발생
→ 상태 변경
→ 렌더 함수 실행
→ DOM 업데이트
→ 화면 변화
```

예를 들어 다크 모드는 다음 흐름으로 동작합니다.

```text
버튼 클릭
→ state.theme 변경
→ renderTheme() 실행
→ html의 data-theme 변경
→ CSS 변수 변경
→ 화면 색상 변경
```

React의 상태와 렌더링 개념도 이 흐름과 연결됩니다. React는 이 과정을 더 편하게 도와주는 도구라고 볼 수 있습니다.

## 11장. 주요 인터랙션

인터랙션은 사용자의 행동에 반응하는 UI 기능입니다.

이 미션에서는 다크 모드, 햄버거 메뉴, 부드러운 스크롤, 스크롤 탑 버튼, 스크롤 애니메이션, 폼 검증이 중요한 인터랙션입니다.

### 다크 모드 토글

토글은 두 상태를 왔다 갔다 바꾸는 UI입니다.

다크 모드 토글은 `light`와 `dark` 상태를 전환합니다.

현재 프로젝트 흐름:

```text
다크 모드 버튼 클릭
→ state.theme 변경
→ localStorage 저장
→ data-theme 변경
→ CSS 변수 변경
→ 화면 색상 변경
```

`localStorage`를 사용하기 때문에 새로고침 후에도 선택한 테마가 유지됩니다.

### 햄버거 메뉴

햄버거 메뉴는 모바일에서 메뉴를 접었다 펼치는 UI입니다.

모바일 화면은 가로 공간이 좁기 때문에 메뉴를 항상 펼쳐두기 어렵습니다. 그래서 버튼을 눌렀을 때 메뉴가 나타나도록 만듭니다.

현재 프로젝트 흐름:

```text
메뉴 버튼 클릭
→ state.isMenuOpen 변경
→ navPanel에 active 클래스 토글
→ 메뉴 표시 또는 숨김
```

### 부드러운 스크롤

부드러운 스크롤은 앵커 링크를 클릭했을 때 해당 위치로 자연스럽게 이동하는 효과입니다.

CSS로 구현할 수 있습니다.

```css
html {
  scroll-behavior: smooth;
}
```

### 스크롤 탑 버튼

스크롤 탑 버튼은 사용자가 페이지 아래로 내려갔을 때 다시 맨 위로 이동할 수 있도록 돕습니다.

현재 프로젝트는 스크롤 위치가 300px을 넘으면 버튼이 보이도록 합니다.

```text
scroll 이벤트 발생
→ window.scrollY 확인
→ visible 클래스 토글
→ 버튼 클릭 시 window.scrollTo 실행
```

### 스크롤 시 헤더 스타일 변경

페이지를 아래로 내리면 헤더가 콘텐츠 위에 겹칠 수 있습니다.

그래서 일정 거리 이상 스크롤하면 헤더에 배경, 테두리, 그림자를 적용해 콘텐츠와 구분합니다.

현재 프로젝트는 60px 이상 스크롤하면 헤더 스타일을 변경합니다.

### 스크롤 애니메이션

스크롤 애니메이션은 섹션이 화면에 들어올 때 자연스럽게 나타나게 하는 효과입니다.

현재 프로젝트에서는 Intersection Observer를 사용합니다.

Intersection Observer는 요소가 화면에 들어왔는지 감지하는 브라우저 API입니다.

현재 프로젝트는 `threshold: 0.2`를 사용합니다. 요소가 20% 이상 보이면 애니메이션을 실행한다는 의미입니다.

## 12장. 폼 유효성 검사

폼 유효성 검사는 사용자가 입력한 값이 올바른지 확인하는 과정입니다.

현재 Contact 폼에는 이름, 이메일, 메시지가 있습니다.

검사 조건:

- 이름은 비어 있으면 안 된다.
- 이메일은 비어 있으면 안 된다.
- 이메일은 기본 형식을 만족해야 한다.
- 메시지는 비어 있으면 안 된다.

### preventDefault

HTML 폼은 제출되면 기본적으로 페이지를 새로고침하거나 서버로 이동하려고 합니다.

현재 프로젝트는 실제 서버 전송이 아니라 입력 검증을 연습하는 것이 목적이므로 `preventDefault()`로 기본 동작을 막습니다.

```js
event.preventDefault();
```

### FormData

`FormData`는 폼 입력값을 쉽게 읽을 수 있게 도와주는 객체입니다.

```js
const formData = new FormData(contactForm);
const email = formData.get('email');
```

### 에러 상태

폼 검증 결과는 `formErrors` 상태에 저장합니다.

```js
formErrors = {
  email: '올바른 이메일 형식으로 입력해 주세요.',
};
```

그 후 `renderFormErrors()`가 에러 메시지를 화면에 표시합니다.

폼 검증도 상태와 렌더링 흐름으로 볼 수 있습니다.

```text
submit 이벤트
→ 입력값 검사
→ formErrors 상태 변경
→ 에러 메시지 렌더링
```

## 13장. GitHub API

API는 Application Programming Interface의 줄임말입니다.

웹 개발에서 API는 다른 서비스의 데이터를 가져오기 위한 주소와 규칙을 뜻하는 경우가 많습니다.

현재 프로젝트는 GitHub API를 사용해 공개 저장소 목록을 가져옵니다.

```text
https://api.github.com/users/{본인아이디}/repos
```

이 주소로 요청하면 GitHub 저장소 데이터가 JSON 배열로 응답됩니다.

### fetch

`fetch`는 JavaScript에서 네트워크 요청을 보내는 함수입니다.

```js
const response = await fetch(url);
```

### async/await

API 요청은 시간이 걸리는 비동기 작업입니다.

`async/await`를 사용하면 비동기 코드를 읽기 쉽게 작성할 수 있습니다.

```js
const loadProjects = async () => {
  const response = await fetch(url);
  const data = await response.json();
};
```

### try/catch

API 요청은 실패할 수 있습니다.

네트워크 문제, 잘못된 URL, GitHub API 제한, 서버 오류가 발생할 수 있기 때문입니다.

그래서 `try/catch`로 실패 상황을 처리합니다.

```js
try {
  const response = await fetch(url);
} catch (error) {
  console.error(error);
}
```

## 14장. API 상태 UI

API를 사용하는 화면은 요청 결과가 오기 전까지 무엇을 보여줄지 결정해야 합니다.

그래서 현재 프로젝트는 `projectStatus` 상태를 사용합니다.

상태 종류:

- `loading`: 데이터를 불러오는 중
- `success`: 데이터를 성공적으로 불러옴
- `error`: 데이터를 불러오지 못함
- `empty`: 요청은 성공했지만 보여줄 데이터가 없음

이렇게 상태를 나누면 사용자는 현재 무슨 일이 일어나고 있는지 알 수 있습니다.

나쁜 예:

```text
아무것도 표시하지 않음
```

좋은 예:

```text
프로젝트를 불러오는 중입니다...
프로젝트를 불러올 수 없습니다.
표시할 프로젝트가 없습니다.
```

API 상태 UI는 실제 서비스에서 매우 중요합니다. 모든 요청이 항상 성공한다고 가정하면 사용자가 문제 상황을 이해할 수 없습니다.

## 15장. 배열 메서드와 데이터 가공

GitHub API에서 받은 데이터는 그대로 화면에 쓰기보다 필요한 형태로 가공해야 합니다.

현재 프로젝트에서 사용하는 배열 메서드는 다음과 같습니다.

### filter

조건에 맞는 항목만 남깁니다.

현재 프로젝트에서는 fork 저장소를 제외할 때 사용합니다.

```js
data.filter(({ fork }) => !fork);
```

### sort

배열을 정렬합니다.

현재 프로젝트에서는 `pushed_at` 기준으로 최신 업데이트순 정렬을 합니다.

### slice

배열의 일부만 잘라냅니다.

현재 프로젝트에서는 저장소가 너무 많이 보이지 않도록 최신 6개만 남깁니다.

### map

배열의 각 항목을 다른 형태로 변환합니다.

현재 프로젝트에서는 GitHub 저장소 객체를 화면에 필요한 프로젝트 카드 데이터로 변환합니다.

### forEach

배열을 순회하면서 작업을 실행합니다.

현재 프로젝트에서는 여러 네비게이션 링크에 이벤트를 연결할 때 사용합니다.

## 16장. 배포

배포는 내가 만든 웹사이트를 다른 사람이 인터넷으로 접속할 수 있게 올리는 과정입니다.

이 미션에서는 GitHub Pages를 사용합니다.

GitHub Pages는 정적 웹사이트를 무료로 배포할 수 있는 기능입니다.

정적 웹사이트란 서버에서 복잡한 계산을 하지 않고 HTML, CSS, JavaScript 파일만으로 동작하는 웹사이트를 말합니다.

배포 후 확인해야 할 것:

- 배포 URL에 접속되는가?
- CSS가 정상 적용되는가?
- JavaScript가 정상 동작하는가?
- GitHub API가 배포 환경에서도 동작하는가?
- 모바일 화면에서도 레이아웃이 깨지지 않는가?
- 다크 모드, 메뉴, 폼 검증이 동작하는가?

## 17장. README

README는 프로젝트를 소개하는 문서입니다.

처음 보는 사람이 이 프로젝트가 무엇인지, 어떻게 실행하는지, 어떤 기술을 사용했는지 이해할 수 있어야 합니다.

README에 포함하면 좋은 내용:

- 프로젝트 이름
- 프로젝트 설명
- 사용 기술
- 주요 기능
- 폴더 구조
- 로컬 실행 방법
- 배포 URL
- 스크린샷
- 구현 기준값

README는 평가자에게 프로젝트의 첫인상을 주는 문서이기도 합니다.

## 18장. 함께 알아두면 좋은 기초 CS

이 미션은 웹 기초 과제이지만, 실제로는 여러 기초 CS 개념과 연결되어 있습니다.

코드를 외우는 것보다 중요한 것은 “브라우저가 왜 이렇게 동작하는가”를 이해하는 것입니다.

### 클라이언트와 서버

웹에서는 보통 사용자의 브라우저를 클라이언트라고 부르고, 데이터를 제공하는 컴퓨터를 서버라고 부릅니다.

현재 프로젝트에서 클라이언트는 사용자의 브라우저입니다.

GitHub API 서버는 저장소 데이터를 제공합니다.

흐름:

```text
브라우저
→ GitHub API에 저장소 데이터 요청
→ GitHub 서버가 JSON 응답
→ 브라우저가 응답을 받아 Projects 섹션 렌더링
```

정적 포트폴리오 사이트는 HTML, CSS, JavaScript 파일을 브라우저에 전달하고, 이후 화면 동작은 브라우저 안에서 실행됩니다.

### 요청과 응답

웹 통신은 요청과 응답으로 이루어집니다.

브라우저가 서버에 무언가를 달라고 보내는 것을 요청이라고 합니다.

서버가 요청에 대한 결과를 보내주는 것을 응답이라고 합니다.

현재 프로젝트에서는 다음 코드가 요청을 보냅니다.

```js
fetch(`https://api.github.com/users/${GITHUB_USERNAME}/repos`);
```

GitHub 서버는 저장소 목록을 JSON으로 응답합니다.

### HTTP 상태 코드

HTTP 상태 코드는 요청이 어떻게 처리되었는지 알려주는 숫자입니다.

자주 보는 상태 코드:

- `200`: 성공
- `404`: 요청한 대상을 찾을 수 없음
- `403`: 접근 제한 또는 요청 횟수 제한
- `500`: 서버 내부 오류

현재 프로젝트에서는 `response.ok`를 확인합니다.

```js
if (!response.ok) {
  throw new Error(`GitHub API error: ${response.status}`);
}
```

응답이 성공이 아니면 에러 상태로 바꾸고, 사용자에게 프로젝트를 불러올 수 없다는 메시지를 보여줍니다.

### URL

URL은 웹에서 자원의 위치를 나타내는 주소입니다.

예시:

```text
https://api.github.com/users/jhkr1/repos
```

구성:

- `https`: 통신 방식
- `api.github.com`: 서버 도메인
- `/users/jhkr1/repos`: 요청 경로

프론트엔드 개발자는 URL을 보고 어떤 서버에 어떤 데이터를 요청하는지 이해할 수 있어야 합니다.

### JSON

JSON은 데이터를 주고받을 때 많이 사용하는 텍스트 형식입니다.

JavaScript 객체와 비슷하게 생겼지만, 서버와 클라이언트가 데이터를 교환하기 위한 형식입니다.

예시:

```json
{
  "name": "portfolio",
  "language": "JavaScript",
  "stargazers_count": 3
}
```

GitHub API 응답도 JSON입니다.

브라우저에서는 다음 코드로 JSON을 JavaScript 데이터로 변환합니다.

```js
const data = await response.json();
```

### 동기와 비동기

동기는 한 작업이 끝날 때까지 다음 작업이 기다리는 방식입니다.

비동기는 시간이 걸리는 작업을 기다리는 동안 다른 작업을 막지 않는 방식입니다.

API 요청은 네트워크 상황에 따라 시간이 달라집니다. 그래서 JavaScript는 `fetch` 같은 네트워크 요청을 비동기로 처리합니다.

현재 프로젝트에서는 `async/await`를 사용해 비동기 코드를 읽기 쉽게 작성합니다.

```js
const loadProjects = async () => {
  const response = await fetch(url);
  const data = await response.json();
};
```

### 이벤트 루프

JavaScript는 기본적으로 한 번에 하나의 작업을 실행합니다.

그런데 클릭, 스크롤, API 응답처럼 언제 발생할지 모르는 작업들이 있습니다.

이런 작업을 처리하기 위해 브라우저는 이벤트 루프라는 구조를 사용합니다.

간단히 말하면 이벤트 루프는 “지금 실행할 수 있는 작업을 순서대로 꺼내 실행하는 흐름”입니다.

현재 프로젝트에서 이벤트 루프와 연결되는 작업:

- 사용자가 버튼을 클릭했을 때 이벤트 핸들러 실행
- 스크롤할 때 `handleScroll()` 실행
- GitHub API 응답이 도착하면 이후 코드 실행
- 폼 입력이 바뀌면 `input` 이벤트 실행

이 개념을 알면 JavaScript가 왜 이벤트 기반으로 동작하는지 이해하기 쉬워집니다.

### 브라우저 렌더링 흐름

브라우저는 대략 다음 흐름으로 화면을 만듭니다.

```text
HTML 파싱
→ DOM 생성
→ CSS 파싱
→ 스타일 계산
→ 레이아웃 계산
→ 페인트
→ 화면 표시
```

JavaScript가 DOM이나 클래스를 바꾸면 브라우저는 필요한 부분을 다시 계산하고 화면을 갱신합니다.

예를 들어 다크 모드 버튼을 클릭하면 다음 일이 일어납니다.

```text
data-theme 변경
→ CSS 변수 값 변경
→ 색상 스타일 재계산
→ 화면 색상 갱신
```

### 메모리와 상태

JavaScript 변수는 브라우저가 페이지를 실행하는 동안 메모리에 저장됩니다.

현재 프로젝트의 `state` 객체도 메모리에 저장되는 데이터입니다.

```js
const state = {
  theme: 'light',
  projects: [],
};
```

하지만 메모리의 값은 새로고침하면 사라집니다.

그래서 다크 모드처럼 새로고침 후에도 유지해야 하는 값은 `localStorage`에 저장합니다.

```js
localStorage.setItem('theme', state.theme);
```

### 캐시

캐시는 한 번 받은 데이터를 다시 빠르게 사용하기 위해 저장해두는 기능입니다.

브라우저는 CSS, JS, 이미지 파일을 캐시할 수 있습니다.

GitHub API 응답도 일정 시간 캐시될 수 있습니다.

배포 후 CSS를 수정했는데 화면이 예전처럼 보이면 브라우저 캐시 때문일 수 있습니다. 이럴 때는 강력 새로고침을 하거나 개발자 도구에서 캐시를 비활성화하고 확인합니다.

## 19장. 디버깅과 개발자 도구

디버깅은 코드의 문제를 찾고 고치는 과정입니다.

프론트엔드 개발에서 가장 중요한 도구는 브라우저 개발자 도구입니다.

Chrome에서는 보통 `F12` 또는 `Command + Option + I`로 열 수 있습니다.

### Elements 탭

Elements 탭에서는 현재 DOM 구조와 적용된 CSS를 볼 수 있습니다.

확인할 수 있는 것:

- HTML 구조가 예상대로 만들어졌는가?
- 클래스가 붙고 빠지는가?
- CSS가 어떤 규칙에 의해 적용되는가?
- 모바일 화면에서 레이아웃이 어떻게 바뀌는가?

햄버거 메뉴를 확인할 때는 모바일 화면으로 줄인 뒤, 메뉴 버튼을 클릭하고 `nav-panel`에 `active` 클래스가 붙는지 보면 됩니다.

### Console 탭

Console 탭에서는 JavaScript 에러와 로그를 확인합니다.

API 요청이 실패하거나, 선택한 DOM 요소가 없거나, 문법 오류가 있으면 Console에 메시지가 나타납니다.

확인할 수 있는 것:

- JavaScript 에러가 있는가?
- `fetch` 요청이 실패했는가?
- 이벤트 핸들러가 실행되는가?

### Network 탭

Network 탭에서는 브라우저가 어떤 파일과 데이터를 요청했는지 볼 수 있습니다.

확인할 수 있는 것:

- `index.html`, `style.css`, `main.js`가 정상 로드되는가?
- GitHub API 요청이 전송되는가?
- 응답 상태 코드가 `200`인가?
- 응답 데이터가 JSON으로 오는가?

GitHub API가 동작하지 않을 때는 Network 탭에서 상태 코드와 응답 내용을 먼저 확인합니다.

### Application 탭

Application 탭에서는 `localStorage` 같은 브라우저 저장소를 확인할 수 있습니다.

다크 모드를 켠 뒤 Application 탭에서 `theme` 값이 저장되는지 확인할 수 있습니다.

새로고침 후에도 다크 모드가 유지된다면 `localStorage` 저장과 복원이 정상 동작하는 것입니다.

## 20장. 기본 보안 감각

프론트엔드에서도 보안 감각이 필요합니다.

이 미션에서 특히 연결되는 개념은 XSS와 HTML 이스케이프입니다.

### XSS

XSS는 Cross-Site Scripting의 줄임말입니다.

사용자가 입력한 값이나 외부 API 데이터에 악성 스크립트가 섞여 들어와 페이지에서 실행되는 문제입니다.

예를 들어 어떤 저장소 설명에 HTML 코드가 들어 있다면, 그 값을 그대로 `innerHTML`에 넣는 것은 위험할 수 있습니다.

현재 프로젝트는 GitHub API 데이터를 카드 HTML로 만들기 전에 `escapeHTML()` 함수를 사용해 특수 문자를 변환합니다.

```js
const escapeHTML = (value) =>
  String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
```

이렇게 하면 `<script>` 같은 문자열이 실제 HTML로 실행되지 않고 텍스트로 표시됩니다.

### target="_blank"와 rel="noreferrer"

새 탭으로 외부 링크를 열 때는 `rel="noreferrer"`를 함께 쓰는 것이 좋습니다.

```html
<a href="https://github.com/jhkr1" target="_blank" rel="noreferrer">
  GitHub
</a>
```

현재 프로젝트의 GitHub 링크도 이 방식을 사용합니다.

## 21장. Git과 GitHub의 역할

Git은 코드 변경 이력을 관리하는 도구입니다.

GitHub는 Git 저장소를 온라인에 올리고 공유할 수 있는 서비스입니다.

이 미션에서 GitHub는 두 가지 역할을 합니다.

첫 번째는 코드를 저장하고 제출하는 저장소 역할입니다.

두 번째는 GitHub API를 통해 Projects 섹션에 표시할 저장소 데이터를 제공하는 역할입니다.

즉, GitHub는 이 프로젝트에서 “코드를 올리는 곳”이면서 동시에 “데이터를 가져오는 외부 서비스”입니다.

### 커밋

커밋은 코드 변경사항을 하나의 기록으로 저장하는 것입니다.

커밋 메시지는 무엇을 바꿨는지 알 수 있게 작성하는 것이 좋습니다.

예시:

```text
Add portfolio layout
Implement dark mode toggle
Connect GitHub API projects
```

### GitHub Pages

GitHub Pages는 GitHub 저장소에 있는 정적 웹사이트를 배포하는 기능입니다.

이 프로젝트는 HTML, CSS, JavaScript만 사용하는 정적 사이트이므로 GitHub Pages로 배포하기 적합합니다.

## 22장. 학습 흐름으로 다시 보기

이 미션을 공부할 때는 파일 단위보다 흐름 단위로 보는 것이 좋습니다.

### 페이지가 처음 열릴 때

```text
브라우저가 index.html 요청
→ HTML 파싱
→ CSS 파일 로드
→ JS 파일 defer로 로드
→ DOM 생성 완료 후 JS 실행
→ init() 실행
→ 테마 복원, 이벤트 연결, 스크롤 관찰, GitHub API 요청
```

### 사용자가 버튼을 클릭할 때

```text
click 이벤트 발생
→ addEventListener로 연결된 함수 실행
→ 상태 변경
→ classList 또는 dataset 변경
→ CSS가 새 상태에 맞게 적용
→ 화면 변화
```

### GitHub 프로젝트가 표시될 때

```text
loadProjects() 실행
→ projectStatus = loading
→ fetch 요청
→ JSON 응답 수신
→ filter, sort, slice, map으로 데이터 가공
→ projectStatus = success
→ innerHTML로 카드 렌더링
```

### 폼을 제출할 때

```text
submit 이벤트 발생
→ preventDefault 실행
→ FormData로 값 읽기
→ validateForm으로 검사
→ formErrors 상태 변경
→ renderFormErrors로 에러 표시
```

이 네 가지 흐름을 설명할 수 있으면, 현재 미션의 핵심 동작을 대부분 이해한 것입니다.

## 23장. 이 미션의 핵심 문장

이 미션의 핵심은 다음 한 문장으로 정리할 수 있습니다.

```text
사용자 이벤트가 발생하면 JavaScript가 상태를 변경하고, 변경된 상태를 기준으로 DOM을 업데이트하여 화면을 바꾼다.
```

모든 기능은 이 흐름으로 설명할 수 있습니다.

다크 모드:

```text
클릭 이벤트
→ theme 상태 변경
→ data-theme 업데이트
→ CSS 변수 변경
→ 화면 색상 변경
```

햄버거 메뉴:

```text
클릭 이벤트
→ isMenuOpen 상태 변경
→ active 클래스 토글
→ 메뉴 표시 변경
```

GitHub API:

```text
페이지 로드
→ loading 상태 표시
→ fetch 요청
→ success/error/empty 상태 변경
→ Projects UI 업데이트
```

폼 검증:

```text
submit 이벤트
→ 입력값 검사
→ formErrors 상태 변경
→ 에러 메시지 렌더링
```

이 흐름을 이해하면 React의 상태, 이벤트, 렌더링 개념도 훨씬 쉽게 이해할 수 있습니다.

## 24장. 미션 완성 기준

이 프로젝트가 완성되었다고 말하려면 다음 요소가 모두 연결되어 있어야 합니다.

프로젝트 구조:

- `index.html`
- `css/style.css`
- `js/main.js`
- `images/`
- `docs/`
- `README.md`

HTML:

- Header, Nav, Main, Section, Article, Footer 사용
- Hero, About, Skills, Projects, Contact, Footer 섹션 구성
- 이미지 `alt` 작성
- 폼 `label` 연결
- 네비게이션 앵커 링크 연결

CSS:

- CSS 변수 사용
- 다크 모드 변수 정의
- 모바일 퍼스트 작성
- 768px, 1024px 브레이크포인트 사용
- Header는 Flexbox
- Projects는 Grid
- hover, transition, shadow 적용

JavaScript:

- `const`, `let` 사용
- `var` 미사용
- `querySelector`, `querySelectorAll` 사용
- `addEventListener` 사용
- `onclick` 미사용
- `classList`로 클래스 조작
- `preventDefault`로 폼 기본 동작 방지

인터랙션:

- 햄버거 메뉴
- 다크 모드
- 부드러운 스크롤
- 스크롤 탑 버튼
- 스크롤 시 헤더 스타일 변경
- 스크롤 애니메이션
- 폼 유효성 검사

API:

- GitHub API 호출
- `fetch`
- `async/await`
- `try/catch`
- 로딩, 성공, 에러, 빈 상태 UI
- 저장소 카드 렌더링

배포:

- GitHub 저장소 URL
- GitHub Pages 배포 URL
- README 정리
- 스크린샷 준비

## 25장. 평가를 통과하기 위한 이해 기준

평가에서 중요한 것은 모든 코드를 외우는 것이 아닙니다.

중요한 것은 각 기능을 다음 방식으로 설명할 수 있는 것입니다.

```text
이 기능은 어떤 문제를 해결하는가?
사용자는 어떤 행동을 하는가?
그 행동은 어떤 이벤트로 감지되는가?
어떤 상태가 바뀌는가?
어떤 DOM이 업데이트되는가?
결과적으로 화면이 어떻게 바뀌는가?
```

이 기준으로 설명할 수 있다면, 단순히 AI가 만든 코드를 제출하는 것이 아니라 프로젝트의 동작 원리를 이해하고 있다고 볼 수 있습니다.
