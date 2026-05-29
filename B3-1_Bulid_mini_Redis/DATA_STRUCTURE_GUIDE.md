# 자료구조 가이드

## 1. 이 문서의 목표

이 문서는 자료구조를 단순히 복습하기 위한 문서가 아니다. 처음 배우는 사람이 “왜 이런 구조가 필요한가”를 이해하도록 돕는 문서다.

Mini Redis에서 사용하는 핵심 자료구조는 세 가지다.

```text
해시맵              키로 값을 빠르게 찾기 위해 사용
이중 연결 리스트     최근 사용 순서를 빠르게 바꾸기 위해 사용
최소 힙             가장 빨리 만료될 키를 빠르게 찾기 위해 사용
```

전체 그림으로 보면 다음과 같다.

```text
                    Mini Redis
                         │
       ┌─────────────────┼──────────────────┐
       │                 │                  │
       ▼                 ▼                  ▼
    HashMap       DoublyLinkedList       MinHeap
  key -> value      최근 사용 순서       만료 시간 순서
       │                 │                  │
       ▼                 ▼                  ▼
  GET/SET/DEL         LRU 제거            TTL 만료
```

자료구조는 외워야 할 이름이 아니다. 문제를 해결하기 위한 도구다. 그래서 각 장은 다음 순서로 설명한다.

```text
어떤 문제가 있는가
단순한 해결은 왜 부족한가
이 자료구조는 어떻게 생겼는가
Mini Redis에서는 어떤 이점이 있는가
```

## 2. 해시맵

### 2.1 우리가 풀고 싶은 문제

Mini Redis는 키로 값을 찾는다.

```text
GET user:1
GET session:abc
TTL token:7
```

가장 단순한 방법은 모든 데이터를 순서대로 저장하고, 찾을 때마다 처음부터 비교하는 것이다.

```text
[user:1, Alice]
[user:2, Bob]
[user:3, Charlie]
```

`user:3`을 찾는다면 이렇게 된다.

```text
user:1인가? 아니오
user:2인가? 아니오
user:3인가? 예
```

데이터가 3개라면 괜찮다. 하지만 데이터가 100만 개라면 매번 처음부터 찾는 방식은 느리다. 시간 복잡도는 O(N)이다.

해시맵은 이 질문에서 출발한다.

```text
키를 이용해서 저장 위치로 바로 갈 수는 없을까?
```

그림으로 비교하면 차이가 더 분명하다.

```text
선형 탐색

GET user:3
   │
   ▼
[user:1] -> [user:2] -> [user:3]
   X          X          O

앞에서부터 하나씩 확인한다.
데이터가 많아질수록 오래 걸린다.
```

```text
해시맵 탐색

GET user:3
   │
   ▼
hash("user:3") % bucket_count
   │
   ▼
bucket[1] -> [user:3]

목적지에 가까운 위치로 바로 이동한다.
```

### 2.2 해시 함수

해시 함수는 키를 숫자로 바꾸는 규칙이다.

```text
"user:1" -> 어떤 숫자
"user:2" -> 또 다른 숫자
```

이 프로젝트의 해시 함수는 `hash_map.py`에 있다.

```python
def _hash(self, key):
    text = str(key)
    hash_value = 5381
    for char in text:
        hash_value = ((hash_value * 33) + ord(char)) % 2147483647
    return hash_value
```

`ord(char)`는 글자를 숫자로 바꾼다. 그리고 이전 결과에 33을 곱한 뒤 새 글자 값을 더한다. 이렇게 하면 글자의 종류와 순서가 모두 결과에 영향을 준다.

해시 함수의 목표는 키를 가능한 한 고르게 흩뿌리는 것이다. 모든 키가 같은 위치로 몰리면 해시맵의 장점이 사라진다.

해시 함수의 흐름을 눈으로 보면 다음과 같다.

```text
key: "user:1"

   u        s        e        r        :        1
   │        │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼        ▼
 ord()    ord()    ord()    ord()    ord()    ord()
   │        │        │        │        │        │
   └──────────── hash_value를 계속 갱신 ───────────┘
                            │
                            ▼
                     큰 정수 hash 값
```

여기서 중요한 것은 “글자를 숫자로 바꾸고, 누적 계산한다”는 점이다. 문자열 전체를 하나의 위치 번호로 바꾸기 위한 과정이다.

### 2.3 버킷

해시 함수가 만든 숫자는 매우 클 수 있다. 그래서 버킷 개수로 나눈 나머지를 사용해 실제 저장 위치를 정한다.

```python
def _bucket_index(self, key):
    return self._hash(key) % self.capacity
```

버킷이 8개라면 위치는 0부터 7까지다.

```text
hash("user:1") % 8 = 5
hash("user:2") % 8 = 6
```

그러면 `user:1`은 5번 버킷, `user:2`는 6번 버킷에 저장된다.

버킷 배열을 그림으로 보면 다음과 같다.

```text
capacity = 8

index  bucket
  0    empty
  1    empty
  2    empty
  3    empty
  4    empty
  5    [user:1, Alice]
  6    [user:2, Bob]
  7    [user:3, Charlie]
```

키를 찾을 때는 먼저 인덱스를 계산하고, 해당 버킷만 본다.

### 2.4 충돌과 체이닝

문제는 서로 다른 키가 같은 버킷으로 갈 수 있다는 점이다.

```text
hash("user:1") % 8 = 5
hash("cart:7") % 8 = 5
```

이것을 충돌이라고 한다.

이 프로젝트는 체이닝 방식으로 충돌을 해결한다. 같은 버킷에 들어온 데이터들을 연결 리스트로 이어 붙인다.

```text
bucket[5] -> [user:1, Alice] <-> [cart:7, Book]
```

조금 더 넓게 그리면 이런 모습이다.

```text
buckets

index  bucket
  0    empty
  1    empty
  2    empty
  3    empty
  4    empty
  5    [user:1, Alice] <-> [cart:7, Book]
  6    [user:2, Bob]
  7    [user:3, Charlie] <-> [cart:9, Pen]
```

5번과 7번 버킷에서는 충돌이 일어났다. 하지만 데이터를 덮어쓰지 않고, 연결 리스트에 차례로 붙여 모두 보관한다.

`GET cart:7`이 들어오면 전체 버킷을 보지 않는다. 5번 버킷으로 간 뒤, 그 안에서만 찾는다.

```text
GET cart:7
   │
   ▼
bucket[5]
   │
   ▼
[user:1] <-> [cart:7]
   X           O
```

그래서 `HashMap`의 각 버킷은 `DoublyLinkedList`다.

```python
def _make_buckets(self, capacity):
    buckets = []
    for _ in range(capacity):
        buckets.append(DoublyLinkedList())
    return buckets
```

### 2.5 put, get, remove

`put`은 키가 이미 있으면 값을 덮어쓰고, 없으면 새 항목을 추가한다.

```python
node = self._find_node(key)
if node is not None:
    node.data.value = value
    return
```

키가 없다면 버킷 위치를 계산하고, 해당 버킷의 리스트 뒤에 새 항목을 붙인다.

```python
index = self._bucket_index(key)
self.buckets[index].insert_back(HashEntry(key, value))
```

`get`은 버킷 위치를 계산한 뒤 그 버킷 안에서만 키를 찾는다. 전체 데이터를 모두 훑지 않는 것이 핵심이다.

`remove`도 같은 방식이다. 버킷 안에서 키를 찾고, 찾으면 연결 리스트에서 해당 노드를 제거한다.

### 2.6 로드 팩터와 리사이징

데이터가 많아지면 충돌도 많아진다. 충돌이 많아지면 한 버킷 안의 연결 리스트가 길어진다. 그러면 해시맵이 점점 느려진다.

그래서 해시맵은 로드 팩터를 본다.

```text
로드 팩터 = 저장된 데이터 개수 / 버킷 개수
```

이 프로젝트에서는 로드 팩터가 0.75를 넘으면 버킷 개수를 2배로 늘린다.

```python
if self.count / self.capacity > 0.75:
    self._resize()
```

버킷 개수가 바뀌면 `hash % capacity` 결과도 바뀐다. 그래서 기존 데이터를 새 버킷 배열에 다시 배치해야 한다. 이 과정을 재해싱이라고 한다.

리사이징 전후를 그림으로 보면 다음과 같다.

```text
resize 전: capacity = 4

index  bucket
  0    [a]
  1    [b] <-> [f]
  2    [c] <-> [g]
  3    [d]

로드 팩터가 높아져 충돌이 늘어난 상태
```

```text
resize 후: capacity = 8

index  bucket
  0    empty
  1    [a]
  2    [b]
  3    [c]
  4    [d]
  5    empty
  6    [f]
  7    [g]

버킷이 늘어나면서 데이터가 더 넓게 퍼진 상태
```

정확한 위치는 해시 값에 따라 달라진다. 핵심은 capacity가 바뀌면 각 키의 버킷 위치를 다시 계산해야 한다는 점이다.

### 2.7 Mini Redis에서 해시맵을 쓰는 이유

Mini Redis는 키 기반 저장소다. 키로 값을 빠르게 찾는 일이 거의 모든 명령의 출발점이다.

```text
store      key -> RedisEntry
lru_nodes  key -> LRU 리스트 노드
expires    key -> expire_at
```

해시맵은 값 저장소이면서 동시에 다른 자료구조를 빠르게 쓰기 위한 인덱스다. 특히 `lru_nodes`는 이중 연결 리스트와 결합해 LRU 갱신을 O(1)에 가깝게 만든다.

## 3. 이중 연결 리스트

### 3.1 배열의 한계에서 시작하기

배열은 인덱스로 접근할 때 빠르다.

```text
index: 0      1      2
value: Alice  Bob    Charlie
```

하지만 중간에 값을 넣거나 빼는 일은 불편하다.

```text
Alice Bob Charlie
Alice Dana Bob Charlie
```

`Dana`를 중간에 넣으려면 Bob과 Charlie를 뒤로 밀어야 한다. 데이터가 많을수록 이동 비용이 커진다.

LRU에서는 어떤 키가 사용될 때마다 그 키를 맨 앞으로 옮겨야 한다. 배열로 구현하면 매번 많은 값을 밀고 당길 수 있다.

배열에서 중간 값을 앞으로 옮기는 모습을 보자.

```text
GET C

기존 배열:
index   0   1   2   3
value   A   B   C   D

C를 앞으로 옮기려면:
value   C   A   B   D

A와 B가 뒤로 밀린다.
데이터가 많으면 많은 칸을 움직여야 한다.
```

### 3.2 연결 리스트의 생각

연결 리스트는 데이터들이 나란히 붙어 있지 않아도 된다. 각 노드가 다음 노드를 가리킨다.

```text
Alice -> Bob -> Charlie
```

이중 연결 리스트는 앞뒤를 모두 가리킨다.

```text
Alice <-> Bob <-> Charlie
```

노드 하나를 확대하면 다음과 같다.

```text
           ┌─────────────┐
prev  ───► │    data     │ ───► next
           └─────────────┘

data에는 실제 값이 들어가고,
prev와 next에는 이웃 노드로 가는 연결이 들어간다.
```

노드는 세 가지 정보를 가진다.

```python
self.prev = None
self.next = None
self.data = data
```

`prev`는 이전 노드, `next`는 다음 노드, `data`는 실제 데이터다.

### 3.3 head와 tail

리스트는 양 끝을 기억한다.

```python
self.head = None
self.tail = None
self.length = 0
```

`head`는 첫 번째 노드, `tail`은 마지막 노드다.

```text
head                 tail
 │                    │
 ▼                    ▼
Alice <-> Bob <-> Charlie
```

LRU에서는 head가 가장 최근에 사용한 키, tail이 가장 오래 사용하지 않은 키다.

LRU 관점으로 보면 리스트는 시간 순서표다.

```text
최근 사용                       오래됨
  │                             │
  ▼                             ▼
head                          tail
 [C]  <->  [A]  <->  [B]  <-> [D]

C는 방금 사용한 키
D는 가장 오래 사용하지 않은 키
```

### 3.4 insert_front

`insert_front`는 새 노드를 맨 앞에 넣는다.

```text
기존:
Bob <-> Charlie

삽입 후:
Alice <-> Bob <-> Charlie
```

연결 변화만 따로 보면 다음과 같다.

```text
1단계: 새 노드 Alice 생성

Alice      Bob <-> Charlie

2단계: Alice.next = Bob

Alice ───► Bob <-> Charlie

3단계: Bob.prev = Alice

Alice <──► Bob <-> Charlie

4단계: head = Alice

head
 │
 ▼
Alice <-> Bob <-> Charlie
```

코드는 새 노드와 기존 head의 연결을 바꾼다.

```python
node.next = self.head
if self.head is not None:
    self.head.prev = node
else:
    self.tail = node
self.head = node
```

비어 있는 리스트에 처음 넣는 경우에는 새 노드가 head이면서 tail이다.

### 3.5 remove_node

이중 연결 리스트의 가장 큰 장점은 이미 알고 있는 노드를 O(1)에 삭제할 수 있다는 점이다.

```text
A <-> B <-> C
```

B를 삭제하려면 A와 C를 서로 연결하면 된다.

```text
A <-> C
```

삭제 전후를 나란히 보면 더 쉽다.

```text
삭제 전

        제거 대상
           │
           ▼
A  <---->  B  <---->  C

삭제 중

A.next = C
C.prev = A

삭제 후

A  <------------->  C

B는 더 이상 리스트에 연결되어 있지 않다.
```

코드는 B가 head인지, tail인지, 중간 노드인지에 따라 연결을 조정한다.

```python
if node.prev is not None:
    node.prev.next = node.next
else:
    self.head = node.next

if node.next is not None:
    node.next.prev = node.prev
else:
    self.tail = node.prev
```

전체 리스트를 다시 만들 필요가 없다. 주변 노드만 바꾸면 된다.

### 3.6 move_to_front

LRU에서 어떤 키가 사용되면 그 키를 가장 앞으로 옮긴다.

```text
기존:
A <-> B <-> C <-> D

GET C 실행 후:
C <-> A <-> B <-> D
```

이때 `lru_nodes` 해시맵이 함께 움직인다.

```text
GET C
  │
  ▼
lru_nodes.get("C")
  │
  ▼
C 노드를 바로 찾음
  │
  ▼
리스트에서 C 제거
  │
  ▼
C를 head에 삽입
```

해시맵이 없었다면 C 노드를 찾기 위해 head부터 하나씩 걸어가야 한다.

`move_to_front`는 노드를 제거한 뒤 같은 데이터를 앞에 다시 넣는다.

```python
data = self.remove_node(node)
return self.insert_front(data)
```

이 구현은 새 노드를 반환한다. 그래서 Mini Redis는 새 노드를 `lru_nodes`에 다시 저장한다.

```python
new_node = self.lru.move_to_front(node)
self.lru_nodes.put(key, new_node)
```

### 3.7 Mini Redis에서 이중 연결 리스트를 쓰는 이유

Mini Redis는 메모리가 부족할 때 가장 오래 사용하지 않은 키를 삭제해야 한다.

이중 연결 리스트를 쓰면 그 키는 항상 `tail`에 있다.

```text
head: 가장 최근에 사용한 키
tail: 가장 오래 사용하지 않은 키
```

LRU 제거는 다음처럼 보인다.

```text
used_memory > maxmemory
         │
         ▼
  head                       tail
   │                           │
   ▼                           ▼
[user:3] <-> [user:2] <-> [user:1]
                               │
                               ▼
                        가장 오래 사용하지 않음
                               │
                               ▼
                           삭제 대상
```

또한 키가 사용될 때마다 해당 노드를 맨 앞으로 옮길 수 있다. 해시맵으로 노드를 찾고, 이중 연결 리스트로 연결을 바꾸면 빠른 LRU 관리가 가능하다.

```text
해시맵: key -> node
연결 리스트: node 순서 관리
```

## 4. 최소 힙

### 4.1 TTL에서 생기는 문제

TTL은 키가 살아 있을 시간을 뜻한다. `EXPIRE user:1 3`은 `user:1`이 3초 뒤 만료된다는 뜻이다.

키가 많아지면 이런 질문을 계속 해야 한다.

```text
지금 만료해야 할 키가 있는가?
가장 빨리 만료될 키는 무엇인가?
```

모든 키를 매번 확인하면 O(N)이 든다.

정렬된 배열을 사용할 수도 있다. 가장 빨리 만료될 키는 맨 앞에 있으므로 확인은 빠르다. 하지만 새 만료 시간을 넣을 때 정렬 위치를 찾아 끼워 넣어야 해서 삽입 비용이 커진다.

힙은 이 둘 사이의 균형점이다.

```text
가장 작은 값 확인: O(1)
삽입: O(log N)
삭제: O(log N)
```

세 방법을 비교하면 다음과 같다.

```text
방법              가장 빠른 만료 확인    새 만료 추가       특징
────────────────────────────────────────────────────────────
전체 순회         O(N)                  O(1)              단순하지만 확인이 느림
정렬 배열         O(1)                  O(N)              확인은 빠르지만 삽입이 느림
최소 힙           O(1)                  O(log N)          TTL 관리에 균형이 좋음
```

### 4.2 힙은 배열로 표현한 완전 이진 트리다

힙은 트리처럼 생각할 수 있지만, 실제 구현은 배열로 한다. 이것이 가능한 이유는 힙이 **완전 이진 트리** 모양을 유지하기 때문이다.

완전 이진 트리는 위에서 아래로, 왼쪽에서 오른쪽으로 빈칸 없이 채워지는 트리다. 마지막 줄만 덜 찰 수 있지만, 마지막 줄도 반드시 왼쪽부터 채워져야 한다.

```text
완전 이진 트리

          1
       /     \
      3       2
    /   \    /
   7     5  4

마지막 줄이 왼쪽부터 채워져 있다.
```

다음 모양은 완전 이진 트리가 아니다.

```text
완전 이진 트리가 아님

          1
       /     \
      3       2
        \    /
         5  4

index 3 자리가 비어 있는데 index 4와 index 5가 채워져 있다.
```

완전 이진 트리는 빈칸 없이 순서대로 채워지므로, 노드를 위에서 아래로, 왼쪽에서 오른쪽으로 읽으면 그대로 배열에 담을 수 있다.

```text
트리

        1
      /   \
     3     2
    / \   /
   7   5 4
```

배열로는 다음과 같다.

```text
index   0  1  2  3  4  5
value   1  3  2  7  5  4
```

트리와 배열을 함께 놓으면 인덱스 관계가 보인다.

```text
트리                          배열

             1                index   0  1  2  3  4  5
          /     \             value   1  3  2  7  5  4
         3       2
       /   \    /
      7     5  4
```

노드에 인덱스를 붙이면 계산 규칙이 더 분명해진다.

```text
값으로 본 트리                 인덱스로 본 트리

             1                         0
          /     \                   /     \
         3       2                 1       2
       /   \    /                /   \    /
      7     5  4                3     4  5
```

예를 들어 index 1의 값은 3이다. index 1의 왼쪽 자식은 index 3, 오른쪽 자식은 index 4다.

```text
index 1의 왼쪽 자식   = 1 * 2 + 1 = 3
index 1의 오른쪽 자식 = 1 * 2 + 2 = 4
index 1의 부모        = (1 - 1) // 2 = 0
```

index 2도 같은 방식으로 계산한다.

```text
index 2의 왼쪽 자식   = 2 * 2 + 1 = 5
index 2의 오른쪽 자식 = 2 * 2 + 2 = 6  (배열 밖이므로 없음)
index 2의 부모        = (2 - 1) // 2 = 0
```

전체 관계를 표로 보면 다음과 같다.

```text
index  value  left child  right child  parent
-----  -----  ----------  -----------  ------
  0      1        1           2          없음
  1      3        3           4           0
  2      2        5          없음          0
  3      7       없음         없음          1
  4      5       없음         없음          1
  5      4       없음         없음          2

index 0의 자식: index 1, index 2
index 1의 자식: index 3, index 4
index 2의 자식: index 5
```

인덱스 `i`의 가족 관계는 계산으로 알 수 있다.

```text
왼쪽 자식:   i * 2 + 1
오른쪽 자식: i * 2 + 2
부모:       (i - 1) // 2
```

포인터 없이도 부모와 자식을 찾을 수 있다는 점이 힙의 구현상 장점이다.

### 4.3 최소 힙의 규칙

최소 힙의 규칙은 하나다.

```text
부모는 자식보다 작거나 같아야 한다.
```

이 규칙이 지켜지면 배열의 0번 인덱스에는 항상 가장 작은 값이 있다.

```text
items[0] == 최솟값
```

최소 힙은 “완전히 정렬된 배열”이 아니다.

```text
최소 힙으로 가능

        1
      /   \
     5     3
    / \   /
   9   8 4

부모가 자식보다 작거나 같으면 된다.
왼쪽과 오른쪽 자식끼리는 정렬되어 있지 않아도 된다.
```

그래서 배열로 보면 정렬된 것처럼 보이지 않을 수 있다.

```text
[1, 5, 3, 9, 8, 4]
```

하지만 0번 인덱스가 최솟값이라는 사실은 유지된다.

힙은 전체를 완벽하게 정렬하지 않는다. 오직 최솟값을 빠르게 찾을 수 있을 정도로만 질서를 유지한다.

### 4.4 왜 O(log N)인가

힙에서 값을 넣거나 뺄 때는 모든 노드를 훑지 않는다. 깨진 규칙이 있는 한 줄의 경로만 따라 움직인다.

`push`에서는 새 값이 마지막 칸에 들어간 뒤 부모 방향으로 올라간다.

```text
새 값에서 루트까지 한 줄만 확인

          1
       /     \
      3       2
    /   \    /
   7     5  4
        ▲
        │
        └── 부모로 올라감
```

`pop`에서는 마지막 값을 루트로 옮긴 뒤 자식 방향으로 내려간다.

```text
루트에서 아래쪽 한 줄만 확인

          5
       /     \
      3       4
    /
   9
   ▲
   │
더 작은 자식을 따라 내려감
```

완전 이진 트리는 한 층 내려갈 때마다 담을 수 있는 노드 수가 거의 2배가 된다.

```text
높이 0: 최대 1개
높이 1: 최대 1 + 2 = 3개
높이 2: 최대 1 + 2 + 4 = 7개
높이 3: 최대 1 + 2 + 4 + 8 = 15개
높이 4: 최대 31개
```

즉 노드 수 `N`이 2배로 늘어도 트리 높이는 1만 늘어난다. 그래서 높이는 `log2(N)`에 비례한다.

힙에서 한 번의 교환은 한 층만 이동한다. 최악의 경우에도 루트에서 마지막 층까지, 또는 마지막 층에서 루트까지 높이만큼만 이동한다.

```text
확인하는 노드 수 ≈ 트리의 높이 ≈ log2(N)
```

그래서 `push`와 `pop`의 시간 복잡도는 O(log N)이다.

### 4.5 push와 heapify_up

`push`는 새 값을 배열 끝에 넣는다.

```python
def push(self, item):
    self.items.append(item)
    self._heapify_up(len(self.items) - 1)
```

새 값이 부모보다 작으면 최소 힙 규칙이 깨진다. 그래서 부모와 자리를 바꾼다. 이 작업을 위쪽으로 반복한다.

예를 들어 2를 추가해보자.

```text
추가 전

        3
      /   \
     5     4
    /
   9

배열: [3, 5, 4, 9]
```

```text
1단계: 끝에 2 추가

        3
      /   \
     5     4
    / \
   9   2

배열: [3, 5, 4, 9, 2]
```

```text
2단계: 2가 부모 5보다 작으므로 교환

        3
      /   \
     2     4
    / \
   9   5

배열: [3, 2, 4, 9, 5]
```

```text
3단계: 2가 부모 3보다 작으므로 교환

        2
      /   \
     3     4
    / \
   9   5

배열: [2, 3, 4, 9, 5]
```

```python
parent = (index - 1) // 2
if self.items[parent] <= self.items[index]:
    break
self.items[parent], self.items[index] = self.items[index], self.items[parent]
```

트리의 높이만큼만 움직이므로 O(log N)이다.

### 4.6 pop과 heapify_down

`pop`은 가장 작은 값을 꺼낸다. 최소 힙에서 가장 작은 값은 0번 인덱스에 있다.

루트를 꺼내면 빈자리가 생긴다. 그래서 마지막 값을 루트로 옮긴 뒤 아래로 내려보내며 규칙을 회복한다.

예를 들어 최솟값을 꺼내보자.

```text
pop 전

        2
      /   \
     3     4
    / \
   9   5

배열: [2, 3, 4, 9, 5]
```

```text
1단계: 루트 2를 꺼내고 마지막 값 5를 루트로 이동

        5
      /   \
     3     4
    /
   9

배열: [5, 3, 4, 9]
```

```text
2단계: 자식 3과 4 중 더 작은 3과 교환

        3
      /   \
     5     4
    /
   9

배열: [3, 5, 4, 9]
```

```python
root = self.items[0]
self.items[0] = self.items.pop()
self._heapify_down(0)
return root
```

`_heapify_down`은 왼쪽 자식과 오른쪽 자식 중 더 작은 쪽을 고른다. 부모가 그 자식보다 크면 자리를 바꾼다.

```python
if left < length and self.items[left] < self.items[smallest]:
    smallest = left
if right < length and self.items[right] < self.items[smallest]:
    smallest = right
```

이 작업도 O(log N)이다.

### 4.7 Mini Redis에서 최소 힙을 쓰는 이유

Mini Redis는 TTL을 관리할 때 힙에 `(expire_at, key)`를 넣는다.

```text
(만료 시각, 키)
```

파이썬 튜플은 앞 요소부터 비교한다. 그래서 `expire_at`이 가장 작은 값이 힙의 맨 위로 간다.

```text
(100.0, "a")
(103.0, "c")
(105.0, "b")
```

힙의 맨 위만 보면 가장 빨리 만료될 키를 알 수 있다.

```text
peek 결과의 expire_at <= 현재 시간
```

이면 만료된 키가 있으므로 `pop`해서 삭제한다. 아직 만료 전이면 그 뒤의 키들은 볼 필요가 없다. 최소 힙에서 맨 위가 아직 만료되지 않았다면 다른 키들은 더 늦게 만료되기 때문이다.

TTL 힙을 그림으로 보면 다음과 같다.

```text
현재 시간: 100

expire_heap

        (101, "a")
        /        \
 (110, "b")   (105, "c")
    /
(130, "d")

peek -> (101, "a")
```

현재 시간이 102라면 `(101, "a")`는 만료되었다. 그래서 pop하고 `a`를 삭제한다.

현재 시간이 100이라면 `(101, "a")`도 아직 만료되지 않았다. 힙의 맨 위가 아직 살아 있으므로 나머지 키도 모두 아직 살아 있다고 볼 수 있다.

## 5. 세 자료구조가 함께 만드는 힘

Mini Redis의 핵심은 자료구조 하나가 아니라 조합이다.

```text
HashMap
  키로 값을 빠르게 찾는다.

DoublyLinkedList
  사용 순서를 빠르게 바꾼다.

MinHeap
  가장 빠른 만료 시간을 빠르게 찾는다.
```

특히 LRU는 해시맵과 이중 연결 리스트가 함께 있어야 빠르다.

```text
해시맵으로 노드를 찾는다.
연결 리스트에서 노드를 떼어낸다.
연결 리스트 맨 앞에 다시 붙인다.
```

이 조합 덕분에 “최근 사용”이라는 시간의 흐름을 빠르게 갱신할 수 있다.

TTL은 해시맵과 힙이 함께 있어야 안정적이다.

```text
expires 해시맵: 현재 키의 진짜 만료 시각
expire_heap: 가장 빠른 만료 후보
```

힙에는 오래된 만료 기록이 남을 수 있다. 하지만 꺼낼 때 `expires`와 비교하면 낡은 기록인지 알 수 있다. 이것이 lazy deletion 전략이다.

lazy deletion을 그림으로 보면 다음과 같다.

```text
1. 처음 EXPIRE a 10

expires
  a -> 110

expire_heap
  (110, "a")
```

```text
2. 다시 EXPIRE a 30

expires
  a -> 130

expire_heap
  (110, "a")
  (130, "a")

힙에는 예전 기록이 남아 있다.
```

```text
3. 시간이 111이 되어 (110, "a")를 꺼냄

힙에서 꺼낸 값:      (110, "a")
expires의 현재 값:   a -> 130

둘이 다르다.
따라서 (110, "a")는 오래된 기록이므로 무시한다.
```

자료구조는 따로 외우는 것이 아니라, 문제에 맞게 조합할 때 힘을 낸다.
