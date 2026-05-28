# Mini Redis

## 1. 미션 소개

Redis는 전 세계에서 널리 사용되는 In-Memory Key-Value 저장소다. 캐시, 세션 저장소, 메시지 브로커 등 여러 곳에서 쓰이며, 빠른 응답 속도로 유명하다.

하지만 Redis가 왜 빠른지 이해하려면 단순히 명령어를 사용하는 것만으로는 부족하다. Redis의 빠름은 내부 자료구조에서 나온다. 키를 빠르게 찾기 위한 해시맵, 최근 사용 순서를 관리하는 이중 연결 리스트, 만료 시간을 효율적으로 처리하는 힙 같은 구조가 함께 움직인다.

이 프로젝트는 Redis 전체를 구현하는 것이 아니다. Redis의 핵심 감각을 배우기 위한 CLI 기반 Mini Redis다. 네트워크 통신도 없고, 파일 저장도 없다. 대신 데이터가 메모리 안에서 어떻게 저장되고, 조회되고, 삭제되고, 만료되는지를 직접 구현 코드로 확인한다.

## 2. 최종 결과물

사용자가 명령어를 입력하면 즉시 결과를 확인할 수 있는 REPL 프로그램을 완성한다.

```text
mini-redis> SET user:1 "Alice"
OK
mini-redis> GET user:1
"Alice"
```

지원하는 명령어는 다음과 같다.

```text
SET key value
GET key
DEL key
EXISTS key
DBSIZE
KEYS
CONFIG SET maxmemory bytes
INFO memory
EXPIRE key seconds
TTL key
```

종료는 `exit` 또는 `quit`으로 한다.

## 3. 파일 구성

```text
.
├── main.py
├── mini_redis.py
├── hash_map.py
├── doubly_linked_list.py
├── min_heap.py
├── test_mini_redis.py
├── README.md
├── DATA_STRUCTURE_GUIDE.md
└── CODE_GUIDE.md
```

`README.md`는 미션 설명과 프로그램 흐름을 다룬다.

`DATA_STRUCTURE_GUIDE.md`는 해시맵, 이중 연결 리스트, 최소 힙을 처음부터 공부하기 위한 문서다.

`CODE_GUIDE.md`는 실제 코드가 어떤 순서로 실행되는지 따라 읽는 문서다.

## 4. 실행 방법

Python 3.8 이상에서 실행한다.

```bash
python3 main.py
```

테스트는 다음 명령으로 실행한다.

```bash
python3 -m unittest
```

## 5. 프로그램 전체 흐름

프로그램은 네 단계로 움직인다.

```text
사용자 입력
  ↓
main.py
  ↓
MiniRedis.execute()
  ↓
명령어별 처리 메서드
  ↓
직접 구현한 자료구조
```

`main.py`는 사용자 입력을 받는다.

```python
line = input("mini-redis> ")
```

입력된 문자열은 `MiniRedis.execute()`로 전달된다. 이 메서드는 입력을 명령어와 인자로 나눈다.

```text
SET user:1 "Alice"
```

위 입력은 다음처럼 해석된다.

```text
command = SET
args = ["user:1", "Alice"]
```

그다음 명령어에 맞는 메서드가 실행된다.

```text
SET     -> _cmd_set
GET     -> _cmd_get
DEL     -> _cmd_del
EXPIRE  -> _cmd_expire
TTL     -> _cmd_ttl
```

명령어 메서드는 직접 만든 자료구조를 사용한다.

```text
HashMap              실제 key-value 저장
DoublyLinkedList     LRU 사용 순서 관리
MinHeap              TTL 만료 시간 관리
```

## 6. 핵심 자료구조의 역할

Mini Redis는 세 가지 자료구조를 중심으로 동작한다.

첫째, 해시맵은 키로 값을 빠르게 찾기 위해 사용한다. `GET user:1`이 들어왔을 때 모든 키를 처음부터 훑지 않고, 해시 함수를 이용해 저장 위치를 찾아간다.

둘째, 이중 연결 리스트는 LRU 순서를 관리하기 위해 사용한다. 가장 최근에 사용한 키는 앞쪽에, 가장 오래 사용하지 않은 키는 뒤쪽에 둔다. 메모리가 초과되면 뒤쪽 키부터 삭제한다.

셋째, 최소 힙은 TTL 만료 시간을 관리하기 위해 사용한다. 가장 빨리 만료될 키가 힙의 맨 위에 오므로, 전체 키를 매번 확인하지 않아도 된다.

## 7. 메모리 관리 흐름

메모리 사용량은 다음 공식으로 계산한다.

```text
used_memory = 모든 key와 value의 UTF-8 바이트 길이 합
```

자료구조 자체의 오버헤드는 계산하지 않는다. 학습 목적상 키와 값의 크기만 다룬다.

`CONFIG SET maxmemory bytes`로 최대 메모리를 설정할 수 있다. `bytes`가 0이면 제한이 없다는 뜻이다.

```text
mini-redis> CONFIG SET maxmemory 30
OK
```

`SET` 이후 `used_memory`가 `maxmemory`를 넘으면 LRU 정책이 실행된다. 가장 오래 사용하지 않은 키부터 삭제하고, 메모리 사용량이 제한 이하가 될 때까지 반복한다.

단일 키와 값의 크기 자체가 `maxmemory`보다 크면 저장하지 않고 OOM 에러를 반환한다.

```text
(error) OOM command not allowed when used_memory > 'maxmemory'
```

## 8. TTL 관리 흐름

`EXPIRE key seconds`는 키에 만료 시간을 설정한다.

```text
mini-redis> EXPIRE user:1 3
(integer) 1
```

내부에서는 현재 시간에 seconds를 더한 `expire_at`을 만든다.

```text
expires: key -> expire_at
expire_heap: (expire_at, key)
```

`TTL key`는 남은 시간을 반환한다.

```text
키가 없으면                 (integer) -2
키는 있지만 TTL이 없으면     (integer) -1
TTL이 있으면                (integer) N
```

만료된 키는 키 기반 명령을 실행하기 전에 먼저 삭제된다. 그래서 만료된 키는 없는 키처럼 처리된다.

## 9. 출력 형식

출력은 Redis 스타일을 따른다.

```text
성공                         OK
없는 값                      (nil)
정수 응답                    (integer) N
에러                         (error) ...
문자열 값                    "value"
```

예시:

```text
mini-redis> GET user:1
(nil)
mini-redis> SET user:1 "Alice"
OK
mini-redis> GET user:1
"Alice"
```

## 10. 실행 예시

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

여기서 `user:1`은 가장 오래 사용하지 않은 키였기 때문에 메모리 제한을 맞추는 과정에서 삭제된다.

## 11. 학습 순서 추천

처음 읽는다면 다음 순서가 좋다.

```text
1. README.md
2. DATA_STRUCTURE_GUIDE.md
3. CODE_GUIDE.md
4. test_mini_redis.py
```

먼저 프로그램이 무엇을 하는지 이해한다. 그다음 자료구조를 배운다. 마지막으로 실제 코드가 그 개념을 어떻게 사용하는지 따라가면 된다.
