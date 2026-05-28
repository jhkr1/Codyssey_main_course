<div align="center">

# Codyssey Main Course

코디세이 본과정에서 수행한 미션을 모아 둔 학습 기록 저장소입니다.

![Course](https://img.shields.io/badge/Codyssey-Main%20Course-2F80ED?style=flat-square)
![Mission](https://img.shields.io/badge/Missions-3-27AE60?style=flat-square)
![Docs](https://img.shields.io/badge/Docs-Learning%20Log-F2994A?style=flat-square)
![Stack](https://img.shields.io/badge/Stack-Linux%20%7C%20Python-333333?style=flat-square)

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

---

## Highlights

| 영역 | 남긴 것 |
|---|---|
| Linux Operation | 사용자, 그룹, 권한, 방화벽, 로그, cron을 다루며 서버 운영 흐름을 정리했습니다. |
| Process Troubleshooting | OOM Crash, CPU Spike, Deadlock을 재현하고 증거 기반 리포트로 분석했습니다. |
| Python Application | 표준 라이브러리만으로 파일 기반 가계부 CLI를 구현하고 구조를 문서화했습니다. |
| Documentation | 각 미션을 실습서처럼 읽을 수 있도록 실행 과정, 판단 근거, 결과물을 함께 기록했습니다. |

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
└── README.md
```

---

## What This Repository Focuses On

### 1. 기록으로 설명하기

미션을 끝냈다는 사실보다, 왜 그렇게 해결했는지 설명할 수 있는 기록을 남깁니다.

- 실행 환경
- 문제 상황
- 사용한 명령어와 코드
- 확인한 증거
- 시행착오와 판단 근거
- 최종 결과

### 2. 운영 감각 익히기

B1 미션들은 Linux 서버를 운영자의 관점에서 바라보는 데 초점을 둡니다.

- 사용자와 권한을 설계하기
- 서비스 실행 환경 구성하기
- 로그와 모니터링으로 상태 관찰하기
- 장애 상황을 재현하고 증거 기반으로 분석하기

### 3. 프로그램 구조화하기

B2 미션부터는 Python 프로그램을 기능별로 나누고, 유지보수 가능한 콘솔 애플리케이션으로 정리합니다.

- CLI 명령 설계
- 모델, 저장소, 서비스 계층 분리
- 입력 검증과 예외 처리
- 파일 기반 데이터 저장
- 코드 설명 문서화

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

---

## Index

- [B1-1 README](B1-1_Developing-System-Control-Automation-Scripts/README.md)
- [B1-2 README](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/README.md)
- [B1-2 장애 리포트](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/reports/)
- [B1-2 실험 스크립트](B1-2_Troubleshooting_LinuxProcesses_and_System-Resources/scripts/)
- [B2-1 README](B2-1_Create_file-based_household_account_console_program/README.md)
- [B2-1 코드 가이드](B2-1_Create_file-based_household_account_console_program/budget_app/CODE_GUIDE.md)
- [B2-1 Python Deep Dive](B2-1_Create_file-based_household_account_console_program/PYTHON_DEEP_DIVE.md)

---

## 성장 기록

이 저장소는 완성된 정답 모음이라기보다, 미션을 수행하며 생각을 정리해 가는 작업 공간입니다.

앞으로 미션이 추가될 때마다 다음 기준으로 정리할 예정입니다.

- 미션별 독립 README 작성
- 실행 방법과 검증 방법 분리
- 실험 증거는 폴더로 보존
- 코드가 있는 경우 구조 설명 문서 추가
- 루트 README의 Mission Map 갱신
