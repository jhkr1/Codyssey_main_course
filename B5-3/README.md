# Project Task Manager

FastAPI와 Jinja2로 만든 SSR 기반 Project/Task 관리 서비스입니다. Session으로 로그인한 사용자는 자신의 Project와 Task를 관리할 수 있으며, Task 상태는 `TODO → IN_PROGRESS → DONE` 순서로 변경합니다.

## 주요 기능

- 로그인 / 로그아웃
- 로그인 사용자별 Project 생성, 조회, 삭제
- Task 생성 및 상태 변경
- 비로그인 사용자의 보호 페이지 접근 차단
- Project 소유자와 Task 상태를 함께 보여주는 SSR 화면

## 기술 스택

| 구분 | 기술 |
| --- | --- |
| Language | Python 3.12.8 |
| Framework | FastAPI 0.141.1 |
| ORM | SQLAlchemy 2.0.51 |
| Database | SQLite |
| Template | Jinja2 3.1.6 |
| Server | Uvicorn 0.52.1 |

## 프로젝트 구조

```text
B5-3/
├─ auth/
├─ models/
├─ repositories/
├─ services/
├─ routers/
├─ templates/
├─ database.py
├─ main.py
├─ requirements.txt
└─ README.md
```

## 설치 및 실행

Windows, Python 3.10 이상을 기준으로 합니다.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

브라우저에서 `http://127.0.0.1:8000`에 접속합니다.

### Troubleshooting

현재 개발 PC처럼 `ensurepip` 문제로 가상환경 안의 pip가 생성되지 않는 경우에만 아래 명령을 사용합니다.

```bash
python -m pip --python .\.venv\Scripts\python.exe install -r requirements.txt
```

## 테스트 계정

| ID | Password |
| --- | --- |
| test | 1234 |

## 사용 방법

```text
로그인
→ Project 생성
→ Project 상세
→ Task 생성
→ 진행 시작 (TODO → IN_PROGRESS)
→ 완료하기 (IN_PROGRESS → DONE)
→ 로그아웃
```

## 주요 URL

| Method | Path | 보호 | 설명 |
| --- | --- | --- | --- |
| GET / POST | `/login` | 아니오 | 로그인 화면 및 처리 |
| POST | `/logout` | 예 | 로그아웃 |
| GET | `/projects` | 예 | 내 Project 목록 |
| GET / POST | `/projects/new`, `/projects` | 예 | Project 생성 폼 및 처리 |
| GET | `/projects/{project_id}` | 예 | Project 상세와 Task 목록 |
| POST | `/projects/{project_id}/delete` | 예 | Project 삭제 |
| GET / POST | `/projects/{project_id}/tasks/new`, `/projects/{project_id}/tasks` | 예 | Task 생성 폼 및 처리 |
| POST | `/tasks/{task_id}/status` | 예 | Task 상태 변경 |

Jinja2 기반 SSR 흐름에 맞춰 Session 인증을 사용합니다. 보호 경로에서는 FastAPI `Depends`로 로그인 사용자를 확인합니다.

자세한 인증/인가, ORM 관계, 상태 전이, 계층 구조 학습 내용은 [CONCEPTS.md](./CONCEPTS.md)를 참고하세요.

## 문서

- [주요 개념 정리](./CONCEPTS.md)
- [코드 구조와 요청 흐름](./CODE_ARCHITECTURE.md)
