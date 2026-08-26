# 이 프로젝트로 배우는 Python·설계 개념

이 문서는 현재 `budget_app` 구현을 기준으로 작성했다. 설명에 나오는 파일과 함수는 모두 실제 코드에 존재하며, 기능을 새로 가정하지 않는다.

## 1. 파일 기반 영속성

영속성은 프로그램이 끝난 뒤에도 데이터를 남기는 일이다. 메모리의 `Transaction` 객체만 사용하면 프로세스 종료와 함께 거래도 사라지므로, 이 프로그램은 `JsonlStore`가 `data/transactions.jsonl`, `categories.jsonl`, `budgets.jsonl`에 기록한다. `cli.build_services()`가 시작 시 `store.initialize()`을 호출해 폴더와 세 파일을 만들고, 카테고리 파일이 비어 있으면 기본 카테고리를 넣는다.

거래·카테고리·예산을 분리하면 각 파일의 행 구조와 변경 규칙이 단순해진다. 작은 개인용 프로그램에는 파일이 눈으로 확인하기 쉽고 별도 서버가 필요 없다는 장점이 있지만, 여러 프로세스의 동시 쓰기·복잡한 질의·강한 트랜잭션 보장은 DB보다 약하다.

## 2. JSONL

이 프로젝트의 저장 형식은 CSV가 아니라 JSON Lines(JSONL)다. `JsonlStore.append_json()`은 `json.dumps(...)+"\n"`으로 **한 줄에 하나의 JSON 객체**를 추가하며, `iter_json()`은 한 줄씩 `json.loads()`한다. JSON은 `tags`처럼 리스트인 필드도 자연스럽게 저장할 수 있고, 줄 단위라 새 거래를 파일 끝에 추가하기 좋다.

반면 import/export 경계에는 CSV를 쓴다. `TransactionService.import_csv()`와 `export_csv()`의 CSV 열은 `date,type,category,amount,memo,tags`이고, CSV에는 거래 ID를 포함하지 않는다. CSV를 읽을 때는 `create()`를 거쳐 새 ID와 동일한 검증 규칙을 적용한다.

## 3. Iterable, iterator, generator, `yield`

반복 가능한(iterable) 객체는 `for`로 순회할 수 있는 값이고, iterator는 `next()`로 다음 값을 하나씩 꺼내는 객체다. generator는 `yield`가 들어 있는 함수 호출로 만들어지는 특별한 iterator다. 일반 `return`은 함수를 끝내고 값을 한 번 돌려주지만, `yield`는 값을 돌려준 뒤 현재 실행 위치와 지역 상태를 보관한다.

실제 흐름은 `JsonlStore.iter_json(path)` → `TransactionRepository.stream()`이다. `iter_json()`이 파일의 유효한 JSON 행을 `yield dict`하고, `stream()`은 각 딕셔너리를 `Transaction.from_dict()`로 바꿔 `yield Transaction`한다. `stream()`을 호출한 순간에는 본문이 전부 실행되지 않으며, `for`나 `heapq.nlargest()`가 `next()`를 요청할 때 다음 행까지 실행한다.

예를 들어 `numbers()`가 `yield 1`, `yield 2`를 포함하면 `numbers()`는 generator 객체만 만든다. 첫 `next()`가 첫 `yield`까지 실행해 1을 받고 멈추며, 다음 `next()`는 저장해 둔 자리에서 재개해 2를 받는다. 파일 스트림도 같은 방식으로 다음 거래가 필요할 때만 다음 줄을 읽는다.

## 4. Streaming과 그 한계

`readlines()`는 파일의 모든 줄을 리스트로 먼저 올리지만, `for line in file`은 한 줄씩 읽는다. `iter_json()`의 파일 읽기는 후자이므로 10건이든 100만 건이든 원본 파일 전체 줄을 한 번에 메모리에 쌓지 않는다. `latest()`도 `heapq.nlargest(limit, stream, ...)`를 사용해 최신 후보 `limit`개 중심으로 처리한다.

다만 generator가 있다고 항상 전체 O(1) 메모리가 되는 것은 아니다. `search()`는 조건에 맞는 모든 거래를 `results` 리스트에 모아 정렬하고, `export_csv()`도 `rows`를 모아 최신순 정렬한다. 즉 파일 읽기는 streaming이지만, 최신순 결과 전체가 필요한 이 두 단계는 결과를 materialize한다. generator는 탐색 시간 자체를 O(n)보다 작게 만들지는 않는다.

## 5. Decorator와 first-class function

decorator는 원래 함수를 감싼 wrapper 함수를 만드는 문법이다. 이 프로젝트의 `log_timing(func)`은 명령 실행 시간을 로그에 기록하는 한 가지 일만 한다.

`cli.py`에서 `@log_timing`이 붙은 `run()`은 개념적으로 `run = log_timing(run)`과 같다. `run()`을 호출하면 wrapper가 먼저 시작 시간을 기록하고 원래 `run()`을 실행한다. 실행이 끝나거나 예외가 나면 `finally`에서 경과 시간을 `budget_app.log`에 남긴다.

## 6. `functools.wraps`

`log_timing()`은 `@functools.wraps(func)`를 사용한다. 이것이 없으면 `run.__name__`, `run.__doc__` 같은 원래 함수 metadata가 wrapper의 이름·문서로 바뀐다. `wraps`는 원본 metadata를 wrapper에 복사해 디버깅, 로그, 도움말 도구가 원래 함수를 더 정확히 볼 수 있게 한다.

## 7. Type hint

타입 힌트는 함수의 입력과 출력 계약을 드러낸다. 예를 들어 `TransactionRepository.stream() -> Iterator[Transaction]`은 리스트가 아니라 거래를 하나씩 내보내는 iterator임을 말하고, `BudgetRepository.get(month: str) -> Optional[Budget]`은 예산이 없으면 `None`일 수 있음을 표시한다. `TransactionService.create()`의 `amount: Union[str, int]`, `SearchCriteria`의 `Optional[str]`, `list[Transaction]`도 실제 사용 타입을 설명한다.

Python의 type hint는 기본적으로 실행 시간에 타입을 강제하지 않는다. 대신 IDE 자동완성, 정적 분석, 호출자와 구현자 사이의 계약, 유지보수 시 이해를 돕는다. `Iterable`과 `Generator`라는 타입은 이 코드에 직접 선언되어 있지 않으므로, 여기서는 사용된 `Iterator`를 중심으로 읽는 것이 정확하다.

## 8. `dataclass`

`models.py`의 `Transaction`, `Budget`, `SearchCriteria`는 `@dataclass(frozen=True)`다. 일반 class에서 직접 작성할 `__init__`, 읽기 쉬운 `__repr__`, 값 비교용 `__eq__`를 dataclass가 필드 정의에서 생성한다. `frozen=True`라 거래 객체 필드는 직접 바꿀 수 없고, `TransactionService.update()`는 `dataclasses.replace()`로 수정본을 새 객체로 만든다.

`Transaction`은 `to_dict()`와 `from_dict()`로 파일의 dict와 도메인 객체 사이를 오간다. dict만 계속 전달하는 것보다 필드 구조와 변환 규칙을 한곳에 모으고, 잘못된 필드 접근을 줄인다.

## 9. Repository pattern과 Service layer

계층은 `CLI → Service → Repository/Store → File`이다. `TransactionRepository`는 거래의 추가·순회·ID 탐색·교체·삭제를, `JsonlStore`는 JSONL 읽기·추가·재작성 같은 파일 세부사항을 맡는다. Category와 Budget repository도 각 파일 접근을 맡는다.

서비스는 업무 규칙을 조합한다. 예를 들어 `TransactionService.create()`는 날짜·타입·금액을 검증하고 카테고리 존재를 확인한 뒤 repository에 저장을 요청한다. `CategoryService.remove()`는 사용 중인 카테고리인지 거래를 순회해 확인한다. CLI는 입력과 출력만 담당하며 직접 파일을 열지 않는다.

## 10. `argparse` CLI

`build_parser()`는 프로그램 이름, 전역 `--data-dir`, 그리고 명령 subparser를 만든다. 실제 최상위 명령은 `add`, `list`, `search`, `summary`, `budget set`, `category add/list/remove`, `update`, `delete`, `import`, `export`다. `parse_args()`가 positional/optional 인수를 `args`에 담고 `run()`의 `if/elif` dispatch가 알맞은 service 메서드를 호출한다.

`argparse`는 `--help`와 필수 옵션 검사도 제공한다. 다만 `add`의 거래 값은 옵션이 아니라 `prompt()`로 대화형 입력을 받는다.

## 11. Validation과 예외

형식 검사는 `validators.py`에 있다. `validate_date`, `validate_month`, `validate_amount`, `validate_type`, `parse_tags`가 날짜·월·양수 금액·income/expense·태그를 처리하며, 등록된 카테고리 검사는 service의 `validate_registered_category()`가 repository를 통해 한다. ID는 별도 형식 validator가 없고 repository의 `next_id()`가 기존 `TX-` 번호 중 최대값 다음을 만든다.

검증 실패는 `AppError`를 `raise`한다. `cli.main()`이 이를 `except`해 오류와 힌트를 stderr로 출력하고 `SystemExit(1)`로 끝낸다. JSONL 파싱 오류도 `iter_json()`에서 `AppError`로 변환되고, 파일 I/O의 `OSError`는 `main()`이 별도 사용자 메시지로 처리한다. 내부 traceback을 사용자에게 노출하지 않아 입력 오류를 읽기 쉬운 메시지로 바꾼다.

## 12. Exit code

CLI에서 0은 정상 종료, 0이 아닌 값은 실패를 뜻한다. 성공한 `run()`은 0을 반환하고 `main()`은 `SystemExit(run())`로 그 값을 운영체제에 전달한다. `AppError`나 `OSError`는 1로 종료하므로 쉘 스크립트나 자동화 도구가 성공 여부를 판단할 수 있다.

## 13. update/delete와 atomic replace

파일 중간의 JSONL 행을 제자리에서 안전하게 수정·삭제하기는 어렵다. `TransactionRepository.update()`와 `delete()`는 모든 거래를 순회해 변경 또는 제외한 `rows`를 만들고, `JsonlStore.rewrite_json()`에 전달한다. `BudgetRepository.set()`과 `CategoryRepository.remove()`도 같은 재작성 방식을 사용한다.

`rewrite_json()`은 `tempfile.mkstemp()`로 같은 데이터 폴더에 임시 파일을 만들고, 모든 행을 성공적으로 쓴 뒤 `os.replace(temp_name, path)`로 원본과 바꾼다. 쓰기 중 실패하면 원본을 직접 덮어쓴 경우보다 손상 위험이 낮고 임시 파일을 삭제하려 한다. 이것은 파일 교체 단위의 안전성으로, DB의 동시성·격리까지 포함한 transaction과는 다르다.

```text
원본 JSONL 읽기 → 변경된 rows 작성 → 임시 파일 완료 → os.replace() → 새 원본
```

## 14. Import/export

import는 `csv.DictReader`로 CSV를 행별로 읽고, 필수 헤더 `date,type,category,amount`를 먼저 확인한다. 각 행은 `create()`에 전달돼 동일한 validation과 category 검사를 받고, `AppError`가 난 행은 `skipped`로 세고 다음 행을 계속 처리한다. 따라서 부분적으로 유효한 입력 파일은 유효한 행만 추가된다.

export는 월 또는 날짜 범위를 요구하며 stream에서 조건에 맞는 거래를 모은 후 최신순으로 정렬해 `csv.DictWriter`로 쓴다. 내보내기 CSV에는 `id`가 없고 tags는 쉼표로 합친 문자열이다.

## 15. Category와 referential integrity

카테고리는 `categories.jsonl`에 별도 저장되고 `Transaction.category`가 그 이름을 참조한다. 새 거래·검색·수정의 카테고리는 `validate_registered_category()`가 존재 여부를 검사한다. 삭제 시 `CategoryService.remove()`가 모든 거래를 stream으로 검사해 사용 중인 이름이면 `AppError`를 낸다.

이는 애플리케이션 코드가 지키는 참조 무결성이다. DB foreign key처럼 DB 엔진이 강제하는 제약과 동일하지 않으며, 동시 실행까지 보호하지는 않는다.

## 16. Budget과 summary

`BudgetService.set()`은 월과 양수 금액을 검증해 `BudgetRepository.set()`에 저장한다. `TransactionService.summary()`는 해당 월 거래를 순회하며 income, expense, 잔액, 카테고리별 지출을 계산하고 그 월의 예산을 조회한다. `formatters.print_summary()`가 지출/예산 비율을 계산하고 지출이 예산보다 크면 경고를 표시한다.

## 17. 주요 복잡도

`next_id()`, `summary()`, category 사용 여부 확인, ID update/delete는 파일을 순회하므로 O(n) 시간이다. `latest()`는 n개를 읽고 limit개 후보를 heap으로 유지하므로 대략 O(n log limit) 시간과 O(limit) 추가 공간을 쓴다. `search()`와 `export_csv()`는 필터된 결과를 정렬하므로 결과 수를 k라 하면 O(n + k log k) 시간과 O(k) 공간이 든다.

제너레이터의 핵심 이점은 원본 파일을 통째로 리스트화하지 않는 공간 사용 방식이다. 필요한 레코드를 찾기 위해 여전히 순회하므로 generator 자체가 검색의 시간 복잡도를 낮추지는 않는다.
