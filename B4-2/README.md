# SceneLog — React 영화 감상 기록장

영화를 보고 느낀 점을 등록하고, 목록·상세에서 다시 확인하며 수정·삭제할 수 있는 React SPA입니다. 이 프로젝트의 목적은 디자인이 아니라 React의 **컴포넌트, state, 이벤트, 라우팅, 비동기 데이터 흐름**을 직접 확인하는 것입니다.

## 가장 빠른 실행 및 종료 (Docker)

이 프로젝트는 Docker로 실행할 수 있습니다. PowerShell에서 프로젝트 폴더로 이동한 뒤 실행하세요.

```powershell
cd "C:\Users\KSTEC-01\Desktop\Codyssey_main_course\B4-2"
docker compose up
```

실행이 완료되면 [http://localhost:5173](http://localhost:5173)을 브라우저에서 엽니다.

종료는 두 단계입니다.

1. `docker compose up`이 실행 중인 터미널에서 `Ctrl + C`를 누릅니다.
2. 같은 폴더의 새 PowerShell에서 아래 명령어를 실행해 컨테이너와 네트워크를 정리합니다.

```powershell
docker compose down
```

다시 실행할 때는 다시 `docker compose up`만 입력하면 됩니다.

## 1. 시작 전: 실행 방법 선택하기

이 프로젝트는 아래 두 방법 중 하나로 실행할 수 있습니다.

| 방법 | 추천 대상 | 필요한 것 |
| --- | --- | --- |
| A. Windows에 Node.js 설치 | 프론트엔드 개발을 계속할 사람 | Node.js LTS 설치 |
| B. Docker로 실행 | 이미 Docker가 있고 Windows에 Node를 설치하고 싶지 않은 사람 | Docker Desktop |

> Docker 컨테이너에 설치된 Node.js는 Windows PowerShell에서 사용할 수 없습니다. `docker run ... node -v`가 성공하지만 `node -v`가 실패하는 것은 정상입니다. 두 명령어가 서로 다른 컴퓨터 환경(컨테이너 / 내 Windows)에서 실행되기 때문입니다.

### A. Windows에 Node.js 설치하기

이 프로젝트를 실행하려면 **Node.js**가 필요합니다. npm은 Node.js를 설치하면 함께 설치됩니다.

1. [Node.js 공식 다운로드 페이지](https://nodejs.org/en/download)로 이동합니다.
2. `LTS`라고 표시된 버전을 선택합니다. `Current`보다 LTS가 과제 개발에 안정적입니다.
3. Windows Installer (`.msi`)를 내려받아 실행합니다.
4. 설치 화면에서는 기본값을 유지한 채 `Next`를 눌러 설치합니다. 특히 `npm package manager` 항목은 선택된 상태여야 합니다.
5. 설치가 끝나면 **PowerShell 또는 VS Code 터미널을 완전히 닫고 새로 엽니다.**

아래 두 명령어를 입력해 숫자가 출력되면 설치가 성공한 것입니다.

```powershell
node -v
npm -v
```

`npm is not recognized`가 다시 나오면 터미널을 재시작해도 같은지 확인하세요. 계속된다면 Windows를 한 번 재시작한 뒤 다시 확인합니다.

## 2. 프로젝트 실행하기 — Windows Node.js 방식

### 2-1. 터미널에서 프로젝트 폴더로 이동

```powershell
cd "C:\Users\KSTEC-01\Desktop\Codyssey_main_course\B4-2"
```

현재 폴더가 맞는지 확인하려면 다음을 입력합니다. `package.json`이 보여야 합니다.

```powershell
Get-ChildItem
```

### 2-2. 필요한 라이브러리 설치

처음 한 번만 실행합니다.

```powershell
npm install
```

정상적으로 끝나면 `node_modules` 폴더와 `package-lock.json` 파일이 생깁니다. `node_modules`는 용량이 크므로 GitHub에 올리지 않습니다. 이미 `.gitignore`에 등록되어 있습니다.

### 2-3. 개발 서버 실행

```powershell
npm run dev
```

터미널에 아래와 비슷한 주소가 보입니다.

```text
Local: http://localhost:5173/
```

`Ctrl`을 누른 채 이 주소를 클릭하거나, 브라우저 주소창에 붙여 넣습니다. 서버를 종료하려면 터미널에서 `Ctrl + C`를 누릅니다.

## 3. 프로젝트 실행하기 — Docker 방식

이미 Docker가 설치되어 있다면 Windows에 Node.js를 별도로 설치하지 않고 실행할 수 있습니다. 프로젝트 폴더에서 아래 명령어 하나만 실행하세요.

```powershell
docker compose up
```

처음 실행하면 Docker가 다음을 자동으로 처리합니다.

1. Node 24 컨테이너를 준비합니다.
2. `npm install`로 라이브러리를 설치합니다.
3. Vite 개발 서버를 실행합니다.

완료되면 브라우저에서 아래 주소를 엽니다.

```text
http://localhost:5173
```

서버를 멈추려면 실행 중인 터미널에서 `Ctrl + C`를 누릅니다. 컨테이너를 완전히 정리하려면 새 터미널에서 다음을 실행합니다.

```powershell
docker compose down
```

### Docker 방식 문제 해결

| 상황 | 해결 |
| --- | --- |
| `docker compose` 명령이 없음 | Docker Desktop을 최신 버전으로 설치하고 다시 실행 |
| 5173 포트를 사용 중이라는 오류 | `compose.yaml`의 왼쪽 포트를 `5174:5173`으로 바꾸고 `http://localhost:5174` 접속 |
| 패키지 설치가 멈춤 | 인터넷 연결을 확인하고 `Ctrl + C` 후 `docker compose up` 재실행 |
| 설치를 처음부터 다시 하고 싶음 | `docker compose down -v` 후 `docker compose up` 실행 |

> Docker 방식에서는 `npm install`, `npm run dev` 앞에 매번 `docker`를 붙일 필요가 없습니다. `docker compose up`이 두 작업을 모두 대신합니다.

## 4. Supabase 연결하기 — 평가용 실제 CRUD

**이 프로젝트는 Supabase 설정이 있어야 실행됩니다.** `VITE_SUPABASE_URL` 또는 `VITE_SUPABASE_ANON_KEY`가 없으면 화면의 오류 UI에 설정 방법이 표시됩니다. 등록·수정·삭제는 모두 원격 데이터베이스를 사용합니다.

### 3-1. Supabase 프로젝트 만들기

1. [Supabase](https://supabase.com/)에 가입하고 로그인합니다.
2. `New project`를 선택합니다.
3. 프로젝트 이름과 데이터베이스 비밀번호를 설정한 뒤 생성합니다.
4. 프로젝트 준비가 끝나면 왼쪽 메뉴의 `SQL Editor`를 엽니다.

### 3-2. movies 테이블 만들기

1. 이 프로젝트의 [supabase-schema.sql](./supabase-schema.sql) 파일을 엽니다.
2. 파일 안의 SQL 전체를 복사합니다.
3. Supabase SQL Editor에 붙여 넣고 `Run`을 누릅니다.
4. 왼쪽 `Table Editor`에 `movies` 테이블이 생겼는지 확인합니다.

이 SQL은 영화 제목, 감독, 개봉 연도, 장르, 평점, 감상, 생성일을 저장하는 테이블과 개발용 접근 정책을 만듭니다.

### 3-3. API 주소와 키 찾기

Supabase 프로젝트에서 `Project Settings` → `API`로 이동합니다.

- `Project URL`을 복사합니다.
- `Project API keys`의 `anon` 또는 `publishable` 키를 복사합니다.

> `service_role` 키는 절대로 프론트엔드나 `.env`에 넣지 마세요. 이 프로젝트에는 공개용 `anon`/`publishable` 키만 사용합니다.

### 3-4. .env 파일 만들기

프로젝트 최상위 폴더에서 `.env.example` 파일을 복사하여 이름을 `.env`로 바꿉니다.

PowerShell에서는 아래 명령어를 사용할 수 있습니다.

```powershell
Copy-Item .env.example .env
```

`.env`를 열어 실제 값으로 교체합니다.

```env
VITE_SUPABASE_URL=https://내-프로젝트-주소.supabase.co
VITE_SUPABASE_ANON_KEY=내-anon-또는-publishable-키
```

저장한 뒤 개발 서버를 실행 중이었다면 `Ctrl + C`로 종료하고 다시 `npm run dev`를 실행합니다. Vite는 시작할 때 환경변수를 읽습니다.

## 5. 기능 테스트 시나리오

Supabase 연결 후 아래 순서대로 확인하세요. 이 흐름이 곧 평가의 CRUD 확인 항목입니다.

1. `/movies`에서 기존 영화 목록 또는 빈 상태가 보이는지 확인합니다.
2. `+ 새 기록`을 누릅니다.
3. 제목·감독·한 줄 감상을 비우고 저장해 필수값 오류가 보이는지 확인합니다.
4. 값을 입력하고 저장합니다. 버튼이 `처리 중…`으로 바뀐 뒤 상세 페이지로 이동해야 합니다.
5. 브라우저를 새로고침해도 방금 만든 기록이 남아 있는지 확인합니다. 남아 있다면 원격 DB 저장 성공입니다.
6. `수정하기`에서 내용을 바꾸고 저장합니다.
7. `삭제하기`를 누르고 목록으로 돌아가는지 확인합니다.
8. 주소창에 존재하지 않는 주소(예: `/wrong-address`)를 입력해 404 페이지가 보이는지 확인합니다.
9. 목록에서 장르 필터 버튼을 눌러 카드 목록이 바뀌는지 확인합니다.

## 6. 배포하기 — Vercel 예시

배포 전에 GitHub 계정과 GitHub 저장소가 필요합니다.

### 5-1. GitHub에 코드 올리기

`.env`는 올리면 안 됩니다. `.gitignore`에 포함되어 있는지 먼저 확인합니다.

```powershell
git init
git add .
git commit -m "feat: create SceneLog React SPA"
git branch -M main
git remote add origin https://github.com/내아이디/저장소이름.git
git push -u origin main
```

GitHub 웹사이트에서 `.env` 파일 또는 Supabase 키가 올라가지 않았는지 반드시 확인합니다.

### 5-2. Vercel 배포

1. [Vercel](https://vercel.com/)에 GitHub 계정으로 로그인합니다.
2. `Add New` → `Project`를 누릅니다.
3. 방금 만든 GitHub 저장소를 Import합니다.
4. Framework Preset이 `Vite`로 잡혔는지 확인합니다.
5. `Environment Variables`에 아래 두 값을 각각 추가합니다.

```text
VITE_SUPABASE_URL = Supabase Project URL
VITE_SUPABASE_ANON_KEY = Supabase anon/publishable key
```

6. `Deploy`를 누릅니다.
7. 배포가 끝난 URL에서 4장의 테스트 시나리오를 다시 실행합니다.

배포 후 환경변수를 새로 추가하거나 수정했다면 `Redeploy`해야 반영됩니다.

## 7. 자주 만나는 문제 해결

| 문제 | 확인/해결 방법 |
| --- | --- |
| `npm is not recognized` | Node.js LTS 설치 후 터미널을 완전히 다시 열고 `npm -v` 확인 |
| `npm install`이 실패 | 인터넷 연결 확인 후 다시 실행. 프록시/학교 네트워크라면 다른 네트워크에서 시도 |
| 빈 화면이 보임 | 브라우저 개발자 도구(F12) Console 오류 확인. 터미널의 Vite 오류도 함께 확인 |
| Supabase 요청이 실패 | `.env` 키 이름과 값 확인 → 개발 서버 재시작 → 테이블 생성 여부 확인 |
| 등록했는데 새로고침하면 사라짐 | `.env`가 실제 Supabase 값인지 확인하고, Supabase 테이블·RLS 정책을 점검 |
| 배포 후 CRUD가 실패 | Vercel Environment Variables 두 개를 등록했는지 확인하고 Redeploy |
| 새로고침 시 404 | Vercel은 Vite SPA 라우팅을 기본 지원한다. 다른 호스팅이라면 SPA rewrite 설정 필요 |

## 8. 프로젝트 구조와 기술 스택

```text
src/
├─ pages/        라우트 단위 화면
├─ components/   재사용 UI 컴포넌트
├─ hooks/        목록/상세 데이터 요청 custom hook
└─ lib/          Supabase 클라이언트와 CRUD 함수
```

- React 18
- React Router DOM
- Vite
- Supabase JavaScript Client
- 순수 CSS

## 9. 제공 라우트

| 주소 | 화면 |
| --- | --- |
| `/` | 홈과 최근 영화 기록 |
| `/movies` | 영화 목록·장르 필터 |
| `/movies/new` | 새 기록 등록 |
| `/movies/:id` | 특정 기록 상세·삭제 |
| `/movies/:id/edit` | 특정 기록 수정 |
| `/about` | 서비스 소개 |
| 그 외 | Not Found 페이지 |

## 10. 학습 자료

평가 대비 개념과 예상 답변은 [MISSION_STUDY_GUIDE.md](./MISSION_STUDY_GUIDE.md)를 읽으세요. 특히 `이벤트 → state 변화 → re-render`, `props와 state의 차이`, `useEffect 의존성`, `loading/error/empty UI`를 자신의 말로 설명할 수 있어야 합니다.
