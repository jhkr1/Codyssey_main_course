# Budget App

파일을 데이터 저장소로 사용하는 Python 콘솔 가계부입니다. 거래를 추가·조회·검색·수정·삭제하고, 월별 수입·지출 요약과 예산을 관리할 수 있습니다. CSV 파일로 거래를 가져오거나 내보낼 수도 있습니다. 데이터 변경은 파일을 임시 파일로 쓴 뒤 교체하는 방식으로 반영됩니다.

## 주요 기능

- 거래 추가, 목록 조회, 검색, 수정, 삭제
- 월별 수입·지출 요약과 지출 상위 카테고리 표시
- 월 예산 설정 및 예산 초과 경고
- 카테고리 추가·조회·삭제
- CSV import/export
- JSONL 파일 기반 저장 및 거래 스트리밍 조회
- 파일 교체 방식의 데이터 갱신

## 요구 환경

```text
Python 3.10+
외부 라이브러리 없음
```

## 프로젝트 구조

이 디렉터리 자체가 `budget_app` Python 패키지입니다. 아래와 같이 **`budget_app` 디렉터리의 상위 경로**에서 명령을 실행하세요.

```text
project/
└── budget_app/
    ├── __main__.py
    ├── cli.py
    ├── services.py
    ├── repositories.py
    ├── data/                 # 첫 실행 시 생성
    ├── README.md
    ├── CONCEPTS.md
    ├── CODE_ARCHITECTURE.md
```

## 실행 방법

별도 패키지 설치는 필요하지 않습니다. `budget_app` 디렉터리의 상위 경로로 이동한 뒤 실행합니다.

```powershell
cd <project>
python -m budget_app --help
```

모든 명령에서 데이터 위치를 바꾸려면 명령어 앞에 `--data-dir`를 둡니다.

```powershell
python -m budget_app --data-dir ./my-data category list
```

## CLI Quick Start

### 1. 전체 도움말

```bash
python -m budget_app --help
```

### 2. 카테고리 조회

```bash
python -m budget_app category list
```

처음 실행하면 `food`, `transport`, `rent`, `salary`, `etc` 카테고리가 생성됩니다.

### 3. 거래 추가

```bash
python -m budget_app add
```

명령을 실행하면 다음 순서로 입력합니다.

```text
날짜(YYYY-MM-DD): 2026-08-11
유형(income/expense): expense
카테고리: food
금액(양의 정수): 15000
메모(선택): 점심
태그(쉼표로 구분, 없으면 엔터): meal,lunch
```

### 4. 최근 거래 조회

```bash
python -m budget_app list --limit 5
```

### 5. 거래 검색

```bash
python -m budget_app search --category food
python -m budget_app search --from 2026-08-01 --to 2026-08-31
python -m budget_app search --type expense --tag meal
```

`--q`로 메모 문자열을 검색할 수도 있습니다.

### 6. 월별 요약과 예산

```bash
python -m budget_app budget set --month 2026-08 --amount 500000
python -m budget_app summary --month 2026-08 --top 3
```

예산이 설정된 월의 지출이 예산을 넘으면 요약 출력에 예산 초과 경고가 표시됩니다.

### 7. 거래 수정과 삭제

수정할 값만 옵션으로 지정합니다.

```bash
python -m budget_app update --id TX-000001 --amount 20000 --memo "점심 식사"
python -m budget_app delete --id TX-000001
```

### 8. CSV 내보내기와 가져오기

내보내기는 월 또는 날짜 범위 조건이 필요합니다.

```bash
python -m budget_app export --out export.csv --month 2026-08
python -m budget_app export --out export.csv --from 2026-08-01 --to 2026-08-31
python -m budget_app import --from import.csv
```

## 주요 명령

| 명령 | 주요 옵션 | 설명 |
| --- | --- | --- |
| `add` | 대화형 입력 | 거래 추가 |
| `list` | `--limit` | 최근 거래 조회 (기본 10개) |
| `search` | `--from`, `--to`, `--category`, `--type`, `--q`, `--tag` | 거래 검색 |
| `summary` | `--month`, `--top` | 월별 요약 |
| `budget set` | `--month`, `--amount` | 월 예산 설정 |
| `category add` | `--name` (생략 시 입력) | 카테고리 추가 |
| `category list` | 없음 | 카테고리 조회 |
| `category remove` | `--name` | 카테고리 삭제 |
| `update` | `--id`, `--date`, `--type`, `--category`, `--amount`, `--memo`, `--tags` | 거래 수정 |
| `delete` | `--id` | 거래 삭제 |
| `import` | `--from` | CSV 가져오기 |
| `export` | `--out`, `--month`, `--from`, `--to` | CSV 내보내기 |

## 데이터 저장 위치와 형식

기본 데이터 디렉터리는 현재 명령 실행 위치의 `./data`입니다. `--data-dir`로 다른 경로를 지정할 수 있습니다. 처음 실행하면 디렉터리와 다음 UTF-8 JSONL 파일이 자동으로 생성됩니다.

```text
data/
├── transactions.jsonl
├── categories.jsonl
└── budgets.jsonl
```

JSONL은 한 줄에 하나의 JSON 객체를 저장하는 형식입니다. `transactions.jsonl`에는 ID, 날짜, 유형, 금액, 카테고리, 메모, 태그가 저장됩니다. `categories.jsonl`과 `budgets.jsonl`은 각각 카테고리와 월별 예산을 저장합니다.

## 거래 조회와 generator

거래 파일은 한 번에 모두 읽지 않습니다. `JsonlStore.iter_json()`이 JSONL 파일을 한 줄씩 읽어 JSON 문자열을 dict로 바꾸고, `TransactionRepository.stream()`이 그 dict를 `Transaction` 객체로 바꿔 한 건씩 반환합니다. 실제 파일 읽기는 `stream()`을 호출했을 때가 아니라, 그 결과를 `for`문 등으로 순회하기 시작할 때 실행됩니다.

```text
transactions.jsonl
→ JsonlStore.iter_json()
→ dict 한 건
→ TransactionRepository.stream()
→ Transaction 한 건
→ Service
```

다만 파일을 한 줄씩 읽는 것과 결과 정렬은 별개의 일입니다. `summary`는 거래를 순회하며 합계만 누적하므로 거래 목록을 만들지 않습니다. 반면 `search`와 `export`는 최신순 결과를 만들기 위해 조건에 맞는 거래를 list에 모아 정렬합니다. `list`는 파일 전체를 확인하되, `heapq.nlargest()`로 최신 후보를 최대 `--limit`개만 유지합니다.

## CSV 형식

CSV는 UTF-8 인코딩과 헤더 행을 사용합니다. `date`, `type`, `category`, `amount` 열은 필수이고 `memo`, `tags`는 선택입니다. `tags`는 쉼표로 구분합니다.

| column | required | description |
| --- | --- | --- |
| `date` | Y | `YYYY-MM-DD` |
| `type` | Y | `income` 또는 `expense` |
| `category` | Y | 등록된 카테고리 |
| `amount` | Y | 0보다 큰 정수 |
| `memo` | N | 메모 문자열 |
| `tags` | N | 쉼표로 구분한 태그 |

예시 `import.csv`:

```csv
date,type,category,amount,memo,tags
2026-08-01,income,salary,3000000,급여,salary
2026-08-02,expense,food,12000,점심,"meal,lunch"
```

목록에 없는 카테고리를 가져오려면 먼저 추가합니다.

```bash
python -m budget_app category add --name shopping
```

## 오류 예시

- 존재하지 않는 ID를 삭제하거나 수정하면 안내 메시지가 출력되고 해당 작업은 수행되지 않습니다.
- `add`에서 `2026-13-40`처럼 유효하지 않은 날짜를 입력하면 `YYYY-MM-DD` 형식 오류와 올바른 예시가 출력됩니다.
- 등록되지 않은 카테고리로 거래를 추가하거나 검색하면 카테고리를 확인하거나 추가하라는 안내가 출력됩니다.

## 5분 Quick Demo

아래는 빈 데이터 디렉터리에서 주요 기능을 순서대로 확인하는 예시입니다. `add` 명령에는 앞서 소개한 대화형 입력 값을 입력합니다.

```bash
python -m budget_app --data-dir ./demo-data --help
python -m budget_app --data-dir ./demo-data category list
python -m budget_app --data-dir ./demo-data add
# 2026-08-02 / expense / food / 12000 / 점심 / meal,lunch
python -m budget_app --data-dir ./demo-data add
# 2026-08-01 / income / salary / 3000000 / 급여 / salary
python -m budget_app --data-dir ./demo-data list --limit 5
python -m budget_app --data-dir ./demo-data search --type expense --tag meal
python -m budget_app --data-dir ./demo-data budget set --month 2026-08 --amount 500000
python -m budget_app --data-dir ./demo-data summary --month 2026-08 --top 3
python -m budget_app --data-dir ./demo-data export --out demo-export.csv --month 2026-08
```

## 학습 문서

- [주요 Python·설계 개념](./CONCEPTS.md)
- [실제 함수 호출 순서](./CODE_FLOW.md)
- [코드 구조와 실행 흐름](./CODE_ARCHITECTURE.md)
