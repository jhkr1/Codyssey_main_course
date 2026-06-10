# Mini Git 미션 가이드

Mini Git은 Git의 핵심 아이디어를 작게 구현해 보는 CLI 프로그램입니다.

이 저장소의 문서는 “짧은 요약본”이 아니라, 미션을 진행하면서 관련 지식을 함께 공부할 수 있도록 구성한 학습 자료입니다. 다만 모든 내용을 README 하나에 몰아넣으면 실행법을 찾기 어려워지므로, README는 미션과 실행 안내를 담당하고 깊은 설명은 두 개의 본문 가이드로 나눕니다.

읽는 순서:

```text
1. README.md
   미션 목표, 실행법, 명령어, 코드 구조를 확인한다.

2. GRAPH_AND_DAG_GUIDE.md
   Git을 그래프와 DAG 관점에서 깊게 공부한다.

3. ALGORITHMS_GUIDE.md
   DFS, BFS, 위상 정렬 감각, merge sort, 역색인을 공부한다.

4. main.py와 mini_git.py
   문서에서 배운 개념이 코드에서 어디에 있는지 확인한다.
```

## 1. 이 프로젝트가 다루는 것

Mini Git은 실제 Git 전체를 구현하지 않습니다. 대신 Git의 핵심 뼈대를 작게 만들어 봅니다.

구현하는 것:

```text
저장소 초기화
브랜치 생성
브랜치 전환
커밋 생성
커밋 로그 출력
커밋 사이 최단 경로 탐색
특정 커밋의 모든 조상 탐색
커밋 메시지 검색
작성자 검색
정렬 기준이 있는 로그 출력
REPL 형태의 CLI
```

구현하지 않는 것:

```text
파일 내용 추적
스테이징 영역
실제 Git object 저장
원격 저장소
네트워크 통신
데이터 영속성
```

이 프로그램은 메모리 안에서만 동작합니다. 종료하면 저장소 상태도 사라집니다.

## 2. 실행 방법

Python 3.10 이상이 필요합니다.

```bash
python main.py
```

실행하면 프롬프트가 나옵니다.

```text
mini-git>
```

종료 명령:

```text
exit
quit
```

## 3. 명령어 규칙

명령어는 대소문자를 구분하지 않습니다.

```text
INIT Alice
init Alice
Init Alice
```

공백이 들어가는 문자열은 따옴표로 감쌉니다.

```text
init "Alice Kim"
commit "Add login feature"
search "login feature"
search "--author=Alice Kim"
```

잘못된 입력에 대한 최소 에러 메시지:

```text
Invalid args
Unknown branch: <name>
Unknown commit: <hash>
```

## 4. 지원 명령어

### INIT

```text
INIT <user_name>
```

저장소를 초기화하고 `main` 브랜치를 만듭니다.

예시:

```text
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice
```

### COMMIT

```text
COMMIT <message>
```

현재 브랜치의 HEAD를 부모로 하는 새 커밋을 만듭니다.

예시:

```text
mini-git> commit "Initial commit"
[main c000001] Initial commit
```

### BRANCH

```text
BRANCH <branch_name>
```

현재 HEAD를 가리키는 새 브랜치를 만듭니다.

예시:

```text
mini-git> branch feature
Created branch: feature
```

### SWITCH

```text
SWITCH <branch_name>
```

현재 브랜치를 바꿉니다.

예시:

```text
mini-git> switch feature
Switched to branch: feature
```

### LOG

```text
LOG
```

기본 로그는 최신순이 아니라 부모가 자식보다 먼저 출력되도록 나옵니다.

### LOG --sort-by

```text
LOG --sort-by=date
LOG --sort-by=author
```

날짜 또는 작성자 기준으로 로그를 정렬합니다. Python의 `sorted()`와 `list.sort()`는 사용하지 않고 직접 구현한 merge sort를 씁니다.

### PATH

```text
PATH <commit1> <commit2>
```

두 커밋 사이의 최단 경로를 찾습니다. 부모 연결을 무방향 간선처럼 봅니다.

### ANCESTORS

```text
ANCESTORS <commit_hash>
```

해당 커밋에서 도달 가능한 모든 조상을 출력합니다.

### SEARCH

```text
SEARCH <keyword>
SEARCH --author=<name>
```

키워드 검색 또는 작성자 검색을 합니다. 역색인을 사용합니다.

## 5. 실행 예시

```text
mini-git> init "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> commit "Initial commit"
[main c000001] Initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit "Add login feature"
[feature c000002] Add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main c000003] Add payment feature

mini-git> log
commit c000001 (Alice, 2026-06-10 16:07:17)
Initial commit
commit c000002 (Alice, 2026-06-10 16:07:18) [feature]
Add login feature
commit c000003 (Alice, 2026-06-10 16:07:19) [main]
Add payment feature

mini-git> path c000002 c000003
Path: c000002 -> c000001 -> c000003

mini-git> ancestors c000003
Ancestors: c000001

mini-git> search login
Found 1 commit:
- c000002: Add login feature
```

## 6. 문서 구성

### README.md

지금 읽고 있는 문서입니다. 미션 목적, 실행 방법, 명령어, 제출 파일, 코드 구조를 빠르게 확인합니다.

### GRAPH_AND_DAG_GUIDE.md

커밋 그래프, 브랜치, HEAD, DAG, 부모 관계를 다룹니다. Git이 왜 단순 파일 저장 프로그램이 아니라 그래프 구조를 다루는 도구인지 설명합니다.

### ALGORITHMS_GUIDE.md

탐색, 정렬, 검색을 다룹니다. `LOG`, `PATH`, `ANCESTORS`, `SEARCH`, `LOG --sort-by`가 어떤 알고리즘으로 동작하는지 설명합니다.

## 7. 코드 구조

파일은 두 개의 Python 파일로 나뉩니다.

```text
main.py
mini_git.py
```

`main.py`는 실행 진입점입니다. `python main.py`로 실행할 때 `MiniGitCLI`를 시작합니다.

`mini_git.py`는 실제 구현을 담고 있습니다.

| 코드 | 역할 |
|---|---|
| `Commit` | 커밋 노드 |
| `MiniGitRepository` | 저장소, 브랜치, 그래프 관리 |
| `InvertedIndex` | 검색 인덱스 관리 |
| `MiniGitCLI` | 명령어 파싱과 실행 |
| `merge_sort` | 직접 구현한 정렬 |

## 8. 공부 순서 추천

1. README에서 실행법과 명령어를 본다.
2. GRAPH_AND_DAG_GUIDE에서 커밋 그래프 그림을 직접 그려 본다.
3. 브랜치가 포인터라는 말을 이해한다.
4. ALGORITHMS_GUIDE에서 LOG, PATH, ANCESTORS, SEARCH의 알고리즘을 읽는다.
5. `mini_git.py`를 열고 개념과 코드를 연결한다.
6. 직접 커밋을 여러 개 만들고 예상 결과와 실제 결과를 비교한다.

## 9. 제출물

```text
main.py
mini_git.py
README.md
GRAPH_AND_DAG_GUIDE.md
ALGORITHMS_GUIDE.md
```
