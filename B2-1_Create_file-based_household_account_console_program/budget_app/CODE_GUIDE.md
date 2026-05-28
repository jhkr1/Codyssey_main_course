# budget_app 코드 해설과 파이썬 개념 정리

이 문서는 가계부 콘솔 프로그램을 학습 관점에서 이해하기 위한 코드 해설서입니다. `README.md`가 실행 방법과 제출 요구사항 중심이라면, 이 문서는 “왜 이렇게 나누었는지”, “각 코드가 어떤 개념을 보여주는지”를 설명합니다.

## 1. 전체 구조 한눈에 보기

```text
budget_app/
  __main__.py       # python -m budget_app 실행 진입점
  cli.py            # 명령어 파싱, 사용자 입력, 화면 출력 연결
  models.py         # Transaction, Budget, SearchCriteria 데이터 구조
  repositories.py   # JSONL 파일 저장소, 스트리밍 읽기, 원자적 교체
  services.py       # 거래/카테고리/예산 업무 로직
  validators.py     # 날짜, 금액, 타입, 태그 검증
  decorators.py     # 실행 시간 로그 데코레이터
  formatters.py     # 콘솔 출력 포맷
  errors.py         # 사용자에게 보여줄 예외 타입
```

이 프로젝트는 크게 네 계층으로 나뉩니다.

| 계층 | 파일 | 책임 |
| --- | --- | --- |
| CLI | `cli.py`, `__main__.py` | 명령어를 받고 서비스를 호출한다 |
| Service | `services.py` | 가계부 업무 규칙을 처리한다 |
| Repository | `repositories.py` | 파일을 읽고 쓴다 |
| Model | `models.py` | 데이터 구조를 정의한다 |

핵심 원칙은 “각 파일이 하나의 책임에 집중한다”입니다. 예를 들어 `cli.py`는 JSONL 파일을 직접 열지 않습니다. 파일 저장 방식이 바뀌어도 CLI 코드는 크게 바뀌지 않게 만들기 위해서입니다.

## 2. 실행 흐름

사용자가 다음 명령을 실행한다고 가정합니다.

```bash
python -m budget_app list --limit 3
```

흐름은 다음과 같습니다.

1. Python이 `budget_app/__main__.py`를 실행합니다.
2. `__main__.py`가 `cli.py`의 `main()`을 호출합니다.
3. `main()`이 `run()`을 실행하고, 오류가 나면 사용자용 메시지로 바꿉니다.
4. `run()`이 `argparse`로 명령어를 해석합니다.
5. `build_services()`가 저장소와 서비스를 생성합니다.
6. `TransactionService.latest()`가 최신 거래를 가져옵니다.
7. `TransactionRepository.stream()`이 거래 파일을 한 줄씩 읽습니다.
8. `formatters.print_transactions()`가 화면에 보기 좋게 출력합니다.

즉, 명령어 하나도 CLI, Service, Repository, Formatter를 거쳐 처리됩니다.

## 3. `__main__.py`: 모듈 실행 진입점

```python
from budget_app.cli import main

main()
```

`python -m budget_app`로 실행하면 Python은 패키지 안의 `__main__.py`를 찾습니다. 이 파일이 있기 때문에 다음처럼 실행할 수 있습니다.

```bash
python -m budget_app --help
```

`__main__.py`에는 복잡한 코드를 넣지 않았습니다. 실제 로직은 `cli.py`에 두고, 진입점은 최대한 얇게 유지했습니다.

## 4. `cli.py`: 명령어와 프로그램을 연결하는 곳

`cli.py`의 핵심 역할은 세 가지입니다.

1. 어떤 명령어와 옵션을 받을지 정의한다.
2. 사용자 입력을 받는다.
3. 알맞은 서비스 메서드를 호출한다.

### argparse

`argparse`는 표준 라이브러리의 CLI 파서입니다.

```python
parser = argparse.ArgumentParser(prog="python -m budget_app")
parser.add_argument("--data-dir", default="./data")
subparsers = parser.add_subparsers(dest="command", required=True)
```

여기서 `subparsers`는 `add`, `list`, `search` 같은 하위 명령을 만들기 위해 사용합니다.

예를 들어 `list` 명령은 이렇게 정의되어 있습니다.

```python
list_parser = subparsers.add_parser("list", help="거래 목록")
list_parser.add_argument("--limit", type=int, default=10)
```

그래서 사용자는 다음처럼 실행할 수 있습니다.

```bash
python -m budget_app list --limit 5
```

### 대화형 입력

`add` 명령은 과제 요구사항에 맞게 대화형 입력을 사용합니다.

```python
def prompt(label: str) -> str:
    return input(label).strip()
```

`strip()`은 앞뒤 공백을 제거합니다. 사용자가 실수로 공백을 넣어도 기본적인 입력 정리가 됩니다.

### 오류 처리와 종료 코드

`main()`은 `AppError`와 `OSError`를 잡아서 스택트레이스 대신 사용자용 메시지를 출력합니다.

```python
except AppError as exc:
    print(f"[오류] {exc.message}", file=sys.stderr)
    if exc.hint:
        print(f"[힌트] {exc.hint}", file=sys.stderr)
    raise SystemExit(1) from None
```

중요한 점은 오류 종료 시 `SystemExit(1)`을 사용한다는 것입니다. 정상 종료는 0, 오류 종료는 0이 아닌 값을 반환해야 한다는 요구사항을 만족합니다.

## 5. `models.py`: dataclass로 데이터 모델 만들기

거래 데이터는 `Transaction` 클래스로 표현합니다.

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

### dataclass

`dataclass`는 데이터 중심 클래스를 간결하게 만들게 해주는 표준 라이브러리 기능입니다. 직접 `__init__`을 작성하지 않아도 필드를 기반으로 생성자가 만들어집니다.

### frozen=True

`frozen=True`는 객체를 만든 뒤 필드 값을 직접 바꾸지 못하게 합니다.

```python
tx.amount = 1000  # frozen=True라서 불가능
```

거래 수정은 객체 내부를 직접 바꾸는 대신, `services.py`에서 `dataclasses.replace()`로 새 객체를 만들어 처리합니다. 이렇게 하면 데이터 변경 지점이 더 명확해집니다.

### mutable default 주의

리스트 같은 변경 가능한 기본값은 바로 `tags: list[str] = []`처럼 쓰면 안 됩니다. 여러 객체가 같은 리스트를 공유할 수 있기 때문입니다.

그래서 다음처럼 씁니다.

```python
tags: list[str] = field(default_factory=list)
```

### to_dict / from_dict

파일에 저장하려면 객체를 JSON으로 바꿀 수 있는 딕셔너리로 변환해야 합니다.

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

반대로 파일에서 읽은 딕셔너리를 다시 `Transaction` 객체로 만드는 역할은 `from_dict()`가 합니다.

## 6. `validators.py`: 입력 검증 분리

입력 검증은 여러 명령에서 반복됩니다. 예를 들어 날짜 검증은 `add`, `update`, `search`, `export`, `summary`에서 모두 필요합니다.

그래서 검증 로직을 `validators.py`로 분리했습니다.

```python
def parse_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise AppError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).", "예: 2024-01-15") from exc
    return value
```

여기서 `datetime.strptime()`은 문자열이 특정 날짜 형식에 맞는지 검사합니다.

### 검증 함수가 값을 반환하는 이유

`parse_amount()`는 단순히 검사만 하지 않고 문자열을 정수로 변환해서 반환합니다.

```python
def parse_amount(value: Union[str, int]) -> int:
    amount = int(value)
    if amount <= 0:
        raise AppError(...)
    return amount
```

이렇게 하면 서비스 계층에서 “검증된 값”을 바로 사용할 수 있습니다.

## 7. `errors.py`: 사용자용 예외

```python
class AppError(Exception):
    def __init__(self, message: str, hint: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
```

`AppError`는 사용자의 입력 오류나 처리 불가 상황을 표현합니다.

예:

- 날짜 형식이 틀림
- 금액이 0 이하임
- 없는 카테고리를 사용함
- export 조건이 없음

이 예외를 쓰면 코드 내부에서는 `raise AppError(...)`만 하고, 최종 출력 방식은 `cli.py`의 `main()`에서 한 번에 처리할 수 있습니다.

## 8. `repositories.py`: 파일 저장소와 제너레이터

저장소 계층은 파일을 직접 다루는 곳입니다.

### 저장 파일 3개

```python
self.transactions_path = self.data_dir / "transactions.jsonl"
self.categories_path = self.data_dir / "categories.jsonl"
self.budgets_path = self.data_dir / "budgets.jsonl"
```

과제 요구사항대로 거래, 카테고리, 예산을 각각 다른 파일에 저장합니다.

### 초기화

```python
def initialize(self) -> None:
    self.data_dir.mkdir(parents=True, exist_ok=True)
    for path in (...):
        path.touch(exist_ok=True)
```

`mkdir(parents=True, exist_ok=True)`는 폴더가 없으면 만들고, 이미 있어도 오류를 내지 않습니다.

`touch(exist_ok=True)`는 파일이 없으면 만들고, 이미 있으면 그대로 둡니다.

카테고리 파일이 비어 있으면 기본 카테고리를 자동 생성합니다.

### JSONL

JSONL은 한 줄에 JSON 객체 하나를 저장하는 형식입니다.

```json
{"name":"food"}
{"name":"transport"}
```

거래 추가처럼 새 데이터를 끝에 붙이는 작업에 잘 맞습니다.

### 제너레이터와 yield

가장 중요한 함수는 `iter_json()`입니다.

```python
def iter_json(self, path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            ...
            yield data
```

`yield`를 사용하면 함수가 값을 한 번에 모두 반환하지 않고 하나씩 생성합니다.

일반 리스트 방식:

```python
rows = [json.loads(line) for line in file]
```

이 방식은 파일 전체를 메모리에 올립니다.

제너레이터 방식:

```python
for row in self.store.iter_json(path):
    ...
```

이 방식은 한 줄씩 읽고 처리합니다. 거래가 많아져도 메모리 부담이 작습니다.

### TransactionRepository.stream()

```python
def stream(self) -> Iterator[Transaction]:
    for row in self.store.iter_json(self.store.transactions_path):
        yield Transaction.from_dict(row)
```

파일에서 읽은 딕셔너리를 `Transaction` 객체로 바꿔서 하나씩 넘겨줍니다. 서비스 계층은 JSONL 구조를 몰라도 되고, `Transaction` 객체만 다루면 됩니다.

### 원자적 교체

수정과 삭제는 파일 중간 한 줄만 안정적으로 바꾸기 어렵습니다. 그래서 전체를 다시 씁니다.

```python
fd, temp_name = tempfile.mkstemp(...)
...
os.replace(temp_name, path)
```

흐름:

1. 임시 파일을 만든다.
2. 변경된 내용을 임시 파일에 모두 쓴다.
3. 성공하면 `os.replace()`로 원본 파일을 교체한다.
4. 실패하면 임시 파일을 삭제한다.

이 방식은 쓰기 중간에 오류가 나도 원본 파일 손상 가능성을 줄입니다.

## 9. `services.py`: 업무 규칙이 모이는 곳

서비스 계층은 “가계부 프로그램이 해야 하는 일”을 처리합니다.

### 거래 추가

```python
def create(...):
    transaction = Transaction(
        id=self.transactions.next_id(),
        date=parse_date(date),
        type=parse_type(tx_type),
        category=self._validated_category(category),
        amount=parse_amount(amount),
        memo=memo,
        tags=parse_tags(tags),
    )
    self.transactions.add(transaction)
    return transaction
```

여기서 일어나는 일:

1. 새 ID를 만든다.
2. 날짜, 타입, 카테고리, 금액, 태그를 검증한다.
3. `Transaction` 객체를 만든다.
4. 저장소에 저장한다.

CLI가 직접 검증과 저장을 하지 않고 서비스에 맡기는 이유는 같은 로직을 import, update 등에서도 재사용하기 위해서입니다.

### 최신 목록

```python
return heapq.nlargest(limit, self.transactions.stream(), key=lambda item: (item.date, item.id))
```

`heapq.nlargest()`는 전체 데이터를 정렬하지 않고 필요한 개수만 효율적으로 뽑을 때 사용합니다. 거래 파일은 `stream()`으로 한 줄씩 읽고, 그중 최신 N개만 유지합니다.

정렬 기준은 `(date, id)`입니다. 날짜가 같으면 ID가 큰 거래가 더 최신으로 간주됩니다.

### 검색

```python
results = [tx for tx in self.transactions.stream() if self._matches(tx, criteria)]
```

`SearchCriteria`는 검색 조건을 한 객체로 묶은 것입니다. 조건이 많아질수록 함수 인자가 길어지는데, dataclass 하나로 묶으면 전달이 편해집니다.

`_matches()`는 거래 하나가 조건에 맞는지 검사합니다.

```python
if criteria.category and transaction.category != criteria.category:
    return False
```

조건이 있으면 검사하고, 조건이 없으면 통과시키는 구조입니다.

### 월별 요약

```python
for transaction in self.transactions.stream():
    if not transaction.date.startswith(month):
        continue
```

날짜가 `YYYY-MM-DD` 형식이므로 `2024-01`로 시작하는 거래를 찾으면 해당 월 거래입니다.

요약에서는 다음 값을 계산합니다.

- 총 수입
- 총 지출
- 잔액
- 카테고리별 지출 합계
- 월 예산

### 수정

수정은 옵션으로 받은 값만 바꿉니다.

```python
return replace(
    transaction,
    amount=parse_amount(str(changes["amount"])) if changes.get("amount") else transaction.amount,
)
```

`dataclasses.replace()`는 기존 dataclass 객체를 바탕으로 일부 필드만 바꾼 새 객체를 만듭니다.

### 삭제

삭제 자체는 서비스에서 저장소로 위임합니다.

```python
def delete(self, transaction_id: str) -> bool:
    return self.transactions.delete(transaction_id)
```

서비스는 “삭제를 요청한다”는 업무 의미를 갖고, 실제 파일 재작성은 저장소가 담당합니다.

### import/export

`csv.DictReader`는 CSV 한 행을 딕셔너리로 읽습니다.

```python
reader = csv.DictReader(file)
```

예를 들어 CSV가 다음과 같으면:

```csv
date,type,category,amount,memo,tags
2024-01-15,expense,food,15000,점심,meal
```

각 행은 이런 딕셔너리가 됩니다.

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

`import_csv()`는 각 행을 `create()`로 보내므로, 일반 거래 추가와 같은 검증 규칙을 공유합니다.

## 10. `decorators.py`: 데코레이터로 공통 관심사 분리

데코레이터는 함수를 감싸서 앞뒤에 공통 동작을 추가하는 문법입니다.

```python
@log_timing
def run(...):
    ...
```

위 코드는 아래와 비슷한 의미입니다.

```python
run = log_timing(run)
```

`log_timing()`은 함수 실행 전 시간을 기록하고, 실행 후 걸린 시간을 로그로 남깁니다.

```python
started = time.perf_counter()
try:
    return func(*args, **kwargs)
finally:
    elapsed_ms = (time.perf_counter() - started) * 1000
    logger.info(...)
```

`finally`를 사용했기 때문에 함수가 정상 종료하든 예외가 발생하든 실행 시간이 기록됩니다.

## 11. `formatters.py`: 출력 전용 코드

출력 포맷은 비즈니스 로직과 분리했습니다.

```python
def print_transactions(transactions: list[Transaction]) -> None:
    ...
```

`widths` 딕셔너리는 각 열의 너비를 계산합니다.

```python
"category": max(8, max(len(tx.category) for tx in transactions))
```

카테고리 이름이 길어져도 표가 어느 정도 정렬되어 보이도록 하기 위한 코드입니다.

`print_summary()`는 요약 결과 딕셔너리를 화면에 출력합니다. 예산이 있으면 사용률과 초과 경고도 함께 보여줍니다.

## 12. 타입 힌트 읽는 법

타입 힌트는 코드의 계약입니다.

```python
def get(self, month: str) -> Optional[Budget]:
```

뜻:

- `month`는 문자열이다.
- 반환값은 `Budget`일 수도 있고 `None`일 수도 있다.

```python
def create(..., amount: Union[str, int], ...) -> Transaction:
```

뜻:

- `amount`는 문자열 또는 정수로 받을 수 있다.
- 최종 반환값은 `Transaction` 객체다.

타입 힌트는 실행 중 자동 검사를 강제하지는 않지만, 함수의 의도를 명확하게 해주고 유지보수할 때 실수를 줄여줍니다.

## 13. 이 프로젝트에서 중요한 설계 결정

### 1. JSONL 사용

거래 추가가 쉽고, 한 줄씩 읽는 스트리밍 처리와 잘 맞습니다.

### 2. 저장 파일 3개 분리

거래, 카테고리, 예산은 바뀌는 주기와 역할이 다릅니다. 파일을 나누면 구조가 명확해집니다.

### 3. CLI와 저장소 분리

CLI가 파일 형식을 직접 알지 않아도 됩니다. 나중에 CSV 저장, SQLite 저장으로 바꾸더라도 서비스/저장소 중심으로 변경하면 됩니다.

### 4. 사용자용 예외

사용자가 잘못 입력했을 때 개발자용 스택트레이스 대신 원인과 힌트를 보여줍니다.

### 5. update/delete의 임시 파일 교체

파일 기반 프로그램에서 데이터 안전성을 높이기 위한 방식입니다.

## 14. 직접 따라가며 읽기 좋은 순서

처음부터 모든 파일을 동시에 읽으면 복잡합니다. 아래 순서로 보면 흐름이 잘 잡힙니다.

1. `__main__.py`: 실행 진입점 확인
2. `cli.py`: 명령어가 어디로 연결되는지 확인
3. `models.py`: 어떤 데이터가 오가는지 확인
4. `validators.py`: 입력값이 어떻게 검증되는지 확인
5. `services.py`: 실제 업무 로직 확인
6. `repositories.py`: 파일 저장과 스트리밍 확인
7. `formatters.py`: 출력 모양 확인
8. `decorators.py`: 공통 기능 분리 확인

## 15. 학습 체크 질문

아래 질문에 답할 수 있으면 이 프로젝트의 핵심을 이해한 것입니다.

- `python -m budget_app`를 실행하면 왜 `__main__.py`가 실행될까?
- `Transaction`을 dict로 바꿔야 하는 이유는 무엇일까?
- JSONL은 일반 JSON 배열 저장 방식과 무엇이 다를까?
- `yield`를 쓰면 파일 전체를 메모리에 올리지 않아도 되는 이유는 무엇일까?
- `AppError`를 따로 만든 이유는 무엇일까?
- `update/delete`에서 임시 파일을 만들고 `os.replace()`를 쓰는 이유는 무엇일까?
- CLI 계층이 파일을 직접 열지 않는 이유는 무엇일까?
- `dataclasses.replace()`는 왜 이 프로젝트의 `frozen=True` 모델과 잘 맞을까?

## 16. 더 자세한 실행 흐름: add 명령

이번에는 `add` 명령 하나를 코드 수준에서 더 자세히 따라가 봅니다.

사용자가 다음 명령을 실행합니다.

```bash
python -m budget_app add
```

그러면 `cli.py`의 `run()` 함수 안에서 아래 분기가 실행됩니다.

```python
if args.command == "add":
    transaction = transaction_service.create(
        date=prompt("날짜(YYYY-MM-DD): "),
        tx_type=prompt("타입(income/expense): "),
        category=prompt("카테고리: "),
        amount=prompt("금액(양수): "),
        memo=prompt("메모(선택): "),
        tags=prompt("태그(쉼표로 구분, 없으면 엔터): "),
    )
    print(f"[저장 완료] id={transaction.id}")
```

이 코드에서 CLI가 하는 일은 입력을 받는 것뿐입니다. 날짜가 맞는지, 카테고리가 있는지, 금액이 양수인지 판단하지 않습니다. 그런 판단은 `TransactionService.create()`가 합니다.

이렇게 역할을 나누면 장점이 있습니다.

- CLI가 단순해집니다.
- 같은 생성 로직을 `import_csv()`에서도 재사용할 수 있습니다.
- 검증 규칙이 한 곳에 모여서 유지보수가 쉽습니다.

`TransactionService.create()`는 다음 순서로 동작합니다.

```python
transaction = Transaction(
    id=self.transactions.next_id(),
    date=parse_date(date),
    type=parse_type(tx_type),
    category=self._validated_category(category),
    amount=parse_amount(amount),
    memo=memo,
    tags=parse_tags(tags),
)
```

각 필드는 그냥 저장되지 않고 검증 또는 변환을 거칩니다.

| 입력값 | 처리 함수 | 역할 |
| --- | --- | --- |
| 날짜 | `parse_date()` | `YYYY-MM-DD` 형식인지 확인 |
| 타입 | `parse_type()` | `income` 또는 `expense`인지 확인 |
| 카테고리 | `_validated_category()` | 등록된 카테고리인지 확인 |
| 금액 | `parse_amount()` | 정수 변환 후 양수인지 확인 |
| 태그 | `parse_tags()` | 쉼표 문자열을 리스트로 변환 |

검증이 모두 끝나면 `Transaction` 객체가 만들어지고 저장소에 저장됩니다.

```python
self.transactions.add(transaction)
```

여기서 `self.transactions`는 `TransactionRepository`입니다. 서비스는 “거래를 저장해줘”라고 요청할 뿐이고, 실제로 JSONL 파일에 쓰는 방식은 저장소가 알고 있습니다.

## 17. 더 자세한 실행 흐름: list 명령

`list` 명령은 거래 파일을 읽어 최신 거래를 보여줍니다.

```bash
python -m budget_app list --limit 10
```

CLI에서는 다음 코드가 실행됩니다.

```python
print_transactions(transaction_service.latest(args.limit))
```

`latest()`는 최신 N개만 가져옵니다.

```python
def latest(self, limit: int) -> list[Transaction]:
    if limit <= 0:
        raise AppError("--limit은 1 이상이어야 합니다.", "예: --limit 10")
    return heapq.nlargest(limit, self.transactions.stream(), key=lambda item: (item.date, item.id))
```

여기서 중요한 부분은 `self.transactions.stream()`입니다.

`stream()`은 거래 전체를 리스트로 한 번에 반환하지 않습니다. 파일에서 한 줄씩 읽고, 하나씩 `Transaction` 객체로 만들어 넘겨줍니다.

그리고 `heapq.nlargest()`는 그 스트림을 보면서 최신 N개만 골라냅니다.

전체 정렬 방식과 비교하면 차이가 있습니다.

```python
sorted(self.transactions.stream(), key=..., reverse=True)[:limit]
```

위 방식은 모든 거래를 정렬해야 합니다. 거래가 10만 개라면 10만 개를 모두 정렬합니다.

현재 방식은 다음과 같습니다.

```python
heapq.nlargest(limit, self.transactions.stream(), key=...)
```

이 방식은 필요한 개수만 유지하면서 큰 값들을 찾습니다. `--limit 10`이면 최신 후보 10개 중심으로 관리합니다. 과제에서 요구한 “스트리밍 처리” 의도에 더 잘 맞습니다.

## 18. 더 자세한 실행 흐름: search 명령

검색은 여러 조건을 조합해야 합니다.

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --category food --type expense
```

검색 조건은 `SearchCriteria` dataclass에 담습니다.

```python
SearchCriteria(
    date_from=args.date_from,
    date_to=args.date_to,
    category=args.category,
    tx_type=args.tx_type,
    query=args.q,
    tag=args.tag,
)
```

이렇게 조건을 객체로 묶은 이유는 함수 인자가 너무 길어지는 것을 막기 위해서입니다.

인자를 직접 넘기면 이런 형태가 됩니다.

```python
search(date_from, date_to, category, tx_type, query, tag)
```

지금은 조건이 6개지만, 나중에 최소 금액, 최대 금액, 정렬 방식이 추가되면 더 길어집니다. `SearchCriteria`를 쓰면 검색 조건이 하나의 의미 있는 데이터로 묶입니다.

실제 조건 검사는 `_matches()`가 합니다.

```python
def _matches(self, transaction: Transaction, criteria: SearchCriteria) -> bool:
    if criteria.date_from and transaction.date < criteria.date_from:
        return False
    if criteria.date_to and transaction.date > criteria.date_to:
        return False
    ...
    return True
```

이 함수는 “거래 하나가 검색 조건에 맞는가?”만 판단합니다.

구조는 단순합니다.

1. 조건이 없으면 검사하지 않습니다.
2. 조건이 있으면 거래와 비교합니다.
3. 하나라도 맞지 않으면 `False`를 반환합니다.
4. 모든 조건을 통과하면 `True`를 반환합니다.

날짜 비교가 문자열 비교로 가능한 이유는 날짜 형식이 `YYYY-MM-DD`이기 때문입니다.

예를 들어:

```text
2024-01-15 < 2024-02-01
2024-10-01 > 2024-02-01
```

연, 월, 일이 앞에서부터 0으로 채워진 형식이라 문자열 순서와 날짜 순서가 일치합니다.

## 19. 더 자세한 실행 흐름: summary 명령

월별 요약은 파일 전체를 훑으면서 해당 월의 거래만 집계합니다.

```python
for transaction in self.transactions.stream():
    if not transaction.date.startswith(month):
        continue
```

`month`가 `2024-01`이면 `2024-01-15`, `2024-01-31` 같은 날짜만 통과합니다.

거래 타입에 따라 수입과 지출을 나눕니다.

```python
if transaction.type == "income":
    total_income += transaction.amount
else:
    total_expense += transaction.amount
    category_totals[transaction.category] = category_totals.get(transaction.category, 0) + transaction.amount
```

여기서 `category_totals`는 카테고리별 지출 합계를 담는 딕셔너리입니다.

예를 들어 거래가 다음과 같다면:

```text
food 15000
food 12000
transport 20000
```

딕셔너리는 이렇게 됩니다.

```python
{
    "food": 27000,
    "transport": 20000,
}
```

`dict.get(key, default)`는 해당 키가 있으면 값을 가져오고, 없으면 기본값을 반환합니다.

```python
category_totals.get(transaction.category, 0)
```

카테고리가 처음 등장했을 때도 0부터 더할 수 있게 해줍니다.

마지막에는 금액이 큰 순서로 TOP N을 뽑습니다.

```python
top_expenses = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[:top]
```

`category_totals.items()`는 `(카테고리, 금액)` 쌍을 반환합니다. `key=lambda item: item[1]`은 그중 금액을 기준으로 정렬하겠다는 뜻입니다.

## 20. 더 자세한 실행 흐름: update 명령

`update`는 옵션 기반으로 구현했습니다.

```bash
python -m budget_app update --id TX-000001 --amount 20000 --memo "저녁"
```

CLI는 바꿀 수 있는 값을 딕셔너리로 묶어 서비스에 넘깁니다.

```python
{
    "date": args.date,
    "type": args.type,
    "category": args.category,
    "amount": args.amount,
    "memo": args.memo,
    "tags": args.tags,
}
```

입력하지 않은 옵션은 `None`입니다. 서비스는 `None`이 아닌 값만 변경합니다.

먼저 변경할 값들을 검증합니다.

```python
if changes.get("amount"):
    parse_amount(str(changes["amount"]))
```

검증을 먼저 하는 이유는 파일을 바꾸기 전에 오류를 발견하기 위해서입니다. 예를 들어 금액이 `-1000`이면 저장소를 건드리지 않고 바로 오류를 냅니다.

실제 변경은 내부 함수 `updater()`가 담당합니다.

```python
def updater(transaction: Transaction) -> Transaction:
    return replace(
        transaction,
        amount=parse_amount(str(changes["amount"])) if changes.get("amount") else transaction.amount,
        memo=str(changes["memo"]) if changes.get("memo") is not None else transaction.memo,
    )
```

여기서 `replace()`는 기존 `Transaction`을 직접 수정하지 않고 새 `Transaction`을 만듭니다.

이 방식은 `Transaction`이 `frozen=True`인 것과 잘 맞습니다. “거래 객체는 불변이고, 수정은 새 객체 생성으로 표현한다”는 규칙이 생깁니다.

저장소는 거래를 하나씩 읽다가 ID가 맞는 거래를 발견하면 `updater()`를 적용합니다.

```python
if transaction.id == transaction_id:
    transaction = updater(transaction)
    found = True
```

이 구조가 좋은 이유는 저장소가 수정 세부 내용을 몰라도 되기 때문입니다. 저장소는 “이 ID의 거래를 찾으면 전달받은 함수로 바꾼다”는 일반적인 작업만 수행합니다.

## 21. 더 자세한 실행 흐름: delete 명령

삭제는 수정보다 단순합니다.

```python
for transaction in self.stream():
    if transaction.id == transaction_id:
        found = True
        continue
    rows.append(transaction.to_dict())
```

ID가 일치하는 거래는 `rows`에 넣지 않습니다. 나머지 거래만 새 파일에 씁니다. 즉, 삭제는 “삭제할 행만 빼고 다시 쓰기”입니다.

파일 기반 저장에서는 중간 한 줄을 안전하게 지우는 것이 간단하지 않습니다. 그래서 전체 재작성 방식을 사용합니다.

## 22. Repository 계층을 더 깊게 보기

저장소 계층은 이 프로젝트의 데이터 안전성과 직접 연결됩니다.

### append와 rewrite를 나눈 이유

거래 추가는 파일 끝에 한 줄을 붙이면 됩니다.

```python
def append_json(self, path: Path, data: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
```

`"a"` 모드는 append 모드입니다. 기존 내용을 지우지 않고 파일 끝에 씁니다.

반면 수정, 삭제, 예산 설정, 카테고리 삭제는 기존 내용을 바꿔야 합니다. 이때는 `rewrite_json()`을 사용합니다.

```python
def rewrite_json(self, path: Path, rows: list[dict[str, Any]]) -> None:
    ...
    os.replace(temp_name, path)
```

즉, 저장 작업은 두 종류입니다.

| 작업 | 방식 |
| --- | --- |
| 단순 추가 | append |
| 기존 데이터 변경 | rewrite + atomic replace |

### ensure_ascii=False

```python
json.dumps(data, ensure_ascii=False)
```

`ensure_ascii=False`를 쓰면 한글이 `\uc810\uc2ec` 같은 이스케이프 문자열로 저장되지 않고 그대로 저장됩니다.

예를 들어 메모가 `점심`이면 파일에도 `점심`으로 보입니다. 콘솔 가계부는 사람이 파일을 열어볼 수도 있으므로 이 설정이 더 읽기 좋습니다.

### encoding="utf-8"

파일을 열 때 항상 UTF-8을 지정합니다.

```python
path.open("r", encoding="utf-8")
```

한글 메모와 카테고리를 안전하게 저장하고 읽기 위해서입니다. 운영체제 기본 인코딩에 의존하면 환경에 따라 깨질 수 있습니다.

### line_no를 기록하는 이유

```python
for line_no, line in enumerate(file, start=1):
```

JSONL 파일 중간에 깨진 줄이 있으면 사용자가 어느 줄이 문제인지 알아야 합니다.

```python
raise AppError(
    f"저장 파일을 읽을 수 없습니다: {path.name}:{line_no}",
    "파일 내용을 확인하거나 백업에서 복구하세요.",
)
```

`transactions.jsonl:12`처럼 알려주면 문제를 찾기 쉽습니다.

## 23. Service 계층과 Repository 계층의 차이

처음 보면 `services.py`와 `repositories.py`가 둘 다 데이터를 다루는 것처럼 보입니다. 하지만 관심사가 다릅니다.

### Service가 아는 것

서비스는 업무 규칙을 압니다.

- 거래 금액은 양수여야 한다.
- 타입은 `income` 또는 `expense`다.
- 카테고리는 등록되어 있어야 한다.
- 사용 중인 카테고리는 삭제할 수 없다.
- 월별 요약에서는 수입, 지출, 잔액을 계산한다.

### Repository가 아는 것

저장소는 파일 저장 방식을 압니다.

- JSONL을 한 줄씩 읽는다.
- 데이터를 파일 끝에 추가한다.
- 임시 파일에 쓴 뒤 원본과 교체한다.
- 거래 ID를 찾기 위해 파일을 순회한다.

서비스는 파일이 JSONL인지 CSV인지 몰라도 됩니다. 저장소는 “예산 초과” 같은 업무 의미를 몰라도 됩니다.

이 분리가 유지보수 가능한 설계의 핵심입니다.

## 24. 왜 클래스가 필요한가

이 과제는 최소 2개 이상의 클래스를 요구합니다. 여기서는 단순히 조건을 맞추기 위해 클래스를 쓴 것이 아니라, 역할을 묶기 위해 사용했습니다.

### 데이터 클래스

`Transaction`, `Budget`, `SearchCriteria`는 데이터 자체를 표현합니다.

```python
Transaction(id="TX-000001", type="expense", ...)
```

### 저장소 클래스

`TransactionRepository`, `CategoryRepository`, `BudgetRepository`는 저장 대상별 파일 접근 방식을 묶습니다.

```python
transaction_repository.stream()
category_repository.list()
budget_repository.get("2024-01")
```

### 서비스 클래스

`TransactionService`, `CategoryService`, `BudgetService`는 업무 로직을 묶습니다.

```python
transaction_service.summary("2024-01", 3)
category_service.remove("food")
budget_service.set("2024-01", 500000)
```

클래스를 쓰면 관련 데이터와 행동을 한 이름 아래 모을 수 있습니다.

## 25. 타입 힌트를 더 자세히 보기

### Optional

```python
Optional[str]
```

이 타입은 `str` 또는 `None`이라는 뜻입니다.

검색 조건은 사용자가 입력하지 않을 수도 있으므로 `Optional[str]`이 적절합니다.

```python
date_from: Optional[str] = None
```

### Union

```python
Union[str, int]
```

이 타입은 문자열 또는 정수라는 뜻입니다.

CLI 입력은 기본적으로 문자열입니다. 하지만 내부 코드나 테스트에서는 정수로 넘길 수도 있습니다. 그래서 금액 입력은 `Union[str, int]`로 받았습니다.

### Iterator

```python
Iterator[Transaction]
```

이 타입은 `Transaction`을 하나씩 순회할 수 있는 객체라는 뜻입니다.

```python
def stream(self) -> Iterator[Transaction]:
    ...
```

`list[Transaction]`과 다릅니다. `list`는 이미 모든 값이 메모리에 들어 있는 컬렉션이고, `Iterator`는 필요할 때 하나씩 값을 꺼내는 흐름입니다.

### Callable

```python
Callable[[Transaction], Transaction]
```

이 타입은 `Transaction` 하나를 받아서 `Transaction` 하나를 반환하는 함수라는 뜻입니다.

`replace()` 메서드에서 사용합니다.

```python
def replace(self, transaction_id: str, updater: Callable[[Transaction], Transaction]) -> bool:
```

저장소는 `updater`가 구체적으로 무엇을 바꾸는지 모릅니다. 단지 거래 하나를 넣으면 변경된 거래 하나가 나온다는 계약만 알고 있습니다.

## 26. 예외 흐름을 더 자세히 보기

사용자가 잘못된 날짜를 입력했다고 가정합니다.

```text
날짜(YYYY-MM-DD): 2024-13-40
```

흐름은 다음과 같습니다.

1. CLI가 문자열을 입력받습니다.
2. `TransactionService.create()`가 `parse_date()`를 호출합니다.
3. `datetime.strptime()`이 `ValueError`를 발생시킵니다.
4. `parse_date()`가 `ValueError`를 잡고 `AppError`로 바꿉니다.
5. `cli.py`의 `main()`이 `AppError`를 잡습니다.
6. 사용자에게 `[오류]`, `[힌트]`를 출력합니다.
7. `SystemExit(1)`로 종료합니다.

왜 `ValueError`를 그대로 보여주지 않을까요?

`ValueError: time data '2024-13-40' does not match format '%Y-%m-%d'` 같은 메시지는 개발자에게는 유용하지만 사용자에게는 딱딱합니다. 그래서 프로그램의 언어로 바꿔 보여줍니다.

```text
[오류] 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).
[힌트] 예: 2024-01-15
```

이것이 “사용자 친화적인 예외 처리”입니다.

## 27. import/export가 같은 검증을 공유하는 방식

`import_csv()`는 CSV 행을 읽은 뒤 직접 저장하지 않고 `create()`를 호출합니다.

```python
self.create(
    date=row.get("date", ""),
    tx_type=row.get("type", ""),
    category=row.get("category", ""),
    amount=row.get("amount", ""),
    memo=row.get("memo", ""),
    tags=row.get("tags", ""),
)
```

이 설계 덕분에 CSV로 들어온 데이터도 대화형 입력과 같은 규칙을 적용받습니다.

예를 들어 CSV에 없는 카테고리가 있으면 `create()` 내부에서 `_validated_category()`가 실패합니다. 금액이 음수여도 `parse_amount()`가 실패합니다.

중복 검증 코드를 만들지 않고 하나의 생성 규칙을 재사용한 것입니다.

## 28. 현재 구현의 한계와 개선 아이디어

이 프로젝트는 과제 요구사항에 맞춘 작은 서비스입니다. 다만 실제 서비스라면 개선할 수 있는 지점도 있습니다.

### 검색 결과 정렬

검색은 조건에 맞는 결과를 리스트에 모은 뒤 최신순으로 정렬합니다.

```python
results = [tx for tx in self.transactions.stream() if self._matches(tx, criteria)]
return sorted(results, key=lambda item: (item.date, item.id), reverse=True)
```

검색 결과가 매우 많으면 메모리를 많이 쓸 수 있습니다. 현재 과제에서는 검색 결과 전체를 보여줘야 하므로 이 방식이 단순하고 충분합니다. 만약 대용량 검색을 더 강화한다면 `--limit` 옵션을 추가하고 `heapq.nlargest()`를 적용할 수 있습니다.

### ID 생성

현재 ID는 파일을 모두 읽어 가장 큰 번호를 찾고 다음 번호를 만듭니다.

```python
return f"TX-{max_number + 1:06d}"
```

단순하고 사람이 읽기 좋습니다. 다만 동시에 여러 프로세스가 실행되어 거래를 추가하면 같은 ID가 생길 수 있습니다. 실제 서비스라면 UUID나 파일 잠금(lock)을 고려할 수 있습니다.

### 동시성

이 프로그램은 개인용 콘솔 프로그램을 가정합니다. 여러 사용자가 동시에 같은 파일에 쓰는 상황은 깊게 처리하지 않습니다. 실제 운영 환경에서는 파일 잠금, 데이터베이스, 트랜잭션이 필요할 수 있습니다.

### 테스트

현재는 수동 검증 중심입니다. 더 발전시키려면 표준 라이브러리 `unittest`로 다음을 테스트할 수 있습니다.

- 날짜/금액 검증
- 거래 추가 후 목록 조회
- 없는 카테고리 추가 실패
- update/delete 후 파일 내용 변경
- import/export CSV 결과

## 29. 발표 또는 평가 답변용 요약

아래처럼 설명하면 이 프로젝트의 의도를 짧게 전달할 수 있습니다.

> 이 프로그램은 파일 기반 가계부지만, 단순히 한 파일에 데이터를 몰아넣지 않고 거래, 카테고리, 예산을 각각 JSONL 파일로 분리했습니다. 거래 파일은 제너레이터로 한 줄씩 읽어 대용량에서도 메모리 부담을 줄였고, 수정과 삭제는 임시 파일에 다시 쓴 뒤 `os.replace()`로 교체해 파일 손상 가능성을 줄였습니다. CLI, 서비스, 저장소, 모델을 나누어 각 계층의 책임을 분리했고, 입력 검증과 사용자용 예외를 통해 잘못된 입력에도 스택트레이스 대신 원인과 힌트를 보여주도록 만들었습니다. 또한 dataclass와 타입 힌트를 사용해 데이터 구조와 함수 계약을 명확히 했습니다.

## 30. 코드 읽기 훈련 방법

학습할 때는 코드를 그냥 읽기보다 “질문을 던지며” 읽는 것이 좋습니다.

예를 들어 `TransactionService.create()`를 볼 때는 다음처럼 질문합니다.

- 이 함수의 입력은 어디서 오는가?
- 이 함수가 직접 파일을 열지 않는 이유는 무엇인가?
- 검증 실패 시 어떤 예외가 발생하는가?
- 반환값은 누가 사용하는가?
- 같은 로직을 다른 기능에서도 재사용하는가?

`TransactionRepository.stream()`을 볼 때는 다음처럼 질문합니다.

- 이 함수는 리스트를 반환하지 않고 왜 `yield`를 쓰는가?
- JSON 딕셔너리를 바로 넘기지 않고 왜 `Transaction.from_dict()`를 거치는가?
- 파일에 깨진 줄이 있으면 어디서 처리되는가?

이런 식으로 보면 단순히 문법을 외우는 것이 아니라, 코드의 책임과 흐름을 이해하게 됩니다.
