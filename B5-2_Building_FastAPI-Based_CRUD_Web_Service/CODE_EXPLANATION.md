이 문서는 FastAPI를 활용한 웹 애플리케이션의 핵심 흐름인 **PRG(Post-Redirect-Get) 패턴과 레이어 분리 구조**를 깊이 있게 분석하기 위한 확장 학습서이다. 코드의 단순 실행을 넘어, 왜 이러한 구조가 현대 웹 개발의 표준으로 자리 잡았는지 그 철학을 이해하는 데 목적이 있다.

---

# 코드 리뷰: PRG 패턴과 계층형 아키텍처 (Deep Dive)

## 0장. 이 과제의 진짜 핵심

이 과제의 핵심은 "메모 CRUD를 만들었다"에서 끝나지 않는다. 더 중요한 목표는 **브라우저 요청이 서버 내부에서 어떤 책임 단위로 이동하는지 설명할 수 있게 되는 것**이다.

즉, 완성된 앱을 볼 때 다음 흐름을 머릿속으로 그릴 수 있어야 한다.

```text
브라우저
  -> Router
  -> Service
  -> Repository
  -> SQLAlchemy Session
  -> SQLite DB
  -> Repository
  -> Service
  -> Router
  -> Jinja2 Template
  -> HTML 응답
  -> 브라우저
```

여기서 각 요소는 단순히 폴더를 나누기 위한 장식이 아니다.

| 구성 요소 | 담당 질문 | 실제 코드 예시 |
| :--- | :--- | :--- |
| Router | 어떤 URL 요청을 받았고, 어떤 응답을 돌려줄 것인가? | `routers/memo_router.py` |
| Service | 이 기능에서 지켜야 할 업무 규칙은 무엇인가? | `services/memo_service.py` |
| Repository | DB에서 어떻게 저장하고 조회할 것인가? | `repositories/memo_repo.py` |
| Model | DB 테이블은 어떤 Python 객체로 표현되는가? | `models/memo.py` |
| Template | 사용자에게 어떤 HTML 화면을 보여줄 것인가? | `templates/*.html` |

이 과제는 작게 보면 메모 앱이지만, 크게 보면 **웹 애플리케이션의 표준적인 책임 분리 연습**이다. 나중에 로그인, 권한, 댓글, 게시글-사용자 관계 같은 기능이 추가되어도 같은 사고방식으로 확장할 수 있다.

---

## 0-1장. GET과 POST를 나누는 이유

웹 요청은 크게 **조회 요청**과 **변경 요청**으로 나눌 수 있다.

| 요청 목적 | HTTP 메서드 | 예시 |
| :--- | :--- | :--- |
| 화면을 보여준다 | GET | `/`, `/memos`, `/memos/1`, `/memos/create` |
| 데이터를 바꾼다 | POST | `/memos/create`, `/memos/1/edit`, `/memos/1/delete` |

GET은 데이터를 바꾸지 않는 요청이어야 한다. 그래서 새로고침하거나, 링크를 공유하거나, 브라우저가 다시 요청해도 안전해야 한다. 반대로 POST는 데이터 등록, 수정, 삭제처럼 서버 상태를 바꾸는 요청에 사용한다.

삭제를 GET 링크로 만들지 않고 POST 폼으로 처리하는 이유도 여기에 있다. 링크 클릭, 브라우저 미리보기, 검색엔진 크롤러 같은 동작이 의도치 않게 데이터를 삭제하면 안 되기 때문이다.

---

## 0-2장. SSR과 TemplateResponse의 의미

이 프로젝트는 API 서버만 만드는 과제가 아니라, **서버가 HTML 화면까지 만들어서 브라우저에 전달하는 SSR(Server-Side Rendering) 방식**을 연습한다.

```text
JSON API 방식:
서버 -> JSON 데이터 -> 프론트엔드가 화면 생성

SSR 방식:
서버 -> 완성된 HTML -> 브라우저가 바로 화면 표시
```

FastAPI에서는 `Jinja2Templates`와 `TemplateResponse`가 SSR의 핵심이다.

```python
return templates.TemplateResponse(
    request=request,
    name="list.html",
    context={"request": request, "memos": service.get_memos()},
)
```

여기서 `context`는 템플릿에 전달되는 데이터 꾸러미이다. 예를 들어 `list.html`은 `memos` 값을 받아서 반복문으로 목록을 출력할 수 있다.

중요한 점은, 템플릿은 DB를 직접 조회하지 않는다는 것이다. 템플릿은 이미 라우터가 넘겨준 데이터를 화면에 표시하는 역할만 맡는다.

---

## 0-3장. HTML Form 데이터가 Python 값이 되는 과정

등록/수정 화면의 핵심은 HTML Form이다. `templates/form.html`에는 다음과 같은 입력 요소가 있다.

```html
<input type="text" id="title" name="title">
<textarea id="content" name="content"></textarea>
```

여기서 중요한 속성은 `id`가 아니라 `name`이다. 브라우저는 폼을 제출할 때 `name`을 key로 사용해서 데이터를 보낸다.

```text
title=입력한 제목
content=입력한 내용
```

FastAPI 라우터에서는 이 값을 `Form(...)`으로 받는다.

```python
@router.post("/memos/create")
def create_memo(
    title: str = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    MemoService(db).create_memo(title, content)
    return RedirectResponse(url="/memos", status_code=303)
```

즉, `name="title"`은 라우터의 `title: str = Form(...)`와 연결되고, `name="content"`는 `content: str = Form(...)`와 연결된다.

JSON API를 만들 때는 Pydantic 모델을 요청 본문으로 받는 경우가 많지만, 이 과제처럼 HTML Form 기반 SSR을 만들 때는 `Form()` 파라미터가 더 직접적이다. 나중에 코드가 커지면 Form으로 받은 값을 서비스에 넘기기 전에 별도 DTO나 Pydantic 모델로 정리할 수도 있다.

---

## 1장. PRG 패턴의 탄생 배경: 중복 제출의 공포

비유하자면, PRG 패턴은 **"주문서 전달 후 영수증을 건네주는 것"**과 같다. 만약 손님이 주문서를 직접 주방에 던져놓고 주방 앞을 서성인다면, 손님이 주문서를 또 제출할 위험이 있다. PRG는 주문을 받은 뒤 "주문이 완료되었습니다. 저쪽 테이블로 가서 기다리세요"라고 안내하여 주방 앞 혼잡을 막는 것이다.

### 1-1. 왜 303 Redirect인가?
처음에는 "그냥 페이지를 보여주면 되지 왜 굳이 한 번 더 이동하는가?"라는 의문이 들 수 있다. 하지만 브라우저의 '새로고침(F5)' 동작은 **마지막으로 수행한 HTTP 요청을 다시 보내는 것**이다.

| 상태 | 요청 종류 | 행동 | 결과 |
| :--- | :--- | :--- | :--- |
| **PRG 미적용** | POST | 데이터 저장 | 화면에 결과 출력 |
| **새로고침** | **POST** | **데이터 재전송** | **데이터 중복 저장** |
| **PRG 적용** | POST | 데이터 저장 | **303 리다이렉트** |
| **이동 후** | GET | 목록 조회 | 화면 출력 |
| **새로고침** | **GET** | **목록 재조회** | **데이터 안전** |

`303 See Other`는 "POST 처리는 끝났으니, 이제 다른 주소를 GET으로 조회하라"는 의미에 가깝다. 그래서 등록, 수정, 삭제가 끝난 뒤에는 다음처럼 응답한다.

```python
return RedirectResponse(url="/memos", status_code=303)
```

이렇게 하면 사용자가 결과 화면에서 새로고침을 눌러도 마지막 요청은 POST가 아니라 GET이 된다. 따라서 같은 메모가 두 번 저장되거나, 같은 삭제가 반복되는 문제를 막을 수 있다.

---

## 2장. 계층형 아키텍처: 역할의 분리

비유하자면, 레이어 분리는 **"대형 프랜차이즈 식당의 업무 분담"**과 같다. 종업원(Router)은 손님을 응대하고, 요리사(Service)는 레시피대로 요리하며, 식자재 담당자(Repository)는 창고에서 재료를 가져온다. 요리사가 창고까지 직접 뛰어다니면 요리 속도가 느려지고 주방이 엉망이 된다.

### 2-1. 계층별 책임 명세

```text
┌──────────────────────────────────────────────────────────┐
│ [Router] : 요청 수신 및 응답 제어 (입구)                  │
└─────────────┬────────────────────────────────────────────┘
              │ (Data Transfer Object)
┌─────────────▼────────────────────────────────────────────┐
│ [Service] : 비즈니스 로직 (요리 방법, 유효성 검사)       │
└─────────────┬────────────────────────────────────────────┘
              │ (Domain Object / Entity)
┌─────────────▼────────────────────────────────────────────┐
│ [Repository] : 데이터 영속성 (식자재 창고 접근)          │
└──────────────────────────────────────────────────────────┘
```

비전공자 관점에서는 **"각자 자기 일만 확실히 한다"**고 기억하면 된다. 라우터는 손님 대면, 서비스는 레시피 준수, 저장소는 재료 관리만 담당한다.

### 2-2. 이 구조가 중요한 이유

작은 앱에서는 라우터 안에 DB 쿼리까지 모두 넣어도 당장은 작동한다. 하지만 기능이 늘어나면 다음 문제가 생긴다.

| 문제가 생기는 상황 | 한 파일에 몰아넣었을 때 | 계층을 나눴을 때 |
| :--- | :--- | :--- |
| URL이 바뀐다 | DB 코드와 화면 코드까지 같이 흔들림 | Router만 수정 |
| 저장 규칙이 바뀐다 | 여러 라우터에서 중복 수정 | Service만 수정 |
| DB 조회 방식이 바뀐다 | 비즈니스 코드까지 같이 수정 | Repository만 수정 |
| 화면이 바뀐다 | 저장 로직과 섞여 읽기 어려움 | Template 중심으로 수정 |

레이어 분리는 코드를 예쁘게 보이게 하려는 장식이 아니라, **변경이 생겼을 때 수정 범위를 작게 만들기 위한 설계 방법**이다.

---

## 3장. 라우터 계층 (routers/memo_router.py)

```python
@router.post("/memos/create")
def create_memo(title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    # 1. 서비스 호출을 통한 비즈니스 로직 처리
    MemoService(db).create_memo(title, content)
    # 2. 리다이렉트 응답 (PRG 패턴)
    return RedirectResponse(url="/memos", status_code=303)
```

라우터는 애플리케이션의 **현관문**이다. 여기서 중요한 것은 `Depends(get_db)`이다. 이는 FastAPI의 의존성 주입(Dependency Injection) 시스템을 활용하는 것인데, 비유하자면 **"필요할 때마다 알아서 세팅되는 개인 비서"**를 두는 것과 같다. 개발자가 직접 데이터베이스 연결을 맺고 끊는 수고를 덜어준다.

라우터가 해야 할 일은 다음 정도로 제한하는 것이 좋다.

```text
1. URL과 HTTP 메서드를 연결한다.
2. Form 데이터나 Path Parameter를 받는다.
3. DB Session 같은 의존성을 주입받는다.
4. Service를 호출한다.
5. TemplateResponse 또는 RedirectResponse를 반환한다.
```

반대로 라우터가 직접 SQLAlchemy 쿼리를 길게 작성하기 시작하면 책임이 섞인다. 라우터는 "웹 요청과 응답의 흐름"을 담당하고, 데이터 접근은 Repository에 맡기는 것이 이 과제의 핵심이다.

---

## 4장. 서비스 계층 (services/memo_service.py)

```python
class MemoService:
    def __init__(self, db: Session):
        self.repo = MemoRepository(db)

    def create_memo(self, title: str, content: str):
        return self.repo.create(title, content)
```

서비스 계층은 시스템의 **두뇌**이다. 만약 "메모의 제목은 반드시 5자 이상이어야 한다"는 규칙이 생긴다면 어디에 적어야 할까? 라우터에 적으면 나중에 API 호출이 아닌 다른 경로로 메모를 생성할 때 규칙을 놓칠 수 있다. 따라서 모든 비즈니스 규칙은 서비스 계층에 모아두어야 한다.

현재 서비스 코드는 Repository를 거의 그대로 호출하는 얇은 구조이다. 이것은 과제 초반에는 자연스럽다. 다만 서비스 계층이 존재하기 때문에 나중에 다음과 같은 규칙을 쉽게 추가할 수 있다.

```python
def create_memo(self, title, content):
    title = title.strip()
    content = content.strip()

    if not title:
        raise ValueError("제목은 필수입니다.")

    return self.repo.create(title, content)
```

이런 검증을 Router에 넣을 수도 있지만, Service에 두면 "메모를 생성할 때 반드시 지켜야 하는 규칙"이 한곳에 모인다.

---

## 5장. 저장소 계층 (repositories/memo_repo.py)

```python
class MemoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, content: str):
        memo = Memo(title=title, content=content)
        self.db.add(memo)
        self.db.commit()
        return memo
```

저장소 계층은 **데이터베이스와의 소통창구**이다. 이곳은 SQL 쿼리나 ORM 문법이 지저분하게 섞이는 곳이다. 이곳을 분리해두면 나중에 데이터베이스를 SQLite에서 PostgreSQL로 바꾸더라도 서비스 계층의 코드는 단 한 줄도 수정할 필요가 없다.

Repository에서 중요한 사고방식은 "무엇을 조회할지"와 "어떻게 조회할지"를 분리하는 것이다.

```text
Service:
메모 목록이 필요하다.

Repository:
Memo 테이블에서 전체 행을 query로 가져온다.
```

서비스는 업무 언어에 가깝고, 저장소는 DB 언어에 가깝다. 이 둘을 분리하면 코드가 훨씬 읽기 쉬워진다.

---

## 6장. 의존성 주입의 마법

처음에는 왜 굳이 `db` 객체를 인자로 계속 넘기는지 의문이 들 수 있다. 하지만 이를 통해 **테스트가 쉬워진다.** 서비스나 저장소 함수를 테스트할 때, 실제 DB가 아닌 '가짜 DB(Mock)'를 주입하기만 하면 테스트가 가능하기 때문이다.

현재 프로젝트의 `database.py`에는 다음 구조가 있다.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

여기서 `yield` 앞은 요청 처리 전에 실행되고, `yield` 뒤의 `finally` 블록은 요청 처리가 끝난 뒤 실행된다. 즉, FastAPI는 요청마다 DB 세션을 하나 열고, 응답이 끝나면 닫는 흐름을 만들어준다.

```text
요청 시작
  -> SessionLocal()로 DB 세션 생성
  -> Router / Service / Repository에서 사용
  -> 응답 반환
  -> finally에서 db.close()
```

이 구조 덕분에 라우터 함수마다 직접 `SessionLocal()`과 `close()`를 반복해서 쓰지 않아도 된다.

---

## 7장. 트랜잭션의 개념 (Commit과 Rollback)

비유하자면, `commit`은 **"은행 창구에서 계좌 이체 버튼을 누르는 것"**이다. 버튼을 누르기 전까지는 돈이 이동한 것처럼 보여도 실제로는 처리되지 않는다. `db.commit()`은 모든 작업이 안전하게 완료되었음을 데이터베이스에 공식적으로 선언하는 행위이다.

SQLAlchemy Session은 DB 작업을 잠시 모아두는 작업 공간처럼 볼 수 있다.

```text
db.add(memo)
  -> 세션에 새 객체 등록

db.commit()
  -> 실제 DB 파일에 변경사항 반영

db.refresh(memo)
  -> DB에서 생성된 id 같은 값을 객체에 다시 반영
```

현재 `create()` 메서드는 `commit()`까지 수행하므로 DB에는 저장된다. 다만 생성 직후 `memo.id`처럼 DB가 만들어준 값을 즉시 확실히 사용해야 한다면 `db.refresh(memo)`까지 호출하는 방식도 자주 사용한다.

에러가 발생했을 때는 `rollback()`으로 아직 확정되지 않은 작업을 되돌릴 수 있다. 지금 과제 수준에서는 필수는 아니지만, 실제 서비스에서는 여러 DB 작업을 하나의 묶음으로 처리할 때 매우 중요하다.

---

## 7-1장. ORM 모델이 의미하는 것

`models/memo.py`의 `Memo` 클래스는 단순한 Python 클래스가 아니라, DB 테이블과 연결된 SQLAlchemy ORM 모델이다.

```python
class Memo(Base):
    __tablename__ = "memos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
```

이 코드는 다음 의미를 가진다.

```text
Memo 클래스 <-> memos 테이블
Memo.id     <-> memos.id 컬럼
Memo.title  <-> memos.title 컬럼
Memo.content <-> memos.content 컬럼
```

ORM을 사용하면 SQL 문자열을 직접 작성하지 않고도 Python 객체를 다루듯 DB 데이터를 조작할 수 있다.

```python
memo = Memo(title="FastAPI 복습", content="PRG 패턴 정리")
db.add(memo)
db.commit()
```

위 코드는 개념적으로 다음 SQL과 비슷한 일을 한다.

```sql
INSERT INTO memos (title, content)
VALUES ('FastAPI 복습', 'PRG 패턴 정리');
```

즉, ORM은 Python 객체와 관계형 데이터베이스 테이블 사이를 연결해주는 번역기 역할을 한다.

---

## 7-2장. 존재하지 않는 데이터 처리

상세 조회, 수정, 삭제에서는 사용자가 존재하지 않는 ID로 접근할 수 있다.

```text
/memos/9999
```

이때 서버가 내부 오류를 내면 사용자는 무엇이 잘못되었는지 알기 어렵다. 그래서 현재 라우터는 조회 결과가 없으면 `HTTPException(status_code=404)`를 발생시킨다.

```python
memo = MemoService(db).get_memo(memo_id)
if not memo:
    raise HTTPException(status_code=404, detail="해당 메모를 찾을 수 없습니다.")
```

이 처리는 "서버가 고장났다"가 아니라 "요청한 메모가 없다"는 의미를 명확히 표현한다. 이것도 웹 애플리케이션에서 중요한 사용자 경험이다.

---

## 8장. 유지보수의 관점 (Change Management)

| 수정 상황 | 수정 위치 | 이유 |
| :--- | :--- | :--- |
| URL 경로 변경 | Router | 외부 인터페이스가 바뀌었으므로 |
| 글자 수 제한 추가 | Service | 비즈니스 로직이 바뀌었으므로 |
| DB 엔진 교체 | Repository | 데이터 저장 매체가 바뀌었으므로 |

---

## 8-1장. 과제 요구사항과 현재 코드 연결표

| 과제 요구사항 | 현재 코드에서 확인할 위치 |
| :--- | :--- |
| 홈 화면 `GET /` | `routers/memo_router.py`의 `home()` |
| 목록 화면 | `GET /memos`, `templates/list.html` |
| 등록 폼 | `GET /memos/create`, `templates/form.html` |
| 등록 처리 | `POST /memos/create` |
| 상세 화면 | `GET /memos/{memo_id}`, `templates/detail.html` |
| 수정 폼 | `GET /memos/{memo_id}/edit` |
| 수정 처리 | `POST /memos/{memo_id}/edit` |
| 삭제 처리 | `POST /memos/{memo_id}/delete` |
| PRG 패턴 | POST 처리 후 `RedirectResponse(..., status_code=303)` |
| DB 세션 주입 | `db: Session = Depends(get_db)` |
| SQLite 연결 | `database.py`의 `sqlite:///./memo.db` |
| ORM 모델 | `models/memo.py`의 `Memo` |
| 저장소 분리 | `repositories/memo_repo.py` |
| 서비스 분리 | `services/memo_service.py` |

이 표를 기준으로 README나 발표 자료를 작성하면, "요구사항을 어디에서 만족하는지"를 코드 근거와 함께 설명할 수 있다.

---

## 8-2장. 학습할 때 스스로 던질 질문

코드를 다 작성한 뒤에는 작동 여부만 확인하지 말고, 다음 질문에 답해보는 것이 좋다.

1. 사용자가 등록 버튼을 누르면 어떤 라우터 함수가 실행되는가?
2. 그 라우터 함수는 어떤 Form 값을 받는가?
3. 라우터는 직접 DB를 만지는가, 아니면 서비스를 호출하는가?
4. 서비스는 어떤 저장소 메서드를 호출하는가?
5. 저장소는 어떤 SQLAlchemy 메서드로 DB를 변경하는가?
6. `commit()`은 어느 시점에 실행되는가?
7. POST 이후 왜 바로 HTML을 반환하지 않고 Redirect를 반환하는가?
8. Redirect 이후 브라우저의 마지막 요청은 GET인가, POST인가?

이 질문에 말로 답할 수 있으면 과제의 핵심을 꽤 잘 이해한 것이다.

---

## 9장. 비전공자를 위한 핵심 요약

1. **PRG 패턴**: 새로고침 버튼을 눌러도 글이 두 번 올라가지 않게 하는 **"보호막"**이다.
2. **계층 분리**: 각 계층은 **"자신의 역할만 수행"**하여 코드가 꼬이는 것을 방지한다.
3. **의존성 주입**: 필요한 도구를 **"알아서 챙겨주는 시스템"**을 사용하여 코드를 깔끔하게 유지한다.

---

## 10장. Q&A 섹션

**Q1. Repository에서 `db.commit()`을 안 하면 어떻게 되는가?**
A1. 데이터가 실제로 저장되지 않고 메모리에만 머물다가 세션이 종료되면 사라진다. 반드시 커밋을 해야 영구 보존된다.

**Q2. 서비스 계층이 너무 비대해지면 어떻게 하는가?**
A2. 서비스 계층을 더 세분화하거나, 도메인 로직을 별도의 '모델 클래스' 내부로 옮겨(Domain-Driven Design) 서비스의 부담을 줄일 수 있다.

**Q3. `303` 말고 다른 리다이렉트 코드는 없는가?**
A3. `301`(영구 이동), `302`(일시 이동) 등이 있다. 하지만 POST 요청 후에는 명확하게 다른 리소스로 안내한다는 의미인 `303(See Other)`을 사용하는 것이 표준 규약(HTTP RFC)상 가장 안전하다.

**Q4. 왜 `db` 세션을 직접 만들지 않고 `Depends`를 사용하는가?**
A4. `Depends(get_db)`가 `get_db()`의 generator dependency 흐름을 실행해주기 때문이다. 요청이 끝나면 `finally` 블록의 `db.close()`가 호출되어 연결 누수(Connection Leak)를 줄일 수 있다.
