# 파일 기반 가계부 콘솔 프로그램

Python 표준 라이브러리만 사용한 파일 기반 가계부입니다. 거래 추가, 목록, 검색, 월별 요약, 예산, 카테고리, 수정/삭제, CSV 가져오기/내보내기를 지원합니다.

코드 구조와 파이썬 개념을 자세히 공부하려면 [budget_app/CODE_GUIDE.md](budget_app/CODE_GUIDE.md)를 함께 읽으면 됩니다.
코드에 사용된 파이썬 심화 문법은 [PYTHON_DEEP_DIVE.md](PYTHON_DEEP_DIVE.md)에 별도로 정리했습니다.

## 1. 실행 방법

Python 3.10 이상에서 실행합니다.

```bash
python -m budget_app --help
python -m budget_app add
python -m budget_app list --limit 10
```

저장 폴더는 기본값이 `./data`입니다. 다른 폴더를 쓰려면 모든 명령에서 `--data-dir`를 지정합니다.

```bash
python -m budget_app --data-dir ./my_data list
```

모든 명령은 `--help`를 지원합니다.

```bash
python -m budget_app search --help
python -m budget_app category --help
```

## 2. 주요 명령 예시

### 거래 추가

`add`는 대화형 입력 방식입니다.

```bash
python -m budget_app add
```

입력 항목:

```text
날짜(YYYY-MM-DD): 2024-01-15
타입(income/expense): expense
카테고리: food
금액(양수): 15000
메모(선택): 점심
태그(쉼표로 구분, 없으면 엔터): meal,lunch
```

### 거래 목록

최신순으로 출력합니다.

```bash
python -m budget_app list --limit 3
```

### 거래 검색

```bash
python -m budget_app search --from 2024-01-01 --to 2024-01-31
python -m budget_app search --category food
python -m budget_app search --type expense --tag meal
python -m budget_app search --q 점심
```

### 월별 요약

```bash
python -m budget_app summary --month 2024-01 --top 3
```

출력 내용:

- 총 수입
- 총 지출
- 잔액
- 예산 사용률과 초과 경고
- 카테고리별 지출 TOP N

### 예산 설정

```bash
python -m budget_app budget set --month 2024-01 --amount 500000
```

예산은 `summary` 출력에 함께 반영됩니다.

### 카테고리 관리

```bash
python -m budget_app category list
python -m budget_app category add --name food
python -m budget_app category remove --name food
```

초기 실행 시 기본 카테고리를 자동 생성합니다.

```text
food, transport, rent, salary, etc
```

이미 거래에서 사용 중인 카테고리는 삭제할 수 없습니다. 먼저 해당 거래를 다른 카테고리로 수정해야 합니다.

### 거래 수정

이 프로젝트의 `update`는 옵션 기반 방식으로 고정했습니다.

```bash
python -m budget_app update --id TX-000001 --amount 18000
python -m budget_app update --id TX-000001 --category transport --memo "버스비"
python -m budget_app update --id TX-000001 --tags commute,bus
```

수정 가능한 필드:

- `--date`
- `--type`
- `--category`
- `--amount`
- `--memo`
- `--tags`

### 거래 삭제

```bash
python -m budget_app delete --id TX-000001
```

### CSV 내보내기

`export`는 `--month` 또는 `--from`/`--to` 조건이 필요합니다.

```bash
python -m budget_app export --out export.csv --month 2024-01
python -m budget_app export --out export.csv --from 2024-01-01 --to 2024-01-31
```

### CSV 가져오기

```bash
python -m budget_app import --from import.csv
```

잘못된 행은 건너뛰고 `skipped` 개수로 표시합니다.

## 3. 저장 파일 위치와 형식

저장 방식은 JSONL입니다. JSONL은 한 줄에 JSON 객체 하나를 저장하는 형식입니다.

기본 저장 위치:

```text
data/
  transactions.jsonl
  categories.jsonl
  budgets.jsonl
```

### transactions.jsonl

```json
{"id":"TX-000001","type":"expense","date":"2024-01-15","amount":15000,"category":"food","memo":"점심","tags":["meal"]}
```

필드:

- `id`: 유일한 거래 ID
- `type`: `income` 또는 `expense`
- `date`: `YYYY-MM-DD`
- `amount`: 양수 정수
- `category`: 등록된 카테고리
- `memo`: 선택 메모
- `tags`: 문자열 배열

### categories.jsonl

```json
{"name":"food"}
```

### budgets.jsonl

```json
{"month":"2024-01","amount":500000}
```

## 4. CSV import/export 스키마

CSV는 UTF-8, 헤더 포함 형식입니다.

| column | required | 설명 |
| --- | --- | --- |
| date | Y | YYYY-MM-DD |
| type | Y | income / expense |
| category | Y | 등록된 카테고리 |
| amount | Y | 양수 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표 구분 문자열 |

예시:

```csv
date,type,category,amount,memo,tags
2024-01-15,expense,food,15000,점심,"meal,lunch"
2024-01-20,income,salary,3000000,월급,salary
```

## 5. 프로젝트 구조

```text
budget_app/
  __main__.py       # python -m budget_app 진입점
  cli.py            # argparse 기반 CLI
  models.py         # dataclass 데이터 모델
  repositories.py   # JSONL 파일 입출력
  services.py       # 비즈니스 로직
  validators.py     # 입력 검증
  decorators.py     # 실행 시간 로그 데코레이터
  formatters.py     # 콘솔 출력 정렬
  errors.py         # 사용자용 예외
```

책임 분리:

- CLI 계층은 명령어 인자와 사용자 입력을 처리합니다.
- 서비스 계층은 거래 생성, 검색, 요약, import/export 같은 업무 규칙을 처리합니다.
- 저장소 계층은 파일 읽기/쓰기만 담당합니다.
- 모델 계층은 데이터 구조와 타입 계약을 정의합니다.

## 6. 핵심 개념 정리

### 파일 기반 영구 저장

프로그램이 종료되어도 데이터가 남으려면 메모리가 아니라 파일에 저장해야 합니다. 이 프로젝트는 JSONL 파일을 사용합니다. 거래, 카테고리, 예산을 각각 다른 파일로 분리해서 데이터의 책임을 명확히 했습니다.

파일 분리의 장점:

- 거래가 많아져도 카테고리/예산 파일은 작게 유지됩니다.
- 예산 수정이 거래 파일에 영향을 주지 않습니다.
- 각 데이터의 구조를 따로 관리할 수 있습니다.

### JSONL을 선택한 이유

JSON 파일 하나에 전체 배열을 저장하면 데이터를 추가할 때 전체 파일을 다시 읽고 써야 합니다. JSONL은 한 줄이 하나의 데이터이므로 새 거래를 추가할 때 파일 끝에 한 줄만 append할 수 있습니다.

예시:

```json
{"id":"TX-000001","type":"expense","date":"2024-01-15","amount":15000,"category":"food","memo":"점심","tags":["meal"]}
{"id":"TX-000002","type":"income","date":"2024-01-20","amount":3000000,"category":"salary","memo":"월급","tags":[]}
```

### 제너레이터 스트리밍

`repositories.py`의 `iter_json()`과 `TransactionRepository.stream()`은 `yield`를 사용합니다. 파일 전체를 리스트로 한 번에 올리지 않고 한 줄씩 읽어서 하나씩 넘깁니다.

장점:

- 거래가 많아져도 메모리 사용량이 작습니다.
- 검색, 요약처럼 전체 데이터를 훑어야 하는 작업에 적합합니다.
- 파일 읽기 로직과 업무 로직을 분리할 수 있습니다.

핵심 형태:

```python
def stream(self) -> Iterator[Transaction]:
    for row in self.store.iter_json(self.store.transactions_path):
        yield Transaction.from_dict(row)
```

### update/delete와 원자적 교체

파일 기반 저장에서는 중간 데이터를 직접 수정하기 어렵습니다. 그래서 수정/삭제는 다음 방식으로 처리합니다.

1. 기존 파일을 스트리밍으로 읽습니다.
2. 변경된 전체 내용을 임시 파일에 씁니다.
3. 임시 파일 쓰기가 성공하면 `os.replace()`로 원본 파일을 교체합니다.

이 방식은 쓰기 도중 오류가 나도 원본 파일이 망가질 가능성을 줄입니다.

### 데코레이터

`decorators.py`에는 `log_timing` 데코레이터가 있습니다. CLI 실행 시간을 로그 파일에 남깁니다.

데코레이터를 쓰는 이유:

- 실행 시간 측정 코드를 명령 처리 로직과 분리할 수 있습니다.
- 여러 함수에 같은 공통 기능을 쉽게 적용할 수 있습니다.
- 핵심 로직이 더 읽기 쉬워집니다.

### 타입 힌트

함수 인자와 반환값에 타입을 적어 코드의 계약을 명확히 했습니다.

예시:

```python
def parse_amount(value: Union[str, int]) -> int:
    ...
```

이 함수는 문자열 또는 정수를 받아 검증한 뒤 정수를 반환한다는 뜻입니다. 타입 힌트는 실행 자체를 강제하지는 않지만, 코드를 읽는 사람과 도구가 의도를 파악하기 쉽게 만듭니다.

### dataclass

`Transaction`, `Budget`, `SearchCriteria`는 dataclass로 정의했습니다. dataclass를 쓰면 데이터 중심 객체를 간결하게 만들 수 있습니다.

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

### 예외 처리와 종료 코드

사용자 입력 오류는 `AppError`로 처리합니다. 스택트레이스 대신 원인과 해결 힌트를 출력합니다.

```text
[오류] 날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).
[힌트] 예: 2024-01-15
```

정상 종료는 exit code `0`, 오류 종료는 exit code `1`입니다.

## 7. 요구사항 체크리스트

- 거래 추가: 지원
- 거래 목록: 지원, 최신순, `--limit`
- 거래 검색: 지원, 기간/카테고리/타입/메모/태그
- 월별 요약: 지원, 수입/지출/잔액/TOP N
- 예산: 지원, summary에서 사용률/초과 경고 출력
- 카테고리 관리: 지원, 사용 중 삭제 방지
- 거래 수정: 지원, 옵션 기반
- 거래 삭제: 지원
- CSV import/export: 지원
- 저장 파일 3개 분리: 지원
- 제너레이터 스트리밍: 지원
- 데코레이터: 지원
- 타입 힌트: 지원
- 표준 라이브러리만 사용: 지원
