# 그래프와 DAG로 이해하는 Mini Git

이 문서는 Git의 커밋 구조를 그래프 관점에서 깊게 이해하기 위한 가이드입니다. Git을 파일 저장 도구로만 보면 branch, HEAD, merge, rebase가 흩어진 명령처럼 보입니다. 하지만 Git을 커밋 그래프로 보면 이 개념들이 하나의 그림 안에 들어옵니다.

## 1. Git은 왜 그래프인가

그래프는 점과 선으로 이루어진 구조입니다.

```text
점: node, vertex
선: edge
```

Mini Git에서는 다음처럼 대응됩니다.

```text
커밋 = 점
부모 관계 = 선
```

커밋 `c000002`가 `c000001`을 부모로 가진다면:

```text
c000001 <- c000002
```

이 구조는 단순한 목록이 아닙니다. 커밋이 여러 갈래로 갈라질 수 있기 때문에 그래프입니다.

```text
          c000002
         /
c000001
         \
          c000003
```

## 2. 커밋은 무엇을 담는가

Mini Git의 커밋은 다음 정보를 가집니다.

```text
hash
message
author
timestamp
parents
```

표로 보면:

| 필드 | 뜻 | 예시 |
|---|---|---|
| hash | 커밋 이름표 | c000002 |
| message | 커밋 설명 | Add login feature |
| author | 작성자 | Alice |
| timestamp | 생성 시간 | 2026-06-10 16:07:18 |
| parents | 부모 커밋 목록 | [c000001] |

여기서 가장 중요한 필드는 `parents`입니다. 이 필드가 커밋을 단순 데이터가 아니라 그래프의 노드로 만듭니다.

## 3. 부모 커밋

부모 커밋은 “이 커밋이 만들어질 때 기준이 된 이전 커밋”입니다.

첫 커밋은 부모가 없습니다.

```text
c000001
parents: []
```

두 번째 커밋은 첫 커밋을 부모로 가집니다.

```text
c000002
parents: [c000001]
```

그래프:

```text
c000001 <- c000002
```

세 번째 커밋까지 만들면:

```text
c000001 <- c000002 <- c000003
```

## 4. 브랜치는 포인터다

브랜치를 처음 배우면 흔히 이렇게 생각하기 쉽습니다.

```text
main 브랜치라는 폴더 안에 커밋들이 들어 있다.
feature 브랜치라는 폴더 안에 또 다른 커밋들이 들어 있다.
```

하지만 Git의 브랜치는 폴더가 아닙니다. 브랜치는 커밋 묶음도 아닙니다. 브랜치는 커밋 하나를 가리키는 아주 작은 이름표입니다.

더 정확히 말하면:

```text
브랜치 = 특정 커밋 hash를 저장하고 있는 이름
```

예를 들어 `main` 브랜치가 `c000001`을 가리킨다는 것은 다음과 같습니다.

```text
main -> c000001
```

여기서 `main`은 커밋 전체를 담고 있지 않습니다. 단지 `c000001`이라는 커밋 해시를 기억하고 있을 뿐입니다.

### 포인터를 비유로 이해하기

포인터라는 말이 낯설다면 “책갈피”를 떠올리면 됩니다.

책갈피는 책 내용을 복사하지 않습니다. 책갈피는 어느 페이지를 펼쳐야 하는지만 알려줍니다.

```text
책 내용 전체 = 커밋 그래프
책갈피 = 브랜치
책갈피가 꽂힌 페이지 = 브랜치가 가리키는 커밋
```

또는 지도 위의 핀으로 생각해도 좋습니다.

```text
지도 전체 = 커밋 그래프
핀 이름 = 브랜치 이름
핀이 꽂힌 위치 = 특정 커밋
```

핀을 옮긴다고 지도가 복사되지는 않습니다. 마찬가지로 브랜치를 이동한다고 커밋들이 복사되지는 않습니다.

### 브랜치가 커밋 묶음이 아니라는 증거

다음 상태를 봅시다.

```text
c000001 <- c000002 <- c000003
```

여기서 `main`이 마지막 커밋을 가리키고 있다면:

```text
c000001 <- c000002 <- c000003
                          ^
                          |
                         main
```

`main` 브랜치가 실제로 저장하는 것은 전체 목록이 아닙니다.

```text
main = c000003
```

그런데 어떻게 `main`의 전체 이력을 알 수 있을까요?

답은 부모를 따라가면 됩니다.

```text
main -> c000003
          |
       parent
          v
       c000002
          |
       parent
          v
       c000001
```

즉, 브랜치가 모든 커밋을 들고 있는 것이 아니라, 브랜치가 마지막 커밋 하나를 가리키고, 그 마지막 커밋에서 부모를 따라가며 이력을 복원합니다.

이것이 Git 브랜치가 가벼운 이유입니다. 브랜치를 하나 만든다고 커밋들이 통째로 복사되지 않습니다. 새 이름표 하나가 생길 뿐입니다.

### 브랜치 생성은 복사가 아니라 이름표 추가다

다음 상태에서:

```text
c000001
main -> c000001
```

`branch feature`를 실행하면 Git은 커밋을 복사하지 않습니다. 같은 커밋을 가리키는 이름표를 하나 더 만듭니다.

```text
c000001
main    -> c000001
feature -> c000001
```

이 시점에서 `main`과 `feature`는 완전히 같은 커밋을 가리킵니다.

중요한 점:

```text
브랜치가 2개가 되었지만 커밋은 여전히 1개다.
```

그래서 브랜치 생성은 매우 빠릅니다. 커밋 그래프를 복사하지 않고, 브랜치 이름과 커밋 해시 하나만 저장하면 되기 때문입니다.

### 커밋하면 현재 브랜치만 이동한다

이제 `feature` 브랜치로 이동한 뒤 새 커밋을 만든다고 합시다.

```text
switch feature
commit "Add login feature"
```

커밋 전:

```text
c000001
main    -> c000001
feature -> c000001
```

커밋 후:

```text
c000001 <- c000002
main    -> c000001
feature -> c000002
```

여기서 움직인 것은 `feature`뿐입니다. `main`은 여전히 `c000001`을 가리킵니다.

이것이 브랜치 분기의 시작입니다.

### main으로 돌아와 커밋하면 왜 갈라질까

다시 `main`으로 돌아옵니다.

```text
switch main
```

현재 상태:

```text
c000001 <- c000002
main    -> c000001
feature -> c000002
```

이 상태에서 `main`에서 새 커밋을 만들면 새 커밋의 부모는 `main`이 가리키던 `c000001`입니다.

```text
commit "Add payment feature"
```

결과:

```text
          c000002
         /
c000001
         \
          c000003

feature -> c000002
main    -> c000003
```

이제 브랜치가 갈라졌습니다. 하지만 여전히 각 브랜치는 커밋 하나만 가리킵니다.

```text
feature = c000002
main    = c000003
```

각 브랜치의 전체 이력은 마지막 커밋에서 부모를 따라가며 알 수 있습니다.

### Mini Git에서는 어떻게 저장할까

Mini Git에서는 브랜치를 딕셔너리로 표현합니다.

```text
branches: branch_name -> commit_hash
```

예를 들어:

```text
branches = {
    "main": "c000003",
    "feature": "c000002"
}
```

이 말은 다음과 같습니다.

```text
main은 c000003을 가리킨다.
feature는 c000002를 가리킨다.
```

브랜치 구조만 보면 단순한 이름표 표입니다.

```text
main    -> c000003
feature -> c000002
```

커밋 그래프는 별도로 `commits`에 저장되어 있습니다.

```text
commits: hash -> Commit
```

그래서 Mini Git의 저장소 구조는 크게 이렇게 나뉩니다.

```text
commits  = 모든 커밋 노드 저장소
branches = 브랜치 이름이 어떤 커밋을 가리키는지 저장하는 표
```

### 왜 이 구조가 중요한가

브랜치를 포인터로 이해하면 다음 개념들이 쉬워집니다.

```text
branch: 새 이름표를 만든다
switch: 현재 사용할 이름표를 바꾼다
commit: 현재 이름표를 새 커밋으로 이동시킨다
log: 이름표가 가리키는 커밋에서 부모를 따라간다
merge: 두 이름표가 가리키는 커밋을 부모로 삼을 수 있다
```

Git에서 브랜치가 가볍고 빠른 이유도 여기 있습니다. 브랜치를 만들 때 프로젝트 전체를 복사하지 않고, 커밋 하나를 가리키는 이름만 추가하기 때문입니다.

정리하면:

```text
브랜치는 커밋 묶음이 아니다.
브랜치는 커밋 하나를 가리키는 이름표다.
브랜치의 이력은 그 커밋에서 부모를 따라가며 얻는다.
커밋하면 현재 브랜치 포인터만 새 커밋으로 이동한다.
```

## 5. HEAD는 현재 위치다

HEAD는 “지금 내가 어느 브랜치 위에서 작업하고 있는가”를 나타냅니다. Mini Git에서는 `current_branch`가 이 역할을 합니다.

```text
current_branch = "main"
```

이 상태에서 커밋하면 `main`이 이동합니다.

```text
current_branch = "feature"
```

이 상태에서 커밋하면 `feature`가 이동합니다.

중요한 점은 `switch`가 커밋을 새로 만들지 않는다는 것입니다. `switch`는 현재 작업 기준 브랜치를 바꿀 뿐입니다.

## 6. 브랜치가 갈라지는 과정

다음 명령을 생각해 봅시다.

```text
init "Alice"
commit "Initial commit"
branch feature
switch feature
commit "Add login feature"
switch main
commit "Add payment feature"
```

처음 커밋:

```text
c000001
main -> c000001
```

브랜치 생성:

```text
c000001
main -> c000001
feature -> c000001
```

feature에서 커밋:

```text
c000001 <- c000002
main -> c000001
feature -> c000002
```

main에서 커밋:

```text
          c000002
         /
c000001
         \
          c000003

feature -> c000002
main -> c000003
```

이제 그래프가 선형 목록이 아니라 갈라진 구조가 되었습니다.

## 7. DAG란 무엇인가

DAG는 Directed Acyclic Graph입니다.

```text
Directed: 방향이 있다
Acyclic: 순환이 없다
Graph: 그래프다
```

즉 방향이 있고, 다시 자기 자신으로 돌아오는 고리가 없는 그래프입니다.

순환이 있는 그래프:

```text
A -> B -> C -> A
```

Git 커밋 그래프는 이런 구조가 되면 안 됩니다. 부모를 따라갔는데 다시 자기 자신이 나오면 “과거”와 “미래”의 구분이 무너집니다.

## 8. Git 커밋 그래프가 DAG인 이유

새 커밋은 이미 존재하는 커밋만 부모로 삼습니다. 아직 만들어지지 않은 미래 커밋을 부모로 삼을 수 없습니다.

그래서 다음 규칙이 성립합니다.

```text
부모는 항상 자식보다 먼저 존재한다.
```

이 규칙 때문에 순환이 생기지 않습니다.

Mini Git에서도 새 커밋을 만들 때 현재 HEAD만 부모로 넣습니다.

```text
새 커밋의 parents = [현재 HEAD]
```

현재 HEAD는 이미 존재하는 커밋이므로 DAG 구조가 유지됩니다.

## 9. LOG와 위상 정렬 감각

이 미션의 `LOG`는 최신순이 아닙니다. 부모 커밋이 자식 커밋보다 먼저 나와야 합니다.

예를 들어:

```text
          c000002
         /
c000001
         \
          c000003
```

가능한 출력:

```text
c000001
c000002
c000003
```

또는:

```text
c000001
c000003
c000002
```

둘 다 부모가 자식보다 먼저 나오므로 조건을 만족합니다.

이 사고방식은 위상 정렬과 연결됩니다. 위상 정렬은 “먼저 와야 하는 것이 먼저 오도록 나열하는 것”입니다.

## 10. 자료구조로서의 그래프

이제 Git 이야기를 잠깐 내려놓고, 그래프 자체를 자료구조로 봅시다.

그래프는 결국 다음 질문에 답하기 위한 구조입니다.

```text
어떤 것들이 존재하는가?
그것들은 서로 어떻게 연결되어 있는가?
어떤 점에서 어떤 점으로 갈 수 있는가?
```

그래프는 보통 두 가지 요소로 설명합니다.

```text
노드: 대상 하나
간선: 대상 사이의 관계
```

Mini Git에서는:

```text
노드 = Commit 객체
간선 = parents 안에 들어 있는 부모 커밋 hash
```

즉, 커밋 그래프를 구현한다는 말은 “커밋 객체들을 만들고, 각 커밋 객체가 부모 커밋을 기억하게 만든다”는 뜻입니다.

## 11. 그래프를 코드로 저장하는 대표 방식

그래프를 코드로 저장하는 방식은 여러 가지가 있습니다.

대표적으로:

```text
1. 인접 행렬
2. 인접 리스트
3. 객체 참조 방식
4. hash 기반 노드 저장소 + 연결 정보
```

Mini Git은 네 번째 방식에 가깝습니다.

```text
commits: hash -> Commit
Commit.parents: parent hash 목록
```

이 구조는 Git 같은 시스템에 잘 맞습니다.

이유:

```text
커밋 hash로 빠르게 커밋을 찾을 수 있다.
각 커밋은 자기 부모만 알면 된다.
브랜치는 마지막 커밋 hash 하나만 저장하면 된다.
그래프 전체를 복사하지 않아도 된다.
```

## 12. Commit 클래스 뜯어보기

`mini_git.py`의 커밋 클래스는 다음과 같습니다.

```python
@dataclass
class Commit:
    """커밋 그래프의 노드 하나."""

    hash: str
    message: str
    author: str
    timestamp: datetime
    parents: list[str]
```

이 코드는 단순해 보이지만 그래프의 핵심이 들어 있습니다.

```text
hash      -> 이 노드를 찾기 위한 고유 이름
message   -> 커밋 설명
author    -> 작성자
timestamp -> 생성 시각
parents   -> 연결된 부모 노드 목록
```

특히 `parents`가 중요합니다.

```python
parents: list[str]
```

왜 `Commit` 객체 자체를 부모로 넣지 않고 `str`, 즉 hash를 넣을까요?

Mini Git은 모든 커밋을 `commits` 딕셔너리에 모아 둡니다.

```text
commits["c000001"] = Commit(...)
commits["c000002"] = Commit(...)
```

그래서 부모를 직접 객체로 들고 있지 않아도, 부모 hash만 있으면 언제든 다음처럼 찾아갈 수 있습니다.

```text
parent_hash = "c000001"
parent_commit = commits[parent_hash]
```

이 방식은 “이름표로 노드를 찾는 그래프”입니다.

## 13. commits 딕셔너리는 노드 저장소다

`MiniGitRepository`에는 다음 필드가 있습니다.

```python
self.commits = {}
```

이 딕셔너리는 그래프의 모든 노드를 보관하는 저장소입니다.

```text
commits
├─ c000001 -> Commit(...)
├─ c000002 -> Commit(...)
└─ c000003 -> Commit(...)
```

리스트가 아니라 딕셔너리를 쓰는 이유는 조회 속도입니다.

만약 리스트에 저장했다면 `c000002`를 찾으려면 앞에서부터 하나씩 봐야 합니다.

```text
c000001인가?
c000002인가?
```

하지만 딕셔너리는 hash를 키로 사용하므로 평균적으로 빠르게 찾을 수 있습니다.

```text
commits["c000002"]
```

그래프 문제에서 “노드 id를 알고 있을 때 노드를 빠르게 찾는 것”은 매우 중요합니다.

## 14. parents는 방향 간선이다

다음 커밋이 있다고 합시다.

```text
c000002.parents = ["c000001"]
```

이것은 방향이 있는 연결입니다.

```text
c000002 -> c000001
```

방향을 말로 풀면:

```text
c000002에서 부모 c000001로 갈 수 있다.
```

이 연결은 반대로 자동 생성되지 않습니다.

즉 `c000001`이 “내 자식은 c000002야”라고 직접 저장하고 있지는 않습니다. Mini Git의 기본 그래프는 자식에서 부모로 향하는 방향 정보를 저장합니다.

이 선택은 커밋 구조와 잘 맞습니다. 커밋은 “내가 어디서 왔는가”를 기억하면 충분하기 때문입니다.

## 15. 커밋 생성 코드를 그래프로 읽기

`commit` 메서드의 핵심은 다음 흐름입니다.

```python
parent = self._head_hash()
parents = [] if parent is None else [parent]
commit_hash = self._next_hash()
commit = Commit(
    hash=commit_hash,
    message=message,
    author=self.current_user,
    timestamp=datetime.now(),
    parents=parents,
)
self.commits[commit_hash] = commit
self.branches[self.current_branch] = commit_hash
```

한 줄씩 그래프 관점으로 읽어 봅시다.

```python
parent = self._head_hash()
```

현재 브랜치가 가리키는 커밋을 가져옵니다. 새 커밋의 부모가 될 후보입니다.

```python
parents = [] if parent is None else [parent]
```

첫 커밋이면 부모가 없습니다. 이미 커밋이 있다면 현재 HEAD를 부모 목록에 넣습니다.

```python
commit_hash = self._next_hash()
```

새 노드의 이름표를 만듭니다.

```python
commit = Commit(...)
```

새 커밋 노드를 만듭니다.

```python
self.commits[commit_hash] = commit
```

그래프의 노드 저장소에 새 노드를 등록합니다.

```python
self.branches[self.current_branch] = commit_hash
```

현재 브랜치 포인터를 새 커밋으로 이동합니다.

이 메서드는 단순히 “커밋을 추가한다”가 아니라, 자료구조 관점에서 다음 세 일을 합니다.

```text
1. 새 노드를 만든다.
2. 새 노드에 부모 간선을 기록한다.
3. 현재 브랜치 포인터를 새 노드로 옮긴다.
```

## 16. DAG 조건이 코드에서 어떻게 지켜지는가

DAG가 되려면 순환이 없어야 합니다.

Mini Git에서 순환이 생기지 않는 핵심 이유는 이 줄에 있습니다.

```python
parent = self._head_hash()
```

새 커밋의 부모는 현재 이미 존재하는 HEAD입니다.

그리고 그 다음에야 새 커밋을 만듭니다.

```python
commit_hash = self._next_hash()
commit = Commit(...)
```

순서를 시간으로 보면:

```text
1. 기존 커밋이 있다.
2. 기존 커밋을 부모로 삼는다.
3. 새 커밋을 만든다.
```

새 커밋이 자기 자신을 부모로 삼으려면 자기 hash가 먼저 있어야 합니다. 하지만 이 코드에서는 새 hash를 만든 뒤 부모를 고르는 것이 아니라, 기존 HEAD를 먼저 부모로 정합니다.

그래서 일반 `commit` 흐름에서는 사이클이 생기지 않습니다.

## 17. 그래프를 순회한다는 것

그래프를 저장하는 것만으로는 충분하지 않습니다. 저장한 그래프를 따라가며 정보를 얻어야 합니다.

그래프 순회는 다음 질문에 답하는 과정입니다.

```text
이 노드에서 연결된 다음 노드는 무엇인가?
그 노드를 방문했는가?
방문하지 않았다면 언제 방문할 것인가?
```

Mini Git에서 대표적인 순회는 두 가지입니다.

```text
부모 방향 순회: ANCESTORS, LOG
무방향 순회: PATH
```

## 18. LOG 코드 뜯어보기: 부모 우선 DFS

기본 `LOG`는 부모가 자식보다 먼저 출력되어야 합니다.

이를 위해 Mini Git은 `_all_commits_parent_first`와 `_visit_parent_first`를 사용합니다.

```python
def _all_commits_parent_first(self) -> list[Commit]:
    visited = set()
    result = []

    for commit_hash in self.commits:
        self._visit_parent_first(commit_hash, visited, result)

    return result
```

`visited`는 이미 출력 순서에 넣은 커밋을 다시 처리하지 않기 위한 집합입니다.

`result`는 최종 로그 순서를 담는 리스트입니다.

핵심은 이 함수입니다.

```python
def _visit_parent_first(self, commit_hash: str, visited: set, result: list[Commit]):
    if commit_hash in visited:
        return

    commit = self.commits[commit_hash]
    for parent_hash in commit.parents:
        self._visit_parent_first(parent_hash, visited, result)

    visited.add(commit_hash)
    result.append(commit)
```

순서는 다음과 같습니다.

```text
1. 이미 방문한 커밋이면 끝낸다.
2. 현재 커밋 객체를 가져온다.
3. 부모들을 먼저 방문한다.
4. 부모 방문이 끝난 뒤 현재 커밋을 결과에 넣는다.
```

여기서 가장 중요한 줄은 이것입니다.

```python
for parent_hash in commit.parents:
    self._visit_parent_first(parent_hash, visited, result)
```

현재 커밋을 결과에 넣기 전에 부모를 먼저 방문합니다. 그래서 부모가 자식보다 먼저 출력됩니다.

이것은 “후위 순회”와 비슷합니다. 먼저 아래로 들어가고, 돌아오면서 현재 노드를 결과에 넣습니다.

## 19. ANCESTORS 코드 뜯어보기: 부모 방향 DFS

`ANCESTORS`는 특정 커밋에서 부모 방향으로 갈 수 있는 모든 커밋을 찾습니다.

핵심 구조:

```python
result = []
visited = set()
stack = self.commits[commit_hash].parents[:]
```

`stack`은 앞으로 방문할 후보입니다. 처음에는 시작 커밋의 부모들을 넣습니다.

```python
while stack:
    current = stack.pop()
```

스택에서 하나를 꺼냅니다.

```python
if current in visited:
    continue
```

이미 방문했다면 건너뜁니다.

```python
visited.add(current)
result.append(current)
```

방문 표시를 하고 결과에 넣습니다.

```python
for parent in self.commits[current].parents:
    if parent not in visited:
        stack.append(parent)
```

현재 커밋의 부모들을 다음 방문 후보로 넣습니다.

자료구조 관점에서 보면 `ANCESTORS`는 “방향 그래프에서 시작점으로부터 부모 방향으로 도달 가능한 모든 노드 찾기”입니다.

## 20. PATH 코드 뜯어보기: 방향 그래프를 무방향 그래프로 바꾸기

Mini Git의 커밋 그래프는 기본적으로 자식에서 부모로 가는 방향을 저장합니다.

```text
c000002 -> c000001
c000003 -> c000001
```

하지만 `PATH` 요구사항은 부모 연결을 무방향 간선으로 보라고 합니다.

```text
c000002 <-> c000001 <-> c000003
```

그래서 Mini Git은 `_undirected_adjacency`를 만듭니다.

```python
def _undirected_adjacency(self):
    adjacency = {}
    for commit_hash in self.commits:
        adjacency[commit_hash] = []

    for commit in self.commits.values():
        for parent in commit.parents:
            adjacency[commit.hash].append(parent)
            adjacency[parent].append(commit.hash)

    return adjacency
```

처음 반복문:

```python
for commit_hash in self.commits:
    adjacency[commit_hash] = []
```

모든 커밋에 대해 빈 연결 목록을 만듭니다.

두 번째 반복문:

```python
adjacency[commit.hash].append(parent)
adjacency[parent].append(commit.hash)
```

여기가 핵심입니다.

원래 저장된 방향은:

```text
commit -> parent
```

하지만 PATH에서는 양쪽 방향을 모두 추가합니다.

```text
commit -> parent
parent -> commit
```

이렇게 하면 BFS가 부모로도, 자식으로도 이동할 수 있습니다.

## 21. 왜 인접 리스트가 필요한가

BFS는 현재 노드에서 갈 수 있는 이웃들을 빠르게 알아야 합니다.

그래서 이런 구조가 필요합니다.

```text
adjacency = {
    "c000001": ["c000002", "c000003"],
    "c000002": ["c000001"],
    "c000003": ["c000001"]
}
```

이 구조를 인접 리스트라고 부릅니다.

인접 리스트는 각 노드 옆에 “바로 갈 수 있는 노드 목록”을 붙여 둔 구조입니다.

```text
c000001 옆에는 c000002, c000003이 있다.
c000002 옆에는 c000001이 있다.
c000003 옆에는 c000001이 있다.
```

그래프 탐색에서는 이웃 목록을 자주 확인하기 때문에 인접 리스트가 유용합니다.

## 22. PATH에서 BFS가 하는 일

`path` 메서드는 큐에 경로 자체를 넣습니다.

```python
queue = deque([[start_hash]])
```

처음에는 시작 커밋만 들어 있는 경로 하나가 있습니다.

```text
queue = [[c000002]]
```

하나를 꺼냅니다.

```python
path = queue.popleft()
current = path[-1]
```

현재 경로의 마지막 커밋을 보고, 그 이웃으로 경로를 확장합니다.

```python
next_path = path + [neighbor]
```

예를 들어:

```text
[c000002] + c000001 = [c000002, c000001]
```

목표 커밋을 만나면 후보 경로에 넣습니다.

```python
if neighbor == end_hash:
    found_depth = next_depth
    found_paths.append(next_path)
```

BFS는 가까운 거리부터 탐색하므로 최단 경로를 찾는 데 적합합니다.

이 코드에서는 최단 경로가 여러 개일 수 있으므로 후보들을 모은 뒤 사전순으로 가장 작은 경로를 고릅니다.

```python
for candidate in found_paths[1:]:
    if compare_paths(candidate, best) < 0:
        best = candidate
```

## 23. 이 문서에서 말하는 DAG는 코드에서 무엇인가

DAG는 추상적인 말처럼 들리지만, Mini Git 코드에서는 다음 조건들의 조합입니다.

```text
Commit은 parents를 가진다.
parents에는 이미 존재하는 커밋 hash가 들어간다.
새 커밋은 기존 HEAD를 부모로 삼는다.
commits 딕셔너리에 새 노드를 추가한다.
브랜치 포인터만 새 노드로 이동한다.
```

이 조건들이 모이면 커밋 그래프는 방향이 있고, 시간이 거꾸로 꼬이지 않으며, 순환이 없는 구조가 됩니다.

## 24. 코드와 연결하기

`mini_git.py`에서 그래프와 연결되는 부분은 다음과 같습니다.

| 코드 | 그래프 개념 |
|---|---|
| `Commit` | 노드 |
| `parents` | 부모 간선 |
| `commits` | 해시로 노드를 찾는 저장소 |
| `branches` | 브랜치 포인터 |
| `current_branch` | HEAD 역할 |
| `_visit_parent_first` | 부모 우선 방문 |
| `_undirected_adjacency` | PATH를 위한 무방향 그래프 변환 |

## 25. 직접 그려 보기

다음 명령을 실행하기 전에 그래프를 먼저 그려 보세요.

```text
init "Alice"
commit "A"
commit "B"
branch feature
switch feature
commit "C"
switch main
commit "D"
```

예상 그래프:

```text
c000001 <- c000002 <- c000003
                \
                 c000004
```

브랜치:

```text
feature -> c000003
main -> c000004
```

이 그림을 스스로 그릴 수 있으면 Git의 핵심 구조를 이해하기 시작한 것입니다.
