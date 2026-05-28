# 파이썬 심화 문법 해설서

이 문서는 파일 기반 가계부 콘솔 프로그램을 만들면서 실제로 사용한 파이썬 문법과 설계 개념을 깊게 설명합니다.

`README.md`가 사용 방법을 설명하고, `budget_app/CODE_GUIDE.md`가 프로젝트 구조를 설명한다면, 이 문서는 코드 속에 등장하는 파이썬 개념을 한 권의 작은 책처럼 정리하는 것을 목표로 합니다.

이 문서는 "이미 프로그래밍을 잘 아는 사람"만을 대상으로 하지 않습니다. 오히려 비전공자가 코드를 읽을 때 자주 막히는 지점, 예를 들어 `yield`가 왜 갑자기 값을 하나씩 내보내는지, `Optional`이 왜 필요한지, `@decorator`가 왜 함수 위에 붙는지 같은 부분을 천천히 풀어 설명합니다.

어려운 용어는 그대로 사용합니다. 현업 코드와 공식 문서에서는 결국 그 용어를 만나게 되기 때문입니다. 대신 용어를 먼저 외우게 하지 않고, "왜 이런 게 필요했는지"를 생활 속 비유와 이 프로젝트의 코드 흐름으로 설명합니다.

## 1. 이 문서를 읽는 방법

이 프로젝트에는 다음과 같은 심화 개념이 들어 있습니다.

- 패키지 실행 구조: `python -m budget_app`
- `argparse`를 이용한 CLI 구성
- `dataclass` 기반 데이터 모델
- 타입 힌트와 `Optional`, `Union`, `Callable`, `Iterator`
- `yield` 기반 제너레이터 스트리밍
- JSONL 파일 저장
- 컨텍스트 매니저와 파일 입출력
- 예외 처리와 사용자 정의 예외
- 데코레이터와 `functools.wraps`
- 원자적 파일 교체
- 리스트 컴프리헨션, 딕셔너리 컴프리헨션, 정렬 키
- `classmethod`, 불변 객체, `dataclasses.replace`
- 표준 라이브러리 중심 설계

중요한 점은 문법을 따로 외우는 것이 아닙니다. 각 문법이 이 프로그램의 어떤 문제를 해결하기 위해 쓰였는지 이해하는 것입니다.

처음 읽을 때는 모든 코드를 완벽하게 이해하려고 하지 않아도 됩니다. 먼저 "이 문법은 어떤 불편함을 해결하려고 나온 것인가"만 잡으면 됩니다. 그다음 두 번째로 읽을 때 코드 조각을 따라가면 훨씬 잘 보입니다.

예를 들어 `yield`를 처음 보면 낯설 수 있습니다. 하지만 "거래 파일을 한 번에 다 읽으면 부담스럽다. 그래서 한 줄씩 꺼내 주는 장치가 필요하다"라고 생각하면 훨씬 쉬워집니다. 문법을 문제 해결 도구로 보면 기억이 오래갑니다.

이 문서의 추천 독서 순서는 다음과 같습니다.

1. 먼저 2장부터 7장까지 읽으며 전체 실행 구조와 데이터 모델을 이해합니다.
2. 그다음 12장부터 16장까지 읽으며 파일 저장과 스트리밍을 이해합니다.
3. 마지막으로 22장부터 27장까지 읽으며 예외 처리와 데코레이터를 이해합니다.
4. 나머지 장은 코드를 보다가 궁금할 때 사전처럼 찾아보면 됩니다.

문법 설명이 아직 어렵게 느껴진다면 마지막의 42장 "쉬운 예제로 다시 보기"를 먼저 읽어도 좋습니다. 42장은 실제 프로젝트 코드보다 더 작은 예제로 핵심 문법을 다시 풀어 설명합니다.

## 2. 패키지 실행 구조

이 프로젝트는 다음 명령으로 실행됩니다.

```bash
python -m budget_app
```

이 방식으로 실행하려면 `budget_app` 폴더가 파이썬 패키지여야 합니다. 패키지는 보통 `__init__.py` 파일을 가진 폴더입니다.

쉽게 말하면 패키지는 "파이썬 파일들을 하나의 프로그램 묶음으로 포장한 폴더"입니다. 그냥 `.py` 파일 하나를 실행하는 방식이 아니라, 여러 파일이 서로 역할을 나누어 하나의 앱처럼 움직이게 만들 때 패키지 구조를 사용합니다.

```text
budget_app/
  __init__.py
  __main__.py
  cli.py
```

`python -m budget_app`를 실행하면 파이썬은 `budget_app/__main__.py`를 찾습니다.

```python
from budget_app.cli import main

main()
```

이 파일은 매우 짧습니다. 실제 로직을 직접 넣지 않고 `cli.py`의 `main()`으로 넘깁니다.

이렇게 나눈 이유는 실행 진입점과 실제 프로그램 로직을 분리하기 위해서입니다. `__main__.py`는 "패키지로 실행될 때 어디로 들어갈지"만 알려주고, 실제 명령 처리와 오류 처리는 `cli.py`가 담당합니다.

비유하자면 `__main__.py`는 건물의 정문 안내판입니다. 안내판 자체가 업무를 처리하지는 않습니다. 대신 "업무는 이쪽 창구로 가세요"라고 알려줍니다. 여기서 실제 창구가 `cli.py`의 `main()`입니다.

이 구조를 사용하면 좋은 점이 있습니다. 나중에 프로그램 실행 방식이 조금 바뀌어도 `__main__.py`는 거의 그대로 둘 수 있고, 명령 처리 로직은 `cli.py` 안에서 관리할 수 있습니다.

## 3. `from __future__ import annotations`

여러 파일의 맨 위에는 다음 코드가 있습니다.

```python
from __future__ import annotations
```

이 문장은 타입 힌트를 나중에 평가하도록 만듭니다. 쉽게 말해, 타입 힌트에 적은 클래스 이름을 파이썬이 즉시 실제 객체로 해석하지 않고 문자열처럼 미뤄 둡니다.

처음 보면 "왜 미래를 import하지?"처럼 이상하게 느껴질 수 있습니다. 여기서 `__future__`는 시간 여행이 아니라, 파이썬의 새로운 동작 방식을 현재 파일에 미리 적용한다는 뜻에 가깝습니다.

타입 힌트는 코드 실행을 위한 본체라기보다 설명표에 가깝습니다. 그런데 설명표에 아직 완성되지 않은 클래스 이름이 등장하면 파이썬이 당황할 수 있습니다. `from __future__ import annotations`는 그런 설명표를 너무 일찍 해석하지 말고, 필요할 때 해석하라고 알려줍니다.

예를 들어 `models.py`에는 이런 코드가 있습니다.

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> "Transaction":
    ...
```

예전 스타일에서는 아직 클래스 본문이 끝나지 않았기 때문에 반환 타입에 `"Transaction"`처럼 문자열을 쓰는 경우가 많았습니다. `from __future__ import annotations`를 쓰면 타입 힌트 처리가 더 유연해집니다.

이 프로젝트에서는 파이썬 3.10 이상을 기준으로 하지만, 타입 힌트를 안정적으로 쓰기 위해 이 문장을 추가했습니다.

비전공자 관점에서는 이 문장을 "타입 힌트를 더 편하게 쓰게 해 주는 준비 코드" 정도로 이해하면 충분합니다. 이 문장이 있다고 해서 프로그램의 핵심 동작이 갑자기 달라지는 것은 아닙니다.

## 4. CLI 파싱과 `argparse`

CLI는 Command Line Interface의 줄임말입니다. 사용자가 터미널에서 명령어와 옵션을 입력해 프로그램을 조작하는 방식입니다.

마우스로 버튼을 누르는 화면 프로그램과 달리, CLI 프로그램은 문장처럼 명령을 입력합니다.

```bash
python -m budget_app list --limit 3
```

이 한 줄은 사람 말로 바꾸면 "가계부 프로그램을 실행해서, 거래 목록을 보여 주되, 3개까지만 보여 줘"라는 뜻입니다.

이 프로젝트는 표준 라이브러리인 `argparse`를 사용합니다.

```python
parser = argparse.ArgumentParser(prog="python -m budget_app")
parser.add_argument("--data-dir", default="./data", help="저장 폴더 경로 (기본: ./data)")
subparsers = parser.add_subparsers(dest="command", required=True)
```

`ArgumentParser`는 명령어 규칙을 정의하는 객체입니다. `add_argument()`는 옵션을 추가합니다.

`argparse`는 터미널 입력을 파이썬이 이해할 수 있는 값으로 번역해 주는 통역사라고 볼 수 있습니다. 사용자는 문자열로 명령을 입력하지만, 프로그램 안에서는 `args.command`, `args.limit`, `args.month` 같은 이름으로 정리된 값을 사용합니다.

```python
parser.add_argument("--data-dir", default="./data")
```

이 코드는 모든 명령에서 사용할 수 있는 `--data-dir` 옵션을 만듭니다. 사용자가 값을 주지 않으면 기본값으로 `./data`를 사용합니다.

### 하위 명령

가계부 프로그램에는 `add`, `list`, `search`, `summary` 같은 여러 명령이 있습니다. 이런 명령은 subparser로 만듭니다.

```python
subparsers = parser.add_subparsers(dest="command", required=True)
subparsers.add_parser("add", help="거래 추가")
```

`dest="command"`는 사용자가 입력한 하위 명령 이름을 `args.command`에 저장하겠다는 뜻입니다.

하위 명령은 큰 프로그램 안에 들어 있는 작은 메뉴라고 생각하면 됩니다. 은행 앱에 이체, 조회, 카드 관리 메뉴가 있듯이, 이 가계부 앱에는 `add`, `list`, `search`, `summary` 메뉴가 있습니다.

예를 들어 사용자가 다음을 실행하면:

```bash
python -m budget_app list --limit 3
```

`args.command`는 `"list"`가 되고, `args.limit`은 `3`이 됩니다.

### `dest`를 쓰는 이유

`--from`은 파이썬 키워드 `from`과 이름이 겹칩니다. 그래서 그대로 `args.from`처럼 쓸 수 없습니다.

이럴 때 `dest`를 씁니다.

```python
search_parser.add_argument("--from", dest="date_from")
```

사용자는 `--from`이라고 입력하지만, 코드에서는 `args.date_from`으로 읽습니다.

이런 처리는 사용자를 위한 이름과 개발자를 위한 이름이 다를 수 있음을 보여줍니다. 사용자는 자연스럽게 `--from`이라고 쓰고, 코드는 파이썬 문법에 맞게 `date_from`이라는 안전한 이름으로 다룹니다.

## 5. 타입 힌트는 코드의 계약이다

타입 힌트는 함수가 어떤 값을 받고 어떤 값을 돌려주는지 알려주는 표시입니다.

타입 힌트는 음식 알레르기 표시나 택배 송장과 비슷합니다. 실제 물건은 상자 안에 있지만, 송장을 보면 이 상자가 어디로 가야 하는지, 무엇을 담고 있는지 대략 알 수 있습니다. 타입 힌트도 코드 실행 자체는 아니지만, 코드를 읽는 사람에게 중요한 정보를 줍니다.

```python
def build_services(data_dir: str) -> tuple[TransactionService, CategoryService, BudgetService]:
    ...
```

이 함수는 문자열 `data_dir`을 받아서 서비스 객체 3개가 들어 있는 튜플을 반환합니다.

이 한 줄만 보고도 다음 사실을 알 수 있습니다.

- `data_dir`에는 폴더 경로를 나타내는 문자열이 들어와야 합니다.
- 결과는 하나가 아니라 세 개의 서비스 객체입니다.
- 반환 순서는 `TransactionService`, `CategoryService`, `BudgetService`입니다.

타입 힌트의 장점은 다음과 같습니다.

- 코드를 읽는 사람이 함수의 사용법을 빨리 이해할 수 있습니다.
- IDE가 자동완성과 오류 표시를 더 잘 해줍니다.
- 함수 사이의 데이터 흐름이 명확해집니다.
- 큰 프로젝트에서 잘못된 타입 전달을 줄일 수 있습니다.

중요한 점은 파이썬 타입 힌트가 기본적으로 실행 시 강제되지 않는다는 것입니다. 아래 함수는 타입 힌트로 `str`을 받는다고 되어 있어도, 실행 중에는 다른 타입이 들어올 수 있습니다.

```python
def parse_date(value: str) -> str:
    ...
```

그래서 이 프로젝트는 타입 힌트만 믿지 않고, `validators.py`에서 실제 검증도 수행합니다.

즉, 타입 힌트는 "약속"이고, 검증 함수는 "검문"입니다. 약속이 있다고 해서 모두가 항상 약속을 지킨다고 가정할 수는 없습니다. 그래서 실제 프로그램에서는 약속을 적어 두고, 중요한 입력은 다시 검사합니다.

## 6. `Optional`과 `Union`

`Optional[str]`은 `str` 또는 `None`이 될 수 있다는 뜻입니다.

`None`은 "값이 없다"는 뜻입니다. 빈 문자열 `""`과도 다릅니다. 빈 문자열은 문자열이긴 하지만 내용이 비어 있는 것이고, `None`은 아예 값이 없다는 표시입니다.

```python
def run(argv: Optional[list[str]] = None) -> int:
    ...
```

`argv`는 리스트일 수도 있고, 아무 값도 전달하지 않으면 `None`일 수도 있습니다.

이것은 "명령어 목록을 직접 줄 수도 있고, 안 줄 수도 있다"는 뜻입니다. 직접 주지 않으면 파이썬은 실제 터미널에서 입력된 명령어를 사용합니다.

`Union[str, int]`는 여러 타입 중 하나를 받을 수 있다는 뜻입니다.

현실의 입력은 늘 깔끔하지 않습니다. 터미널에서 들어온 금액은 `"15000"`처럼 문자열입니다. 하지만 코드 내부에서는 이미 `15000`처럼 정수일 수도 있습니다. `Union[str, int]`는 이 두 경우를 모두 받아들이겠다는 표시입니다.

```python
def parse_amount(value: Union[str, int]) -> int:
    ...
```

이 함수는 CLI에서 들어온 문자열 `"15000"`도 받을 수 있고, 코드 내부에서 이미 정수인 `15000`도 받을 수 있습니다. 하지만 최종 결과는 항상 `int`로 반환합니다.

파이썬 3.10 이상에서는 다음처럼 쓸 수도 있습니다.

```python
def parse_amount(value: str | int) -> int:
    ...
```

이 프로젝트는 `Union`을 사용해 타입 의미를 명시적으로 보여줍니다.

비전공자 관점에서는 `Optional`은 "없을 수도 있음", `Union`은 "여러 종류 중 하나일 수 있음"이라고 기억하면 됩니다.

## 7. `dataclass`

`dataclass`는 데이터 중심 클래스를 간결하게 만들기 위한 표준 라이브러리 기능입니다.

가계부의 거래는 여러 정보를 한 덩어리로 가지고 있습니다. 거래 ID, 날짜, 타입, 금액, 카테고리, 메모, 태그가 따로 흩어져 있으면 다루기 어렵습니다. `dataclass`는 이런 관련 정보를 하나의 묶음으로 만드는 데 어울립니다.

```python
@dataclass(frozen=True)
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)
```

직접 `__init__`을 만들지 않아도 다음처럼 객체를 생성할 수 있습니다.

객체를 만든다는 것은 "거래 한 건을 코드 안에서 다룰 수 있는 형태로 만든다"는 뜻입니다. 엑셀의 한 행이 거래 한 건을 나타내듯이, `Transaction` 객체 하나도 거래 한 건을 나타냅니다.

```python
transaction = Transaction(
    id="TX-000001",
    type="expense",
    date="2024-01-15",
    amount=15000,
    category="food",
)
```

`dataclass`가 자동으로 만들어 주는 대표 기능은 다음과 같습니다.

- `__init__`
- `__repr__`
- `__eq__`

즉, 데이터 저장용 클래스를 만들 때 반복 코드를 줄일 수 있습니다.

`dataclass`를 쓰지 않았다면 `__init__` 메서드를 직접 작성해야 합니다. 필드가 많아질수록 이런 반복 코드는 길어지고 실수하기 쉬워집니다. `dataclass`는 "이 클래스는 데이터를 담는 그릇입니다"라고 선언하면, 파이썬이 기본적인 그릇 제작을 도와주는 기능입니다.

## 8. `frozen=True`와 불변 객체

`Transaction`은 `frozen=True`로 선언되어 있습니다.

```python
@dataclass(frozen=True)
class Transaction:
    ...
```

이 설정은 객체를 만든 뒤 필드를 직접 바꾸지 못하게 합니다.

불변 객체는 "한 번 작성한 영수증은 마음대로 고쳐 쓰지 않는다"는 생각과 비슷합니다. 거래 기록은 나중에 바뀔 수 있지만, 바뀌는 과정이 명확해야 합니다. 아무 곳에서나 금액을 슬쩍 바꾸면 추적이 어려워집니다.

```python
tx.amount = 20000  # 오류 발생
```

왜 이런 제한을 둘까요?

거래 데이터는 중요한 기록입니다. 아무 곳에서나 객체 내부 값을 바꿀 수 있으면, 언제 어디서 데이터가 변경되었는지 추적하기 어려워집니다.

이 프로젝트에서는 수정할 때 기존 객체를 바꾸지 않고, 새 객체를 만듭니다.

```python
from dataclasses import replace

new_transaction = replace(transaction, amount=20000)
```

이 방식은 변경 지점을 명확하게 만들어 줍니다.

즉, 이 프로젝트에서 수정은 "기존 거래를 몰래 고치기"가 아니라 "기존 거래를 바탕으로 수정된 새 거래 객체를 만들기"입니다. 파일에 저장할 때는 이 새 객체로 원래 줄을 대체합니다.

## 9. `field(default_factory=list)`

`Transaction`의 `tags` 필드는 리스트입니다.

```python
tags: list[str] = field(default_factory=list)
```

리스트는 변경 가능한 객체입니다. 다음처럼 기본값을 직접 `[]`로 두면 문제가 생길 수 있습니다.

변경 가능한 객체란 안의 내용이 나중에 바뀔 수 있는 객체입니다. 리스트는 항목을 추가하거나 삭제할 수 있으므로 변경 가능합니다.

```python
tags: list[str] = []
```

이렇게 쓰면 여러 객체가 같은 리스트를 공유할 위험이 있습니다. 한 거래의 태그를 바꿨는데 다른 거래에도 영향이 갈 수 있습니다.

그래서 `default_factory=list`를 씁니다. 객체가 새로 만들어질 때마다 새로운 빈 리스트를 만들어 줍니다.

비유하면 손님마다 새 장바구니를 하나씩 나눠 주는 것과 같습니다. `[]`를 기본값으로 직접 두는 실수는 모든 손님에게 같은 장바구니를 들게 하는 것과 비슷합니다. 한 사람이 물건을 넣었는데 다른 사람 장바구니에도 보이는 이상한 일이 생길 수 있습니다.

이것은 파이썬에서 매우 중요한 습관입니다. 기본값으로 리스트, 딕셔너리, 세트 같은 변경 가능한 객체를 직접 넣지 않습니다.

## 10. `to_dict()`와 `from_dict()`

객체를 파일에 저장하려면 JSON으로 바꿀 수 있는 형태가 필요합니다. JSON은 파이썬 객체를 그대로 저장하지 못합니다.

`Transaction` 객체는 파이썬 프로그램 안에서는 편리하지만, 파일에 적어 두기에는 그대로 사용할 수 없습니다. 파일은 결국 문자로 저장됩니다. 그래서 객체를 저장 가능한 모양, 즉 딕셔너리로 바꾸는 과정이 필요합니다.

그래서 `Transaction`에는 `to_dict()`가 있습니다.

```python
def to_dict(self) -> dict[str, Any]:
    return {
        "id": self.id,
        "type": self.type,
        "date": self.date,
        "amount": self.amount,
        "category": self.category,
        "memo": self.memo,
        "tags": self.tags,
    }
```

이 함수는 `Transaction` 객체를 딕셔너리로 바꿉니다.

딕셔너리는 이름표가 붙은 값들의 묶음입니다. 예를 들어 `"amount": 15000`은 amount라는 이름표에 15000이라는 값이 들어 있다는 뜻입니다. JSON도 이런 이름표 구조를 잘 저장할 수 있습니다.

반대로 파일에서 읽은 딕셔너리를 다시 객체로 만들 때는 `from_dict()`를 사용합니다.

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> "Transaction":
    ...
```

`to_dict()`와 `from_dict()`를 모델 안에 둔 이유는 데이터 변환 규칙을 모델 가까이에 두기 위해서입니다. 저장소는 파일을 읽고 쓰는 일에 집중하고, 모델은 자신이 어떤 데이터 구조인지 설명합니다.

쉽게 말해 `to_dict()`는 "객체를 파일에 적기 좋게 포장하기"이고, `from_dict()`는 "파일에서 읽은 내용을 다시 객체로 조립하기"입니다. 포장과 조립 방법을 모델이 알고 있으면, 다른 코드가 거래의 내부 구조를 너무 자세히 알 필요가 없습니다.

## 11. `@classmethod`

`from_dict()` 앞에는 `@classmethod`가 붙어 있습니다.

```python
@classmethod
def from_dict(cls, data: dict[str, Any]) -> "Transaction":
    return cls(...)
```

일반 메서드는 첫 번째 인자로 `self`를 받습니다. `self`는 이미 만들어진 객체입니다.

`self`는 "나 자신"입니다. 이미 만들어진 거래 객체가 자기 자신의 값을 다룰 때 사용합니다.

클래스 메서드는 첫 번째 인자로 `cls`를 받습니다. `cls`는 클래스 자체입니다.

`cls`는 아직 만들어진 객체 하나가 아니라, 객체를 만들어 낼 설계도 자체를 가리킵니다.

`from_dict()`는 아직 객체가 없는 상태에서 딕셔너리를 이용해 새 객체를 만들어야 합니다. 그래서 `self`가 아니라 `cls`가 필요합니다.

```python
transaction = Transaction.from_dict(row)
```

이 코드는 `Transaction` 클래스에게 "이 딕셔너리로 너 자신을 만들어라"라고 요청하는 형태입니다.

비유하자면 `Transaction` 클래스는 거래 양식이고, `from_dict()`는 이미 적혀 있는 종이 내용을 보고 정식 거래 카드로 다시 만드는 작업입니다.

## 12. JSONL 파일 형식

이 프로젝트는 JSONL을 사용합니다. JSONL은 JSON Lines의 줄임말입니다.

JSONL은 이름 그대로 "줄 단위 JSON"입니다. 한 줄에 하나의 데이터가 들어갑니다. 가계부에서는 거래 한 건을 한 줄로 저장한다고 생각하면 됩니다.

일반 JSON 배열은 다음과 같습니다.

```json
[
  {"name": "food"},
  {"name": "transport"}
]
```

JSONL은 한 줄에 JSON 객체 하나를 저장합니다.

```json
{"name": "food"}
{"name": "transport"}
```

JSONL을 선택한 이유는 거래 추가에 유리하기 때문입니다. 새 거래를 추가할 때 파일 끝에 한 줄만 붙이면 됩니다.

일반 JSON 배열은 전체 목록을 하나의 큰 상자로 묶어 둔 형태입니다. 새 물건을 넣으려면 상자를 열고, 전체 모양을 다시 맞춰야 합니다. JSONL은 줄마다 독립된 작은 봉투가 놓여 있는 형태라서, 새 봉투를 맨 뒤에 하나 더 놓으면 됩니다.

```python
def append_json(self, path: Path, data: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
```

`"a"` 모드는 append의 뜻입니다. 기존 내용을 지우지 않고 파일 끝에 추가합니다.

그래서 거래 추가는 빠르고 단순합니다. 기존 거래를 모두 다시 쓰지 않고, 새 거래 한 줄만 뒤에 붙입니다.

## 13. `with`와 컨텍스트 매니저

파일을 열 때는 `with`를 사용합니다.

파일을 열었다면 언젠가는 닫아야 합니다. 사람이 책을 꺼내 읽고 나서 다시 책장에 꽂아 두는 것처럼, 프로그램도 파일을 다 썼으면 닫아야 합니다.

```python
with path.open("r", encoding="utf-8") as file:
    for line in file:
        ...
```

`with`는 작업이 끝난 뒤 자원을 자동으로 정리합니다. 파일의 경우 자동으로 `close()`를 호출합니다.

직접 쓰면 다음과 비슷합니다.

```python
file = path.open("r", encoding="utf-8")
try:
    ...
finally:
    file.close()
```

`with`를 쓰면 파일 닫기를 깜빡할 가능성이 줄어듭니다. 특히 예외가 발생해도 파일이 닫히기 때문에 안전합니다.

비전공자 관점에서는 `with`를 "빌린 자원을 자동으로 반납해 주는 문법"이라고 이해하면 됩니다. 파일뿐 아니라 네트워크 연결, 잠금, 임시 작업 같은 곳에서도 같은 개념이 쓰입니다.

## 14. 제너레이터와 `yield`

이 프로젝트의 핵심 문법 중 하나는 `yield`입니다.

`yield`는 처음 볼 때 가장 낯선 문법 중 하나입니다. 하지만 아이디어는 단순합니다. "한꺼번에 다 주지 말고, 필요할 때 하나씩 주자"입니다.

```python
def iter_json(self, path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            ...
            yield data
```

`return`은 값을 한 번에 반환하고 함수를 끝냅니다. `yield`는 값을 하나 내보낸 뒤 함수의 상태를 잠시 멈춰 둡니다. 다음 값이 필요할 때 이어서 실행합니다.

비유하자면 `return`은 창고에 있는 물건을 한 번에 트럭에 다 실어 보내는 방식입니다. `yield`는 컨베이어 벨트처럼 물건을 하나씩 흘려보내는 방식입니다.

일반 리스트 방식:

```python
rows = []
for line in file:
    rows.append(json.loads(line))
return rows
```

이 방식은 파일 전체를 메모리에 올립니다.

제너레이터 방식:

```python
for row in self.store.iter_json(path):
    ...
```

이 방식은 한 줄씩 읽고 한 줄씩 처리합니다.

거래가 10개일 때는 차이가 작지만, 거래가 100만 개라면 차이가 커집니다. 제너레이터는 대용량 파일을 다룰 때 메모리 사용량을 줄이는 중요한 도구입니다.

이 프로젝트에서 `yield`가 중요한 이유는 과제 요구사항에 "파일 전체를 한 번에 모두 읽지 않고 스트리밍 처리"가 있기 때문입니다. `iter_json()`과 `stream()`은 바로 이 요구사항을 코드로 보여주는 부분입니다.

## 15. `Iterator`

제너레이터 함수의 반환 타입은 보통 `Iterator[T]`로 적습니다.

`Iterator`는 "하나씩 꺼내 볼 수 있는 것"이라는 뜻입니다. 리스트처럼 이미 모든 값이 준비된 상자가 아니라, 다음 값을 요청할 때마다 하나씩 나오는 흐름입니다.

```python
def stream(self) -> Iterator[Transaction]:
    for row in self.store.iter_json(self.store.transactions_path):
        yield Transaction.from_dict(row)
```

이 함수는 `Transaction` 객체를 하나씩 만들어 냅니다. 반환 타입이 `list[Transaction]`이 아닌 이유는 한 번에 전체 리스트를 돌려주지 않기 때문입니다.

`Iterator[Transaction]`은 "반복하면 Transaction이 하나씩 나온다"는 의미입니다.

즉, `Iterator[Transaction]`은 "거래 객체가 줄줄이 나오는 통로"라고 생각하면 됩니다. 이 통로를 `for`문이 하나씩 지나가며 처리합니다.

## 16. 스트리밍과 최신 N개 조회

`list --limit N`은 최신 거래 N개만 보여줍니다.

```python
return heapq.nlargest(limit, self.transactions.stream(), key=lambda item: (item.date, item.id))
```

`heapq.nlargest()`는 전체 데이터를 정렬해서 모두 보관하는 대신, 필요한 상위 N개를 효율적으로 뽑습니다.

전체 성적표에서 1등부터 10등까지만 알고 싶을 때, 모든 학생을 완벽히 줄 세우지 않아도 됩니다. 상위 10명 후보만 계속 관리하면 됩니다. `heapq.nlargest()`는 이런 상황에 어울리는 도구입니다.

여기서 중요한 점은 `self.transactions.stream()`이 제너레이터라는 것입니다. 거래 파일을 한 줄씩 읽으면서 최신 N개만 추립니다.

정렬 기준은 다음 튜플입니다.

```python
lambda item: (item.date, item.id)
```

날짜가 더 큰 거래가 최신입니다. 날짜가 같다면 ID가 큰 거래가 더 나중에 만들어진 것으로 봅니다.

여기서도 중요한 점은 "최신순"이라는 사용자 요구사항과 "파일을 한 줄씩 읽는다"는 기술 요구사항을 함께 만족한다는 것입니다. 단순히 정렬하는 코드가 아니라, 요구사항 두 개를 동시에 해결하는 코드입니다.

## 17. `lambda`

`lambda`는 이름 없는 짧은 함수를 만들 때 사용합니다.

함수는 보통 이름을 붙여서 만듭니다. 그런데 아주 짧고 한 번만 쓰는 함수라면 이름을 따로 붙이는 것이 오히려 번거로울 수 있습니다. 그럴 때 `lambda`를 사용합니다.

```python
key=lambda item: (item.date, item.id)
```

이 코드는 다음 함수와 비슷합니다.

```python
def sort_key(item: Transaction) -> tuple[str, str]:
    return (item.date, item.id)
```

정렬 기준처럼 한 번만 쓰는 간단한 함수에는 `lambda`가 잘 맞습니다.

너무 복잡한 로직을 `lambda`로 쓰면 읽기 어려워집니다. 이 프로젝트에서는 날짜와 ID를 뽑는 정도의 간단한 용도로만 사용합니다.

비전공자 관점에서는 `lambda`를 "짧은 임시 함수"라고 기억하면 됩니다. 정식으로 이름 붙인 함수가 아니라, 특정 작업을 잠깐 도와주는 작은 도구입니다.

## 18. 리스트 컴프리헨션

검색 결과를 만들 때 리스트 컴프리헨션을 사용합니다.

리스트 컴프리헨션은 파이썬을 처음 배울 때 어렵게 느껴질 수 있습니다. 하지만 읽는 순서를 바꾸면 쉽습니다.

```python
results = [tx for tx in self.transactions.stream() if self._matches(tx, criteria)]
```

이 코드는 다음 순서로 읽으면 됩니다.

1. `self.transactions.stream()`에서 거래를 하나씩 꺼낸다.
2. 꺼낸 거래를 `tx`라고 부른다.
3. `self._matches(tx, criteria)`가 참인 거래만 남긴다.
4. 남은 거래들을 리스트로 만든다.

이 코드는 다음과 같습니다.

```python
results = []
for tx in self.transactions.stream():
    if self._matches(tx, criteria):
        results.append(tx)
```

리스트 컴프리헨션은 "반복하면서 조건에 맞는 값을 리스트로 만든다"는 뜻을 짧게 표현합니다.

단, 리스트 컴프리헨션은 결과를 리스트로 모읍니다. 따라서 모든 검색 결과를 메모리에 담습니다. 이 프로젝트는 파일 읽기는 스트리밍으로 하지만, 최종 출력은 최신순 정렬이 필요하기 때문에 결과를 모은 뒤 정렬합니다.

여기서 중요한 균형이 있습니다. 파일을 읽는 과정은 스트리밍으로 처리하지만, 검색 결과를 최신순으로 보여 주려면 결과끼리 비교해야 합니다. 그래서 조건에 맞는 결과만 리스트로 모은 뒤 정렬합니다.

## 19. 딕셔너리와 누적 계산

월별 요약에서는 카테고리별 지출 합계를 딕셔너리로 누적합니다.

딕셔너리는 이름표와 값이 짝을 이루는 자료구조입니다. 가계부 요약에서는 카테고리 이름이 이름표가 되고, 해당 카테고리의 총 지출액이 값이 됩니다.

```python
category_totals[transaction.category] = category_totals.get(transaction.category, 0) + transaction.amount
```

`dict.get(key, default)`는 키가 있으면 값을 가져오고, 없으면 기본값을 반환합니다.

예를 들어 `food`가 처음 나오면:

```python
category_totals.get("food", 0)
```

결과는 `0`입니다. 여기에 금액을 더해 저장합니다.

두 번째로 `food`가 나오면 기존 합계가 반환되고, 다시 금액을 더합니다.

이 패턴은 집계 로직에서 자주 쓰입니다.

말로 풀면 이렇습니다.

```text
food 카테고리가 처음 나오면 0원에서 시작한다.
이번 거래 금액을 더한다.
다음 food 거래가 나오면 기존 합계에 또 더한다.
```

엑셀에서 카테고리별 합계를 내는 것과 같은 작업을 코드로 작성한 것입니다.

## 20. 정렬과 `key`

카테고리별 지출 TOP N은 다음 코드로 구합니다.

정렬은 단순히 가나다순이나 숫자순으로만 하는 것이 아닙니다. "무엇을 기준으로 정렬할 것인가"를 정해야 합니다. 파이썬의 `key`는 바로 그 기준을 알려주는 역할을 합니다.

```python
top_expenses = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[:top]
```

`category_totals.items()`는 `(카테고리, 금액)` 형태의 튜플들을 반환합니다.

```python
("food", 45000)
("rent", 150000)
```

`key=lambda item: item[1]`은 튜플의 두 번째 값, 즉 금액을 기준으로 정렬하겠다는 뜻입니다.

`reverse=True`는 큰 값부터 정렬합니다.

마지막의 `[:top]`은 앞에서부터 top개만 자릅니다.

이 코드를 사람 말로 바꾸면 다음과 같습니다.

```text
카테고리별 지출 합계를 금액 기준으로 큰 순서대로 정렬하고,
그중 앞에서부터 N개만 가져온다.
```

## 21. 슬라이싱

슬라이싱은 리스트나 문자열의 일부를 잘라내는 문법입니다.

슬라이싱은 빵을 필요한 만큼 자르는 것과 비슷합니다. 전체를 다 쓰지 않고, 원하는 구간만 잘라 가져옵니다.

```python
items[:3]
```

이 코드는 처음부터 세 번째 전까지, 즉 앞의 3개를 가져옵니다.

이 프로젝트에서는 TOP N 결과를 만들 때 사용합니다.

```python
sorted_items[:top]
```

`[:top]`은 "처음부터 top개까지"라는 뜻입니다. 예를 들어 `top`이 3이면 앞의 3개만 가져옵니다.

## 22. 사용자 정의 예외

`errors.py`에는 `AppError`가 있습니다.

예외는 프로그램 실행 중 문제가 생겼다는 신호입니다. 파이썬에는 이미 `ValueError`, `FileNotFoundError` 같은 예외가 있지만, 이 프로젝트에서는 사용자에게 보여주기 좋은 오류를 따로 표현하기 위해 `AppError`를 만들었습니다.

```python
class AppError(Exception):
    def __init__(self, message: str, hint: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
```

`AppError`는 사용자에게 보여줄 수 있는 오류를 표현합니다.

일반 예외는 개발자에게는 유용하지만 사용자에게는 너무 어렵습니다. 예를 들어 날짜 형식이 틀렸을 때 긴 스택트레이스를 보여 주는 것보다, "날짜 형식이 올바르지 않습니다. 예: 2024-01-15"라고 말해 주는 편이 훨씬 친절합니다.

예를 들어 날짜가 잘못되었을 때:

```python
raise AppError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).", "예: 2024-01-15")
```

이 예외에는 오류 메시지와 해결 힌트가 함께 들어 있습니다.

일반적인 파이썬 오류를 그대로 보여주면 사용자는 내부 스택트레이스를 보게 됩니다. 하지만 이 프로그램은 콘솔 서비스이므로 사용자에게 원인과 해결 방법을 간단히 보여주는 것이 더 좋습니다.

비유하면 `AppError`는 고객 응대용 안내문입니다. 내부 직원용 사고 보고서가 아니라, 사용자가 다음 행동을 할 수 있게 도와주는 문장입니다.

## 23. `try`, `except`, `finally`

오류 처리는 `try`, `except`로 합니다.

`try`는 "일단 이 일을 시도해 보자"라는 뜻입니다. `except`는 "하다가 이런 문제가 생기면 이렇게 처리하자"라는 뜻입니다. `finally`는 "성공하든 실패하든 마지막에는 반드시 하자"라는 뜻입니다.

```python
try:
    raise SystemExit(run())
except AppError as exc:
    print(f"[오류] {exc.message}", file=sys.stderr)
    if exc.hint:
        print(f"[힌트] {exc.hint}", file=sys.stderr)
    raise SystemExit(1) from None
```

`try` 안에서 오류가 발생하면, 해당 오류를 처리할 수 있는 `except` 블록이 실행됩니다.

`finally`는 오류가 나든 나지 않든 실행됩니다. 데코레이터에서 실행 시간 로그를 남길 때 사용합니다.

```python
try:
    return func(*args, **kwargs)
finally:
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info("%s completed in %.2fms", func.__name__, elapsed_ms)
```

프로그램이 정상 종료하든, 중간에 예외가 발생하든 실행 시간은 기록됩니다.

생활 속 예로 보면, 온라인 주문을 시도하는 과정이 `try`입니다. 결제 실패 시 안내하는 과정이 `except`입니다. 주문 성공 여부와 상관없이 장바구니 화면을 정리하는 과정이 `finally`입니다.

## 24. `raise ... from exc`와 `from None`

검증 함수에는 이런 코드가 있습니다.

`raise`는 예외를 발생시키는 문법입니다. 문제를 발견했을 때 그냥 조용히 넘어가지 않고, "여기서 문제가 생겼다"고 프로그램 흐름에 알립니다.

```python
except ValueError as exc:
    raise AppError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).", "예: 2024-01-15") from exc
```

`from exc`는 원래 발생한 예외와 새 예외의 관계를 연결합니다. 개발자가 디버깅할 때 "ValueError 때문에 AppError가 발생했다"는 흐름을 알 수 있습니다.

즉, 내부 기록에는 원인까지 남겨 둡니다. 날짜 파싱 중 `ValueError`가 났고, 그것을 사용자용 `AppError`로 바꿨다는 연결을 유지합니다.

반대로 `main()`에서는 다음처럼 씁니다.

```python
raise SystemExit(1) from None
```

`from None`은 예외 연결 정보를 사용자에게 보여주지 않겠다는 뜻입니다. 콘솔 사용자에게는 긴 내부 오류보다 `[오류]`, `[힌트]`가 더 중요하기 때문입니다.

정리하면 `from exc`는 개발자를 위한 추적 정보이고, `from None`은 사용자 화면을 깔끔하게 만들기 위한 처리입니다.

## 25. 데코레이터

데코레이터는 함수를 감싸서 기능을 추가하는 문법입니다.

데코레이터는 이름 그대로 함수를 장식합니다. 다만 겉모습만 꾸미는 장식이 아니라, 함수가 실행되기 전후에 추가 동작을 붙이는 장식입니다.

```python
@log_timing
def run(argv: Optional[list[str]] = None) -> int:
    ...
```

이 코드는 다음과 비슷합니다.

```python
run = log_timing(run)
```

`log_timing`은 함수를 하나 받아서 새로운 함수를 반환합니다.

처음에는 이 말이 어렵게 들릴 수 있습니다. 쉽게 말하면 `log_timing`은 원래 함수 `run()`을 그대로 실행하되, 실행 시간을 재는 포장지를 한 겹 씌웁니다.

```python
def log_timing(func: Callable[..., R]) -> Callable[..., R]:
    ...
```

이 타입 힌트는 "어떤 함수를 받아서, 같은 반환 타입을 가진 함수를 돌려준다"는 뜻입니다.

데코레이터를 쓰는 이유는 공통 관심사를 분리하기 위해서입니다. 실행 시간 측정은 중요한 기능이지만, 명령 처리 로직의 핵심은 아닙니다. 그래서 `run()` 내부에 시간 측정 코드를 섞지 않고 데코레이터로 분리합니다.

비유하면 음식 주문을 처리하는 직원에게 매번 "일 시작 시간 기록하고, 일 끝난 시간 기록하고, 차이를 계산해"라고 시키는 대신, 출퇴근 기록 시스템을 따로 붙여 두는 것과 같습니다. 직원은 주문 처리에 집중하고, 시간 기록은 별도 장치가 담당합니다.

## 26. `Callable`, `TypeVar`, `*args`, `**kwargs`

데코레이터에는 조금 어려운 타입 문법이 나옵니다.

이 장은 문서에서 가장 어렵게 느껴질 수 있습니다. 하지만 목적은 단순합니다. 데코레이터는 여러 종류의 함수를 감쌀 수 있어야 하므로, 인자와 반환 타입을 너무 좁게 정하면 안 됩니다.

```python
R = TypeVar("R")

def log_timing(func: Callable[..., R]) -> Callable[..., R]:
    ...
```

`Callable[..., R]`은 어떤 인자든 받을 수 있고, 반환 타입은 `R`인 함수라는 뜻입니다.

`Callable`은 "호출할 수 있는 것"입니다. 보통 함수가 여기에 해당합니다. 괄호를 붙여 실행할 수 있다면 호출 가능하다고 말합니다.

`TypeVar("R")`은 반환 타입을 보존하기 위한 타입 변수입니다. 예를 들어 감싸는 함수가 `int`를 반환하면, 데코레이터를 적용한 뒤에도 `int`를 반환한다고 표현할 수 있습니다.

`R`은 특정 타입 하나로 고정된 것이 아니라, "원래 함수가 반환하던 바로 그 타입"을 가리키는 자리표시자입니다.

wrapper 함수는 다음처럼 정의됩니다.

```python
def wrapper(*args: Any, **kwargs: Any) -> R:
    return func(*args, **kwargs)
```

`*args`는 위치 인자를 튜플로 받습니다.

```python
func(1, 2, 3)
```

이 호출에서 `args`는 `(1, 2, 3)`입니다.

`**kwargs`는 키워드 인자를 딕셔너리로 받습니다.

```python
func(name="food", amount=15000)
```

이 호출에서 `kwargs`는 `{"name": "food", "amount": 15000}`입니다.

데코레이터는 어떤 함수에도 적용될 수 있어야 하므로 인자 모양을 고정하지 않고 `*args`, `**kwargs`를 사용합니다.

쉽게 말하면 `*args`와 `**kwargs`는 인자를 받아 담는 넓은 바구니입니다. 함수마다 필요한 인자 모양이 다르기 때문에, 데코레이터는 그 인자들을 일단 그대로 받아서 원래 함수에 다시 넘겨 줍니다.

## 27. `functools.wraps`

데코레이터 내부에는 다음 코드가 있습니다.

데코레이터를 만들 때 `functools.wraps`를 쓰지 않으면, 원래 함수의 이름표가 사라지고 감싼 함수인 `wrapper`의 이름표만 남을 수 있습니다.

```python
@functools.wraps(func)
def wrapper(*args: Any, **kwargs: Any) -> R:
    ...
```

데코레이터를 적용하면 원래 함수가 `wrapper`로 바뀝니다. 이때 함수 이름, 문서 문자열 같은 정보도 `wrapper`의 것으로 바뀔 수 있습니다.

`functools.wraps(func)`는 원래 함수의 이름과 메타데이터를 유지해 줍니다.

비유하면 선물 포장을 해도 안에 든 물건의 라벨은 그대로 보존하는 것입니다. 포장을 했다고 해서 `run` 함수가 정체불명의 `wrapper`로만 보이면 로그와 디버깅이 불편해집니다.

예를 들어 `run.__name__`이 `"wrapper"`가 아니라 `"run"`으로 남습니다. 로그, 디버깅, 도움말 생성에서 유용합니다.

## 28. 파일 경로와 `pathlib.Path`

이 프로젝트는 파일 경로를 다룰 때 `pathlib.Path`를 사용합니다.

파일 경로는 운영체제마다 표현 방식이 조금씩 다를 수 있습니다. 문자열로 직접 이어 붙이면 작은 실수가 생기기 쉽습니다. `Path`는 경로를 전용 객체로 다루게 해 줍니다.

```python
self.data_dir = Path(data_dir)
self.transactions_path = self.data_dir / "transactions.jsonl"
```

`Path`는 문자열보다 경로 작업에 적합합니다.

`/` 연산자로 하위 경로를 붙일 수 있습니다.

```python
Path("./data") / "transactions.jsonl"
```

결과는 `data/transactions.jsonl` 경로입니다.

문자열을 직접 이어 붙이는 방식보다 운영체제별 경로 차이를 덜 신경 써도 됩니다.

비전공자 관점에서는 `Path`를 "파일 주소를 안전하게 다루는 도구"라고 이해하면 됩니다.

## 29. 파일 초기화

초기 실행 시 저장 폴더와 파일이 없을 수 있습니다.

프로그램을 처음 실행하는 사용자는 아직 `data` 폴더도, `transactions.jsonl` 파일도 가지고 있지 않을 수 있습니다. 이런 상태에서 바로 파일을 읽으려 하면 오류가 납니다. 그래서 실행 초기에 필요한 폴더와 파일을 준비합니다.

```python
self.data_dir.mkdir(parents=True, exist_ok=True)
```

`parents=True`는 중간 폴더가 없어도 함께 만들겠다는 뜻입니다.

`exist_ok=True`는 이미 폴더가 있어도 오류를 내지 않겠다는 뜻입니다.

파일은 `touch()`로 만듭니다.

```python
path.touch(exist_ok=True)
```

파일이 없으면 만들고, 있으면 그대로 둡니다.

이 초기화 과정 덕분에 사용자는 따로 빈 파일을 만들 필요가 없습니다. 프로그램이 자기 작업 공간을 스스로 준비합니다.

## 30. 원자적 파일 교체

거래 수정과 삭제는 기존 파일을 다시 써야 합니다. 이때 바로 원본 파일을 덮어쓰면 위험합니다. 쓰기 도중 오류가 나면 원본 파일이 깨질 수 있기 때문입니다.

파일 기반 저장에서 가장 조심해야 할 부분이 바로 수정과 삭제입니다. 새 거래 추가는 파일 끝에 한 줄만 붙이면 되지만, 기존 거래를 수정하거나 삭제하려면 파일 전체를 다시 구성해야 합니다.

문제는 원본 파일에 바로 쓰다가 중간에 프로그램이 꺼지거나 오류가 나면 데이터가 어중간한 상태로 남을 수 있다는 점입니다. 가계부처럼 기록이 중요한 프로그램에서는 이런 위험을 줄여야 합니다.

그래서 임시 파일을 만들고, 성공한 뒤에 교체합니다.

```python
fd, temp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=self.data_dir)
try:
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(temp_name, path)
except Exception:
    try:
        os.unlink(temp_name)
    except FileNotFoundError:
        pass
    raise
```

핵심은 `os.replace(temp_name, path)`입니다. 임시 파일을 원본 파일 위치로 교체합니다.

비유하자면 원본 문서를 바로 수정하지 않고, 복사본에 먼저 수정합니다. 복사본이 완성되면 그때 원본과 교체합니다. 복사본 작성 중 문제가 생기면 원본은 그대로 남아 있습니다.

이 방식의 장점은 다음과 같습니다.

- 쓰기 실패 시 원본 파일을 보존할 가능성이 높습니다.
- 성공한 파일만 원본으로 교체합니다.
- 파일 기반 저장에서도 간단한 트랜잭션처럼 동작합니다.

여기서 "원자적"이라는 말은 중간 상태를 가능한 한 보이지 않게 처리한다는 뜻입니다. 성공하면 새 파일이 되고, 실패하면 기존 파일이 남습니다. 반쯤 성공한 애매한 상태를 피하려는 설계입니다.

## 31. `os.fdopen()`과 임시 파일

`tempfile.mkstemp()`는 파일 디스크립터와 임시 파일 이름을 반환합니다.

이 부분은 운영체제와 가까운 코드라 조금 낯설 수 있습니다. 보통 파이썬에서는 `open()`으로 파일 객체를 바로 얻습니다. 하지만 `mkstemp()`는 안전한 임시 파일을 만들기 위해 더 낮은 수준의 파일 번호를 함께 돌려줍니다.

```python
fd, temp_name = tempfile.mkstemp(...)
```

파일 디스크립터는 운영체제 수준의 파일 핸들입니다. 파이썬에서 익숙한 파일 객체처럼 쓰려면 `os.fdopen()`으로 감쌉니다.

```python
with os.fdopen(fd, "w", encoding="utf-8") as file:
    ...
```

이렇게 하면 일반 파일 객체처럼 `write()`를 사용할 수 있습니다.

비전공자 관점에서는 `mkstemp()`가 "안전한 임시 파일 자리 만들기"이고, `os.fdopen()`이 "그 자리를 파이썬에서 쓰기 쉬운 파일 객체로 바꾸기"라고 이해하면 됩니다.

## 32. CSV 처리와 `DictReader`, `DictWriter`

CSV 가져오기는 `csv.DictReader`를 사용합니다.

CSV는 엑셀 표처럼 행과 열로 이루어진 텍스트 파일입니다. 쉼표로 값을 구분하기 때문에 Comma-Separated Values라고 부릅니다.

그냥 한 줄씩 읽으면 각 값이 어떤 의미인지 직접 순서로 판단해야 합니다. 하지만 `DictReader`를 쓰면 헤더 이름을 기준으로 값을 읽을 수 있습니다.

```python
reader = csv.DictReader(file)
```

CSV의 헤더를 기준으로 각 행을 딕셔너리로 읽습니다.

```csv
date,type,category,amount,memo,tags
2024-01-15,expense,food,15000,점심,meal
```

이 행은 다음처럼 읽힙니다.

```python
{
    "date": "2024-01-15",
    "type": "expense",
    "category": "food",
    "amount": "15000",
    "memo": "점심",
    "tags": "meal",
}
```

CSV 내보내기는 `csv.DictWriter`를 사용합니다.

```python
writer = csv.DictWriter(file, fieldnames=["date", "type", "category", "amount", "memo", "tags"])
writer.writeheader()
writer.writerow({...})
```

딕셔너리 키와 CSV 컬럼 이름을 맞춰 쓰기 때문에, 컬럼 순서와 스키마를 명확히 관리할 수 있습니다.

즉, `DictReader`는 CSV 한 줄을 딕셔너리로 바꾸는 도구이고, `DictWriter`는 딕셔너리를 CSV 한 줄로 쓰는 도구입니다. import/export 기능에서 데이터 스키마를 일정하게 유지하는 데 중요합니다.

## 33. 표준 출력과 표준 오류

일반 결과는 `print()`로 출력합니다.

터미널 출력에는 크게 두 통로가 있습니다. 하나는 정상 결과가 나가는 표준 출력이고, 다른 하나는 오류 메시지가 나가는 표준 오류입니다.

```python
print(f"[저장 완료] id={transaction.id}")
```

오류 메시지는 `sys.stderr`로 출력합니다.

```python
print(f"[오류] {exc.message}", file=sys.stderr)
```

표준 출력(stdout)과 표준 오류(stderr)를 나누면 명령어를 자동화할 때 편합니다.

예를 들어 정상 결과만 파일로 저장하고, 오류는 터미널에 그대로 보여줄 수 있습니다.

비유하면 정상 안내 방송과 긴급 안내 방송을 다른 스피커로 내보내는 것과 비슷합니다. 둘 다 화면에 보일 수 있지만, 프로그램 입장에서는 서로 다른 통로입니다.

## 34. 종료 코드

콘솔 프로그램은 종료 코드를 통해 성공과 실패를 알려줍니다.

사람은 화면 메시지를 읽고 성공인지 실패인지 판단할 수 있습니다. 하지만 다른 프로그램이나 자동 채점기는 메시지를 읽는 것보다 숫자로 된 종료 코드를 확인하는 편이 확실합니다.

```python
raise SystemExit(0)
raise SystemExit(1)
```

관례적으로 `0`은 성공, `0`이 아닌 값은 실패입니다.

이 프로젝트에서는 `run()`이 정상적으로 끝나면 `0`을 반환합니다.

```python
return 0
```

오류가 발생하면 `main()`에서 `SystemExit(1)`로 종료합니다.

이것은 자동 채점이나 셸 스크립트에서 매우 중요합니다. 화면 메시지뿐 아니라 프로그램의 성공 여부를 기계적으로 판단할 수 있기 때문입니다.

즉, 종료 코드는 프로그램이 남기는 최종 상태 표시등입니다. 초록불이 `0`, 빨간불이 `0`이 아닌 값이라고 생각하면 됩니다.

## 35. f-string과 포맷 지정

이 프로젝트는 f-string을 사용해 문자열을 만듭니다.

f-string은 문자열 안에 변수 값을 자연스럽게 끼워 넣는 문법입니다. 기존 방식보다 읽기 쉽고 실수도 줄어듭니다.

```python
print(f"[저장 완료] id={transaction.id}")
```

출력 정렬에도 f-string 포맷을 사용합니다.

```python
f"{tx.id:<{widths['id']}}"
f"{tx.amount:>{widths['amount']}}"
```

`<`는 왼쪽 정렬, `>`는 오른쪽 정렬입니다.

금액은 숫자라서 오른쪽 정렬이 보기 좋습니다. ID, 날짜, 타입, 카테고리는 왼쪽 정렬합니다.

```text
TX-000012 | 2024-01-15 | expense | food      |  15000 | 점심
```

콘솔 프로그램은 화면이 단순하기 때문에 정렬이 중요합니다. 열이 삐뚤어지면 사용자가 정보를 비교하기 어렵습니다. 이 프로젝트의 포맷 지정은 외부 라이브러리 없이 표 형태의 가독성을 높이기 위한 장치입니다.

## 36. `isinstance`

요약 출력에서는 예산 객체인지 확인합니다.

`isinstance()`는 어떤 값이 특정 클래스의 객체인지 확인하는 함수입니다. 쉽게 말해 "이 값이 Budget 맞아?"라고 물어보는 코드입니다.

```python
if isinstance(budget, Budget):
    ...
```

`summary["budget"]`에는 `Budget` 객체가 들어 있을 수도 있고, 예산이 없으면 `None`이 들어 있을 수도 있습니다.

`isinstance()`로 타입을 확인하면, 예산이 있을 때만 사용률을 계산할 수 있습니다.

예산이 없는데 사용률을 계산하려 하면 오류가 납니다. 그래서 먼저 예산이 실제로 있는지 확인한 뒤 계산합니다.

## 37. `Any`와 타입의 한계

`to_dict()`는 다음 타입을 반환합니다.

```python
dict[str, Any]
```

`Any`는 어떤 타입이든 가능하다는 뜻입니다. 딕셔너리 값에는 문자열, 정수, 리스트가 함께 들어가기 때문에 하나의 타입으로 표현하기 어렵습니다.

타입 힌트는 코드를 명확하게 해 주지만, 현실의 데이터가 항상 한 가지 타입으로만 깔끔하게 떨어지지는 않습니다. JSON으로 저장할 딕셔너리에는 문자열도 있고, 숫자도 있고, 리스트도 있습니다.

```python
{
    "id": "TX-000001",
    "amount": 15000,
    "tags": ["meal"],
}
```

이럴 때 `Any`를 사용합니다.

하지만 `Any`를 너무 많이 쓰면 타입 힌트의 장점이 줄어듭니다. 이 프로젝트에서는 JSON 변환처럼 값 타입이 섞일 수밖에 없는 곳에 제한적으로 사용합니다.

`Any`는 편리하지만 남용하면 "아무거나 가능"이라는 뜻이 되어 버립니다. 그러면 타입 힌트가 주는 안전함이 약해집니다. 그래서 꼭 필요한 곳에만 쓰는 것이 좋습니다.

## 38. 서비스 계층과 저장소 계층

이 문법은 특정 키워드는 아니지만, 중요한 설계 개념입니다.

프로그램이 작을 때는 모든 코드를 한 파일에 넣어도 돌아갑니다. 하지만 기능이 늘어나면 어디에서 입력을 받고, 어디에서 검증을 하고, 어디에서 파일을 저장하는지 뒤섞이기 쉽습니다.

그래서 역할별로 계층을 나눕니다. 계층은 "일의 담당 구역"이라고 보면 됩니다.

서비스 계층은 업무 규칙을 담당합니다.

```python
class TransactionService:
    def create(...):
        ...
```

저장소 계층은 파일 입출력을 담당합니다.

```python
class TransactionRepository:
    def add(self, transaction: Transaction) -> None:
        self.store.append_json(self.store.transactions_path, transaction.to_dict())
```

이렇게 나누면 장점이 있습니다.

- CLI가 파일 형식을 몰라도 됩니다.
- 저장 방식이 바뀌어도 서비스 규칙을 유지할 수 있습니다.
- 검증, 검색, 요약 같은 업무 로직을 한곳에서 관리할 수 있습니다.
- 테스트할 때 각 계층을 따로 확인하기 쉽습니다.

작은 프로그램이라도 계층을 나누면 "작은 서비스"처럼 설명할 수 있습니다.

비유하면 식당 운영과 비슷합니다. 손님 응대는 홀 직원이 하고, 요리는 주방이 하고, 재고 관리는 창고 담당이 합니다. 모든 사람이 모든 일을 하면 처음에는 빨라 보일 수 있지만, 규모가 조금만 커져도 혼란스러워집니다. 이 프로젝트에서 CLI는 손님 응대, Service는 업무 규칙, Repository는 장부 관리에 가깝습니다.

## 39. 공통 관심사 분리

공통 관심사는 여러 곳에 반복될 수 있지만 핵심 업무 로직은 아닌 기능을 말합니다.

예를 들어 실행 시간 측정, 로그 기록, 권한 확인, 예외 처리 같은 기능은 여러 곳에서 필요할 수 있습니다. 하지만 거래 추가나 월별 요약이라는 핵심 업무 자체는 아닙니다.

이 프로젝트에서는 실행 시간 측정이 공통 관심사입니다.

```python
@log_timing
def run(...):
    ...
```

실행 시간 측정 코드를 `run()` 내부에 직접 넣으면 명령 처리 코드가 지저분해집니다. 데코레이터로 분리하면 핵심 로직은 그대로 두고, 부가 기능만 바깥에서 감쌀 수 있습니다.

이 개념은 웹 서버의 인증, 로깅, 트랜잭션 처리에서도 자주 사용됩니다.

이 관점은 매우 중요합니다. 좋은 코드는 기능이 많아서 좋은 것이 아니라, 서로 다른 성격의 일을 잘 분리해서 이해하기 쉬운 코드입니다.

## 40. 코드 설명을 잘하는 방법

이 프로젝트를 설명할 때는 함수 하나하나를 단순 번역하지 않는 것이 좋습니다. 좋은 설명은 다음 순서를 가집니다.

코드 설명을 잘한다는 것은 코드를 한국어로 그대로 옮기는 것이 아닙니다. "왜 이 코드가 필요한지", "이 코드가 없으면 어떤 문제가 생기는지", "이 코드가 요구사항 중 무엇을 만족하는지"를 말할 수 있어야 합니다.

1. 이 함수가 해결하는 문제를 말합니다.
2. 입력과 반환값을 설명합니다.
3. 내부에서 중요한 문법이나 알고리즘을 짚습니다.
4. 어떤 요구사항을 만족하는지 연결합니다.

예시는 다음과 같습니다.

```md
### TransactionRepository.stream()

거래 파일을 한 줄씩 읽어 Transaction 객체로 변환해 넘겨주는 함수다.
반환 타입은 Iterator[Transaction]이며, 내부에서 yield를 사용한다.

이 함수 덕분에 list, search, summary는 거래 파일 전체를 한 번에 메모리에 올리지 않고
스트리밍 방식으로 처리할 수 있다.

관련 요구사항:
- 제너레이터 기반 스트리밍 처리
- 파일 기반 저장소 분리
- 대용량 데이터에 대한 메모리 부담 감소
```

이런 방식으로 설명하면 문법 지식과 설계 의도를 함께 보여줄 수 있습니다.

발표나 제출 문서에서는 다음 문장 구조를 자주 사용하면 좋습니다.

```text
이 함수는 ...하기 위해 만들었습니다.
입력으로 ...을 받고, 결과로 ...을 반환합니다.
내부에서는 ... 문법을 사용해 ... 문제를 해결합니다.
따라서 ... 요구사항을 만족합니다.
```

이 구조를 쓰면 설명이 흔들리지 않습니다. 단순한 코드 낭독이 아니라 설계 의도를 말하는 설명이 됩니다.

## 41. 이 프로젝트에서 특히 중요한 개념 10개

최종 발표나 제출 설명에서 가장 중요하게 말할 개념은 다음 10개입니다.

1. `dataclass`로 거래와 예산 모델을 명확히 정의했다.
2. 타입 힌트로 함수의 입력과 반환 계약을 드러냈다.
3. JSONL을 사용해 거래를 한 줄 단위로 저장했다.
4. `yield` 제너레이터로 파일을 스트리밍 처리했다.
5. CLI, Service, Repository, Model로 책임을 분리했다.
6. `AppError`로 사용자용 오류와 내부 오류를 구분했다.
7. 데코레이터로 실행 시간 로깅을 핵심 로직에서 분리했다.
8. update/delete는 임시 파일과 `os.replace()`로 안정성을 높였다.
9. CSV import/export는 `DictReader`, `DictWriter`로 스키마를 고정했다.
10. `argparse` subparser로 여러 명령을 하나의 콘솔 앱에 묶었다.

이 10개를 설명할 수 있으면, 단순히 코드를 완성한 것이 아니라 유지보수 가능한 콘솔 서비스를 설계했다는 점을 충분히 보여줄 수 있습니다.

## 42. 쉬운 예제로 다시 보기

앞 장들은 실제 프로젝트 코드를 기준으로 설명했습니다. 이번 장에서는 같은 개념을 더 작은 예제로 다시 봅니다. 실제 가계부 코드가 길게 느껴질 때는 여기 있는 짧은 예제부터 이해한 뒤, 다시 프로젝트 코드로 돌아가면 훨씬 읽기 쉽습니다.

### 42.1 `argparse`는 터미널 입력을 정리해 주는 도구

가계부 앱에서는 사용자가 이런 명령을 입력합니다.

```bash
python -m budget_app list --limit 3
```

이 명령은 코드 안에서 `command="list"`, `limit=3` 같은 값으로 정리되어야 합니다. 아주 작은 예제로 보면 다음과 같습니다.

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("name")
parser.add_argument("--age", type=int, default=0)

args = parser.parse_args()

print(args.name)
print(args.age)
```

사용자가 다음처럼 실행하면:

```bash
python hello.py Mina --age 20
```

코드 안에서는 이렇게 볼 수 있습니다.

```python
args.name  # "Mina"
args.age   # 20
```

즉, `argparse`는 사용자가 입력한 문자열 명령을 프로그램이 쓰기 좋은 변수로 바꿔 줍니다. 가계부 앱의 `add`, `list`, `search`, `summary`도 같은 원리로 동작합니다.

### 42.2 `dataclass`는 데이터 묶음을 쉽게 만든다

거래 한 건에는 날짜, 금액, 카테고리 같은 값이 함께 있어야 합니다. 이를 따로따로 변수로 들고 다니면 실수하기 쉽습니다.

```python
date = "2024-01-15"
amount = 15000
category = "food"
```

`dataclass`를 쓰면 관련 값을 하나의 객체로 묶을 수 있습니다.

```python
from dataclasses import dataclass

@dataclass
class SimpleTransaction:
    date: str
    amount: int
    category: str

tx = SimpleTransaction("2024-01-15", 15000, "food")

print(tx.date)      # 2024-01-15
print(tx.amount)    # 15000
print(tx.category)  # food
```

이 예제에서 `tx`는 거래 한 건입니다. 가계부 프로젝트의 `Transaction`은 이보다 필드가 더 많을 뿐, 기본 생각은 같습니다. 여러 값을 하나의 의미 있는 묶음으로 만드는 것입니다.

### 42.3 `Optional`은 값이 없을 수도 있다는 표시

검색 조건은 사용자가 입력할 수도 있고, 입력하지 않을 수도 있습니다. 예를 들어 메모 검색어가 없을 수도 있습니다.

```python
from typing import Optional

def print_memo(memo: Optional[str]) -> None:
    if memo is None:
        print("메모 없음")
    else:
        print(f"메모: {memo}")

print_memo("점심")
print_memo(None)
```

`Optional[str]`은 `str`이거나 `None`이라는 뜻입니다. 그래서 이 함수 안에서는 `None`인지 먼저 확인합니다.

가계부 앱에서도 `--memo`, `--category`, `--from`, `--to` 같은 검색 조건은 사용자가 생략할 수 있습니다. 이런 값들은 "없을 수도 있음"을 코드에 표시해야 하므로 `Optional`이 어울립니다.

### 42.4 `Union`은 여러 타입 중 하나를 받겠다는 뜻

금액은 터미널에서 들어오면 문자열입니다.

```python
"15000"
```

하지만 프로그램 내부에서는 이미 정수일 수도 있습니다.

```python
15000
```

둘 다 받을 수 있게 하려면 `Union`을 사용할 수 있습니다.

```python
from typing import Union

def parse_amount(value: Union[str, int]) -> int:
    return int(value)

print(parse_amount("15000"))  # 15000
print(parse_amount(15000))    # 15000
```

중요한 점은 입력은 두 종류를 허용하지만, 결과는 항상 `int`로 맞춘다는 것입니다. 가계부 앱의 검증 함수들도 이런 식으로 바깥에서 들어온 값을 내부에서 쓰기 좋은 형태로 바꿉니다.

### 42.5 `yield`는 값을 하나씩 꺼내 주는 문법

`return`은 값을 돌려주고 함수가 끝납니다.

```python
def get_numbers() -> list[int]:
    return [1, 2, 3]

for number in get_numbers():
    print(number)
```

`yield`는 값을 하나 내보낸 뒤, 함수의 상태를 잠시 멈춥니다. 다음 값이 필요할 때 이어서 실행합니다.

```python
def make_numbers():
    yield 1
    yield 2
    yield 3

for number in make_numbers():
    print(number)
```

출력은 둘 다 `1`, `2`, `3`입니다. 하지만 동작 방식이 다릅니다.

- `return [1, 2, 3]`은 숫자 목록을 한 번에 만들어서 돌려줍니다.
- `yield`는 숫자를 하나씩 필요할 때마다 내보냅니다.

가계부 앱에서는 거래 파일을 한 줄씩 읽기 위해 `yield`를 사용합니다. 거래가 많아져도 파일 전체를 한 번에 메모리에 올리지 않고 처리할 수 있습니다.

### 42.6 JSONL은 한 줄에 데이터 하나를 저장한다

일반 JSON은 전체 목록을 하나의 큰 배열로 저장할 수 있습니다.

```json
[
  {"amount": 15000, "category": "food"},
  {"amount": 3000, "category": "transport"}
]
```

JSONL은 한 줄에 하나의 JSON 객체를 저장합니다.

```json
{"amount": 15000, "category": "food"}
{"amount": 3000, "category": "transport"}
```

새 거래를 추가할 때 JSONL은 파일 끝에 한 줄만 붙이면 됩니다.

```python
import json

transaction = {"amount": 15000, "category": "food"}

with open("transactions.jsonl", "a", encoding="utf-8") as file:
    file.write(json.dumps(transaction, ensure_ascii=False) + "\n")
```

가계부처럼 기록이 계속 늘어나는 프로그램에서는 이 방식이 단순하고 효율적입니다.

### 42.7 `with`는 파일을 자동으로 닫아 준다

파일을 열면 작업이 끝난 뒤 닫아야 합니다.

```python
file = open("memo.txt", "w", encoding="utf-8")
file.write("hello")
file.close()
```

하지만 중간에 오류가 나면 `close()`까지 도달하지 못할 수 있습니다. 그래서 보통 `with`를 사용합니다.

```python
with open("memo.txt", "w", encoding="utf-8") as file:
    file.write("hello")
```

`with` 블록이 끝나면 파일은 자동으로 닫힙니다. 가계부 앱에서 JSONL과 CSV 파일을 읽고 쓸 때도 같은 이유로 `with`를 사용합니다.

### 42.8 리스트 컴프리헨션은 필터링을 짧게 쓴 것이다

다음 코드는 짝수만 모읍니다.

```python
numbers = [1, 2, 3, 4, 5, 6]

even_numbers = []
for number in numbers:
    if number % 2 == 0:
        even_numbers.append(number)
```

리스트 컴프리헨션으로 쓰면 다음과 같습니다.

```python
numbers = [1, 2, 3, 4, 5, 6]
even_numbers = [number for number in numbers if number % 2 == 0]
```

읽는 순서는 다음과 같습니다.

1. `numbers`에서 값을 하나씩 꺼낸다.
2. 꺼낸 값을 `number`라고 부른다.
3. `number % 2 == 0`인 값만 남긴다.
4. 남은 값으로 새 리스트를 만든다.

가계부 앱의 검색도 비슷합니다. 전체 거래를 하나씩 보면서, 조건에 맞는 거래만 결과 리스트에 담습니다.

### 42.9 딕셔너리는 이름표가 붙은 값들의 묶음

카테고리별 지출 합계를 계산한다고 생각해 봅니다.

```python
transactions = [
    {"category": "food", "amount": 15000},
    {"category": "transport", "amount": 3000},
    {"category": "food", "amount": 8000},
]

totals = {}

for tx in transactions:
    category = tx["category"]
    amount = tx["amount"]
    totals[category] = totals.get(category, 0) + amount

print(totals)
```

결과는 다음과 같습니다.

```python
{"food": 23000, "transport": 3000}
```

`totals.get(category, 0)`은 "이미 합계가 있으면 가져오고, 처음 보는 카테고리면 0에서 시작하라"는 뜻입니다. 월별 요약 기능의 카테고리 집계도 이 패턴을 사용합니다.

### 42.10 예외는 문제를 발견했을 때 보내는 신호

잘못된 날짜가 들어오면 그냥 넘어가면 안 됩니다. 사용자에게 무엇이 잘못되었는지 알려야 합니다.

```python
class AppError(Exception):
    pass

def check_amount(amount: int) -> None:
    if amount <= 0:
        raise AppError("금액은 0보다 커야 합니다.")

try:
    check_amount(-1000)
except AppError as exc:
    print(f"[오류] {exc}")
```

`raise`는 문제를 발견했음을 알리는 신호입니다. `except`는 그 신호를 잡아서 사용자에게 보여주기 좋은 메시지로 바꿉니다.

가계부 앱에서는 날짜 형식, 금액, 거래 유형 등이 잘못되었을 때 `AppError`를 사용합니다. 덕분에 사용자는 긴 내부 오류 대신 이해하기 쉬운 오류 메시지를 볼 수 있습니다.

### 42.11 데코레이터는 함수에 기능을 한 겹 덧붙인다

다음 함수는 인사말을 출력합니다.

```python
def say_hello():
    print("hello")
```

이 함수가 실행되기 전후에 메시지를 추가하고 싶다면 데코레이터를 만들 수 있습니다.

```python
def add_message(func):
    def wrapper():
        print("시작")
        func()
        print("끝")
    return wrapper

@add_message
def say_hello():
    print("hello")

say_hello()
```

출력은 다음과 같습니다.

```text
시작
hello
끝
```

`@add_message`는 `say_hello()` 자체의 핵심 동작은 그대로 두고, 앞뒤에 부가 동작을 붙입니다. 가계부 앱의 `@log_timing`도 같은 원리입니다. 명령 실행 로직은 그대로 두고, 실행 시간 측정 기능만 바깥에서 덧붙입니다.

### 42.12 `Path`는 파일 경로를 다루기 쉽게 만든다

문자열로 경로를 만들면 직접 `/`를 붙여야 합니다.

```python
data_dir = "./data"
path = data_dir + "/transactions.jsonl"
```

`Path`를 쓰면 경로를 객체처럼 다룰 수 있습니다.

```python
from pathlib import Path

data_dir = Path("./data")
path = data_dir / "transactions.jsonl"

print(path)
```

`Path`는 폴더 만들기, 파일 존재 확인, 파일 열기 같은 작업도 자연스럽게 처리합니다.

```python
data_dir.mkdir(exist_ok=True)
path.touch(exist_ok=True)
```

가계부 앱은 저장 폴더와 JSONL 파일을 다루기 때문에 문자열보다 `Path`가 더 안전하고 읽기 좋습니다.

### 42.13 큰 흐름으로 다시 연결하기

위 예제들을 가계부 앱 흐름에 연결하면 다음과 같습니다.

1. 사용자가 터미널에 명령을 입력한다.
2. `argparse`가 명령을 `args`로 정리한다.
3. 서비스 계층이 입력값을 검증하고 `Transaction` 같은 `dataclass` 객체를 만든다.
4. 객체는 `to_dict()`로 파일에 저장하기 좋은 딕셔너리가 된다.
5. 저장소 계층이 JSONL 파일에 한 줄로 기록한다.
6. 목록, 검색, 요약을 할 때는 `yield`로 거래를 한 줄씩 읽는다.
7. 문제가 있으면 `AppError`로 사용자에게 친절한 오류를 보여준다.
8. `@log_timing` 같은 데코레이터는 핵심 로직 바깥에서 실행 시간을 기록한다.

따라서 이 프로젝트의 심화 문법은 따로따로 흩어진 지식이 아닙니다. 터미널 입력을 받고, 거래 데이터를 만들고, 파일에 저장하고, 다시 읽어서 보여주기 위한 하나의 흐름 안에서 서로 연결되어 있습니다.
