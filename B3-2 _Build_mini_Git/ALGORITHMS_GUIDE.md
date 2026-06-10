# Mini Git 알고리즘 가이드

이 문서는 Mini Git에 들어간 알고리즘을 깊게 공부하기 위한 가이드입니다.

목표는 “DFS는 깊이 우선 탐색이다”처럼 짧게 외우는 것이 아닙니다.  
어떤 명령이 어떤 알고리즘 문제로 바뀌는지, 왜 그 알고리즘을 선택했는지, 코드가 실제로 어떤 순서로 움직이는지를 이해하는 것이 목표입니다.

이 문서에서 다루는 핵심 질문은 다음과 같습니다.

```text
커밋을 빠르게 찾으려면 어떤 자료구조가 필요한가?
LOG는 왜 부모를 먼저 방문해야 하는가?
ANCESTORS는 왜 DFS와 잘 맞는가?
PATH는 왜 BFS와 잘 맞는가?
정렬 API 없이 LOG --sort-by를 어떻게 구현하는가?
검색을 빠르게 하려면 왜 역색인이 필요한가?
CLI 입력은 왜 단순 split으로 처리하면 안 되는가?
```

## 1. 알고리즘을 공부한다는 것

알고리즘은 문제를 푸는 절차입니다.  
하지만 코딩 테스트에서만 쓰는 특별한 공식은 아닙니다.

예를 들어 “두 커밋 사이의 가장 짧은 경로를 찾아라”라는 요구사항은 자연스럽게 알고리즘 문제로 바뀝니다.

```text
입력: 시작 커밋, 도착 커밋
데이터: 커밋들이 연결된 그래프
목표: 간선 수가 가장 적은 경로 찾기
알고리즘: BFS
```

“커밋 메시지에서 login이 들어간 커밋을 찾아라”도 알고리즘 문제입니다.

```text
입력: 검색어 login
데이터: 커밋 메시지들
목표: login이 들어간 커밋 목록 찾기
알고리즘/자료구조: 역색인
```

Mini Git은 작은 프로그램이지만, 그 안에는 여러 알고리즘 문제가 들어 있습니다.

## 2. 시간복잡도를 왜 배워야 할까

시간복잡도는 입력이 커질 때 일이 얼마나 늘어나는지 보는 도구입니다.

커밋이 5개일 때는 거의 모든 방법이 빠릅니다. 모든 커밋을 하나씩 훑어도 금방 끝납니다.

하지만 커밋이 100만 개라면 이야기가 달라집니다.

```text
5개를 훑는 것
100만 개를 훑는 것
```

둘 다 “반복문 한 번”처럼 보일 수 있지만 실제 비용은 완전히 다릅니다.

그래서 알고리즘을 볼 때는 다음 질문을 합니다.

```text
입력이 커지면 이 코드는 얼마나 더 많이 일하는가?
```

자주 쓰는 표기:

| 표기 | 뜻 | 직관 |
|---|---|---|
| O(1) | 거의 일정 | 바로 찾기 |
| O(log n) | 매우 천천히 증가 | 반씩 줄이기 |
| O(n) | 입력 크기만큼 증가 | 전체 한 번 훑기 |
| O(n log n) | 좋은 정렬에서 자주 등장 | 나누고 합치기 |
| O(n^2) | 이중 반복에서 자주 등장 | 모든 쌍 비교 |

그래프에서는 보통 `n` 대신 `V`, `E`를 씁니다.

```text
V: vertex 수, 즉 노드 수
E: edge 수, 즉 간선 수
```

Mini Git에서는:

```text
V = 커밋 수
E = 부모 연결 수
```

그래프 전체를 한 번 훑는 알고리즘은 보통:

```text
O(V + E)
```

입니다. 커밋도 보고, 커밋 사이 연결도 보기 때문입니다.

## 3. O(1)을 가능하게 하는 해시맵

Mini Git은 커밋을 다음 구조로 저장합니다.

```text
commits: hash -> Commit
```

예:

```text
commits["c000001"] = Commit(...)
commits["c000002"] = Commit(...)
commits["c000003"] = Commit(...)
```

이 구조는 Python의 `dict`입니다.

```python
self.commits = {}
```

커밋 hash를 알고 있을 때:

```python
self.commits["c000002"]
```

처럼 바로 커밋을 찾을 수 있습니다.

만약 커밋을 리스트에 저장했다면 어떻게 될까요?

```text
[
  Commit(hash="c000001"),
  Commit(hash="c000002"),
  Commit(hash="c000003")
]
```

`c000003`을 찾으려면 앞에서부터 확인해야 합니다.

```text
c000001인가? 아니다.
c000002인가? 아니다.
c000003인가? 맞다.
```

커밋이 많아질수록 느려집니다. 이 방식은 최악의 경우 `O(n)`입니다.

반면 딕셔너리는 평균적으로 `O(1)`에 가깝게 찾습니다.

물론 엄밀히 말해 해시 충돌 같은 개념이 있어서 항상 완벽한 O(1)은 아닙니다. 하지만 일반적인 상황에서는 매우 빠른 조회를 기대할 수 있습니다.

Mini Git의 여러 명령은 커밋 hash를 입력으로 받습니다.

```text
PATH <commit1> <commit2>
ANCESTORS <commit_hash>
```

이때 `commits` 딕셔너리가 없으면 매번 커밋을 찾는 데 많은 시간이 듭니다. 그래서 hash 기반 저장소는 Mini Git의 기본 뼈대입니다.

## 4. DFS란 무엇인가

DFS는 Depth First Search, 깊이 우선 탐색입니다.

말 그대로 깊게 들어가는 탐색입니다.

```text
한 방향으로 갈 수 있을 만큼 간다.
더 갈 곳이 없으면 돌아온다.
다른 길을 다시 탐색한다.
```

예를 들어 다음 그래프가 있다고 합시다.

```text
        A
       / \
      B   C
     /
    D
```

DFS는 보통 이런 식으로 움직입니다.

```text
A -> B -> D
돌아옴
A -> C
```

중요한 것은 “가까운 것부터 골고루”가 아니라 “한 길을 깊게”라는 점입니다.

Mini Git에서 DFS가 잘 맞는 명령은 다음입니다.

```text
ANCESTORS
LOG
```

둘 다 부모를 계속 따라가야 하기 때문입니다.

## 5. 재귀 DFS와 스택 DFS

DFS는 보통 두 가지 방식으로 구현합니다.

```text
1. 재귀 함수 사용
2. 명시적인 stack 사용
```

재귀 방식:

```text
visit(node):
    for next in node.neighbors:
        visit(next)
```

스택 방식:

```text
stack = [start]

while stack:
    node = stack.pop()
    다음 노드들을 stack에 넣는다
```

Mini Git은 둘 다 사용합니다.

```text
LOG        -> 재귀 DFS
ANCESTORS  -> 스택 DFS
```

둘의 본질은 같습니다.  
다만 재귀 DFS는 함수 호출 스택을 사용하고, 스택 DFS는 우리가 직접 만든 리스트를 스택처럼 사용합니다.

## 6. ANCESTORS 문제 정의

명령:

```text
ANCESTORS <commit_hash>
```

문제를 알고리즘 언어로 바꾸면:

```text
방향 그래프에서 특정 노드로부터 부모 방향으로 도달 가능한 모든 노드를 찾아라.
```

예:

```text
c000001 <- c000002 <- c000003
```

`ANCESTORS c000003`의 답:

```text
c000002
c000001
```

브랜치가 갈라진 그래프에서도 같습니다.

```text
          c000003
         /
c000001 <- c000002
         \
          c000004
```

어떤 커밋의 조상은 “부모를 따라가서 도달할 수 있는 모든 커밋”입니다.

## 7. ANCESTORS 코드 뜯어보기

`mini_git.py`의 핵심 코드는 다음과 같습니다.

```python
result = []
visited = set()
stack = self.commits[commit_hash].parents[:]
```

세 자료구조가 등장합니다.

```text
result: 최종 조상 목록
visited: 이미 방문한 커밋 집합
stack: 앞으로 방문할 커밋 후보
```

처음에는 시작 커밋 자체가 아니라 시작 커밋의 부모들을 stack에 넣습니다.

```python
stack = self.commits[commit_hash].parents[:]
```

왜 시작 커밋 자체를 넣지 않을까요?

`ANCESTORS c000003`에서 `c000003`은 자기 자신의 조상이 아닙니다. 조상은 부모부터 시작합니다.

반복문:

```python
while stack:
    current = stack.pop()
```

스택에서 하나를 꺼냅니다. `pop()`은 리스트의 마지막 원소를 꺼내므로 후입선출 구조입니다.

```python
if current in visited:
    continue
```

이미 방문했다면 넘어갑니다. 이 줄이 없으면 같은 조상을 여러 번 결과에 넣을 수 있습니다.

```python
visited.add(current)
result.append(current)
```

현재 커밋을 방문 처리하고 결과에 추가합니다.

```python
for parent in self.commits[current].parents:
    if parent not in visited:
        stack.append(parent)
```

현재 커밋의 부모들을 다음 방문 후보로 넣습니다.

전체 흐름:

```text
부모를 꺼낸다
방문한다
그 부모의 부모를 넣는다
반복한다
```

## 8. visited가 왜 필요한가

단순한 선형 그래프에서는 `visited`가 없어도 문제가 없어 보입니다.

```text
c000001 <- c000002 <- c000003
```

하지만 부모가 여러 개인 merge commit을 생각해 봅시다. Mini Git 기본 요구사항에는 merge가 필수는 아니지만, 커밋 노드는 “0개 이상의 부모”를 가질 수 있습니다.

```text
      c000002
     /       \
c000001     c000004
     \       /
      c000003
```

어떤 커밋이 두 부모를 가지고 있고, 그 부모들이 같은 조상을 공유하면 같은 커밋을 여러 경로로 만날 수 있습니다.

`visited`가 없다면:

```text
c000001을 첫 번째 경로에서 방문
c000001을 두 번째 경로에서 또 방문
```

이런 중복이 생깁니다.

더 일반적인 그래프에서는 사이클이 있을 때 무한 반복을 막는 역할도 합니다. Git 커밋 그래프는 DAG라 사이클이 없어야 하지만, 그래프 탐색에서는 `visited`를 두는 습관이 안전합니다.

## 9. ANCESTORS 시간복잡도

DFS는 방문 가능한 노드와 간선을 한 번씩 살펴봅니다.

따라서 시간복잡도는:

```text
O(V + E)
```

입니다.

하지만 정확히는 전체 커밋 수가 아니라 “해당 커밋에서 조상 방향으로 도달 가능한 커밋 수”에 비례합니다.

예를 들어 전체 커밋이 10만 개라도, 어떤 커밋의 조상이 3개뿐이라면 실제 탐색은 그 주변만 봅니다.

공간복잡도는:

```text
O(V)
```

입니다. `visited`, `stack`, `result`가 방문한 커밋 수만큼 커질 수 있기 때문입니다.

## 10. LOG 문제 정의

명령:

```text
LOG
```

미션의 요구사항:

```text
부모 커밋이 항상 자식 커밋보다 먼저 출력되어야 한다.
```

이것은 단순히 “오래된 순서대로 정렬”과는 다릅니다.

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

둘 다 괜찮습니다. 핵심은 `c000001`이 자식들보다 먼저 나오는 것입니다.

이 문제는 위상 정렬과 닮았습니다.

## 11. 위상 정렬 감각

위상 정렬은 “먼저 해야 하는 일이 앞에 오도록 나열하는 것”입니다.

예를 들어:

```text
양말을 신은 뒤 신발을 신는다.
반죽을 만든 뒤 빵을 굽는다.
부모 커밋이 있어야 자식 커밋을 이해할 수 있다.
```

관계가 이렇게 있을 때:

```text
A가 B보다 먼저 와야 한다.
B가 C보다 먼저 와야 한다.
```

가능한 순서는:

```text
A, B, C
```

입니다.

커밋 그래프에서도 마찬가지입니다.

```text
부모 -> 자식
```

이라는 의존 관계로 보면 부모가 먼저 와야 합니다.

Mini Git의 `LOG`는 일반적인 위상 정렬 알고리즘을 완전하게 구현한 것은 아니지만, DAG에서 부모를 먼저 방문하는 DFS로 요구사항을 만족합니다.

## 12. LOG 코드 뜯어보기

먼저 전체 커밋을 순회합니다.

```python
def _all_commits_parent_first(self) -> list[Commit]:
    visited = set()
    result = []

    for commit_hash in self.commits:
        self._visit_parent_first(commit_hash, visited, result)

    return result
```

`self.commits`에 있는 모든 커밋에 대해 `_visit_parent_first`를 호출합니다.

그런데 이미 방문한 커밋은 다시 처리하지 않습니다.

핵심 함수:

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

순서:

```text
1. 이미 방문했으면 종료
2. 현재 커밋을 가져옴
3. 부모들을 먼저 방문
4. 부모 방문이 끝난 뒤 현재 커밋을 결과에 추가
```

중요한 줄:

```python
for parent_hash in commit.parents:
    self._visit_parent_first(parent_hash, visited, result)
```

이 줄 때문에 부모가 먼저 처리됩니다.

그리고:

```python
result.append(commit)
```

이 줄이 부모 방문 뒤에 있기 때문에 현재 커밋은 부모보다 나중에 출력됩니다.

## 13. LOG를 손으로 따라가기

그래프:

```text
c000001 <- c000002 <- c000003
```

`_visit_parent_first("c000003")`를 호출한다고 합시다.

```text
visit(c000003)
  parent c000002 방문
    visit(c000002)
      parent c000001 방문
        visit(c000001)
          부모 없음
          result에 c000001 추가
      result에 c000002 추가
  result에 c000003 추가
```

결과:

```text
c000001
c000002
c000003
```

이 흐름은 “내 일을 하기 전에 부모 일을 먼저 끝낸다”는 구조입니다.

## 14. BFS란 무엇인가

BFS는 Breadth First Search, 너비 우선 탐색입니다.

DFS가 한 길을 깊게 들어간다면, BFS는 가까운 곳부터 차례대로 퍼집니다.

예를 들어:

```text
        A
       / \
      B   C
     /
    D
```

BFS 순서는 보통:

```text
A
B, C
D
```

입니다.

거리 기준으로 보면:

```text
거리 0: A
거리 1: B, C
거리 2: D
```

이 성질 때문에 BFS는 간선 비용이 모두 같을 때 최단 경로를 찾는 데 적합합니다.

## 15. BFS가 최단 경로를 보장하는 이유

BFS는 큐를 사용합니다.

큐는 먼저 들어온 것이 먼저 나갑니다.

```text
enqueue: 뒤에 넣기
dequeue: 앞에서 꺼내기
```

BFS는 시작점에서 가까운 노드를 먼저 큐에 넣고, 그다음 거리의 노드를 넣습니다.

그래서 큐에서 꺼내는 순서는 거리 순서가 됩니다.

```text
거리 0 노드들
거리 1 노드들
거리 2 노드들
거리 3 노드들
```

따라서 어떤 목표 노드를 처음 만났을 때, 그 경로는 최단 거리입니다.

Mini Git은 같은 최단 거리의 경로가 여러 개일 수 있어서 후보들을 비교하는 로직을 추가로 둡니다.

## 16. PATH 문제 정의

명령:

```text
PATH <commit1> <commit2>
```

미션 요구사항:

```text
커밋-부모 연결을 무방향 간선으로 간주했을 때 최단 경로를 찾는다.
```

기본 커밋 그래프는 방향이 있습니다.

```text
c000002 -> c000001
c000003 -> c000001
```

하지만 PATH에서는 이렇게 봅니다.

```text
c000002 <-> c000001 <-> c000003
```

이제 `c000002`에서 `c000003`으로 가는 경로는:

```text
c000002 -> c000001 -> c000003
```

입니다.

## 17. 무방향 인접 리스트 만들기

Mini Git은 먼저 부모 관계를 무방향 인접 리스트로 바꿉니다.

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

처음 부분:

```python
adjacency[commit_hash] = []
```

모든 커밋에 빈 이웃 목록을 만듭니다.

핵심:

```python
adjacency[commit.hash].append(parent)
adjacency[parent].append(commit.hash)
```

원래 관계는:

```text
commit -> parent
```

입니다.

하지만 무방향으로 보려면 양쪽을 모두 추가해야 합니다.

```text
commit -> parent
parent -> commit
```

예:

```text
c000002.parents = [c000001]
c000003.parents = [c000001]
```

인접 리스트:

```text
c000001: [c000002, c000003]
c000002: [c000001]
c000003: [c000001]
```

## 18. PATH 코드 뜯어보기

초기화:

```python
adjacency = self._undirected_adjacency()
queue = deque([[start_hash]])
best_depth_by_hash = {start_hash: 0}
found_paths = []
found_depth = None
```

각 변수의 의미:

```text
adjacency: 무방향 그래프
queue: 앞으로 확장할 경로들
best_depth_by_hash: 각 커밋을 몇 간선 거리에서 만났는지
found_paths: 찾은 최단 경로 후보들
found_depth: 현재까지 찾은 최단 거리
```

왜 큐에 커밋 하나가 아니라 “경로 리스트”를 넣을까요?

```python
queue = deque([[start_hash]])
```

최종 출력이 경로 전체이기 때문입니다.

```text
Path: c000002 -> c000001 -> c000003
```

경로를 복원하려면 부모 포인터를 따로 저장하는 방식도 있지만, 이 구현은 학습 목적상 경로 자체를 큐에 넣어 흐름을 보기 쉽게 했습니다.

반복문:

```python
path = queue.popleft()
current = path[-1]
depth = len(path) - 1
```

큐에서 경로 하나를 꺼내고, 그 경로의 마지막 커밋을 현재 위치로 봅니다.

예:

```text
path = [c000002, c000001]
current = c000001
depth = 1
```

이웃 순회:

```python
neighbors = merge_sort(adjacency.get(current, []), compare_strings)
for neighbor in neighbors:
```

이웃을 hash 사전순으로 정렬합니다. 최단 경로가 여러 개일 때 사전순 tie-breaking을 다루기 쉽게 하기 위한 선택입니다.

경로 확장:

```python
next_path = path + [neighbor]
next_depth = depth + 1
```

예:

```text
[c000002, c000001] + c000003
= [c000002, c000001, c000003]
```

목표를 찾으면:

```python
if neighbor == end_hash:
    found_depth = next_depth
    found_paths.append(next_path)
    continue
```

찾은 경로를 후보에 넣습니다.

탐색이 끝난 뒤:

```python
best = found_paths[0]
for candidate in found_paths[1:]:
    if compare_paths(candidate, best) < 0:
        best = candidate
```

최단 경로 후보들 중 문자열 기준으로 가장 작은 경로를 선택합니다.

## 19. PATH를 손으로 따라가기

그래프:

```text
          c000002
         /
c000001
         \
          c000003
```

명령:

```text
PATH c000002 c000003
```

무방향 인접 리스트:

```text
c000001: [c000002, c000003]
c000002: [c000001]
c000003: [c000001]
```

초기 큐:

```text
[[c000002]]
```

1단계:

```text
꺼냄: [c000002]
현재: c000002
이웃: c000001
추가: [c000002, c000001]
```

큐:

```text
[[c000002, c000001]]
```

2단계:

```text
꺼냄: [c000002, c000001]
현재: c000001
이웃: c000002, c000003
c000002는 이미 경로에 있으므로 제외
c000003은 목표
```

찾은 경로:

```text
[c000002, c000001, c000003]
```

출력:

```text
Path: c000002 -> c000001 -> c000003
```

## 20. 사전순 tie-breaking

미션은 최단 경로가 여러 개라면 다음 기준으로 하나를 고르라고 합니다.

```text
경로를 hash1->hash2->... 문자열로 만들었을 때 사전순으로 가장 작은 경로
```

예:

```text
c000001->c000002->c000005
c000001->c000003->c000005
```

두 경로의 길이가 같다면 문자열 비교를 합니다.

```text
c000002가 c000003보다 앞선다.
따라서 첫 번째 경로가 선택된다.
```

Mini Git은 `compare_paths`로 이 비교를 합니다.

```python
def compare_paths(a: list[str], b: list[str]) -> int:
    return compare_strings("->".join(a), "->".join(b))
```

이 조건은 프로그램 결과를 예측 가능하게 만듭니다.

## 21. merge sort가 필요한 이유

미션 조건:

```text
Python 표준 정렬 API 사용 금지
sorted(), list.sort() 금지
```

하지만 Mini Git은 정렬이 필요합니다.

```text
LOG --sort-by=date
LOG --sort-by=author
조상 목록 정렬
브랜치 이름 정렬
PATH 이웃 정렬
```

그래서 직접 정렬 알고리즘을 구현해야 합니다.

Mini Git은 merge sort를 선택했습니다.

왜 merge sort가 좋은 선택일까요?

```text
평균 O(n log n)
최악 O(n log n)
안정 정렬로 구현 가능
비교 함수를 바꿔 재사용 가능
```

## 22. merge sort의 핵심 아이디어

merge sort는 분할 정복 알고리즘입니다.

분할 정복은 큰 문제를 작은 문제로 나누고, 작은 문제의 답을 합쳐 큰 문제의 답을 만드는 방식입니다.

merge sort의 절차:

```text
1. 리스트를 반으로 나눈다.
2. 왼쪽 리스트를 정렬한다.
3. 오른쪽 리스트를 정렬한다.
4. 정렬된 두 리스트를 합친다.
```

예:

```text
[5, 2, 4, 1]
```

분할:

```text
[5, 2]        [4, 1]
[5] [2]       [4] [1]
```

합치기:

```text
[2, 5]        [1, 4]
[1, 2, 4, 5]
```

중요한 점은 “합칠 때 정렬된다”는 것입니다.

하나짜리 리스트는 이미 정렬되어 있습니다. 그래서 하나짜리 리스트들을 차례로 합치면 전체 정렬이 됩니다.

## 23. merge_sort 코드 뜯어보기

```python
def merge_sort(items, compare):
    length = len(items)
    if length <= 1:
        return items[:]

    mid = length // 2
    left = merge_sort(items[:mid], compare)
    right = merge_sort(items[mid:], compare)
    return merge(left, right, compare)
```

기저 조건:

```python
if length <= 1:
    return items[:]
```

원소가 0개 또는 1개인 리스트는 이미 정렬되어 있습니다.

분할:

```python
mid = length // 2
left = merge_sort(items[:mid], compare)
right = merge_sort(items[mid:], compare)
```

왼쪽과 오른쪽을 각각 재귀적으로 정렬합니다.

결합:

```python
return merge(left, right, compare)
```

정렬된 두 리스트를 합칩니다.

## 24. merge 코드 뜯어보기

```python
def merge(left, right, compare):
    result = []
    left_i = 0
    right_i = 0
```

`left_i`, `right_i`는 각각 왼쪽/오른쪽 리스트에서 현재 보고 있는 위치입니다.

```python
while left_i < len(left) and right_i < len(right):
    if compare(left[left_i], right[right_i]) <= 0:
        result.append(left[left_i])
        left_i += 1
    else:
        result.append(right[right_i])
        right_i += 1
```

왼쪽의 현재 원소와 오른쪽의 현재 원소를 비교해서 더 앞에 와야 할 것을 결과에 넣습니다.

여기서 `<= 0`이 중요합니다.

```python
if compare(left[left_i], right[right_i]) <= 0:
```

두 원소가 같다고 판단되면 왼쪽 원소를 먼저 넣습니다. 그래서 안정 정렬이 됩니다.

남은 원소 붙이기:

```python
while left_i < len(left):
    result.append(left[left_i])
    left_i += 1

while right_i < len(right):
    result.append(right[right_i])
    right_i += 1
```

한쪽 리스트가 먼저 끝나면 다른 쪽에 남은 원소들은 이미 정렬되어 있으므로 그대로 붙입니다.

## 25. 안정 정렬

안정 정렬은 비교 기준이 같은 원소들의 기존 상대 순서를 유지하는 정렬입니다.

예:

```text
c000001 Alice
c000002 Bob
c000003 Alice
```

작성자 기준으로 정렬하면 Alice 커밋 두 개가 같은 그룹에 들어갑니다.

안정 정렬이라면 원래 `c000001`이 `c000003`보다 앞에 있었으므로 그 순서를 유지합니다.

```text
c000001 Alice
c000003 Alice
c000002 Bob
```

Mini Git의 merge sort는 같은 값일 때 왼쪽 원소를 먼저 넣으므로 안정 정렬입니다.

## 26. 비교 함수로 정렬 기준 바꾸기

정렬 알고리즘은 하나지만 기준은 여러 개입니다.

Mini Git은 비교 함수를 바꿔서 정렬 기준을 바꿉니다.

날짜 기준:

```python
def _compare_by_date(self, a: Commit, b: Commit) -> int:
    if a.timestamp < b.timestamp:
        return -1
    if a.timestamp > b.timestamp:
        return 1
    return compare_strings(a.hash, b.hash)
```

작성자 기준:

```python
def _compare_by_author(self, a: Commit, b: Commit) -> int:
    author_cmp = compare_strings(a.author.lower(), b.author.lower())
    if author_cmp != 0:
        return author_cmp
    return self._compare_by_date(a, b)
```

이 설계의 장점:

```text
merge_sort는 정렬 방법만 담당한다.
compare 함수는 정렬 기준만 담당한다.
정렬 방법과 기준이 분리된다.
```

이런 분리는 코드를 읽기 좋게 만들고 재사용성을 높입니다.

## 27. merge sort 시간복잡도

merge sort는 매번 리스트를 반으로 나눕니다.

나누는 깊이는:

```text
log n
```

각 깊이마다 모든 원소를 한 번씩 merge합니다.

```text
n
```

그래서 전체 시간복잡도는:

```text
O(n log n)
```

입니다.

최악의 경우에도 반으로 나누고 전체를 merge하므로:

```text
최악 O(n log n)
```

입니다.

공간복잡도는 새 리스트를 만들어 합치므로:

```text
O(n)
```

입니다.

## 28. 역색인이 필요한 이유

검색을 가장 단순하게 만들면 모든 커밋을 검사합니다.

```text
모든 커밋을 하나씩 본다.
각 메시지에 login이 있는지 확인한다.
있으면 결과에 넣는다.
```

커밋이 10개라면 괜찮습니다.

하지만 커밋이 100만 개라면 검색 한 번마다 100만 개를 검사해야 합니다.

그래서 검색 시스템은 보통 “미리 찾기 좋은 형태로 정리”해 둡니다. 이것이 인덱스입니다.

역색인은 데이터를 뒤집어 저장합니다.

일반 저장:

```text
c000002 -> "Add login feature"
c000003 -> "Fix login bug"
```

역색인:

```text
login -> [c000002, c000003]
feature -> [c000002]
bug -> [c000003]
```

이제 `login` 검색은 모든 커밋 순회가 아니라 딕셔너리 조회가 됩니다.

## 29. InvertedIndex 코드 뜯어보기

초기 구조:

```python
self.keyword_to_hashes = {}
self.author_to_hashes = {}
```

두 인덱스가 있습니다.

```text
keyword_to_hashes: 메시지 단어 -> 커밋 hash 목록
author_to_hashes: 작성자 -> 커밋 hash 목록
```

커밋 추가:

```python
def add_commit(self, commit: Commit):
    author_key = normalize_token(commit.author)
    self._append_unique(self.author_to_hashes, author_key, commit.hash)
```

작성자를 소문자로 정규화해서 작성자 인덱스에 추가합니다.

메시지 토큰화:

```python
seen_tokens = set()
for raw_token in commit.message.split():
    token = normalize_token(raw_token)
    if token and token not in seen_tokens:
        self._append_unique(self.keyword_to_hashes, token, commit.hash)
        seen_tokens.add(token)
```

여기서 하는 일:

```text
1. 메시지를 공백 기준으로 나눈다.
2. 각 토큰을 소문자로 바꾼다.
3. 같은 커밋 안에서 같은 토큰이 중복 등록되지 않게 한다.
4. token -> commit hash 목록에 추가한다.
```

예:

```text
message = "Fix login login bug"
```

단순히 모두 넣으면:

```text
login -> [c000004, c000004]
```

처럼 같은 커밋이 중복될 수 있습니다.

그래서 `seen_tokens`를 사용합니다.

## 30. 검색 코드 뜯어보기

키워드 검색:

```python
def search_keyword(self, keyword: str) -> list[str]:
    tokens = []
    seen_tokens = set()
    for raw_token in keyword.split():
        token = normalize_token(raw_token)
        if token and token not in seen_tokens:
            tokens.append(token)
            seen_tokens.add(token)
```

검색어도 메시지와 같은 방식으로 토큰화합니다.

검색어가:

```text
login feature
```

라면:

```text
tokens = ["login", "feature"]
```

첫 번째 토큰 후보:

```python
candidates = self.keyword_to_hashes.get(tokens[0], [])[:]
```

`login`이 들어간 커밋 목록을 가져옵니다.

다음 토큰들과 교집합:

```python
for token in tokens[1:]:
    token_hashes = set(self.keyword_to_hashes.get(token, []))
    filtered = []
    for commit_hash in candidates:
        if commit_hash in token_hashes:
            filtered.append(commit_hash)
    candidates = filtered
```

이 코드는 여러 단어 검색을 “모든 단어를 포함하는 커밋”으로 처리합니다.

예:

```text
login -> [c000002, c000003]
feature -> [c000002]
```

`login feature` 검색 결과:

```text
[c000002]
```

작성자 검색:

```python
def search_author(self, author: str) -> list[str]:
    return self.author_to_hashes.get(normalize_token(author), [])[:]
```

작성자 인덱스는 바로 조회합니다.

## 31. 역색인 시간복잡도

순회 검색은 매번 모든 커밋을 봅니다.

```text
O(커밋 수 * 메시지 검사 비용)
```

역색인 검색은 보통 다음 비용이 듭니다.

```text
O(검색어 토큰 수 + 후보 결과 수)
```

딕셔너리 조회 자체는 평균적으로 빠릅니다.

다만 역색인은 공짜가 아닙니다.

커밋을 만들 때마다 인덱스를 갱신해야 합니다.

```text
커밋 생성 비용이 조금 늘어난다.
검색 비용이 크게 줄어든다.
```

검색을 자주 하는 시스템에서는 이 교환이 매우 유리합니다.

검색 엔진, 데이터베이스 인덱스, IDE의 심볼 검색도 같은 아이디어와 연결됩니다.

## 32. CLI 파싱도 알고리즘 문제다

사용자 입력:

```text
commit "Add login feature"
```

이 입력을 단순히 공백으로 나누면:

```text
commit
"Add
login
feature"
```

이렇게 깨집니다.

우리가 원하는 결과는:

```text
command = commit
args = ["Add login feature"]
```

입니다.

그래서 Mini Git은 `shlex.split()`을 사용합니다.

```python
parts = shlex.split(line)
```

`shlex`는 shell-like syntax를 다루는 도구입니다. 따옴표로 감싼 문자열을 하나의 인자로 처리해 줍니다.

그 다음:

```python
command = parts[0].lower()
args = parts[1:]
```

명령어는 소문자로 바꿔 대소문자를 구분하지 않게 합니다.

## 33. 명령어별 알고리즘 지도

| 명령 | 문제로 바꾸면 | 사용한 구조/알고리즘 |
|---|---|---|
| INIT | 저장소 상태 초기화 | dict 초기화 |
| COMMIT | 새 노드 추가 | hash 생성, 부모 연결, 인덱스 갱신 |
| BRANCH | 현재 커밋에 이름 붙이기 | branch dict |
| SWITCH | 현재 브랜치 변경 | current_branch 변경 |
| LOG | 부모가 먼저 오게 출력 | DFS, 위상 정렬 감각 |
| LOG --sort-by=date | 날짜 기준 정렬 | merge sort |
| LOG --sort-by=author | 작성자 기준 정렬 | merge sort + compare 함수 |
| ANCESTORS | 부모 방향 도달 가능 노드 찾기 | DFS |
| PATH | 무방향 최단 경로 찾기 | 인접 리스트 + BFS |
| SEARCH | 검색 후보 빠르게 찾기 | 역색인 |

## 34. 전체 흐름으로 다시 보기

커밋을 만들면:

```text
1. 새 hash를 만든다.
2. 현재 HEAD를 부모로 기록한다.
3. commits 딕셔너리에 Commit을 저장한다.
4. 현재 브랜치 포인터를 새 커밋으로 옮긴다.
5. 메시지와 작성자를 역색인에 등록한다.
```

로그를 보면:

```text
1. 모든 커밋을 대상으로 DFS를 시작한다.
2. 각 커밋의 부모를 먼저 방문한다.
3. 부모 방문이 끝난 뒤 현재 커밋을 결과에 넣는다.
```

경로를 찾으면:

```text
1. 부모 관계를 무방향 인접 리스트로 바꾼다.
2. 시작 커밋에서 BFS를 시작한다.
3. 경로를 하나씩 확장한다.
4. 목표에 도달한 최단 후보를 모은다.
5. 사전순으로 가장 작은 경로를 고른다.
```

검색하면:

```text
1. 검색어를 소문자 토큰으로 만든다.
2. 역색인에서 후보 커밋 목록을 가져온다.
3. 여러 토큰이면 후보 목록의 교집합을 구한다.
4. 결과 커밋을 출력한다.
```

## 35. 공부 체크리스트

다음 질문에 답할 수 있으면 Mini Git의 알고리즘 핵심을 이해한 것입니다.

```text
왜 commits는 list가 아니라 dict인가?
DFS와 BFS의 차이는 무엇인가?
ANCESTORS는 왜 DFS와 잘 맞는가?
LOG는 왜 부모를 먼저 방문해야 하는가?
부모 우선 LOG가 위상 정렬과 닮은 이유는 무엇인가?
PATH에서 왜 방향 그래프를 무방향 그래프로 바꾸는가?
BFS가 최단 경로를 보장하는 이유는 무엇인가?
최단 경로가 여러 개일 때 사전순 tie-breaking은 어떻게 처리하는가?
merge sort는 왜 O(n log n)인가?
안정 정렬은 무엇이고 Mini Git에서는 어떻게 보장하는가?
비교 함수 분리는 왜 좋은 설계인가?
역색인은 왜 전체 순회 검색보다 빠른가?
인덱스를 만들면 어떤 비용을 추가로 내는가?
shlex.split()이 필요한 이유는 무엇인가?
```

## 36. 직접 실험 과제

다음 명령을 실행하기 전에 결과를 먼저 예상해 보세요.

```text
init "Alice"
commit "A"
commit "B"
branch feature
switch feature
commit "C login"
switch main
commit "D login"
log
path c000003 c000004
ancestors c000004
search login
log --sort-by=author
```

예상해야 할 것:

```text
그래프 모양
각 브랜치가 가리키는 커밋
LOG 출력에서 부모가 먼저 나오는지
PATH가 어느 커밋을 거쳐 가는지
ANCESTORS 결과가 무엇인지
SEARCH login 결과가 몇 개인지
```

이 과제의 핵심은 맞히는 것이 아니라, 실행 전에 머릿속으로 자료구조가 어떻게 변하는지 그려 보는 것입니다.
