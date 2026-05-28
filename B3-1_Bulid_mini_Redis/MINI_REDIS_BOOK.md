# 손으로 만드는 Mini Redis

## 프롤로그: 빠름을 이해하는 가장 느린 방법

Redis는 빠르다. 많은 사람이 그렇게 말한다. 하지만 왜 빠른지 묻는 순간 대답은 흐려지기 쉽다. 이유는 단순하다. 우리는 보통 Redis를 사용하지만, Redis가 기대고 있는 자료구조를 직접 만져보지는 않기 때문이다.

이 작은 프로젝트는 Redis 전체를 다시 만드는 일이 아니다. 대신 Redis의 핵심 감각을 익히는 일이다. 키를 저장하는 해시맵, 최근 사용 순서를 기억하는 이중 연결 리스트, 만료 시간을 관리하는 최소 힙을 직접 만들고, 그 위에 CLI 기반 Mini Redis를 세운다.

---

## 1장. 우리가 만들 프로그램

프로그램을 실행하면 다음과 같은 프롬프트가 나타난다.

```text
mini-redis>
```

사용자는 Redis처럼 명령어를 입력한다.

```text
SET user:1 "Alice"
GET user:1
EXPIRE user:1 3
TTL user:1
```

이 프로젝트는 네트워크 서버가 아니다. 파일에 저장하지도 않는다. 오직 메모리 안에서만 동작하는 작은 Key-Value 저장소다. 그래서 더 좋다. 핵심이 선명하게 보인다.

---

## 2장. 저장소의 심장, 해시맵

키로 값을 빠르게 찾으려면 해시맵이 필요하다. 해시맵은 키를 숫자로 바꾸고, 그 숫자를 배열의 위치로 바꾼다.

예를 들어 `user:1`이라는 키가 들어오면 직접 만든 해시 함수가 이 문자열을 숫자로 바꾼다. 그 숫자를 버킷 개수로 나눈 나머지가 저장 위치가 된다.

하지만 서로 다른 키가 같은 위치를 가리킬 수 있다. 이것을 충돌이라고 부른다. 이 프로젝트에서는 충돌을 체이닝 방식으로 해결한다. 한 버킷 안에 이중 연결 리스트를 두고, 같은 위치로 온 여러 키를 줄줄이 연결한다.

구현 파일은 `hash_map.py`다.

주요 메서드는 다음과 같다.

- `put`: 키와 값을 저장한다.
- `get`: 키로 값을 찾는다.
- `remove`: 키를 삭제한다.
- `contains`: 키가 있는지 확인한다.
- `keys`: 전체 키 목록을 반환한다.
- `size`: 저장된 키 개수를 반환한다.

로드 팩터가 0.75를 넘으면 버킷 배열을 2배로 늘린다. 사람이 많아진 교실에서 책상을 더 놓는 것과 비슷하다. 충돌이 너무 많아지면 탐색이 느려지므로, 공간을 넓혀 평균 탐색 시간을 지킨다.

---

## 3장. 최근 사용 순서를 기억하는 법

메모리가 부족하면 무엇을 지워야 할까? Mini Redis는 LRU 정책을 사용한다. LRU는 Least Recently Used, 즉 가장 오래 사용되지 않은 데이터를 먼저 지운다는 뜻이다.

이 정책을 빠르게 구현하려면 두 가지가 함께 필요하다.

첫째, 사용 순서를 담는 이중 연결 리스트가 필요하다. 가장 최근에 사용한 키는 앞쪽에 둔다. 가장 오래 사용하지 않은 키는 뒤쪽에 둔다.

둘째, 특정 키의 리스트 노드를 바로 찾는 해시맵이 필요하다. 키를 사용할 때마다 그 노드를 찾아 리스트 맨 앞으로 옮겨야 하기 때문이다.

이 조합이 중요한 이유는 시간 복잡도에 있다.

- 해시맵으로 키의 노드를 찾는다: 평균 O(1)
- 이중 연결 리스트에서 노드를 제거한다: O(1)
- 리스트 맨 앞에 다시 넣는다: O(1)

그래서 GET이나 SET이 성공했을 때 LRU 갱신을 빠르게 처리할 수 있다.

구현 파일은 `doubly_linked_list.py`와 `mini_redis.py`다.

---

## 4장. 메모리 제한과 자동 제거

이 프로젝트의 메모리 계산은 일부러 단순하게 정했다.

```text
used_memory = 모든 키와 값의 UTF-8 바이트 길이 합
```

노드, 포인터, 버킷 같은 자료구조 오버헤드는 계산하지 않는다. 학습 목표가 메모리 정책의 흐름을 이해하는 것이기 때문이다.

예를 들어 다음 명령은 최대 메모리를 30바이트로 설정한다.

```text
CONFIG SET maxmemory 30
```

이후 `SET` 때문에 `used_memory`가 30을 넘으면 LRU 리스트의 뒤쪽부터 키를 삭제한다. 삭제할 때는 저장소, LRU 노드, TTL 정보가 함께 정리된다.

단일 키와 값의 크기 자체가 `maxmemory`보다 크면 저장하지 않는다. 이때는 OOM 에러를 반환한다.

```text
(error) OOM command not allowed when used_memory > 'maxmemory'
```

현재 메모리 상태는 다음 명령으로 확인한다.

```text
INFO memory
```

출력에는 최소 세 가지가 포함된다.

```text
used_memory:22
maxmemory:30
evicted_keys:1
```

---

## 5장. 시간이 지나면 사라지는 키

Redis에는 TTL이라는 개념이 있다. Time To Live, 즉 키가 살아 있을 시간을 뜻한다.

```text
EXPIRE user:1 3
```

위 명령은 `user:1` 키가 3초 뒤 만료되도록 설정한다.

만료 시간을 빠르게 관리하려면 최소 힙이 잘 맞는다. 힙의 맨 위에는 가장 작은 값이 온다. TTL에서는 가장 빨리 만료될 시간이 가장 작은 값이다.

이 프로젝트의 힙에는 다음 형태의 값이 들어간다.

```text
(expire_at, key)
```

가장 빨리 만료될 키를 확인하고 싶으면 힙의 맨 위만 보면 된다. 시간이 지났다면 꺼내서 삭제한다.

단, 같은 키에 EXPIRE를 여러 번 줄 수 있다. 그래서 오래된 만료 정보가 힙 안에 남을 수 있다. 이 프로젝트는 lazy deletion 전략을 사용한다. 힙에서 꺼낸 만료 정보가 현재 해시맵에 저장된 만료 시간과 다르면 낡은 정보로 보고 무시한다.

구현 파일은 `min_heap.py`와 `mini_redis.py`다.

---

## 6장. 명령어가 지나가는 길

사용자가 입력한 한 줄은 `mini_redis.py`의 `execute` 메서드로 들어간다.

```text
SET user:1 "Alice"
```

프로그램은 이 줄을 명령어와 인자로 나눈다.

```text
명령어: SET
인자: user:1, Alice
```

그리고 명령어에 맞는 메서드를 호출한다.

- `SET`: 값을 저장하고 LRU를 갱신한다.
- `GET`: 값을 읽고 LRU를 갱신한다.
- `DEL`: 저장소, TTL, LRU 정보를 함께 삭제한다.
- `EXISTS`: 키가 있는지 확인한다.
- `DBSIZE`: 현재 키 개수를 반환한다.
- `KEYS`: 전체 키 목록을 출력한다.
- `CONFIG SET maxmemory`: 최대 메모리를 설정한다.
- `INFO memory`: 메모리 상태를 출력한다.
- `EXPIRE`: 만료 시간을 설정한다.
- `TTL`: 남은 만료 시간을 확인한다.

키 기반 명령은 먼저 만료 여부를 확인한다. 만료된 키는 삭제한 뒤 없는 키처럼 처리한다.

---

## 7장. 프로그램 전체 흐름

Mini Redis는 크게 세 층으로 나눌 수 있다.

```text
사용자 입력
  ↓
main.py
  ↓
MiniRedis.execute()
  ↓
명령어별 메서드
  ↓
직접 만든 자료구조
```

첫 번째 층은 `main.py`다. 이 파일은 사용자의 입력을 계속 받는다. 사용자가 `exit` 또는 `quit`을 입력하면 반복문을 끝낸다. 그 외의 입력은 `MiniRedis` 객체에게 넘긴다.

```python
redis = MiniRedis()
line = input("mini-redis> ")
result = redis.execute(stripped)
```

두 번째 층은 `mini_redis.py`의 `execute` 메서드다. 이 메서드는 입력 문자열을 명령어와 인자로 나눈다. 이때 `shlex.split`을 사용하므로 `"Alice Smith"`처럼 큰따옴표로 감싼 값도 하나의 값으로 읽을 수 있다.

```text
SET user:1 "Alice"
```

위 입력은 다음처럼 나뉜다.

```text
command = SET
args = ["user:1", "Alice"]
```

세 번째 층은 명령어별 메서드다. 예를 들어 `SET`은 `_cmd_set`, `GET`은 `_cmd_get`, `TTL`은 `_cmd_ttl`로 이어진다.

네 번째 층은 직접 만든 자료구조다. 실제 데이터 저장은 `HashMap`, 사용 순서 관리는 `DoublyLinkedList`, 만료 시간 관리는 `MinHeap`이 담당한다.

이 구조의 장점은 역할이 분리된다는 점이다. `main.py`는 입력과 출력만 생각한다. `mini_redis.py`는 Redis 명령의 규칙을 생각한다. 자료구조 파일들은 저장, 연결, 정렬이라는 자기 일만 한다.

---

## 8장. MiniRedis 안에는 무엇이 들어 있나

`MiniRedis` 객체가 만들어질 때 다음 필드들이 준비된다.

```python
self.store = HashMap()
self.lru = DoublyLinkedList()
self.lru_nodes = HashMap()
self.expires = HashMap()
self.expire_heap = MinHeap()
self.used_memory = 0
self.maxmemory = 0
self.evicted_keys = 0
```

하나씩 풀어보자.

`store`는 실제 키와 값을 저장하는 공간이다. `SET user:1 Alice`를 실행하면 `store`에는 `user:1`이라는 키와 `RedisEntry("Alice")`라는 값이 들어간다.

`lru`는 사용 순서를 기억하는 이중 연결 리스트다. 리스트의 앞쪽은 최근에 사용한 키, 뒤쪽은 가장 오래 사용하지 않은 키다.

`lru_nodes`는 키와 LRU 노드를 연결하는 보조 해시맵이다. 키를 사용했을 때 그 키가 LRU 리스트 어디에 있는지 바로 찾기 위해 존재한다.

`expires`는 키별 만료 시간을 저장한다. `EXPIRE user:1 3`을 실행하면 `user:1`의 만료 시각이 여기에 저장된다.

`expire_heap`은 만료 시각을 빠르게 확인하기 위한 최소 힙이다. 가장 빨리 만료될 키가 힙의 맨 위에 온다.

`used_memory`는 현재 사용 중인 메모리다. 이 프로젝트에서는 키와 값의 UTF-8 바이트 길이만 더한다.

`maxmemory`는 최대 메모리 제한이다. 값이 0이면 제한이 없다는 뜻이다.

`evicted_keys`는 LRU 정책 때문에 자동으로 삭제된 키의 누적 개수다.

---

## 9장. SET은 어떻게 흘러가는가

`SET key value`는 가장 많은 일이 일어나는 명령이다. 저장, 메모리 계산, LRU 갱신, TTL 초기화, 메모리 초과 시 자동 삭제가 모두 들어 있다.

흐름은 다음과 같다.

```text
1. 인자 개수를 확인한다.
2. 같은 키가 이미 만료되었는지 확인한다.
3. 새 키와 값의 메모리 크기를 계산한다.
4. 단일 엔트리가 maxmemory보다 크면 OOM 에러를 반환한다.
5. 새 키라면 store에 추가하고 LRU 맨 앞으로 보낸다.
6. 기존 키라면 used_memory를 다시 계산하고 값을 덮어쓴다.
7. 기존 TTL은 삭제한다.
8. used_memory가 maxmemory보다 크면 LRU 뒤쪽부터 삭제한다.
9. OK를 반환한다.
```

여기서 중요한 규칙은 기존 키를 덮어쓸 때 TTL이 사라진다는 점이다.

```text
SET a b
EXPIRE a 10
SET a c
TTL a
```

마지막 `TTL a`의 결과는 `(integer) -1`이다. 키는 있지만 만료 시간이 없다는 뜻이다.

---

## 10장. GET은 왜 LRU를 움직이는가

`GET key`는 값을 읽는 명령이다. 하지만 단순히 읽기만 하지 않는다. Redis의 LRU 관점에서는 읽은 키도 방금 사용한 키다.

흐름은 다음과 같다.

```text
1. 인자 개수를 확인한다.
2. 키가 만료되었으면 삭제하고 (nil)을 반환한다.
3. store에서 키를 찾는다.
4. 없으면 (nil)을 반환한다.
5. 있으면 LRU 리스트에서 해당 키를 맨 앞으로 옮긴다.
6. 값을 "value" 형태로 반환한다.
```

만료로 삭제된 키는 LRU를 갱신하지 않는다. 이미 사라진 키를 최근 사용했다고 기록하면 순서가 어긋나기 때문이다.

---

## 11장. 삭제는 하나만 지우는 일이 아니다

`DEL key`는 저장소에서 키를 지우는 명령이다. 하지만 이 프로젝트에서 키 하나는 여러 구조에 흔적을 남긴다.

키가 저장되면 `store`에 들어간다. 사용 순서를 위해 `lru`에도 들어간다. 그 노드를 찾기 위해 `lru_nodes`에도 들어간다. 만료 시간이 있다면 `expires`에도 들어간다.

그래서 삭제는 다음을 함께 처리해야 한다.

```text
store에서 실제 값 삭제
expires에서 TTL 정보 삭제
lru_nodes에서 LRU 노드 정보 삭제
lru에서 실제 노드 삭제
used_memory 감소
```

이 일을 모아둔 메서드가 `_delete_key`다. 키를 지우는 모든 상황에서 이 메서드를 사용하면 삭제 규칙이 한곳에 모인다.

---

## 12장. 해시맵 자세히 읽기

`hash_map.py`의 `HashMap`은 파이썬 `dict`를 대신하기 위해 만든 구조다. 해시맵을 처음 공부할 때는 먼저 아주 단순한 저장소를 상상하는 것이 좋다.

우리가 키와 값을 저장하고 싶다고 해보자.

```text
user:1 -> Alice
user:2 -> Bob
user:3 -> Charlie
```

가장 쉬운 방법은 모든 데이터를 순서대로 보관하는 것이다.

```text
[user:1, Alice]
[user:2, Bob]
[user:3, Charlie]
```

이 방식은 이해하기 쉽다. 하지만 문제가 있다. `user:3`을 찾으려면 앞에서부터 하나씩 비교해야 한다. 데이터가 3개면 괜찮다. 데이터가 100만 개라면 이야기가 달라진다.

```text
user:1인가? 아니네.
user:2인가? 아니네.
user:3인가? 맞네.
```

이렇게 하나씩 찾는 방식을 선형 탐색이라고 한다. 시간 복잡도는 O(N)이다. 데이터가 많아질수록 느려진다.

해시맵의 생각은 여기서 출발한다.

```text
키를 바로 배열의 위치로 바꿀 수는 없을까?
```

키를 숫자로 바꾸고, 그 숫자로 저장 위치를 정하면 매번 처음부터 찾지 않아도 된다.

### 12.1 해시 함수는 이름표를 숫자로 바꾸는 규칙이다

해시맵은 먼저 키를 숫자로 바꾼다. 이 일을 하는 함수가 해시 함수다.

이 프로젝트의 해시 함수는 다음과 같다.

```python
def _hash(self, key):
    text = str(key)
    hash_value = 5381
    for char in text:
        hash_value = ((hash_value * 33) + ord(char)) % 2147483647
    return hash_value
```

여기서 중요한 부분은 세 가지다.

첫째, 키를 문자열로 본다. 이 프로젝트의 키는 `user:1` 같은 문자열이지만, 혹시 다른 값이 들어와도 문자열로 바꿔 처리한다.

둘째, 글자를 하나씩 읽는다. `ord(char)`는 글자를 숫자로 바꾼다. 예를 들어 `A`는 어떤 숫자, `B`는 또 다른 숫자가 된다.

셋째, 이전 결과에 33을 곱하고 새 글자 값을 더한다. 이렇게 하면 글자의 종류뿐 아니라 순서도 결과에 영향을 준다.

```text
abc
acb
bac
```

세 문자열은 같은 글자를 가지고 있지만 순서가 다르다. 해시 함수는 이런 차이를 숫자 결과에 반영하려고 한다.

해시 함수의 목표는 완벽한 마법이 아니다. 목표는 키들을 가능한 한 여러 위치에 고르게 흩뿌리는 것이다. 한쪽에만 몰리면 결국 다시 하나씩 찾는 일이 많아진다.

### 12.2 버킷은 실제 저장 칸이다

해시 함수가 큰 숫자를 만들었다고 해서 배열을 그만큼 크게 만들 수는 없다. 그래서 버킷 개수로 나눈 나머지를 사용한다.

```python
def _bucket_index(self, key):
    return self._hash(key) % self.capacity
```

예를 들어 버킷이 8개라면 인덱스는 0부터 7까지만 가능하다.

```text
hash("user:1") % 8 = 3
hash("user:2") % 8 = 4
hash("user:3") % 8 = 1
```

그러면 각 키는 자기 위치로 바로 갈 수 있다.

```text
bucket[1] -> user:3
bucket[3] -> user:1
bucket[4] -> user:2
```

이것이 해시맵이 빠른 이유다. 모든 데이터를 처음부터 보는 것이 아니라, 해시 함수로 목적지 근처까지 바로 간다.

### 12.3 충돌은 피할 수 없다

하지만 버킷 개수는 제한되어 있다. 키는 얼마든지 많아질 수 있다. 그러면 서로 다른 키가 같은 위치를 가리키는 일이 생긴다.

```text
hash("user:1") % 8 = 3
hash("cart:9") % 8 = 3
```

이것을 충돌이라고 부른다.

충돌이 생겼다고 해서 둘 중 하나를 버릴 수는 없다. 둘 다 저장해야 한다. 이 프로젝트는 체이닝 방식으로 충돌을 해결한다.

체이닝은 같은 버킷에 들어온 데이터를 연결 리스트로 이어 붙이는 방법이다.

```text
bucket[3] -> [user:1, Alice] <-> [cart:9, Book]
```

그래서 이 프로젝트의 버킷은 단순한 값 하나가 아니라 `DoublyLinkedList`다.

```python
self.buckets = self._make_buckets(capacity)
```

```python
def _make_buckets(self, capacity):
    buckets = []
    for _ in range(capacity):
        buckets.append(DoublyLinkedList())
    return buckets
```

처음에는 버킷 8개를 만들고, 각 버킷마다 빈 이중 연결 리스트를 넣는다. 충돌이 생기면 그 버킷의 리스트 뒤에 새 값을 붙인다.

### 12.4 put은 저장하거나 덮어쓴다

`put`은 두 가지 일을 한다. 이미 있는 키라면 값을 바꾸고, 없는 키라면 새로 넣는다.

```python
def put(self, key, value):
    node = self._find_node(key)
    if node is not None:
        node.data.value = value
        return

    index = self._bucket_index(key)
    self.buckets[index].insert_back(HashEntry(key, value))
    self.count += 1
```

여기서 `HashEntry`는 키와 값을 함께 담는 작은 상자다.

```python
class HashEntry:
    def __init__(self, key, value):
        self.key = key
        self.value = value
```

해시맵은 값만 저장하면 안 된다. 충돌 때문에 같은 버킷 안에 여러 키가 들어올 수 있으므로, 나중에 비교할 키도 함께 저장해야 한다.

### 12.5 get은 버킷 안에서만 찾는다

`get`은 먼저 키가 들어갈 버킷을 계산한다. 그다음 그 버킷 안의 연결 리스트만 살펴본다.

```python
def get(self, key):
    node = self._find_node(key)
    if node is None:
        return None
    return node.data.value
```

전체 데이터를 전부 보는 것이 아니다. 이 차이가 크다.

```text
나쁜 경우: 전체 키 100만 개를 처음부터 확인
해시맵: 목적 버킷 하나로 이동한 뒤 그 안만 확인
```

충돌이 적게 유지된다면 버킷 안의 리스트는 짧다. 그래서 평균적으로 O(1)에 가까운 탐색이 가능하다.

### 12.6 remove는 연결을 끊는다

`remove`도 같은 방식으로 버킷을 찾고, 버킷 안의 리스트에서 키를 찾는다. 찾으면 그 노드를 연결 리스트에서 제거한다.

```python
value = current.data.value
bucket.remove_node(current)
self.count -= 1
return value
```

해시맵 입장에서는 이 값이 사라졌으므로 `count`도 줄인다.

Mini Redis에서 이 반환값은 중요하다. 삭제한 값의 크기를 알아야 `used_memory`를 줄일 수 있기 때문이다.

### 12.7 로드 팩터는 교실의 밀도다

버킷이 너무 적고 데이터가 많으면 충돌이 늘어난다. 충돌이 늘어나면 버킷 안의 연결 리스트가 길어진다. 그러면 해시맵이 점점 선형 탐색처럼 변한다.

그래서 해시맵은 로드 팩터를 본다.

```text
로드 팩터 = 저장된 데이터 개수 / 버킷 개수
```

이 프로젝트에서는 로드 팩터가 0.75를 넘으면 버킷을 2배로 늘린다.

```python
if self.count / self.capacity > 0.75:
    self._resize()
```

버킷이 8개일 때 데이터가 7개가 되면 로드 팩터는 0.875다. 이때 버킷을 16개로 늘린다.

중요한 점은 단순히 배열 크기만 늘리면 안 된다는 것이다. 버킷 위치는 `hash % capacity`로 정해진다. capacity가 바뀌면 위치도 달라질 수 있다.

```text
hash("user:1") % 8 = 3
hash("user:1") % 16 = 11
```

그래서 `_resize`는 기존 데이터를 새 버킷 배열에 다시 넣는다. 이 과정을 재해싱이라고 부른다.

### 12.8 Mini Redis에서 해시맵을 쓰는 이유

Mini Redis는 키 기반 저장소다. 사용자는 항상 키로 값을 찾는다.

```text
GET user:1
DEL session:abc
TTL token:7
```

이때 모든 키를 처음부터 훑으면 Redis다운 빠른 느낌을 만들 수 없다. 해시맵을 쓰면 키로 거의 바로 접근할 수 있다.

이 프로젝트에서는 해시맵을 여러 곳에서 쓴다.

```text
store: 실제 key -> value 저장
lru_nodes: key -> LRU 리스트 노드 저장
expires: key -> 만료 시각 저장
```

즉 해시맵은 단순히 값 저장소 하나가 아니다. 다른 자료구조를 빠르게 사용하게 해주는 인덱스 역할도 한다.

---

## 13장. 이중 연결 리스트 자세히 읽기

`doubly_linked_list.py`에는 `ListNode`와 `DoublyLinkedList`가 있다. 연결 리스트를 처음 배울 때는 배열과 비교하면 이해하기 쉽다.

배열은 데이터가 나란히 놓인 구조다.

```text
index: 0      1      2
value: Alice  Bob    Charlie
```

인덱스를 알면 바로 접근할 수 있다. `array[1]`은 Bob이다. 하지만 중간에 값을 넣거나 빼면 뒤의 값들을 밀거나 당겨야 한다.

```text
Alice Bob Charlie
Alice Dana Bob Charlie
```

`Dana`를 중간에 넣으려면 Bob과 Charlie가 한 칸씩 밀려야 한다.

연결 리스트는 생각이 다르다. 데이터들이 메모리상에 나란히 있어야 한다고 요구하지 않는다. 대신 각 노드가 다음 노드를 가리킨다.

```text
Alice -> Bob -> Charlie
```

이중 연결 리스트는 여기서 한 걸음 더 간다. 다음 노드뿐 아니라 이전 노드도 가리킨다.

```text
Alice <-> Bob <-> Charlie
```

### 13.1 노드는 데이터와 연결 정보를 함께 가진다

노드는 세 가지 정보를 가진다.

```python
self.prev = None
self.next = None
self.data = data
```

`prev`는 앞 노드, `next`는 뒤 노드, `data`는 실제 데이터다.

이 구조에서 데이터는 혼자 존재하지 않는다. 데이터는 언제나 앞뒤 연결 정보와 함께 움직인다.

```text
        data
         ↓
prev <- node -> next
```

### 13.2 head와 tail은 양쪽 문이다

`DoublyLinkedList`는 `head`와 `tail`을 가진다.

```python
self.head = None
self.tail = None
self.length = 0
```

`head`는 첫 번째 노드다. `tail`은 마지막 노드다.

```text
head                      tail
 ↓                         ↓
Alice <-> Bob <-> Charlie
```

이 둘을 기억하면 앞에 넣는 일과 뒤에서 빼는 일이 빠르다. LRU에서는 특히 이 점이 중요하다. 가장 최근 사용한 키는 앞에 두고, 가장 오래 사용하지 않은 키는 뒤에서 바로 찾는다.

### 13.3 insert_front는 앞문으로 들어오는 일이다

새 노드를 맨 앞에 넣는 과정을 보자.

```text
기존:
head
 ↓
Bob <-> Charlie

새 노드:
Alice
```

`Alice`를 앞에 붙이면 이렇게 된다.

```text
head
 ↓
Alice <-> Bob <-> Charlie
```

코드에서는 새 노드의 `next`를 기존 head로 연결하고, 기존 head의 `prev`를 새 노드로 연결한다.

```python
node.next = self.head
if self.head is not None:
    self.head.prev = node
else:
    self.tail = node
self.head = node
```

리스트가 비어 있었다면 새 노드는 head이면서 tail이다. 그래서 `else`에서 `self.tail = node`를 설정한다.

### 13.4 remove_node는 주변 연결만 바꾸는 일이다

이중 연결 리스트의 가장 큰 장점은 이미 알고 있는 노드를 O(1)에 삭제할 수 있다는 점이다.

가운데 노드 B를 지운다고 해보자.

```text
A <-> B <-> C
```

해야 할 일은 두 가지다.

```text
A.next = C
C.prev = A
```

그러면 B는 더 이상 리스트에 속하지 않는다.

```text
A <-> C
```

코드는 이 상황뿐 아니라 B가 head인 경우, B가 tail인 경우도 처리한다.

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

앞 노드가 없다면 이 노드는 head였다는 뜻이다. 그래서 head를 다음 노드로 바꾼다. 뒤 노드가 없다면 이 노드는 tail이었다는 뜻이다. 그래서 tail을 이전 노드로 바꾼다.

### 13.5 move_to_front는 LRU의 핵심 동작이다

LRU에서는 어떤 키가 사용되면 그 키를 가장 앞으로 보내야 한다.

```text
기존:
head             tail
 ↓                ↓
A <-> B <-> C <-> D

GET C 실행 후:
head            tail
 ↓                ↓
C <-> A <-> B <-> D
```

`move_to_front`는 이 일을 한다. 먼저 기존 위치에서 노드를 제거하고, 같은 데이터를 맨 앞에 다시 넣는다.

```python
data = self.remove_node(node)
return self.insert_front(data)
```

이 구현은 새 노드를 만들어 반환한다. 그래서 Mini Redis는 반환된 새 노드를 `lru_nodes`에 다시 저장한다.

```python
new_node = self.lru.move_to_front(node)
self.lru_nodes.put(key, new_node)
```

이 한 줄이 없으면 `lru_nodes`는 예전 노드를 가리키게 된다. 예전 노드는 이미 리스트에서 빠졌으므로, 다음 LRU 갱신이나 삭제가 꼬일 수 있다.

### 13.6 왜 배열이 아니라 이중 연결 리스트인가

LRU를 배열로 구현한다고 생각해보자.

```text
[A, B, C, D]
```

`GET C`가 실행되면 C를 맨 앞으로 옮겨야 한다.

```text
[C, A, B, D]
```

배열에서는 C를 빼고, A와 B를 뒤로 밀고, C를 앞에 넣어야 한다. 데이터가 많으면 이 이동 비용이 커진다. 시간 복잡도는 O(N)이 된다.

이중 연결 리스트에서는 C 노드를 알고 있다면 주변 연결만 바꾸면 된다. 시간 복잡도는 O(1)이다.

하지만 연결 리스트만 쓰면 C 노드를 찾기 위해 앞에서부터 훑어야 한다. 그래서 해시맵이 함께 필요하다.

```text
해시맵: key -> 리스트 노드
리스트: 사용 순서 관리
```

이 조합이 LRU의 핵심이다.

이 프로젝트의 LRU 방향은 다음과 같다.

```text
head: 가장 최근에 사용한 키
tail: 가장 오래 사용하지 않은 키
```

메모리가 초과되면 `tail`부터 삭제한다.

### 13.7 Mini Redis에서 이중 연결 리스트를 쓰는 이유

Mini Redis는 메모리가 부족해졌을 때 가장 오래 사용하지 않은 키를 삭제해야 한다. 이 질문에 빠르게 답해야 한다.

```text
가장 오래 사용하지 않은 키가 무엇인가?
```

이중 연결 리스트를 쓰면 답은 `tail`이다. tail을 보면 바로 알 수 있다.

또 다른 질문도 있다.

```text
방금 사용한 키를 가장 최근 위치로 어떻게 옮길 것인가?
```

해시맵으로 노드를 찾고, 이중 연결 리스트가 그 노드를 앞으로 옮긴다. 이 흐름 덕분에 `GET`, `SET`, LRU 삭제가 빠르게 동작한다.

---

## 14장. 최소 힙 자세히 읽기

`min_heap.py`의 `MinHeap`은 가장 작은 값을 빠르게 꺼내기 위한 구조다. 힙을 처음 공부할 때는 먼저 정렬된 배열과 비교해보면 좋다.

TTL을 관리하려면 이런 질문을 계속 해야 한다.

```text
가장 빨리 만료될 키는 무엇인가?
```

가장 단순한 방법은 모든 키를 매번 훑는 것이다.

```text
user:1 만료 시각 확인
user:2 만료 시각 확인
user:3 만료 시각 확인
...
```

키가 적으면 괜찮다. 하지만 키가 많아지면 매번 O(N)이 든다.

다른 방법은 만료 시간을 정렬된 배열에 넣어두는 것이다.

```text
[(10초 뒤, a), (20초 뒤, b), (30초 뒤, c)]
```

그러면 가장 빨리 만료될 키는 맨 앞에 있어서 바로 알 수 있다. 하지만 새 만료 시간을 넣을 때 정렬 위치를 찾아 끼워 넣어야 한다. 중간 삽입 때문에 값들을 밀어야 하므로 비용이 커진다.

힙은 이 두 방식 사이에서 좋은 균형을 잡는다.

```text
가장 작은 값 확인: O(1)
새 값 넣기: O(log N)
가장 작은 값 꺼내기: O(log N)
```

정렬된 전체 순서를 완벽히 유지하지는 않는다. 대신 가장 작은 값만 빠르게 알 수 있도록 약한 정렬 상태를 유지한다.

### 14.1 힙은 배열로 표현한 나무다

힙은 완전 이진 트리를 배열로 표현한다. 배열에서 어떤 인덱스 `i`의 자식 위치는 다음과 같다.

```text
왼쪽 자식: i * 2 + 1
오른쪽 자식: i * 2 + 2
부모: (i - 1) // 2
```

완전 이진 트리는 위에서 아래로, 왼쪽에서 오른쪽으로 빈칸 없이 채워지는 트리다.

```text
        1
      /   \
     3     2
    / \   /
   7   5 4
```

이 트리를 배열에 담으면 다음과 같다.

```text
index: 0  1  2  3  4  5
value: 1  3  2  7  5  4
```

포인터로 자식 노드를 연결하지 않아도 된다. 인덱스 계산만으로 부모와 자식을 찾을 수 있다. 그래서 힙은 배열과 잘 어울린다.

### 14.2 최소 힙의 규칙은 하나다

최소 힙의 규칙은 단순하다.

```text
부모는 자식보다 작거나 같아야 한다.
```

이 규칙이 지켜지면 루트, 즉 배열의 0번 인덱스에는 전체에서 가장 작은 값이 온다.

```text
items[0] == 가장 작은 값
```

하지만 두 번째로 작은 값, 세 번째로 작은 값이 정확히 어디에 있는지는 중요하지 않다. 힙은 전체 정렬이 아니라 최솟값 접근에 집중한다.

### 14.3 push는 아래에서 위로 올라간다

`push`는 새 값을 배열 끝에 넣고 `_heapify_up`을 실행한다.

```python
def push(self, item):
    self.items.append(item)
    self._heapify_up(len(self.items) - 1)
```

새 값은 일단 마지막 자리에 들어간다. 그런데 그 값이 부모보다 작으면 최소 힙 규칙이 깨진다.

```text
부모: 10
자식: 3
```

부모가 자식보다 작거나 같아야 하는데, 10은 3보다 크다. 그래서 둘의 자리를 바꾼다.

```python
if self.items[parent] <= self.items[index]:
    break
self.items[parent], self.items[index] = self.items[index], self.items[parent]
```

이 과정을 루트에 도착하거나 부모가 더 작을 때까지 반복한다. 트리의 높이만큼만 움직이므로 O(log N)이다.

### 14.4 pop은 위에서 아래로 내려간다

`pop`은 가장 작은 값을 꺼낸다. 최소 힙에서 가장 작은 값은 항상 0번 인덱스에 있다.

문제는 0번 값을 꺼내면 루트 자리가 빈다는 것이다. 힙은 완전 이진 트리 모양을 유지해야 하므로, 마지막 값을 루트로 옮긴다.

```python
root = self.items[0]
self.items[0] = self.items.pop()
self._heapify_down(0)
return root
```

마지막 값이 루트로 올라오면 최소 힙 규칙이 깨질 수 있다. 그래서 `_heapify_down`이 더 작은 자식과 자리를 바꾸며 아래로 내려간다.

```python
if left < length and self.items[left] < self.items[smallest]:
    smallest = left
if right < length and self.items[right] < self.items[smallest]:
    smallest = right
```

왼쪽 자식과 오른쪽 자식 중 더 작은 쪽을 고른다. 그리고 부모가 그 자식보다 크면 자리를 바꾼다. 이 역시 트리 높이만큼만 움직이므로 O(log N)이다.

### 14.5 왜 TTL에 힙이 어울리는가

TTL에서 정말 자주 필요한 질문은 이것이다.

```text
지금 만료해야 할 키가 있는가?
```

이 질문에 답하려면 가장 빨리 만료될 키만 보면 된다. 모든 키가 정렬되어 있을 필요는 없다.

힙의 `peek`는 가장 작은 값을 꺼내지 않고 보기만 한다.

```python
def peek(self):
    if len(self.items) == 0:
        return None
    return self.items[0]
```

Mini Redis는 힙의 맨 위를 본다.

```text
맨 위 expire_at <= 현재 시간
```

이면 만료된 키가 있다는 뜻이다. 그러면 `pop`으로 꺼내 삭제한다. 아직 만료 시간이 오지 않았다면 그 뒤의 값들은 볼 필요가 없다. 최소 힙에서 맨 위가 아직 만료되지 않았다면, 다른 값들은 그보다 늦게 만료되기 때문이다.

### 14.6 튜플을 넣는 이유

TTL 관리에서는 힙에 `(expire_at, key)`가 들어간다. 파이썬의 튜플 비교는 앞 요소부터 비교하므로 `expire_at`이 작은 값이 먼저 나온다. 즉 가장 빨리 만료될 키가 힙의 맨 위에 놓인다.

```text
(100.0, "a")
(105.0, "b")
(103.0, "c")
```

이 값들이 힙에 들어가면 `expire_at`이 가장 작은 `(100.0, "a")`가 먼저 나온다.

키도 함께 넣는 이유는 삭제할 대상을 알아야 하기 때문이다. 만료 시각만 있으면 어떤 키를 지워야 하는지 알 수 없다.

### 14.7 Mini Redis에서 최소 힙을 쓰는 이유

Mini Redis는 TTL이 있는 키를 관리해야 한다. 키가 많아질수록 모든 키를 매번 검사하는 방식은 부담이 된다.

힙을 쓰면 가장 빨리 만료될 키만 계속 확인할 수 있다.

```text
DBSIZE 실행
  ↓
_purge_expired_keys 실행
  ↓
힙의 맨 위 확인
  ↓
만료되었으면 pop 후 삭제
  ↓
아직 만료 전이면 중단
```

이 흐름은 “필요한 만큼만 정리한다”는 장점이 있다. 모든 키를 매번 훑지 않고, 현재 시점에서 만료된 후보만 빠르게 처리한다.

---

## 15장. TTL의 실제 처리

`EXPIRE key seconds`가 실행되면 현재 시간에 seconds를 더해 만료 시각을 만든다.

```python
expire_at = time.time() + seconds
```

그다음 두 곳에 기록한다.

```text
expires: key -> expire_at
expire_heap: (expire_at, key)
```

왜 두 곳에 저장할까?

`expires`는 특정 키의 만료 시간을 바로 찾기 위해 필요하다. `TTL key`가 들어왔을 때 이 해시맵을 보면 된다.

`expire_heap`은 전체 키 중 가장 빨리 만료될 키를 찾기 위해 필요하다. `DBSIZE`, `KEYS`, `INFO memory`처럼 전체 상태를 보여주는 명령에서는 `_purge_expired_keys`가 힙을 보며 만료된 키들을 정리한다.

이 프로젝트는 lazy deletion을 사용한다. 같은 키에 EXPIRE가 여러 번 실행되면 힙 안에 예전 만료 기록이 남을 수 있다. 대신 꺼낼 때 확인한다.

```text
힙에서 꺼낸 expire_at == expires에 저장된 현재 expire_at
```

둘이 같으면 진짜 만료다. 다르면 오래된 기록이므로 무시한다.

---

## 16장. 메모리와 LRU 제거 흐름

메모리 사용량은 `_entry_memory`에서 계산한다.

```python
len(key.encode("utf-8")) + len(value.encode("utf-8"))
```

영어 한 글자는 보통 1바이트다. 한글은 UTF-8에서 보통 3바이트다. 그래서 같은 글자 수라도 실제 바이트 수는 다를 수 있다.

`SET` 이후 `used_memory`가 `maxmemory`를 넘으면 `_evict_until_memory_fits`가 실행된다.

```text
1. maxmemory가 0이면 아무것도 하지 않는다.
2. used_memory가 maxmemory보다 크면 LRU tail을 본다.
3. tail에 있는 키를 삭제한다.
4. used_memory가 제한 이하가 될 때까지 반복한다.
```

삭제된 키는 `evicted_keys`에 누적된다. 사용자가 직접 `DEL`로 지운 것은 eviction이 아니므로 이 숫자에 포함하지 않는다.

---

## 17장. 에러는 어디에서 만들어지는가

Redis 스타일 출력도 중요한 부분이다. 잘못된 입력이 들어오면 프로그램은 정해진 형식으로 답한다.

알 수 없는 명령은 `execute`의 마지막 줄에서 처리된다.

```text
(error) ERR unknown command 'HELLO'
```

인자 개수 오류는 `_wrong_args`에서 만든다.

```text
(error) ERR wrong number of arguments for 'GET' command
```

정수로 바꿀 수 없는 값은 `_parse_int` 또는 `_parse_non_negative_int`가 잡는다.

```text
(error) ERR value is not an integer or out of range
```

메모리 제한을 넘는 단일 엔트리는 `SET`에서 OOM으로 거절된다.

```text
(error) OOM command not allowed when used_memory > 'maxmemory'
```

---

## 18장. 테스트 코드는 무엇을 확인하는가

`test_mini_redis.py`는 프로그램이 요구사항대로 움직이는지 확인한다.

`test_string_commands`는 기본 문자열 명령을 확인한다. `SET`, `GET`, `EXISTS`, `DBSIZE`, `DEL`이 한 흐름 안에서 제대로 동작하는지 본다.

`test_lru_eviction`은 메모리 제한을 걸고 세 개의 키를 넣는다. 제한을 넘었을 때 가장 오래 사용하지 않은 키가 삭제되는지 확인한다.

`test_ttl`은 키에 만료 시간을 걸고, 시간이 지난 뒤 `GET`과 `TTL`이 없는 키처럼 응답하는지 확인한다.

`test_del_treats_expired_key_as_missing`은 이미 만료된 키에 `DEL`을 실행했을 때 `(integer) 0`이 나오는지 확인한다.

`test_set_clears_ttl`은 기존 키를 `SET`으로 덮어쓸 때 TTL이 초기화되는지 확인한다.

`test_oom_single_entry`는 키 하나가 `maxmemory`보다 큰 경우 저장하지 않고 OOM을 반환하는지 확인한다.

자료구조 테스트도 있다. 해시맵이 확장 후에도 값을 잃지 않는지, 최소 힙이 작은 값부터 꺼내는지 확인한다.

---

## 19장. 실행 방법

Python 3.8 이상에서 실행한다.

```bash
python3 main.py
```

종료할 때는 다음 중 하나를 입력한다.

```text
exit
quit
```

테스트는 다음 명령으로 실행한다.

```bash
python3 -m unittest
```

---

## 20장. 예시 장면

```text
mini-redis> CONFIG SET maxmemory 30
OK
mini-redis> SET user:1 "Alice"
OK
mini-redis> SET user:2 "Bob"
OK
mini-redis> SET user:3 "Charlie"
OK
mini-redis> GET user:1
(nil)
mini-redis> INFO memory
used_memory:22
maxmemory:30
evicted_keys:1
mini-redis> KEYS
"user:2"
"user:3"
```

여기서 `user:1`은 가장 오래 사용되지 않은 키였기 때문에 메모리 제한을 맞추는 과정에서 삭제된다.

---

## 21장. 핵심을 다시 말해보기

해시맵은 키를 빠르게 찾기 위한 구조다. 충돌은 체이닝으로 해결했다.

이중 연결 리스트는 사용 순서를 빠르게 바꾸기 위한 구조다. 해시맵으로 노드를 바로 찾고, 리스트에서 바로 떼어 맨 앞으로 옮긴다. 그래서 LRU 갱신이 O(1)에 가깝게 동작한다.

힙은 가장 빨리 만료될 키를 빠르게 찾기 위한 구조다. 모든 키를 매번 훑지 않아도 된다.

Mini Redis는 이 세 구조를 함께 사용한다. 해시맵은 저장을 맡고, 이중 연결 리스트는 기억의 순서를 맡고, 힙은 시간의 순서를 맡는다. 작지만 Redis의 중요한 감각이 이 안에 들어 있다.
