<div align="center">

# Codyssey Main Course

코디세이 본과정에서 수행한 미션을 모아 둔 학습 기록 저장소입니다.

![Course](https://img.shields.io/badge/Codyssey-Main%20Course-2F80ED?style=flat-square)
![Mission](https://img.shields.io/badge/Missions-7-27AE60?style=flat-square)
![Docs](https://img.shields.io/badge/Docs-Learning%20Log-F2994A?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-Linux%20%7C%20Python%20%7C%20HTML%2FCSS%2FJS%20%7C%20SQL-333333?style=flat-square)

각 폴더는 하나의 미션을 담고 있으며, 단순 결과물보다  
**문제를 이해한 과정**, **실험과 검증**, **코드와 문서로 남긴 흔적**을 함께 정리하는 것을 목표로 합니다.

</div>

---

## Mission Map

| 단계 | 미션 | 핵심 주제 | 바로가기 |
|---|---|---|---|
| `B1-1` | System Control Automation Scripts | Linux 서버 운영, 계정/권한, 방화벽, 로그, cron, Bash 자동화 | [Mission](B1-1_Developing-System-Control-Automation-Scripts/) |
| `B1-2` | Linux Processes and System Resources | OOM Crash, CPU Spike, Deadlock, 프로세스 관찰, 장애 리포트 | [Mission](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/) |
| `B2-1` | File-based Household Account Console Program | Python CLI, 파일 저장소, JSONL, CSV, 예외 처리, 계층형 구조 | [Mission](B2-1_Create_file-based_household_account_console_program/) |
| `B3-1` | Mini Redis | 메모리 기반 키-값 저장소, 해시맵, LRU, TTL, REPL | [Mission](B3-1_Bulid_mini_Redis/) |
| `B3-2` | Mini Git | 커밋 그래프, 브랜치, DAG 탐색, 검색, 정렬, CLI | [Mission](B3-2%20_Build_mini_Git/) |
| `B4-1` | Complete Web Foundation | Vanilla HTML/CSS/JavaScript, 반응형 UI, 다크 모드, DOM, GitHub API | [Mission](B4-1_Complete_Web_Foundation/) |
| `B5-1` | Database Practice | MySQL, 테이블 설계, PK/FK, JOIN, GROUP BY, SQL 실습 | [Mission](B5-1_Database%20/README.md) |

---

## Highlights

| 영역 | 남긴 것 |
|---|---|
| Linux Operation | 사용자, 그룹, 권한, 방화벽, 로그, cron을 다루며 서버 운영 흐름을 정리했습니다. |
| Process Troubleshooting | OOM Crash, CPU Spike, Deadlock을 재현하고 증거 기반 리포트로 분석했습니다. |
| Python Application | 표준 라이브러리만으로 파일 기반 가계부 CLI를 구현하고 구조를 문서화했습니다. |
| In-Memory Data Store | Redis 핵심 아이디어를 자료구조 수준에서 구현하고 TTL/LRU 동작을 확인했습니다. |
| Graph-based VCS | Git의 커밋 그래프, 브랜치, 검색, 경로 탐색을 작게 재구성했습니다. |
| Web Foundation | 순수 HTML, CSS, JavaScript로 반응형 포트폴리오와 브라우저 상호작용을 구현했습니다. |
| Database Design | 관계형 데이터베이스 설계와 SQL 조회, 조인, 집계를 순서대로 실습했습니다. |

---

## Repository Structure

```text
Codyssey_main_course/
├── B1-1_Developing-System-Control-Automation-Scripts/
│   ├── README.md
│   ├── images/
│   └── linux_agent_app.zip
├── B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/
│   ├── README.md
│   ├── reports/
│   ├── scripts/
│   ├── evidence/
│   └── agent-app-leak.zip
├── B2-1_Create_file-based_household_account_console_program/
│   ├── README.md
│   ├── PYTHON_DEEP_DIVE.md
│   └── budget_app/
├── B3-1_Bulid_mini_Redis/
│   ├── README.md
│   ├── CODE_GUIDE.md
│   ├── DATA_STRUCTURE_GUIDE.md
│   └── ...
├── B3-2 _Build_mini_Git/
│   ├── README.md
│   ├── ALGORITHMS_GUIDE.md
│   ├── GRAPH_AND_DAG_GUIDE.md
│   └── ...
├── B4-1_Complete_Web_Foundation/
│   ├── README.md
│   ├── index.html
│   ├── css/
│   ├── js/
│   ├── images/
│   └── docs/
├── B5-1_Database /
│   ├── README.md
│   ├── DATABASE_STUDY.md
│   ├── SCHEMA_GUIDE.md
│   ├── SQL_QUERY_GUIDE.md
│   └── ...
└── README.md
```

---

## Mission Notes

### `B1-1` Linux Server Operation

작은 Linux 서버를 운영한다고 가정하고 사용자, 그룹, 디렉토리 권한, 방화벽, 애플리케이션 실행, 모니터링 스크립트, cron 설정까지 구성한 미션입니다.

주요 결과물:

- 서버 운영 수행 내역서
- 시스템 상태 점검용 `monitor.sh`
- 실습 화면 캡처 이미지

[미션 보기](B1-1_Developing-System-Control-Automation-Scripts/)

### `B1-2` Process Troubleshooting Lab

`agent-app-leak` 실행 파일을 사용해 OOM Crash, CPU Spike, Deadlock을 재현하고 분석한 미션입니다.

주요 결과물:

- 장애별 GitHub Issue 형식 리포트
- 실험 자동화 스크립트
- 로그, 스냅샷, 모니터링 CSV 증거 자료

[미션 보기](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/)

### `B2-1` Household Account CLI

Python 표준 라이브러리만 사용해 파일 기반 가계부 콘솔 프로그램을 구현한 미션입니다.

주요 기능:

- 거래 추가, 조회, 검색, 수정, 삭제
- 월별 요약과 예산 관리
- 카테고리 관리
- CSV 가져오기와 내보내기
- JSONL 기반 파일 저장

[미션 보기](B2-1_Create_file-based_household_account_console_program/)

### `B3-1` Mini Redis

메모리 기반 키-값 저장소를 직접 구현하며 해시맵, 이중 연결 리스트, 최소 힙으로 LRU와 TTL 동작을 다룬 미션입니다.

주요 결과물:

- REPL 기반 `mini_redis`
- 자료구조 설명서
- 코드 실행 흐름 가이드

[미션 보기](B3-1_Bulid_mini_Redis/)

### `B3-2` Mini Git

Git의 핵심 아이디어를 작게 구현해 커밋 그래프, 브랜치, 탐색, 검색을 다뤄 보는 CLI 미션입니다.

주요 결과물:

- `mini_git` CLI
- DAG와 알고리즘 가이드
- 명령어 및 코드 설명 문서

[미션 보기](B3-2%20_Build_mini_Git/)

### `B4-1` Complete Web Foundation

순수 HTML, CSS, JavaScript만으로 반응형 포트폴리오 웹사이트를 만들며 브라우저의 기본 동작 흐름을 익힌 미션입니다.

주요 기능:

- 모바일 햄버거 메뉴
- 다크 모드와 로컬스토리지 저장
- 부드러운 스크롤과 스크롤 탑 버튼
- Intersection Observer 기반 스크롤 애니메이션
- Contact 폼 유효성 검사
- GitHub API 기반 프로젝트 카드 렌더링

[미션 보기](B4-1_Complete_Web_Foundation/)

### `B5-1` Database Practice

카페 주문 데이터를 주제로 MySQL 스키마 설계와 SQL 실습을 단계별로 정리한 미션입니다.

주요 결과물:

- `schema.sql`
- `sample_data.sql`
- `queries.sql`
- 데이터베이스와 SQL 해설 문서

[미션 보기](B5-1_Database%20/README.md)

---

## Index

- [B1-1 README](B1-1_Developing-System-Control-Automation-Scripts/README.md)
- [B1-2 README](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/README.md)
- [B1-2 장애 리포트](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/reports/)
- [B1-2 실험 스크립트](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/scripts/)
- [B2-1 README](B2-1_Create_file-based_household_account_console_program/README.md)
- [B2-1 코드 가이드](B2-1_Create_file-based_household_account_console_program/budget_app/CODE_GUIDE.md)
- [B2-1 Python Deep Dive](B2-1_Create_file-based_household_account_console_program/PYTHON_DEEP_DIVE.md)
- [B3-1 README](B3-1_Bulid_mini_Redis/README.md)
- [B3-1 코드 가이드](B3-1_Bulid_mini_Redis/CODE_GUIDE.md)
- [B3-1 자료구조 가이드](B3-1_Bulid_mini_Redis/DATA_STRUCTURE_GUIDE.md)
- [B3-2 README](B3-2%20_Build_mini_Git/README.md)
- [B3-2 그래프/DAG 가이드](B3-2%20_Build_mini_Git/GRAPH_AND_DAG_GUIDE.md)
- [B3-2 알고리즘 가이드](B3-2%20_Build_mini_Git/ALGORITHMS_GUIDE.md)
- [B4-1 README](B4-1_Complete_Web_Foundation/README.md)
- [B4-1 미션북](B4-1_Complete_Web_Foundation/docs/mission-book.md)
- [B5-1 README](B5-1_Database%20/README.md)
- [B5-1 데이터베이스 스터디](B5-1_Database%20/DATABASE_STUDY.md)
- [B5-1 스키마 가이드](B5-1_Database%20/SCHEMA_GUIDE.md)
- [B5-1 SQL 쿼리 가이드](B5-1_Database%20/SQL_QUERY_GUIDE.md)

---

## 성장 기록

이 저장소는 완성된 정답 모음이라기보다, 미션을 수행하며 생각을 정리해 가는 작업 공간입니다.

앞으로 미션이 추가될 때마다 다음 기준으로 정리할 예정입니다.

- 미션별 독립 README 작성
- 실행 방법과 검증 방법 분리
- 실험 증거는 폴더로 보존
- 코드가 있는 경우 구조 설명 문서 추가
- 루트 README의 Mission Map 갱신
