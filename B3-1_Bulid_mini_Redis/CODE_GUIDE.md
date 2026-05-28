# 코드 설명 가이드

## 1. 이 문서의 목표

이 문서는 Mini Redis의 코드를 실제 실행 흐름에 맞춰 읽는 가이드다.

자료구조의 개념은 `DATA_STRUCTURE_GUIDE.md`에서 깊게 다룬다. 이 문서는 그 개념이 코드 안에서 어떻게 연결되는지 설명한다.

## 2. 전체 파일 역할

```text
main.py
  사용자의 입력을 받는 REPL

mini_redis.py
  Redis 명령어 처리, 메모리 관리, LRU, TTL 흐름

hash_map.py
  직접 구현한 체이닝 해시맵

doubly_linked_list.py
  LRU와 해시맵 버킷에 쓰는 이중 연결 리스트

min_heap.py
  TTL 만료 시간 관리를 위한 최소 힙

test_mini_redis.py
  주요 기능 검증 테스트
```

## 3. main.py 읽기

`main.py`는 프로그램의 입구다.

```python
redis = MiniRedis()
```

먼저 Mini Redis 객체를 하나 만든다. 이 객체 안에 실제 저장소, LRU 리스트, TTL 힙이 들어 있다.

그다음 무한 반복으로 입력을 받는다.

```python
line = input("mini-redis> ")
```

사용자가 `exit` 또는 `quit`을 입력하면 종료한다.

```python
if stripped.lower() == "exit" or stripped.lower() == "quit":
    break
```

그 외의 입력은 `execute`로 넘긴다.

```python
result = redis.execute(stripped)
```

`main.py`는 명령어의 의미를 알지 않는다. 입력을 받고, 결과를 출력하는 일만 한다.

## 4. MiniRedis 객체의 내부 상태

`mini_redis.py`의 `MiniRedis.__init__`을 보면 프로그램의 핵심 상태가 보인다.

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

`store`는 실제 데이터를 저장한다.

```text
key -> RedisEntry(value)
```

`lru`는 사용 순서를 저장한다.

```text
head: 최근 사용
tail: 오래 사용하지 않음
```

`lru_nodes`는 키가 LRU 리스트의 어느 노드에 있는지 저장한다.

```text
key -> ListNode
```

`expires`는 키의 현재 만료 시각을 저장한다.

```text
key -> expire_at
```

`expire_heap`은 가장 빠른 만료 후보를 찾기 위한 힙이다.

```text
(expire_at, key)
```

`used_memory`, `maxmemory`, `evicted_keys`는 메모리 정책을 위해 사용한다.

## 5. execute 흐름

모든 명령은 `execute`에서 시작한다.

```python
parts = shlex.split(line)
```

`shlex.split`은 따옴표로 감싼 문자열을 하나의 값으로 처리한다.

```text
SET user:1 "Alice Smith"
```

이 입력은 다음처럼 나뉜다.

```text
["SET", "user:1", "Alice Smith"]
```

명령어는 대문자로 바꾼다.

```python
command = parts[0].upper()
args = parts[1:]
```

그다음 명령어에 맞는 메서드로 보낸다.

```python
if command == "SET":
    return self._cmd_set(command, args)
```

모르는 명령어는 에러를 반환한다.

```python
return "(error) ERR unknown command '" + command + "'"
```

## 6. SET 코드 흐름

`SET key value`는 값을 저장한다. 이 명령은 가장 많은 일을 한다.

```python
if len(args) != 2:
    return self._wrong_args(command)
```

먼저 인자 개수를 확인한다. `SET`은 반드시 key와 value가 필요하다.

```python
key = args[0]
value = args[1]
self._delete_if_expired(key)
```

같은 키가 이미 있고 만료되었다면 먼저 삭제한다. 만료된 키는 없는 키처럼 다루기 위해서다.

```python
entry_memory = self._entry_memory(key, value)
```

새 데이터의 메모리 크기를 계산한다.

```python
if self.maxmemory > 0 and entry_memory > self.maxmemory:
    return "(error) OOM command not allowed when used_memory > 'maxmemory'"
```

단일 엔트리 자체가 최대 메모리보다 크면 저장하지 않는다.

새 키라면 다음 흐름으로 간다.

```python
self.used_memory += entry_memory
self.store.put(key, RedisEntry(value))
self._add_lru_key(key)
```

값을 저장하고, 메모리 사용량을 늘리고, LRU 맨 앞에 키를 넣는다.

기존 키라면 값을 덮어쓴다.

```python
self.used_memory -= self._entry_memory(key, old_entry.value)
self.used_memory += entry_memory
old_entry.value = value
self._touch_lru_key(key)
```

기존 값의 메모리는 빼고 새 값의 메모리는 더한다. 그리고 방금 사용한 키이므로 LRU 맨 앞으로 보낸다.

마지막으로 TTL을 초기화하고 메모리 제한을 맞춘다.

```python
self.expires.remove(key)
self._evict_until_memory_fits()
return "OK"
```

Redis 요구사항에 따라 기존 키를 `SET`으로 덮어쓰면 TTL은 사라진다.

## 7. GET 코드 흐름

`GET key`는 값을 조회한다.

```python
if self._delete_if_expired(key):
    return "(nil)"
```

먼저 만료 여부를 확인한다. 만료되었다면 삭제하고 `(nil)`을 반환한다.

```python
entry = self.store.get(key)
if entry is None:
    return "(nil)"
```

저장소에 키가 없으면 `(nil)`이다.

```python
self._touch_lru_key(key)
return '"' + entry.value + '"'
```

값이 있으면 LRU를 갱신하고 문자열을 반환한다. 조회도 사용이므로 LRU 순서가 바뀐다.

## 8. DEL 코드 흐름

`DEL key`는 키를 삭제한다.

```python
if self._delete_if_expired(args[0]):
    return "(integer) 0"
```

이미 만료된 키는 먼저 삭제되고, 사용자 입장에서는 없는 키처럼 보인다.

```python
removed = self._delete_key(args[0], count_eviction=False)
```

실제 삭제는 `_delete_key`에 맡긴다. 사용자가 직접 삭제한 것이므로 `count_eviction`은 `False`다.

삭제에 성공하면 `(integer) 1`, 키가 없으면 `(integer) 0`을 반환한다.

## 9. EXISTS, DBSIZE, KEYS

`EXISTS key`는 만료 여부를 먼저 확인한 뒤 `store.contains(key)`로 존재 여부를 본다.

`DBSIZE`는 `_purge_expired_keys()`로 만료된 키를 정리한 뒤 `store.size()`를 반환한다.

`KEYS`도 먼저 만료 키를 정리한다. 그다음 `store.keys()`로 모든 키를 가져와 한 줄씩 출력한다.

```python
keys = self.store.keys()
if len(keys) == 0:
    return "(empty array)"
```

이 프로젝트는 패턴 매칭은 구현하지 않는다.

## 10. CONFIG SET maxmemory

`CONFIG SET maxmemory bytes`는 최대 메모리를 설정한다.

```python
if len(args) != 3 or args[0].upper() != "SET" or args[1].lower() != "maxmemory":
    return self._wrong_args(command)
```

형식이 맞는지 확인한다.

```python
maxmemory = self._parse_non_negative_int(args[2])
```

음수나 정수가 아닌 값은 에러다.

```python
self.maxmemory = maxmemory
self._evict_until_memory_fits()
```

새 제한을 설정한 뒤, 현재 메모리가 제한을 넘고 있다면 LRU 제거를 실행한다.

## 11. INFO memory

`INFO memory`는 현재 메모리 상태를 출력한다.

```python
self._purge_expired_keys()
```

출력 전에 만료 키를 정리한다.

```python
return (
    "used_memory:" + str(self.used_memory) + "\n"
    + "maxmemory:" + str(self.maxmemory) + "\n"
    + "evicted_keys:" + str(self.evicted_keys)
)
```

최소 세 항목을 보여준다.

```text
used_memory
maxmemory
evicted_keys
```

## 12. EXPIRE 코드 흐름

`EXPIRE key seconds`는 키에 만료 시간을 설정한다.

```python
seconds = self._parse_int(args[1])
```

seconds가 정수가 아니면 에러다.

```python
self._delete_if_expired(key)
if not self.store.contains(key):
    return "(integer) 0"
```

없는 키에는 만료 시간을 설정할 수 없다.

```python
if seconds <= 0:
    self._delete_key(key, count_eviction=False)
    return "(integer) 1"
```

0 이하라면 즉시 만료로 처리한다.

```python
expire_at = time.time() + seconds
self.expires.put(key, expire_at)
self.expire_heap.push((expire_at, key))
```

정상적인 경우에는 만료 시각을 해시맵과 힙에 모두 저장한다.

## 13. TTL 코드 흐름

`TTL key`는 남은 만료 시간을 반환한다.

```python
self._delete_if_expired(key)
if not self.store.contains(key):
    return "(integer) -2"
```

키가 없으면 -2다.

```python
expire_at = self.expires.get(key)
if expire_at is None:
    return "(integer) -1"
```

키는 있지만 만료 시간이 없으면 -1이다.

```python
remaining = int(expire_at - time.time())
if remaining < 0:
    remaining = 0
return "(integer) " + str(remaining)
```

만료 시간이 있으면 남은 초를 반환한다.

## 14. 삭제 공통 함수

키 하나를 삭제할 때는 여러 자료구조를 함께 정리해야 한다.

```python
def _delete_key(self, key, count_eviction):
    entry = self.store.remove(key)
    if entry is None:
        return False

    self.used_memory -= self._entry_memory(key, entry.value)
    self.expires.remove(key)
    self._remove_lru_key(key)
    if count_eviction:
        self.evicted_keys += 1
    return True
```

삭제할 때 정리되는 것은 다음과 같다.

```text
store
expires
lru_nodes
lru
used_memory
evicted_keys
```

삭제 규칙을 한 함수에 모아두면 `DEL`, TTL 만료, LRU 제거가 같은 방식으로 안전하게 삭제할 수 있다.

## 15. LRU 관련 함수

새 키는 LRU 맨 앞에 들어간다.

```python
def _add_lru_key(self, key):
    node = self.lru.insert_front(key)
    self.lru_nodes.put(key, node)
```

기존 키가 사용되면 맨 앞으로 이동한다.

```python
def _touch_lru_key(self, key):
    node = self.lru_nodes.get(key)
    if node is None:
        self._add_lru_key(key)
        return
    new_node = self.lru.move_to_front(node)
    self.lru_nodes.put(key, new_node)
```

LRU에서 키를 제거할 때는 먼저 보조 해시맵에서 노드를 찾고, 실제 리스트에서 그 노드를 삭제한다.

```python
def _remove_lru_key(self, key):
    node = self.lru_nodes.remove(key)
    if node is not None:
        self.lru.remove_node(node)
```

## 16. 메모리 초과와 자동 제거

`_evict_until_memory_fits`는 메모리 제한을 만족할 때까지 LRU tail을 삭제한다.

```python
while self.used_memory > self.maxmemory:
    least_recent_key = self.lru.tail.data if self.lru.tail is not None else None
    if least_recent_key is None:
        break
    self._delete_key(least_recent_key, count_eviction=True)
```

tail은 가장 오래 사용하지 않은 키다. 그래서 tail부터 삭제하면 LRU 정책이 된다.

자동 삭제이므로 `count_eviction=True`를 넘긴다. 이때 `evicted_keys`가 증가한다.

## 17. TTL 정리와 lazy deletion

`_purge_expired_keys`는 힙을 보며 만료된 키를 정리한다.

```python
item = self.expire_heap.peek()
expire_at = item[0]
key = item[1]
if expire_at > now:
    break
```

힙의 맨 위가 아직 만료되지 않았다면 중단한다. 최소 힙에서는 맨 위가 가장 빠른 만료 시간이기 때문이다.

만료되었다면 꺼낸다.

```python
self.expire_heap.pop()
```

그리고 현재 `expires`에 저장된 만료 시각과 비교한다.

```python
current_expire_at = self.expires.get(key)
if current_expire_at is not None and current_expire_at == expire_at:
    self._delete_key(key, count_eviction=False)
```

같으면 진짜 만료다. 다르면 예전 EXPIRE 기록이므로 무시한다. 이것이 lazy deletion이다.

## 18. 자료구조 코드 읽기

### 18.1 hash_map.py

`HashMap`은 버킷 배열을 만들고, 각 버킷에 이중 연결 리스트를 둔다.

```python
self.buckets = self._make_buckets(capacity)
```

`_find_node`는 특정 키가 들어갈 버킷만 찾아서 그 안을 순회한다.

```python
bucket = self.buckets[self._bucket_index(key)]
current = bucket.head
```

`_resize`는 버킷 개수를 2배로 늘리고 기존 데이터를 다시 넣는다.

### 18.2 doubly_linked_list.py

`ListNode`는 `prev`, `next`, `data`를 가진다.

`insert_front`는 새 노드를 head로 만든다.

`remove_node`는 앞뒤 연결을 바꿔 특정 노드를 제거한다.

`move_to_front`는 노드를 제거한 뒤 같은 데이터를 앞에 다시 넣는다.

### 18.3 min_heap.py

`MinHeap`은 내부 배열 `items`를 사용한다.

`push`는 끝에 넣고 위로 올린다.

`pop`은 루트를 꺼내고 마지막 값을 루트로 옮긴 뒤 아래로 내린다.

`peek`은 가장 작은 값을 꺼내지 않고 확인한다.

## 19. 테스트 코드가 확인하는 것

`test_mini_redis.py`는 다음을 확인한다.

```text
기본 문자열 명령어
LRU 자동 삭제
TTL 만료
SET 시 TTL 초기화
단일 엔트리 OOM
해시맵 리사이징
최소 힙 정렬 순서
```

테스트는 다음 명령으로 실행한다.

```bash
python3 -m unittest
```

테스트를 먼저 읽고 코드를 보면 “이 코드는 어떤 동작을 보장해야 하는가”를 더 쉽게 이해할 수 있다.
