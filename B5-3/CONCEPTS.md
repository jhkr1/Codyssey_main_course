# B5-3 주요 개념 정리

이 문서는 Project Task Manager의 실제 구현을 이해하고, 평가나 발표에서 설계를 설명하기 위한 학습 자료입니다.

## 1. 전체 요청 흐름

```text
Browser
  → SessionMiddleware
  → Depends(get_current_user)
  → Router
  → Service
  → Repository
  → SQLAlchemy ORM
  → SQLite
```

SessionMiddleware는 요청에서 Session을 읽을 수 있게 합니다. 보호 경로에서는 `get_current_user`가 먼저 로그인 사용자를 찾고, Router는 HTTP와 화면 처리를 맡습니다. Service는 업무 규칙을, Repository는 DB 접근을 담당합니다.

## 2. Authentication과 Authorization

Authentication(인증)은 “현재 사용자가 누구인가?”를 확인하는 일입니다. 이 프로젝트에서는 `Depends(get_current_user)`가 Session의 `user_id`로 User를 찾아 인증합니다.

Authorization(인가)은 “이 사용자가 이 Project나 Task에 접근할 수 있는가?”를 확인하는 일입니다. `ProjectService`와 `TaskService`가 `project_id + user_id` 조건으로 소유권을 확인합니다. 예를 들어 User B가 로그인에 성공해도 User A의 Project를 조회하려 하면 인가는 실패합니다.

## 3. Session 기반 인증

로그인 요청은 다음 순서로 처리됩니다.

```text
POST /login
  → AuthService.authenticate()
  → username/password 확인
  → request.session["user_id"] = user.id
```

이후 요청에서는 Session의 `user_id`를 읽고 DB에서 User를 다시 조회합니다. Session에는 password 대신 최소 식별 정보인 `user_id`만 저장합니다. Starlette의 SessionMiddleware는 서명된 cookie를 사용하므로 위변조 방지에 도움을 주지만, 민감한 정보를 담는 용도는 아닙니다.

## 4. FastAPI Depends와 sub-dependency

보호 경로의 `current_user = Depends(get_current_user)`는 Router보다 먼저 실행됩니다.

```text
GET /projects
  → get_current_user
    → Depends(get_db)
    → UserRepository.get_by_id()
  → User 반환
  → Router 실행
```

Session에 user_id가 없거나 해당 User가 DB에 없으면 `AuthenticationRequiredError`가 발생합니다. 이때 Router는 실행되지 않고 exception handler가 `/login`으로 리다이렉트합니다. `Depends(get_db)`가 `get_current_user` 안에서 사용되는 구조를 sub-dependency라고 볼 수 있습니다.

## 5. Middleware와 Depends의 차이

| 구분 | SessionMiddleware | `Depends(get_current_user)` |
| --- | --- | --- |
| 역할 | Session 기능 제공 | 로그인 User 확인 |
| 범위 | 모든 요청 | 적용한 endpoint |
| 인증 차단 | 하지 않음 | 실패 시 endpoint 실행 차단 |

모든 URL을 Middleware에서 막으면 공개 홈과 로그인 화면도 접근할 수 없습니다. 따라서 Middleware는 기능 제공만 하고, 보호가 필요한 Router에만 Depends를 붙입니다.

## 6. SQLAlchemy ORM과 모델

ORM은 DB의 row를 Python 객체처럼 다루게 해주는 방식입니다. 이 프로젝트의 모델은 `User`, `Project`, `Task` 세 개입니다. Repository는 이 ORM 객체를 통해 조회·생성·저장·삭제를 수행합니다.

## 7. 1:N 관계

```text
User 1:N Project
Project 1:N Task
```

한 User는 여러 Project를 가질 수 있고, 각 Project는 한 User에게 속합니다. 또한 한 Project는 여러 Task를 가지며 Task는 하나의 Project에 속합니다.

## 8. ForeignKey와 relationship

ForeignKey는 DB 테이블의 참조 관계입니다.

```text
projects.user_id → users.id
tasks.project_id → projects.id
```

`relationship`은 Python 객체 사이의 탐색 관계입니다.

```text
user.projects
project.owner
project.tasks
task.project
```

즉 ForeignKey는 DB의 연결이고, relationship은 ORM 객체에서 편하게 연관 데이터를 다루는 방법입니다.

## 9. back_populates

`back_populates`는 양방향 relationship의 두 속성이 서로 연결됐음을 알려줍니다.

```text
User.projects ↔ Project.owner
Project.tasks ↔ Task.project
```

그래서 `project.owner`로 소유자를 찾거나 `user.projects`로 소유 Project를 찾는 양쪽 탐색이 가능합니다.

## 10. cascade="all, delete-orphan"

`Project.tasks`에는 `cascade="all, delete-orphan"`이 적용되어 있습니다. Task는 Project 없이 독립적인 업무 의미가 없으므로, Project를 삭제하면 소속 Task도 함께 삭제됩니다.

```text
Project 삭제
  → Task A 삭제
  → Task B 삭제
```

이 정책은 Project에서 분리돼 의미 없는 Task가 남는 orphan 데이터를 막습니다.

## 11. Repository Pattern

Repository는 SQLAlchemy를 사용한 데이터 접근만 담당합니다.

```text
UserRepository    → User 조회/생성
ProjectRepository → Project 조회/생성/삭제
TaskRepository    → Task 조회/생성/저장
```

Repository는 로그인 여부, Project 접근 허용 여부, `TODO → DONE` 전이 가능 여부를 판단하지 않습니다. 예를 들어 Repository는 “Task 3을 찾아줘”를 수행하고, Service는 “Task 3을 DONE으로 바꿔도 되는가?”를 판단합니다.

## 12. Session, commit, refresh

Repository는 호출자로부터 SQLAlchemy `Session`을 전달받아 사용합니다. 새 engine이나 SessionLocal을 만들지 않습니다.

- `db.add()`: 새 객체를 Session에 등록
- `db.commit()`: 변경 내용을 DB에 확정
- `db.refresh()`: DB 기준의 최신 값을 객체에 다시 반영

이 프로젝트에서는 B5-2의 단순한 구조를 유지해 생성·삭제·저장 Repository 메서드가 commit합니다.

## 13. Service Layer

Service는 Repository를 조합하고 업무 규칙을 적용합니다. ProjectService는 사용자의 소유 Project를 찾고, TaskService는 Task의 소속 Project와 현재 User를 확인합니다.

```text
Task 조회
  → 소속 Project 조회
  → 현재 User 소유 여부 확인
  → 상태 전이 가능 여부 확인
  → Repository.save()
```

Router가 아닌 Service에 규칙을 두면 HTTP 요청이 아닌 다른 호출 경로에서도 같은 규칙을 적용할 수 있습니다.

## 14. Task 상태 전이 규칙

```text
TODO → IN_PROGRESS → DONE
```

허용되는 전이는 `TODO → IN_PROGRESS`, `IN_PROGRESS → DONE`뿐입니다. `TODO → DONE`, 역방향 전이, 동일 상태 변경은 TaskService가 거부합니다. 이처럼 단순 CRUD를 넘어 상태에 따른 행동을 제어하는 것이 비즈니스 로직입니다.

## 15. DB CHECK와 Service 검증

DB CHECK 제약은 상태값이 `TODO`, `IN_PROGRESS`, `DONE` 중 하나인지 확인합니다. 반면 Service 검증은 현재 상태에서 목표 상태로 바꾸는 것이 허용되는지 확인합니다.

예를 들어 `TODO`와 `DONE`은 모두 DB에서 유효한 값이지만 `TODO → DONE`은 업무 규칙상 허용되지 않습니다. DB 제약과 Service 규칙은 서로 대체하지 않습니다.

## 16. Router의 역할

Router는 URL, HTTP Method, Form 입력, Depends, Service 호출, TemplateResponse, RedirectResponse를 담당합니다. Router는 SQLAlchemy query를 직접 작성하지 않고, 소유권 판단이나 상태 전이 규칙도 직접 구현하지 않습니다.

Service의 `ValueError`는 Router가 HTTP 결과로 바꿉니다. 다른 User의 Project/Task 접근은 404, 잘못된 상태 전이는 400으로 응답합니다.

## 17. Jinja2 SSR

SSR은 서버가 HTML을 렌더링해 브라우저에 반환하는 방식입니다. 이 프로젝트에서는 Jinja2가 로그인 상태에 따른 UI, Project 정보, 소유자 이름, Task 목록과 상태를 화면에 출력합니다.

Project 상세에서는 `project.owner.username`과 `tasks`를 함께 사용합니다. 이 화면은 ORM 연관 데이터를 실제 UI에 사용하는 예입니다.

## 18. PRG Pattern

PRG는 Post / Redirect / Get 패턴입니다.

```text
POST /projects
  → Project 생성
  → 303 Redirect
  → GET /projects
```

로그인 성공, 로그아웃, Project 생성·삭제, Task 생성·상태 변경에 적용했습니다. 사용자가 새로고침할 때 같은 POST 요청이 반복되는 문제를 줄입니다. 로그인 실패는 즉시 오류를 보여줘야 하므로 로그인 템플릿을 다시 렌더링합니다.

## 19. UI 검증과 서버 검증

화면은 TODO일 때만 `진행 시작`, IN_PROGRESS일 때만 `완료하기` 버튼을 보여주며 DONE에는 버튼을 보여주지 않습니다. 하지만 UI 제한만으로는 충분하지 않습니다. 사용자가 직접 HTTP 요청을 만들 수 있으므로 TaskService가 상태 전이를 다시 검증합니다.

## 20. 전체 사용자 흐름

```text
로그인
→ Project 목록
→ Project 생성
→ Project 상세
→ Task 생성
→ TODO
→ IN_PROGRESS
→ DONE
→ 결과 확인
→ 로그아웃
```

개발자 관점의 흐름은 `Request → Authentication → Router → Authorization / Business Logic → Repository → DB → Template / Redirect`입니다.

## 21. 예상 질문과 답변

### 인증과 인가의 차이는 무엇인가요?

인증은 현재 요청을 보낸 사람이 누구인지 확인하는 과정이고, 인가는 그 사람이 특정 리소스에 접근해도 되는지 확인하는 과정입니다. 이 프로젝트에서는 get_current_user가 인증을, ProjectService와 TaskService가 인가를 담당합니다.

### Depends를 왜 사용하나요?

보호 경로마다 Session을 읽고 User를 찾는 코드를 반복하지 않기 위해 사용합니다. Dependency가 먼저 실행되므로 인증 실패 시 Router 본문이 실행되지 않는 장점도 있습니다.

### Middleware와 Depends는 어떻게 다른가요?

SessionMiddleware는 모든 요청에서 Session 기능을 제공합니다. Depends는 필요한 endpoint에만 적용해 로그인 User를 검증하므로 공개 페이지와 보호 페이지를 함께 운영할 수 있습니다.

### Session에는 왜 user_id만 저장하나요?

현재 사용자를 식별하는 데 필요한 최소 정보이기 때문입니다. password 같은 민감한 값을 Session에 넣지 않고, user_id로 DB에서 User를 다시 조회합니다.

### ForeignKey와 relationship의 차이는 무엇인가요?

ForeignKey는 DB 테이블의 참조 관계이고, relationship은 Python ORM 객체의 연관 탐색 기능입니다. 둘을 함께 사용하면 DB 무결성과 객체 수준의 편의성을 모두 얻습니다.

### back_populates는 왜 사용하나요?

양쪽 relationship이 같은 관계의 반대편임을 명확히 연결하기 위해 사용합니다. 그래서 User에서 Project를, Project에서 User를 자연스럽게 탐색할 수 있습니다.

### cascade는 왜 사용하나요?

Task가 Project에 종속돼 있기 때문입니다. Project를 삭제할 때 Task를 함께 삭제해 의미 없는 orphan 데이터를 남기지 않습니다.

### Repository와 Service의 차이는 무엇인가요?

Repository는 DB에서 데이터를 읽고 쓰는 역할입니다. Service는 그 데이터를 사용해 소유권 확인, 상태 전이 같은 업무 규칙을 판단합니다.

### 상태 변경 로직을 Service에 둔 이유는 무엇인가요?

상태 전이는 단순 저장이 아니라 업무 규칙입니다. Router나 UI에 두면 다른 호출 경로에서 우회될 수 있으므로 Service가 최종적으로 검증합니다.

### DB CHECK와 Service 검증은 왜 둘 다 필요한가요?

CHECK는 유효한 상태값만 저장하게 하는 최후의 DB 보호 장치입니다. Service는 값 자체가 아니라 상태 전이 순서라는 업무 규칙을 검증합니다.

### 다른 사용자의 Project에 접근하면 어떻게 되나요?

로그인에는 성공해도 ProjectService 또는 TaskService의 소유권 조건을 통과하지 못합니다. Router는 이를 404로 처리해 다른 사용자의 데이터 존재를 불필요하게 노출하지 않습니다.

### UI에서 버튼을 숨겼는데 Service 검증이 필요한가요?

필요합니다. 화면을 거치지 않고 HTTP 요청을 직접 보낼 수 있기 때문입니다. UI는 사용성을 돕고, Service는 실제 규칙을 보장합니다.

### PRG 패턴은 왜 사용하나요?

POST 처리 뒤 GET으로 이동하면 새로고침으로 동일한 POST가 반복되는 일을 줄일 수 있습니다. 이 프로젝트의 데이터 변경 요청은 대부분 303 Redirect를 사용합니다.
