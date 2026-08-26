# 코드 실행 흐름 따라가기

이 문서는 파일을 열어 두고 실제 함수 호출 순서를 따라가기 위한 학습용 안내서입니다.

## 1. 프로그램 전체 구조

```text
사용자
↓
CLI
↓
Service
↓
Repository
↓
JSONL 파일
```

- **CLI** (`cli.py`): 명령과 옵션을 받고 Service를 호출한 뒤 결과를 출력합니다.
- **Service** (`services.py`): 거래 생성, 검색, 수정, 요약 같은 기능 규칙을 처리합니다.
- **Repository** (`repositories.py`): Service와 JSONL 파일 사이에서 데이터를 읽고 저장합니다.
- **Model** (`models.py`): `Transaction`, `Budget`, `SearchCriteria` 데이터 구조를 정의합니다.
- **Validator** (`validators.py`): 날짜, 월, 금액, 타입을 검사하고 태그 문자열을 나눕니다.
- **Decorator** (`decorators.py`): `run()`의 실행 시간을 로그에 기록합니다.

## 2. 프로그램 시작 흐름

예: `python -m budget_app list --limit 3`

```text
budget_app/__main__.py
↓  cli.main() 호출
cli.main()
↓  run() 실행, 오류는 여기서 처리
@log_timing wrapper
↓  실행 시간을 기록할 준비
run()
↓  argparse가 명령과 옵션을 분석
command_list()
↓  args.limit을 전달
TransactionService.latest()
↓
TransactionRepository.stream()
↓
JsonlStore.iter_json()
↓
transactions.jsonl
```

`run()`은 parser와 Service를 준비한 뒤, 명령에 맞는 `command_*()` 함수를 호출합니다.

## 3. 주요 기능별 흐름

### add

```text
command_add()
↓  input()으로 date, type, category, amount, memo, tags 입력
TransactionService.create()
↓  validate_date(), validate_type(), validate_registered_category()
↓  validate_amount(), parse_tags()
Transaction 생성
↓  예: amount="15000" → amount=15000
TransactionRepository.add()
↓
JsonlStore.append_json()
↓
transactions.jsonl에 JSON 한 줄 추가
```

### list

```text
command_list()
↓
TransactionService.latest()
↓  모든 거래를 확인하며 최신 후보를 최대 limit개 유지
TransactionRepository.stream()
↓
JsonlStore.iter_json()
↓  JSON 한 줄 → dict yield
Transaction.from_dict()
↓  dict → Transaction yield
print_transactions()
```

### search

```text
command_search()
↓  CLI 옵션으로 SearchCriteria 생성
TransactionService.search(criteria)
↓  날짜, 타입, 카테고리 조건 검증
TransactionRepository.stream()
↓  각 Transaction이 조건에 맞는지 _matches()로 확인
조건에 맞는 거래를 list에 모아 최신순 정렬
↓
print_transactions()
```

### summary와 budget

```text
command_summary()
↓
TransactionService.summary(month, top)
↓  Transaction을 한 건씩 확인
해당 월인가?
↓  income / expense / 카테고리별 지출 누적
BudgetRepository.get(month)
↓
print_summary()
```

`command_budget()`은 `BudgetService.set()`으로 월과 금액을 저장합니다. 요약은 같은 월의 예산을 읽어 사용률과 초과 경고를 출력합니다.

### update

```text
command_update()
↓
TransactionService.update(id, changes)
↓  전달된 값 검증
TransactionRepository.find_by_id(id)
↓  기존 Transaction 찾기
dataclasses.replace(current_transaction, ...)
↓  기존 객체는 그대로 두고 새 Transaction 생성
TransactionRepository.update(updated_transaction)
↓  모든 거래를 읽어 수정본을 포함한 rows 만들기
JsonlStore.rewrite_json()
↓  임시 파일에 rows 작성
os.replace(temp, transactions.jsonl)
```

### delete

```text
command_delete()
↓
TransactionService.delete(id)
↓
TransactionRepository.delete(id)
↓  모든 거래를 읽음
같은 id인가?
├─ 예: rows에 넣지 않음
└─ 아니오: rows에 넣음
↓
JsonlStore.rewrite_json()
↓  임시 파일 작성 후 os.replace()
```

### import와 export

```text
import
command_import()
↓
TransactionService.import_csv()
↓  csv.DictReader가 CSV 행을 읽음
각 행 → TransactionService.create()
↓  검증 성공 행만 transactions.jsonl에 추가

export
command_export()
↓
TransactionService.export_csv()
↓  TransactionRepository.stream()으로 거래를 읽음
조건에 맞는 거래를 모아 최신순 정렬
↓
csv.DictWriter가 CSV 파일에 작성
```

## 4. Generator 흐름

```text
JsonlStore.iter_json()
↓
파일 한 줄
↓
json.loads()
↓
dict yield

TransactionRepository.stream()
↓
dict
↓
Transaction.from_dict()
↓
Transaction yield
```

```python
generator = repository.stream()
```

이 줄만 실행하면 아직 파일 전체를 읽지 않습니다.

```python
for transaction in generator:
    ...
```

반복이 시작될 때 파일을 열고 거래를 한 건씩 처리합니다. 다만 `search()`와 `export_csv()`는 최신순 정렬을 위해 조건에 맞는 결과를 list에 모읍니다. 파일 읽기 자체는 한 줄씩이지만, 이 두 결과는 완전한 streaming 결과가 아닙니다.

## 5. Decorator와 오류 처리

```text
run() 호출
↓
@log_timing의 wrapper()
↓  시작 시간 저장
원래 run() 실행
↓
finally
↓  budget_app.log에 실행 시간 기록
```

`@functools.wraps(func)`는 wrapper가 `run`의 이름과 문서 정보를 유지하게 합니다.

```text
잘못된 날짜 입력
↓
validate_date()
↓
AppError 발생
↓
wrapper의 finally가 실행 시간 기록
↓
cli.main()
↓  [오류]와 [힌트] 출력
SystemExit(1)
```

오류가 없으면 `run()`은 `0`을 반환해 정상 종료합니다.

## 6. 파일별 역할

| 파일 | 가장 중요한 역할 |
| --- | --- |
| `__main__.py` | `python -m budget_app`의 시작점입니다. |
| `cli.py` | 명령 입력·출력, `command_*()` 호출, 오류 종료를 처리합니다. |
| `services.py` | 거래 기능과 검증 조합을 처리합니다. |
| `repositories.py` | JSONL 읽기·쓰기와 안전한 파일 교체를 처리합니다. |
| `models.py` | `Transaction` 등 데이터 구조를 정의합니다. |
| `validators.py` | 입력값을 검사하거나 태그를 나눕니다. |
| `decorators.py` | `run()` 실행 시간을 기록합니다. |
| `formatters.py` | 거래 목록과 요약을 콘솔에 출력합니다. |

## 7. 직접 답해 볼 질문

1. **가장 먼저 실행되는 파일은?** `__main__.py`입니다.
2. **argparse의 역할은?** 명령과 옵션을 `args`에 담아 검사합니다.
3. **CLI와 Service의 차이는?** CLI는 입력·출력, Service는 기능 규칙을 담당합니다.
4. **Repository가 필요한 이유는?** 파일 읽기·쓰기를 Service에서 분리하기 위해서입니다.
5. **Transaction은 어디서 만들어지는가?** `TransactionService.create()`와 `Transaction.from_dict()`입니다.
6. **yield는 어디에서 쓰는가?** `JsonlStore.iter_json()`과 `TransactionRepository.stream()`입니다.
7. **stream() 호출만으로 파일 전체를 읽는가?** 아니요. 반복할 때 읽습니다.
8. **update가 새 Transaction을 만드는 이유는?** `Transaction`이 `frozen=True`라 기존 객체를 직접 바꾸지 않기 때문입니다.
9. **update/delete가 전체 파일을 다시 쓰는 이유는?** JSONL 중간 행을 안전하게 제자리 수정하기 어렵기 때문입니다.
10. **os.replace()는 왜 사용하는가?** 임시 파일 작성이 끝난 뒤 원본을 교체하기 위해서입니다.
11. **decorator는 왜 사용하는가?** 명령 실행 시간을 `run()` 로직과 분리해 기록하기 위해서입니다.
12. **오류는 어디에서 최종 처리되는가?** `cli.main()`입니다.
13. **exit code 0과 1은 무엇인가?** 0은 정상, 1은 처리한 입력·파일 오류입니다.
