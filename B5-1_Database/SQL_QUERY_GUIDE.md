# `queries.sql` 쿼리 해설서

이 문서는 `queries.sql`에 들어 있는 SQL을 하나씩 읽기 위한 해설서이다. SQL을 외우는 것보다 중요한 일은 쿼리가 어떤 질문에 답하고 있는지 이해하는 것이다. 데이터베이스 쿼리는 결국 “데이터에게 묻는 질문”이다.

## 1. 쿼리를 읽는 기본 순서

SQL은 보통 `SELECT`부터 적지만, 데이터베이스가 쿼리를 이해하는 논리적 순서는 `SELECT`가 먼저가 아니다. 먼저 어느 테이블에서 데이터를 가져올지 정하고, 필요한 테이블을 붙이고, 조건에 맞지 않는 행을 걸러 낸 뒤, 그룹을 만들고, 마지막에 보여 줄 컬럼을 고른다고 생각하면 쉽다.

작성 순서는 보통 다음과 같다.

```sql
SELECT 보여줄_컬럼
FROM 기준_테이블
JOIN 연결할_테이블 ON 연결_조건
WHERE 행_필터
GROUP BY 그룹_기준
HAVING 그룹_필터
ORDER BY 정렬_기준
LIMIT 개수;
```

하지만 읽고 이해할 때는 다음 순서가 더 자연스럽다.

1. `FROM`: 어느 테이블에서 시작하는가.
2. `JOIN`: 어떤 테이블을 연결하는가.
3. `WHERE`: 어떤 행만 남기는가.
4. `GROUP BY`: 어떤 기준으로 묶는가.
5. `HAVING`: 그룹 결과 중 어떤 그룹만 남기는가.
6. `SELECT`: 어떤 컬럼이나 계산 결과를 보여 주는가.
7. `ORDER BY`: 어떤 순서로 정렬하는가.
8. `LIMIT`: 몇 개만 보여 주는가.

이 순서로 읽으면 긴 쿼리도 덜 어렵다.

이 문서의 시각화에서는 다음 표시를 사용한다.

| 표시 | 의미 |
| --- | --- |
| `->` | 다음 단계로 데이터가 흘러간다. |
| `+` | JOIN으로 컬럼이 옆으로 붙는다. |
| `NULL` | 연결되는 값이 없어서 빈칸으로 남는다. |
| `COUNT`, `SUM`, `AVG` | 여러 행을 묶은 뒤 계산한다. |
| `AS 이름` | 결과 컬럼이나 테이블에 읽기 쉬운 별명을 붙인다. |

쿼리를 볼 때는 "SQL이 어떻게 적혀 있는가"와 "데이터가 어떤 순서로 처리되는가"를 나누어 보면 좋다.

```text
작성 순서
SELECT -> FROM -> JOIN -> WHERE -> GROUP BY -> HAVING -> ORDER BY -> LIMIT

이해 순서
FROM -> JOIN -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT
```

같은 내용을 데이터의 모양 변화로 보면 다음과 같다.

```text
+--------------------+     +--------------------+     +--------------------+
| 1. FROM            | --> | 2. JOIN            | --> | 3. WHERE           |
| 시작 테이블 선택       |     | 필요한 표 붙이기       |     | 필요한 행만 남김       |
+--------------------+     +--------------------+     +--------------------+
          |                          |                          |
          v                          v                          v
     행과 컬럼의 출발점        컬럼이 옆으로 늘어남        행 수가 줄어들 수 있음

+--------------------+     +--------------------+     +--------------------+
| 4. GROUP BY        | --> | 5. SELECT          | --> | 6. ORDER BY/LIMIT  |
| 같은 값끼리 묶기             | 보여 줄 모양 결정      |     | 순서와 개수 결정       |
+--------------------+     +--------------------+     +--------------------+
          |                          |                          |
          v                          v                          v
     여러 행이 한 그룹이 됨        계산 컬럼과 별칭 생성            최종 결과표 완성
```

여기서 말하는 순서는 "논리적으로 이해하는 순서"이다. 즉 SQL을 읽을 때는 `FROM`과 `JOIN`으로 데이터 범위를 먼저 만들고, `WHERE`로 행을 걸러 낸 뒤, `SELECT`로 보여 줄 컬럼을 고른다고 생각하면 쉽다.

하지만 실제 데이터베이스 내부에서 항상 이 순서대로 물리적인 작업이 일어나는 것은 아니다. 특히 테이블 2개를 JOIN한다고 해서, 두 테이블을 합친 거대한 결과표가 반드시 메모리에 통째로 만들어지고, 그다음에야 `SELECT`가 실행되는 것은 아니다.

학습할 때는 다음처럼 "가상의 중간 결과"를 떠올리면 좋다.

```text
FROM cafe_order
JOIN customer
    |
    v
가상의 조인 결과
cafe_order 컬럼 + customer 컬럼
    |
    v
WHERE로 필요한 행만 남김
    |
    v
SELECT로 보여 줄 컬럼만 선택
```

예를 들어 다음 쿼리가 있다고 하자.

```sql
SELECT o.order_id, c.name
FROM cafe_order AS o
INNER JOIN customer AS c ON o.customer_id = c.customer_id;
```

개념적으로는 먼저 주문과 고객이 `customer_id`로 연결된 중간 결과를 생각할 수 있다.

```text
가상의 조인 결과
+----------+-------------+--------+---------------------+
| order_id | customer_id | name   | email               |
+----------+-------------+--------+---------------------+
| 1        | 1           | 김민준 | minjun@example.com  |
| 2        | 3           | 박도윤 | doyoon@example.com  |
+----------+-------------+--------+---------------------+

SELECT o.order_id, c.name

최종 결과
+----------+--------+
| order_id | name   |
+----------+--------+
| 1        | 김민준 |
| 2        | 박도윤 |
+----------+--------+
```

다만 실제 실행에서는 데이터베이스의 옵티마이저가 더 효율적인 방법을 고른다. 전체 조인 결과를 메모리에 모두 만든 뒤 컬럼을 버리는 방식이 아니라, 인덱스로 필요한 행을 찾거나, 필요한 컬럼만 읽거나, 조건을 먼저 적용하거나, 임시 테이블을 일부만 사용하는 식으로 처리할 수 있다.

정리하면 다음과 같다.

| 관점 | 설명 |
| --- | --- |
| 학습용 이해 | JOIN 결과가 먼저 만들어지고, `SELECT`가 그중 보여 줄 컬럼을 고른다고 생각한다. |
| 실제 실행 | 데이터베이스가 실행 계획을 세워 전체 조인 결과를 만들지 않고도 결과를 만들 수 있다. |

따라서 `SELECT`는 "논리적으로 결과 컬럼을 결정하는 뒤쪽 단계"라고 이해하면 된다. 다만 `ORDER BY`, `LIMIT`은 `SELECT` 결과를 다시 정렬하거나 일부만 보여 주는 단계이므로 `SELECT` 뒤에 온다고 볼 수 있다.

예를 들어 다음 쿼리를 보자.

```sql
SELECT o.payment_method, SUM(od.quantity * od.unit_price) AS total_sales
FROM cafe_order AS o
INNER JOIN order_detail AS od ON o.order_id = od.order_id
WHERE o.order_status <> 'CANCELED'
GROUP BY o.payment_method
ORDER BY total_sales DESC;
```

이 쿼리는 화면에는 `SELECT`가 먼저 보이지만, 머릿속에서는 다음 순서로 읽는다.

```text
+------+-----------------------------------------+------------------------------+
| 순서 | 읽을 부분                               | 머릿속 질문                  |
+------+-----------------------------------------+------------------------------+
| 1    | FROM cafe_order AS o                    | 주문 테이블에서 시작하는가?  |
| 2    | JOIN order_detail AS od                 | 주문 상세를 어떻게 붙이는가? |
| 3    | WHERE o.order_status <> 'CANCELED'      | 어떤 주문을 제외하는가?      |
| 4    | GROUP BY o.payment_method               | 무엇별로 묶는가?             |
| 5    | SELECT payment_method, SUM(...)         | 무엇을 보여 주고 계산하는가? |
| 6    | ORDER BY total_sales DESC               | 어떤 순서로 보여 주는가?     |
+------+-----------------------------------------+------------------------------+
```

실행 순서를 더 친절하게 시각화하면 다음과 같다.

```text
+-------------------------------+
| FROM cafe_order               |
| 주문 한 건당 1행에서 시작           |
+---------------+---------------+
                |
                v
+-------------------------------+
| JOIN order_detail             |
| 주문의 메뉴 줄이 옆에 붙음          |
| 주문 1건이 여러 행으로 늘 수        |
| 있음                          |
+---------------+---------------+
                |
                v
+-------------------------------+
| WHERE order_status <> CANCELED |
| 취소 주문 행을 제거                |
+---------------+---------------+
                |
                v
+-------------------------------+
| GROUP BY payment_method       |
| CARD, CASH, MOBILE별 묶음 생성   |
+---------------+---------------+
                |
                v
+-------------------------------+
| SELECT payment_method, SUM    |
| 그룹별 줄 금액 합계 계산            |
+---------------+---------------+
                |
                v
+-------------------------------+
| ORDER BY total_sales DESC     |
| 매출이 큰 결제수단부터 표시          |
+-------------------------------+
```

주의할 점은 `WHERE`가 `GROUP BY`보다 먼저 실행된다는 것이다. `WHERE`는 아직 그룹이 만들어지기 전의 개별 행을 걸러 낸다. 반대로 `HAVING`은 그룹을 만든 뒤의 결과를 걸러 낸다.

| 구분 | 필터링 대상 | 예시 질문 |
| --- | --- | --- |
| `WHERE` | 그룹이 만들어지기 전의 개별 행 | 취소되지 않은 주문만 남길까? |
| `HAVING` | `GROUP BY`로 만들어진 그룹 결과 | 주문 수가 3건 이상인 결제수단만 남길까? |

```sql
SELECT payment_method, COUNT(*) AS order_count
FROM cafe_order
GROUP BY payment_method
HAVING COUNT(*) >= 3;
```

위 쿼리에서 `HAVING COUNT(*) >= 3`은 결제수단별로 묶은 뒤, 주문 수가 3건 이상인 그룹만 남긴다는 뜻이다. 개별 주문 행을 필터링하는 조건이 아니므로 `WHERE`가 아니라 `HAVING`을 사용한다.

```text
개별 주문 행
CARD, CARD, CARD, CASH, MOBILE

GROUP BY payment_method
CARD 그룹: 3행
CASH 그룹: 1행
MOBILE 그룹: 1행

HAVING COUNT(*) >= 3
CARD 그룹만 남음
```

## 2. 쿼리 01: 판매 중이고 6,000원 미만인 메뉴 조회

```sql
SELECT menu_item_id, name, price
FROM menu_item
WHERE is_available = TRUE AND price < 6000
ORDER BY price ASC;
```

이 쿼리는 판매 가능한 메뉴 중 가격이 6,000원 미만인 메뉴를 찾는다.

`FROM menu_item`은 메뉴 테이블에서 데이터를 읽겠다는 뜻이다. `WHERE is_available = TRUE`는 판매 중인 메뉴만 남긴다. `price < 6000`은 가격이 6,000원보다 작은 메뉴만 남긴다. 두 조건 사이의 `AND`는 두 조건을 모두 만족해야 한다는 뜻이다.

`ORDER BY price ASC`는 가격이 낮은 메뉴부터 높은 메뉴 순서로 정렬한다. `ASC`는 오름차순이다.

이 쿼리에서 익힐 개념은 `WHERE`, 비교 연산자, 논리 연산자 `AND`, 정렬이다.

개념을 조금 더 나누어 보면 다음과 같다.

| 부분 | 역할 | 이 쿼리에서의 의미 |
| --- | --- | --- |
| `WHERE` | 결과에 남길 행을 고른다. | 판매 중이고 가격이 낮은 메뉴만 남긴다. |
| `= TRUE` | 참/거짓 값 중 참을 고른다. | 판매 가능한 메뉴만 고른다. |
| `< 6000` | 기준값보다 작은 값을 고른다. | 6,000원 미만 메뉴만 고른다. |
| `AND` | 조건을 모두 만족해야 한다. | 판매 중이면서 동시에 6,000원 미만이어야 한다. |
| `ORDER BY price ASC` | 결과를 정렬한다. | 가격이 낮은 순서로 보여 준다. |

```text
menu_item 전체
    |
    v
is_available = TRUE
판매 중인 메뉴만 남김
    |
    v
price < 6000
6,000원 미만만 남김
    |
    v
ORDER BY price ASC
낮은 가격부터 정렬
```

`WHERE`의 조건은 행마다 한 번씩 검사된다. 어떤 메뉴가 조건을 만족하면 결과에 남고, 만족하지 않으면 결과에서 빠진다.

## 3. 쿼리 02: 최신 주문 5건 조회

```sql
SELECT order_id, customer_id, order_status, ordered_at, payment_method
FROM cafe_order
ORDER BY ordered_at DESC
LIMIT 5;
```

이 쿼리는 최근에 들어온 주문 5건을 조회한다.

`ORDER BY ordered_at DESC`는 주문 시각을 기준으로 최신순 정렬한다. `DESC`는 내림차순이다. 날짜와 시간에서 내림차순은 더 나중 시간이 먼저 나온다는 뜻이다.

`LIMIT 5`는 정렬된 결과 중 앞의 5개만 보여 준다. 실제 서비스에서 최근 주문 목록, 최근 게시글, 최근 결제 내역을 보여 줄 때 자주 쓰이는 방식이다.

여기서 중요한 점은 `LIMIT`보다 `ORDER BY`를 먼저 생각해야 한다는 것이다. 먼저 전체 주문을 최신순으로 세운 뒤, 그중 맨 위 5건만 자른다.

```text
cafe_order 전체 주문
    |
    v
ORDER BY ordered_at DESC
가장 늦은 주문 시각이 위로 올라옴
    |
    v
LIMIT 5
위에서부터 5행만 남김
```

만약 `ORDER BY` 없이 `LIMIT 5`만 사용하면 "최근 5건"이라는 의미가 되지 않는다. 데이터베이스가 어떤 5행을 먼저 읽었는지에 따라 결과가 달라질 수 있기 때문이다. 그래서 "최신", "가장 비싼", "가장 많이 팔린"처럼 순위가 있는 질문은 보통 `ORDER BY`와 `LIMIT`을 함께 사용한다.

## 4. 쿼리 03: 특정 이메일 도메인을 가진 고객 조회

```sql
SELECT customer_id, name, email, joined_at
FROM customer
WHERE email LIKE '%@example.com'
ORDER BY joined_at ASC;
```

이 쿼리는 이메일이 `@example.com`으로 끝나는 고객을 찾는다.

`LIKE`는 문자열 패턴을 검색할 때 사용한다. `%`는 어떤 문자열이든 올 수 있다는 뜻이다. 따라서 `'%@example.com'`은 앞에는 무엇이 오든 상관없고, 마지막이 `@example.com`이면 된다는 의미이다.

`ORDER BY joined_at ASC`는 가입일이 오래된 고객부터 보여 준다.

이 쿼리에서 익힐 개념은 패턴 검색과 와일드카드 `%`이다.

`LIKE`에서 자주 쓰는 패턴은 다음과 같다.

| 패턴 | 의미 | 예시 |
| --- | --- | --- |
| `'abc%'` | `abc`로 시작하는 문자열 | `abc@example.com` |
| `'%abc'` | `abc`로 끝나는 문자열 | `user-abc` |
| `'%abc%'` | 중간 어딘가에 `abc`가 들어 있는 문자열 | `my-abc-user` |
| `'a_c'` | `a`와 `c` 사이에 글자 하나가 있는 문자열 | `abc`, `a1c` |

이 쿼리의 `'%@example.com'`은 앞부분은 무엇이든 허용하지만 끝은 반드시 `@example.com`이어야 한다.

```text
minjun@example.com      남김
seoyeon@example.com     남김
doyoon@test.com         제외
```

`%`가 앞에 붙으면 앞부분이 길어도 상관없다는 뜻이다. 대신 찾을 범위가 넓어질 수 있으므로, 큰 테이블에서는 패턴 모양에 따라 검색 성능이 달라질 수 있다.

## 5. 쿼리 04: 아직 주의가 필요한 주문 조회

```sql
SELECT order_id, customer_id, order_status, ordered_at
FROM cafe_order
WHERE order_status IN ('ORDERED', 'CANCELED')
ORDER BY ordered_at;
```

이 쿼리는 주문 상태가 `ORDERED` 또는 `CANCELED`인 주문을 찾는다.

`IN`은 여러 값 중 하나에 해당하는지를 확인한다. 다음 조건과 의미가 같다.

```sql
order_status = 'ORDERED' OR order_status = 'CANCELED'
```

`ORDERED`는 아직 처리 중인 주문이고, `CANCELED`는 취소된 주문이다. 실무에서는 이런 상태를 따로 확인하여 후속 처리를 할 수 있다.

`IN`은 비교할 값이 여러 개일 때 쿼리를 읽기 쉽게 만든다.

```text
order_status
ORDERED    -> 목록 안에 있음 -> 남김
PAID       -> 목록 안에 없음 -> 제외
CANCELED   -> 목록 안에 있음 -> 남김
COMPLETED  -> 목록 안에 없음 -> 제외
```

값이 두세 개일 때는 `OR`로 써도 되지만, 값이 많아질수록 `IN (...)`이 더 읽기 쉽다. 반대로 목록에 없는 값만 찾고 싶다면 `NOT IN (...)`을 사용할 수 있다.

## 6. 쿼리 05: 주문 목록에 고객 이름 붙이기

```sql
SELECT o.order_id, c.name AS customer_name, o.order_status, o.ordered_at
FROM cafe_order AS o
INNER JOIN customer AS c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

이 쿼리는 주문 목록을 보여 주되, 고객 ID만 보여 주지 않고 고객 이름까지 함께 보여 준다.

`cafe_order`에는 `customer_id`만 저장되어 있다. 고객 이름은 `customer` 테이블에 있다. 따라서 두 테이블을 `customer_id` 기준으로 연결해야 한다.

`AS o`, `AS c`는 테이블 별칭이다. 긴 테이블 이름을 짧게 줄여 쿼리를 읽기 쉽게 만든다.

```text
o.customer_id = c.customer_id
```

이 조건은 주문 테이블의 고객 번호와 고객 테이블의 고객 번호가 같은 행끼리 연결하라는 뜻이다.

`INNER JOIN`은 양쪽에 매칭되는 데이터가 있는 행만 보여 준다.

흐름 일부를 샘플 데이터로 시각화하면 다음과 같다.

```text
cafe_order AS o                  customer AS c
+----------+-------------+       +-------------+--------+
| order_id | customer_id |       | customer_id | name   |
+----------+-------------+       +-------------+--------+
| 1        | 1           | ----> | 1           | 김민준 |
| 2        | 3           | ----> | 3           | 박도윤 |
| 3        | 1           | ----> | 1           | 김민준 |
+----------+-------------+       +-------------+--------+

ON o.customer_id = c.customer_id

결과
+----------+---------------+--------------+---------------------+
| order_id | customer_name | order_status | ordered_at          |
+----------+---------------+--------------+---------------------+
| 1        | 김민준        | COMPLETED    | 2026-03-01 09:10:00 |
| 2        | 박도윤        | PAID         | 2026-03-01 10:20:00 |
| 3        | 김민준        | ORDERED      | 2026-03-01 11:30:00 |
+----------+---------------+--------------+---------------------+
```

주문 테이블의 한 행이 고객 테이블의 한 행을 찾아 붙는다. 그래서 결과에는 주문 정보와 고객 이름이 한 줄에 함께 나온다.

JOIN을 읽을 때는 세 가지를 확인하면 좋다.

| 확인할 것 | 이 쿼리의 답 |
| --- | --- |
| 기준 테이블은 무엇인가? | `cafe_order AS o` |
| 어떤 테이블을 붙이는가? | `customer AS c` |
| 어떤 값이 같아야 붙는가? | `o.customer_id = c.customer_id` |

`INNER JOIN`은 "양쪽 모두에 짝이 있는 행"만 남긴다. 주문에 적힌 `customer_id`가 고객 테이블에 없다면 그 주문은 결과에서 빠진다. 이 프로젝트에서는 FK가 있어서 그런 잘못된 주문이 저장되지 않지만, `INNER JOIN`의 기본 성격은 이렇게 이해하면 된다.

```text
주문 행                       고객 행
customer_id = 1      +        customer_id = 1      -> 결과에 남음
customer_id = 99     +        매칭 없음             -> INNER JOIN에서는 빠짐
```

현재 샘플 데이터에서는 `cafe_order`의 모든 `customer_id`가 실제 `customer`에 존재한다. 그래서 이 쿼리의 결과는 주문 10건이 모두 남고, 각 주문 옆에 고객 이름이 붙는다. `INNER JOIN`의 핵심은 행 수를 무조건 늘리거나 줄이는 것이 아니라, `ON` 조건으로 짝을 찾은 행만 결과에 남긴다는 점이다.

```text
+----------+---------------+--------------+---------------------+
| order_id | customer_name | order_status | ordered_at          |
+----------+---------------+--------------+---------------------+
| 1        | Kim Minjun    | COMPLETED    | 2026-03-01 09:10:00 |
| 2        | Lee Seoyeon   | COMPLETED    | 2026-03-01 12:30:00 |
| 3        | Park Jiho     | PAID         | 2026-03-02 14:05:00 |
| ...      | ...           | ...          | ...                 |
+----------+---------------+--------------+---------------------+
```

`AS customer_name`처럼 컬럼 별칭을 붙이면 결과표의 제목이 더 읽기 좋아진다. 특히 `customer.name`, `menu_item.name`, `menu_category.name`처럼 여러 테이블에 같은 컬럼명이 있을 때 별칭이 유용하다.

## 7. 쿼리 06: 주문 상세와 메뉴명, 줄 금액 조회

```sql
SELECT od.order_detail_id, od.order_id, mi.name AS menu_name,
       od.quantity, od.unit_price, od.quantity * od.unit_price AS line_total
FROM order_detail AS od
INNER JOIN menu_item AS mi ON od.menu_item_id = mi.menu_item_id
ORDER BY od.order_detail_id;
```

이 쿼리는 주문 상세 한 줄마다 메뉴명과 금액을 계산해서 보여 준다.

`order_detail`에는 `menu_item_id`가 있지만 메뉴 이름은 없다. 메뉴 이름은 `menu_item`에 있으므로 두 테이블을 조인한다.

```sql
od.quantity * od.unit_price AS line_total
```

이 부분은 수량과 단가를 곱해 한 줄의 금액을 계산한다. `AS line_total`은 계산 결과에 이름을 붙이는 것이다.

이 쿼리에서 중요한 점은 데이터베이스가 저장된 값만 보여 주는 것이 아니라, 저장된 값을 이용해 계산한 결과도 보여 줄 수 있다는 점이다.

간단한 예시로 흐름을 시각화하면 다음과 같다.

1단계: `order_detail`에서 주문 상세 정보를 읽는다.

```text
order_detail
+-----------+----------+--------------+-----+----------+
| detail_id | order_id | menu_item_id | qty | unit     |
+-----------+----------+--------------+-----+----------+
| 1         | 1        | 2            | 2   | 4500.00  |
| 2         | 1        | 5            | 1   | 6500.00  |
+-----------+----------+--------------+-----+----------+
```

2단계: `menu_item_id`가 같은 메뉴 행을 찾는다.

```text
ON od.menu_item_id = mi.menu_item_id

+-----------------+----+-----------------+------------+
| od.menu_item_id |    | mi.menu_item_id | mi.name    |
+-----------------+----+-----------------+------------+
| 2               | =  | 2               | 카페라떼   |
| 5               | =  | 5               | 치즈케이크 |
+-----------------+----+-----------------+------------+
```

3단계: JOIN 후 메뉴 이름을 붙이고 줄 금액을 계산한다.

```text
line_total = quantity * unit_price

+-----------+----------+------------+-----+----------+------------+
| detail_id | order_id | menu_name  | qty | unit     | line_total |
+-----------+----------+------------+-----+----------+------------+
| 1         | 1        | 카페라떼   | 2   | 4500.00  | 9000.00    |
| 2         | 1        | 치즈케이크 | 1   | 6500.00  | 6500.00    |
+-----------+----------+------------+-----+----------+------------+
```

`order_detail`은 "무엇을 몇 개 샀는지"를 알고 있고, `menu_item`은 "그 메뉴 이름이 무엇인지"를 알고 있다. JOIN 후에 두 정보가 한 줄로 합쳐지고, 마지막에 줄 금액이 계산된다.

이 쿼리에서는 저장된 컬럼과 계산된 컬럼이 함께 나온다.

| 컬럼 | 어디에서 오는가 | 의미 |
| --- | --- | --- |
| `od.quantity` | `order_detail`에 저장된 값 | 주문 수량 |
| `od.unit_price` | `order_detail`에 저장된 값 | 주문 당시 단가 |
| `mi.name` | `menu_item`에서 JOIN으로 붙인 값 | 메뉴 이름 |
| `line_total` | `quantity * unit_price` 계산 결과 | 주문 상세 한 줄의 금액 |

`line_total`은 테이블에 직접 저장된 컬럼이 아니라 조회 순간에 계산되는 값이다. 이런 계산 컬럼은 결과를 읽기 쉽게 만들지만, 쿼리가 끝난 뒤 테이블 구조가 바뀌는 것은 아니다.

```text
저장된 값
quantity = 2
unit_price = 4500.00

조회 중 계산
2 * 4500.00 = 9000.00

결과 컬럼
line_total = 9000.00
```

## 8. 쿼리 07: 메뉴 목록에 카테고리명 붙이기

```sql
SELECT mi.menu_item_id, mi.name AS menu_name, mc.name AS category_name, mi.price
FROM menu_item AS mi
INNER JOIN menu_category AS mc ON mi.category_id = mc.category_id
ORDER BY mi.menu_item_id;
```

이 쿼리는 메뉴 목록을 보여 주면서, 메뉴가 속한 카테고리 이름도 함께 보여 준다.

`menu_item`에는 `category_id`만 저장되어 있다. 카테고리 이름은 `menu_category` 테이블에 있다. 그래서 두 테이블을 `category_id` 기준으로 연결한다.

```text
mi.category_id = mc.category_id
```

이 조건은 메뉴 테이블의 카테고리 번호와 카테고리 테이블의 카테고리 번호가 같은 행끼리 붙이라는 뜻이다.

```text
menu_item                         menu_category
+--------------+-------------+    +-------------+--------+
| name         | category_id |    | category_id | name   |
+--------------+-------------+    +-------------+--------+
| Americano    | 1           | -> | 1           | Coffee |
| Cheesecake   | 3           | -> | 3           | Dessert|
+--------------+-------------+    +-------------+--------+

결과
+--------------+------------+---------------+---------+
| menu_item_id | menu_name  | category_name | price   |
+--------------+------------+---------------+---------+
| 1            | Americano  | Coffee        | 4500.00 |
| 7            | Cheesecake | Dessert       | 6800.00 |
+--------------+------------+---------------+---------+
```

이 쿼리의 핵심은 "ID만 저장된 곳에 이름을 붙인다"이다. 테이블을 나누어 저장하면 메뉴 테이블에 카테고리명을 반복해서 적지 않아도 되고, 필요할 때 JOIN으로 카테고리명을 가져올 수 있다.

JOIN을 읽을 때는 다음 세 가지만 먼저 보면 된다.

| 확인할 것 | 이 쿼리의 답 |
| --- | --- |
| 기준 테이블 | `menu_item AS mi` |
| 붙이는 테이블 | `menu_category AS mc` |
| 연결 조건 | `mi.category_id = mc.category_id` |

## 9. 쿼리 08: 주문이 없는 고객까지 포함한 주문 수 조회

```sql
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY order_count ASC, c.customer_id;
```

이 쿼리는 고객별 주문 수를 구한다. 중요한 점은 주문이 없는 고객도 결과에 포함한다는 것이다.

그래서 `INNER JOIN`이 아니라 `LEFT JOIN`을 사용한다. `customer`를 왼쪽에 두었기 때문에 모든 고객이 결과에 남는다. 주문이 없는 고객은 `o.order_id`가 `NULL`이 된다.

`COUNT(o.order_id)`는 `NULL`이 아닌 주문 ID만 센다. 따라서 주문이 없는 고객의 주문 수는 0으로 계산된다.

`GROUP BY c.customer_id, c.name`은 고객별로 묶겠다는 뜻이다.

샘플 데이터 기준으로 결과를 읽으면 핵심은 `Oh Eunwoo`이다. `Oh Eunwoo`는 고객 테이블에는 있지만 주문 테이블에는 등장하지 않는다. 그래도 `LEFT JOIN`을 사용했기 때문에 결과에 남고, 주문 수는 0으로 계산된다.

```text
LEFT JOIN 직후
+-------------+-------------+----------+
| customer_id | name        | order_id |
+-------------+-------------+----------+
| 1           | Kim Minjun  | 1        |
| 1           | Kim Minjun  | 6        |
| 2           | Lee Seoyeon | 2        |
| 10          | Oh Eunwoo   | NULL     |
+-------------+-------------+----------+

GROUP BY c.customer_id, c.name 이후
+-------------+-------------+-------------------+
| customer_id | name        | COUNT(o.order_id) |
+-------------+-------------+-------------------+
| 1           | Kim Minjun  | 2                 |
| 2           | Lee Seoyeon | 1                 |
| 10          | Oh Eunwoo   | 0                 |
+-------------+-------------+-------------------+
```

실제 전체 결과는 주문 수가 적은 고객부터 정렬된다.

```text
+-------------+-------------+-------------+
| customer_id | name        | order_count |
+-------------+-------------+-------------+
| 10          | Oh Eunwoo   | 0           |
| 2           | Lee Seoyeon | 1           |
| 3           | Park Jiho   | 1           |
| 4           | Choi Yuna   | 1           |
| 5           | Jung Haein  | 1           |
| 6           | Kang Doyun  | 1           |
| 7           | Yoon Harin  | 1           |
| 8           | Lim Siwoo   | 1           |
| 9           | Han Jisoo   | 1           |
| 1           | Kim Minjun  | 2           |
+-------------+-------------+-------------+
```

여기서 `Oh Eunwoo`는 주문이 없지만 `LEFT JOIN` 덕분에 사라지지 않는다. 대신 오른쪽 주문 컬럼이 `NULL`로 채워지고, `COUNT(o.order_id)`는 `NULL`을 세지 않으므로 0이 된다. 같은 조회를 `INNER JOIN`으로 바꾸면 주문이 없는 고객은 매칭되는 주문 행이 없어서 결과에서 빠진다.

`LEFT JOIN`은 "왼쪽 테이블은 무조건 살린다"는 JOIN이다. 이 쿼리에서는 왼쪽이 `customer`이므로, 주문이 없는 고객도 결과에 남는다.

| JOIN 종류 | 주문 없는 고객의 결과 |
| --- | --- |
| `INNER JOIN` | 주문과 매칭되지 않으므로 사라진다. |
| `LEFT JOIN` | 고객 행은 남고, 주문 컬럼은 `NULL`이 된다. |

이 쿼리에서 `COUNT(*)`가 아니라 `COUNT(o.order_id)`를 사용한 점도 중요하다.

```text
주문 없는 고객의 LEFT JOIN 결과
+-------------+-----------+----------+
| customer_id | name      | order_id |
+-------------+-----------+----------+
| 10          | Oh Eunwoo | NULL     |
+-------------+-----------+----------+

COUNT(*)          = 1   행 자체는 1개이기 때문
COUNT(o.order_id) = 0   order_id가 NULL이기 때문
```

그래서 "주문 수"를 세려면 `COUNT(o.order_id)`가 더 정확하다. `COUNT(*)`는 JOIN 결과 행 수를 세기 때문에 주문이 없는 고객도 1로 세어질 수 있다.

## 10. 쿼리 09: 주문 상태별 주문 수

```sql
SELECT order_status, COUNT(*) AS order_count
FROM cafe_order
GROUP BY order_status
ORDER BY order_count DESC;
```

이 쿼리는 주문 상태별로 주문이 몇 건인지 센다.

`GROUP BY order_status`는 주문 상태가 같은 행끼리 묶는다. `COUNT(*)`는 각 그룹에 몇 행이 있는지 센다.

예를 들어 `COMPLETED` 주문이 5건이면 `COMPLETED, 5`와 같은 결과가 나온다.

이 쿼리는 집계의 가장 기본 형태이다.

`GROUP BY`는 행을 바로 없애는 것이 아니라, 같은 값을 가진 행들을 하나의 묶음으로 만든다. 그다음 `COUNT(*)` 같은 집계 함수가 각 묶음 안의 행 수를 센다.

샘플 데이터에서는 주문 상태가 다음처럼 묶인다. `COMPLETED` 주문이 6건, `PAID` 주문이 2건, `CANCELED`와 `ORDERED` 주문이 각각 1건이다.

```text
+--------------+-------------+
| order_status | order_count |
+--------------+-------------+
| COMPLETED    | 6           |
| PAID         | 2           |
| CANCELED     | 1           |
| ORDERED      | 1           |
+--------------+-------------+
```

`ORDER BY order_count DESC`는 주문 수가 많은 상태부터 보여 준다. 주문 수가 같은 `CANCELED`와 `ORDERED`의 순서는 DBMS가 선택할 수 있으므로, 정확한 tie-break가 필요하면 `ORDER BY order_count DESC, order_status`처럼 정렬 기준을 하나 더 추가한다.

```text
묶기 전 주문 행
ORDERED
PAID
PAID
COMPLETED
COMPLETED
COMPLETED

GROUP BY order_status
ORDERED 그룹:    1행
PAID 그룹:       2행
COMPLETED 그룹:  3행

SELECT order_status, COUNT(*)
ORDERED    1
PAID       2
COMPLETED  3
```

집계 쿼리에서 `SELECT`에는 보통 두 종류의 값이 온다.

| 종류 | 예시 | 설명 |
| --- | --- | --- |
| 그룹 기준 컬럼 | `order_status` | 어떤 그룹인지 보여 준다. |
| 집계 함수 결과 | `COUNT(*)` | 그 그룹에 속한 행들을 계산한다. |

따라서 `GROUP BY order_status`를 했다면 `SELECT order_status, COUNT(*)`처럼 "그룹 이름 + 그룹 계산값"을 보여 주는 구조가 자연스럽다.

## 11. 쿼리 10: 결제수단별 매출 합계

```sql
SELECT o.payment_method, SUM(od.quantity * od.unit_price) AS total_sales
FROM cafe_order AS o
INNER JOIN order_detail AS od ON o.order_id = od.order_id
WHERE o.order_status <> 'CANCELED'
GROUP BY o.payment_method
ORDER BY total_sales DESC;
```

이 쿼리는 결제수단별 매출 합계를 구한다.

매출은 주문 상세의 `수량 * 주문 당시 단가`로 계산한다. 주문의 결제수단은 `cafe_order`에 있고, 수량과 단가는 `order_detail`에 있다. 그래서 두 테이블을 조인한다.

`WHERE o.order_status <> 'CANCELED'`는 취소 주문을 제외한다. `<>`는 같지 않다는 뜻이다.

`GROUP BY o.payment_method`는 결제수단별로 묶는다. 그 안에서 `SUM()`이 금액을 합산한다.

이 쿼리는 비즈니스 규칙이 중요하다. 매출을 계산할 때 취소 주문을 포함하면 실제보다 큰 값이 나올 수 있다.

샘플 데이터 기준 결과는 다음과 같다. `MOBILE` 결제의 매출 합계가 가장 크고, 그다음이 `CARD`, `CASH` 순서이다.

```text
+----------------+-------------+
| payment_method | total_sales |
+----------------+-------------+
| MOBILE         | 40200.00    |
| CARD           | 28100.00    |
| CASH           | 14400.00    |
+----------------+-------------+
```

이 값은 취소 주문을 제외한 뒤, 주문 상세 한 줄마다 `quantity * unit_price`를 계산하고, 같은 결제수단끼리 더한 결과이다. 예를 들어 `MOBILE`은 주문 2번, 6번, 10번의 상세 금액이 합쳐져 `40200.00`이 된다.

아래는 일부 행으로 계산 흐름을 보여 주는 예시이다.

```text
1단계: 주문과 주문 상세를 order_id로 연결한다.

cafe_order AS o                  order_detail AS od
+----------+----------------+       +----------+----------+------------+
| order_id | payment_method |       | order_id | quantity | unit_price |
+----------+----------------+       +----------+----------+------------+
| 1        | CARD           | ----> | 1        | 2        | 4500.00    |
| 1        | CARD           | ----> | 1        | 1        | 3200.00    |
| 2        | MOBILE         | ----> | 2        | 1        | 5200.00    |
| 2        | MOBILE         | ----> | 2        | 2        | 6800.00    |
+----------+----------------+       +----------+----------+------------+

2단계: 취소 주문을 제외하고 줄 금액을 계산한다.

+----------------+----------+------------+------------+
| payment_method | quantity | unit_price | line_total |
+----------------+----------+------------+------------+
| CARD           | 2        | 4500.00    | 9000.00    |
| CARD           | 1        | 3200.00    | 3200.00    |
| MOBILE         | 1        | 5200.00    | 5200.00    |
| MOBILE         | 2        | 6800.00    | 13600.00   |
+----------------+----------+------------+------------+

3단계: payment_method별로 묶고 SUM으로 합산한다. 아래 표는 위에 보인 일부 행만 묶은 예시이다.

+----------------+-------------+
| payment_method | total_sales |
+----------------+-------------+
| CARD           | 12200.00    |
| MOBILE         | 18800.00    |
+----------------+-------------+
```

JOIN은 결제수단과 주문 상세 금액을 한 줄로 모으는 역할을 하고, `GROUP BY`와 `SUM()`은 결제수단별 총액을 만드는 역할을 한다.

집계 함수는 각각 쓰임이 다르다.

| 함수 | 하는 일 | 이 프로젝트의 예 |
| --- | --- | --- |
| `COUNT()` | 행 개수를 센다. | 주문 수, 고객 수 |
| `SUM()` | 숫자 값을 모두 더한다. | 매출 합계 |
| `AVG()` | 숫자 값의 평균을 구한다. | 평균 메뉴 가격 |
| `MIN()` | 가장 작은 값을 구한다. | 가장 낮은 메뉴 가격 |
| `MAX()` | 가장 큰 값을 구한다. | 가장 비싼 메뉴 가격 |

이 쿼리에서는 `SUM(od.quantity * od.unit_price)`처럼 집계 함수 안에 계산식이 들어간다. 먼저 각 주문 상세 행의 줄 금액을 계산하고, 같은 결제수단 그룹 안에서 그 값을 모두 더한다고 생각하면 된다.

```text
CARD 그룹
9000.00 + 3200.00 + ... = 28100.00

MOBILE 그룹
5200.00 + 13600.00 + ... = 40200.00
```

`WHERE o.order_status <> 'CANCELED'`가 `GROUP BY`보다 앞에서 적용되기 때문에, 취소 주문의 상세 금액은 애초에 그룹에 들어가지 않는다.

## 12. 쿼리 11: 카테고리별 평균 메뉴 가격

```sql
SELECT mc.name AS category_name, ROUND(AVG(mi.price), 2) AS average_menu_price
FROM menu_category AS mc
INNER JOIN menu_item AS mi ON mc.category_id = mi.category_id
GROUP BY mc.category_id, mc.name
ORDER BY average_menu_price DESC;
```

이 쿼리는 카테고리별 평균 메뉴 가격을 구한다. `AVG()`를 처음 연습하기에 좋은 예시이다.

`menu_item`에는 메뉴 가격이 있고, `menu_category`에는 카테고리 이름이 있다. 그래서 두 테이블을 `category_id`로 연결한 뒤, 카테고리별로 묶어서 평균을 계산한다.

읽는 순서는 다음과 같다.

```text
1. FROM menu_category
   카테고리 테이블에서 시작한다.

2. INNER JOIN menu_item
   각 카테고리에 속한 메뉴를 붙인다.

3. GROUP BY mc.category_id, mc.name
   같은 카테고리끼리 묶는다.

4. AVG(mi.price)
   각 카테고리 안의 메뉴 가격 평균을 구한다.

5. ORDER BY average_menu_price DESC
   평균 가격이 높은 카테고리부터 보여 준다.
```

예를 들어 Coffee 카테고리에 메뉴가 4개 있다.

```text
Coffee 메뉴 가격
Americano     4500.00
Cafe Latte    5200.00
Vanilla Latte 5800.00
Cold Brew     5500.00

AVG(price)
(4500 + 5200 + 5800 + 5500) / 4 = 5250.00
```

결과는 다음처럼 "카테고리 이름 + 평균 가격" 모양으로 나온다.

```text
+---------------+--------------------+
| category_name | average_menu_price |
+---------------+--------------------+
| Sandwich      | 7600.00            |
| Seasonal      | 6500.00            |
| Non Coffee    | 5750.00            |
| Coffee        | 5250.00            |
| Dessert       | 5000.00            |
+---------------+--------------------+
```

`COUNT()`는 개수를 세고, `SUM()`은 합계를 구하고, `AVG()`는 평균을 구한다. 이 쿼리에서는 `GROUP BY`로 카테고리별 묶음을 만든 뒤, 각 묶음 안에서 `AVG(mi.price)`를 계산한다.

## 13. 쿼리 12: 주문 이력이 없는 고객 찾기

```sql
SELECT customer_id, name, email
FROM customer
WHERE customer_id NOT IN (
  SELECT customer_id
  FROM cafe_order
)
ORDER BY customer_id;
```

이 쿼리는 주문한 적이 없는 고객을 찾는다.

안쪽 쿼리는 주문 테이블에 등장한 고객 ID 목록을 만든다.

```sql
SELECT customer_id
FROM cafe_order
```

바깥 쿼리는 고객 테이블에서 그 목록에 없는 고객을 찾는다.

```sql
WHERE customer_id NOT IN (...)
```

이 쿼리는 서브쿼리의 기본 예시이다. 같은 문제는 `LEFT JOIN`과 `WHERE o.order_id IS NULL`로도 풀 수 있다.

시각화하면 다음과 같다.

```text
안쪽 쿼리 결과: 주문 테이블에 등장한 고객 ID

cafe_order
+-------------+
| customer_id |
+-------------+
| 1           |
| 3           |
+-------------+

바깥 쿼리: customer에서 위 목록에 없는 고객만 남긴다.

customer
+-------------+--------+---------------------+----------------+
| customer_id | name   | email               | NOT IN 결과    |
+-------------+--------+---------------------+----------------+
| 1           | 김민준 | minjun@example.com  | 제외           |
| 2           | 이서연 | seoyeon@example.com | 남김           |
| 3           | 박도윤 | doyoon@example.com  | 제외           |
+-------------+--------+---------------------+----------------+

최종 결과
+-------------+--------+---------------------+
| customer_id | name   | email               |
+-------------+--------+---------------------+
| 2           | 이서연 | seoyeon@example.com |
+-------------+--------+---------------------+
```

같은 요구를 `LEFT JOIN`으로 생각하면 "모든 고객을 남긴 뒤, 주문이 붙지 않아 `NULL`인 고객만 고른다"는 흐름이다. 서브쿼리는 "주문한 고객 목록을 먼저 만들고, 그 목록에 없는 고객을 고른다"는 흐름이다.

서브쿼리는 위치에 따라 역할이 조금씩 달라진다. 이 예시에서는 `WHERE` 안에 있으므로 "필터 조건을 만들기 위한 보조 쿼리"로 쓰였다.

```text
안쪽 쿼리
주문한 고객 ID 목록을 만든다.

바깥 쿼리
전체 고객 중 그 목록에 없는 고객만 남긴다.
```

`NOT IN`을 사용할 때는 안쪽 쿼리 결과에 `NULL`이 섞이면 의도와 다르게 동작할 수 있다. 이 프로젝트의 `cafe_order.customer_id`는 `NOT NULL`이고 FK로 보호되기 때문에 안전하지만, 실무에서는 안쪽 쿼리의 컬럼이 `NULL`을 가질 수 있는지 확인하는 습관이 좋다.

같은 문제를 `LEFT JOIN` 방식으로 쓰면 다음처럼 표현할 수 있다.

```sql
SELECT c.customer_id, c.name, c.email
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.customer_id;
```

두 방식 모두 결과는 같지만, 사고방식이 다르다. `NOT IN`은 "주문한 고객 목록에서 빠진 사람"을 찾는 방식이고, `LEFT JOIN`은 "고객을 모두 펼친 뒤 주문이 붙지 않은 사람"을 찾는 방식이다.

## 14. 쿼리 13: 주문 상태 수정

```sql
UPDATE cafe_order
SET order_status = 'PAID'
WHERE order_id = 9;

SELECT order_id, order_status
FROM cafe_order
WHERE order_id = 9;
```

이 쿼리는 `order_id = 9`인 주문의 상태를 `PAID`로 바꾼다.

`UPDATE`는 기존 행을 수정하는 명령이다. `SET`은 어떤 컬럼을 어떤 값으로 바꿀지 정한다. `WHERE`는 어떤 행만 수정할지 정한다.

`WHERE`가 매우 중요하다. `WHERE` 없이 실행하면 모든 주문의 상태가 바뀔 수 있다.

뒤의 `SELECT`는 수정이 잘 되었는지 확인하기 위한 조회이다.

`UPDATE`는 데이터를 바꾸는 명령이므로 조회 쿼리보다 더 조심해서 읽어야 한다. 안전하게 읽는 순서는 다음과 같다.

```text
1. UPDATE cafe_order
   어느 테이블을 수정하는가?

2. SET order_status = 'PAID'
   어떤 컬럼을 어떤 값으로 바꾸는가?

3. WHERE order_id = 9
   어떤 행만 바꾸는가?

4. SELECT로 확인
   바뀐 결과가 의도와 같은가?
```

`UPDATE`를 실행하기 전에는 같은 `WHERE` 조건으로 먼저 조회해 보는 습관이 좋다.

```sql
SELECT order_id, order_status
FROM cafe_order
WHERE order_id = 9;
```

이 조회 결과가 정확히 수정하려는 행인지 확인한 뒤 `UPDATE`를 실행하면 실수를 줄일 수 있다.

## 15. 쿼리 14: 취소 주문 삭제와 CASCADE 확인

```sql
DELETE FROM cafe_order
WHERE order_id = 5 AND order_status = 'CANCELED';

SELECT COUNT(*) AS remaining_order_rows
FROM cafe_order
WHERE order_id = 5;

SELECT COUNT(*) AS remaining_order_detail_rows
FROM order_detail
WHERE order_id = 5;
```

이 쿼리는 취소된 주문 한 건을 삭제한다.

`DELETE FROM cafe_order`는 주문 테이블에서 행을 삭제한다. `WHERE order_id = 5 AND order_status = 'CANCELED'`는 주문 번호가 5이고 상태가 취소인 경우에만 삭제하라는 뜻이다. 조건을 두 개 둔 이유는 실수로 정상 주문을 삭제하지 않기 위해서이다.

이 프로젝트에서는 `order_detail.order_id`에 `ON DELETE CASCADE`가 설정되어 있다. 따라서 주문이 삭제되면 그 주문에 속한 주문 상세도 함께 삭제된다.

뒤의 두 `SELECT COUNT(*)`는 주문 행과 주문 상세 행이 실제로 사라졌는지 확인한다.

`DELETE`도 `UPDATE`처럼 `WHERE`가 핵심이다. 이 쿼리는 `order_id = 5`만 확인하지 않고 `order_status = 'CANCELED'`까지 함께 확인한다.

```text
삭제 조건
order_id = 5
AND
order_status = 'CANCELED'

두 조건을 모두 만족해야 삭제됨
```

`ON DELETE CASCADE`의 흐름은 다음처럼 볼 수 있다.

```text
cafe_order
order_id = 5 삭제
    |
    v
order_detail
order_id = 5를 참조하던 주문 상세도 함께 삭제
```

이 설정은 부모 행이 사라질 때 자식 행을 어떻게 처리할지 정하는 FK 규칙이다. 이 프로젝트에서는 주문 상세가 주문 없이 의미를 갖기 어렵기 때문에, 주문 삭제 시 주문 상세도 함께 삭제되도록 설계했다.

## 16. 쿼리 15: 인덱스 생성과 실행 계획 확인

```sql
CREATE INDEX idx_cafe_order_ordered_at ON cafe_order(ordered_at);

EXPLAIN
SELECT order_id, customer_id, order_status, ordered_at
FROM cafe_order
WHERE ordered_at >= '2026-03-04 00:00:00'
ORDER BY ordered_at;
```

이 쿼리는 인덱스를 직접 만든 뒤, 실행 계획을 확인한다.

먼저 `CREATE INDEX`가 실행된다.

```sql
CREATE INDEX idx_cafe_order_ordered_at ON cafe_order(ordered_at);
```

이 명령은 `cafe_order` 테이블의 `ordered_at` 컬럼에 인덱스를 만든다. 주문 목록은 날짜 조건으로 검색하거나 주문 시각순으로 정렬하는 일이 많기 때문에 `ordered_at`을 인덱스 대상으로 골랐다.

그다음 `EXPLAIN`이 실행된다. `EXPLAIN`은 MySQL이 쿼리를 어떤 방식으로 실행할지 보여 준다. 여기서는 방금 만든 인덱스가 날짜 조건과 정렬에서 사용될 수 있는지 확인한다.

이 쿼리가 바로 `ordered_at` 컬럼을 `WHERE`의 날짜 범위 조건과 `ORDER BY`의 정렬 기준으로 사용하므로, 인덱스 선택 이유가 가장 잘 드러난다.

```text
WHERE ordered_at >= '2026-03-04 00:00:00'
ORDER BY ordered_at

-> 주문 시각을 기준으로 범위를 찾고 같은 기준으로 정렬한다.
```

주문 ID나 고객 ID는 특정 한 건 또는 특정 고객의 주문을 찾을 때 유용하지만, 이 쿼리의 관심사는 "어느 시점 이후의 주문을 시간순으로 읽기"이다. 그래서 `ordered_at`이 인덱스 대상이 된다.

주의할 점은 같은 이름의 인덱스를 두 번 만들 수 없다는 것이다. 15번 쿼리를 다시 실행하고 싶다면 먼저 `schema.sql`과 `sample_data.sql`을 다시 실행해 데이터베이스를 처음 상태로 되돌린 뒤 실행한다.

실행 계획에서 볼 수 있는 대표 항목은 다음과 같다.

| 항목 | 의미 |
| --- | --- |
| `table` | 어떤 테이블을 읽는가 |
| `type` | 테이블 접근 방식 |
| `possible_keys` | 사용할 가능성이 있는 인덱스 |
| `key` | 실제 선택된 인덱스 |
| `rows` | 읽을 것으로 예상되는 행 수 |
| `Extra` | 추가 실행 정보 |

데이터가 아주 적으면 인덱스가 있어도 MySQL이 전체 테이블을 읽는 것이 더 낫다고 판단할 수 있다. 따라서 작은 실습 데이터에서는 실행 계획이 환경에 따라 조금 다르게 보일 수 있다.

`EXPLAIN`은 쿼리를 실제로 실행해 결과를 보여 주는 명령이라기보다, 데이터베이스가 세운 실행 계획을 미리 보여 주는 도구이다. "이 쿼리를 어떤 길로 읽으려고 하는가"를 확인하는 용도라고 생각하면 된다.

인덱스가 없는 경우와 있는 경우를 단순화하면 다음과 같다.

```text
인덱스 없음
테이블 처음부터 끝까지 훑으며 ordered_at 조건을 확인

인덱스 있음
ordered_at 기준으로 정리된 길을 따라 필요한 범위부터 찾을 수 있음
```

실행 계획에서 `key`에 `idx_cafe_order_ordered_at`이 보이면 MySQL이 해당 인덱스를 선택했다는 뜻이다. `rows`는 실제로 읽은 행 수가 아니라 읽을 것으로 예상한 행 수이다. 그래서 실행 계획은 정답표가 아니라 데이터베이스의 예상과 선택을 보여 주는 힌트로 읽어야 한다.

## 17. 보너스 A: JOIN으로 Coffee 메뉴 찾기

```sql
SELECT mi.menu_item_id, mi.name, mi.price
FROM menu_item AS mi
INNER JOIN menu_category AS mc ON mi.category_id = mc.category_id
WHERE mc.name = 'Coffee'
ORDER BY mi.price;
```

이 쿼리는 `Coffee` 카테고리에 속한 메뉴를 조인으로 찾는다.

메뉴 테이블에는 카테고리 이름이 직접 저장되어 있지 않고 `category_id`만 있다. 카테고리 이름은 `menu_category`에 있으므로 두 테이블을 조인해야 한다.

이 방식은 카테고리 이름과 메뉴 정보를 함께 보고 싶을 때 자연스럽다.

시각화하면 다음과 같다.

```text
menu_item AS mi                         menu_category AS mc
+--------------+-------------+--------+       +-------------+--------+
| menu_item_id | category_id | name   |       | category_id | name   |
+--------------+-------------+--------+       +-------------+--------+
| 1            | 1           | 아메리카노 | --> | 1           | Coffee |
| 2            | 1           | 카페라떼   | --> | 1           | Coffee |
| 5            | 3           | 치즈케이크 | --> | 3           | Dessert|
+--------------+-------------+--------+       +-------------+--------+

WHERE mc.name = 'Coffee'

최종 결과
+--------------+------------+---------+
| menu_item_id | name       | price   |
+--------------+------------+---------+
| 1            | 아메리카노 | 4000.00 |
| 2            | 카페라떼   | 4500.00 |
+--------------+------------+---------+
```

JOIN으로 카테고리 이름을 붙인 뒤, `WHERE mc.name = 'Coffee'`로 Coffee 카테고리만 남기는 구조이다.

JOIN 방식은 결과에 양쪽 테이블의 컬럼을 함께 보여 주고 싶을 때 특히 자연스럽다. 예를 들어 메뉴명뿐 아니라 카테고리 설명까지 같이 보고 싶다면 이미 `menu_category`가 붙어 있으므로 `mc.description`을 `SELECT`에 추가하면 된다.

```text
JOIN 방식의 사고 흐름
메뉴에 카테고리 정보를 붙인다.
붙은 결과에서 카테고리 이름이 Coffee인 행만 남긴다.
필요한 메뉴 컬럼을 보여 준다.
```

## 18. 보너스 B: 서브쿼리로 Coffee 메뉴 찾기

```sql
SELECT menu_item_id, name, price
FROM menu_item
WHERE category_id = (
  SELECT category_id
  FROM menu_category
  WHERE name = 'Coffee'
)
ORDER BY price;
```

이 쿼리는 보너스 A와 같은 결과를 서브쿼리로 구한다.

안쪽 쿼리는 `Coffee` 카테고리의 `category_id`를 찾는다. 바깥 쿼리는 그 `category_id`를 가진 메뉴를 찾는다.

같은 요구사항을 JOIN으로도 풀 수 있고 서브쿼리로도 풀 수 있다는 점을 보여 주는 예시이다.

시각화하면 다음과 같다.

```text
1단계: 안쪽 쿼리

menu_category
+-------------+--------+
| category_id | name   |
+-------------+--------+
| 1           | Coffee |
+-------------+--------+

결과: category_id = 1

2단계: 바깥 쿼리

menu_item
+--------------+-------------+------------+---------+
| menu_item_id | category_id | name       | price   |
+--------------+-------------+------------+---------+
| 1            | 1           | 아메리카노 | 4000.00 |
| 2            | 1           | 카페라떼   | 4500.00 |
| 5            | 3           | 치즈케이크 | 6500.00 |
+--------------+-------------+------------+---------+

WHERE category_id = 1

최종 결과
+--------------+------------+---------+
| menu_item_id | name       | price   |
+--------------+------------+---------+
| 1            | 아메리카노 | 4000.00 |
| 2            | 카페라떼   | 4500.00 |
+--------------+------------+---------+
```

보너스 A는 두 테이블을 붙여서 필터링하고, 보너스 B는 먼저 필요한 ID를 찾은 뒤 그 ID로 필터링한다. 결과는 같지만 머릿속 흐름이 다르다.

JOIN과 서브쿼리를 비교하면 다음과 같다.

| 방식 | 머릿속 흐름 | 잘 어울리는 상황 |
| --- | --- | --- |
| JOIN | 두 테이블을 붙인 뒤 필요한 행을 고른다. | 양쪽 테이블의 컬럼을 함께 보고 싶을 때 |
| 서브쿼리 | 필요한 값을 먼저 찾고, 그 값으로 바깥 쿼리를 필터링한다. | 조건에 필요한 값만 다른 테이블에서 가져오면 될 때 |

이 예시에서는 `menu_category.name`을 결과에 보여 주지 않으므로 서브쿼리도 깔끔하다. 반대로 결과에 `mc.name`이나 `mc.description`까지 보여 주고 싶다면 JOIN 방식이 더 자연스럽다.

## 19. 참고: UNION과 FULL OUTER JOIN의 차이

`FULL OUTER JOIN`과 `UNION`은 둘 다 결과를 합치는 것처럼 보이지만, 합치는 방향이 다르다.

| 구분 | FULL OUTER JOIN | UNION |
| --- | --- | --- |
| 합치는 방향 | 두 테이블을 옆으로 붙인다. | 두 SELECT 결과를 아래로 이어 붙인다. |
| 기준 | `ON` 조건으로 행끼리 연결한다. | 두 SELECT의 컬럼 개수와 타입이 맞아야 한다. |
| 결과 | 양쪽 테이블 컬럼이 함께 나온다. | 하나의 SELECT 결과 모양으로 나온다. |
| 매칭 안 되는 행 | 반대쪽 컬럼을 `NULL`로 채워 남긴다. | 매칭 개념이 없다. |

`FULL OUTER JOIN`은 다음처럼 관계 있는 데이터를 한 줄로 연결한다.

```text
customer + cafe_order

+-------------+--------+----------+
| customer_id | name   | order_id |
+-------------+--------+----------+
| 1           | 김민준 | 101      |
| 2           | 이서연 | NULL     |
| NULL        | NULL   | 102      |
+-------------+--------+----------+
```

`UNION`은 두 결과 목록을 아래로 합친다.

```sql
SELECT customer_id FROM customer
UNION
SELECT customer_id FROM cafe_order;
```

```text
+-------------+
| customer_id |
+-------------+
| 1           |
| 2           |
| 999         |
+-------------+
```

MySQL은 `FULL OUTER JOIN`을 직접 지원하지 않는다. 그래서 필요한 경우에는 `LEFT JOIN` 결과와 `RIGHT JOIN` 결과를 `UNION`으로 합쳐 비슷하게 표현한다. 이때 `UNION`은 조인 자체가 아니라, 두 조인 결과를 세로로 합치는 도구로 쓰인다.

## 20. 보너스 C: FK 무결성 테스트

```sql
-- INSERT INTO cafe_order (customer_id, order_status, ordered_at, payment_method)
-- VALUES (999, 'ORDERED', '2026-03-10 10:00:00', 'CARD');
```

이 쿼리는 주석 처리되어 있다. 주석을 해제하면 실패해야 정상이다.

이유는 `customer_id = 999`인 고객이 `customer` 테이블에 없기 때문이다. `cafe_order.customer_id`는 `customer.customer_id`를 참조하는 FK이므로, 존재하지 않는 고객의 주문은 저장될 수 없다.

이 예시는 FK가 단순한 장식이 아니라 실제로 잘못된 데이터를 막는 규칙임을 보여 준다.

FK 무결성 테스트를 데이터 흐름으로 보면 다음과 같다.

```text
INSERT 요청
customer_id = 999인 주문을 저장하려고 함
    |
    v
FK 확인
customer 테이블에 customer_id = 999가 있는가?
    |
    v
없음
    |
    v
INSERT 거부
```

이런 규칙이 없으면 주문은 저장되지만 고객 정보를 찾을 수 없는 어색한 데이터가 남는다. FK는 애플리케이션 코드가 실수하더라도 데이터베이스 안의 관계가 끊어지지 않게 막아 주는 안전장치이다.

## 21. 쿼리 읽기 순서

긴 SQL은 한 번에 이해하려고 하면 어렵다. 다음 순서로 읽으면 쿼리의 구조가 더 분명해진다.

```text
무엇을 찾으려는 쿼리인지 확인한다.
FROM에서 어느 테이블을 읽는지 확인한다.
JOIN에서 어떤 테이블을 연결하는지 확인한다.
WHERE에서 어떤 행을 남기는지 확인한다.
GROUP BY가 있다면 무엇을 기준으로 묶는지 확인한다.
SELECT에서 어떤 컬럼이나 계산 결과를 보여 주는지 확인한다.
ORDER BY나 LIMIT으로 결과 표시 방식을 확인한다.
```

예를 들어 결제수단별 매출 쿼리는 다음 흐름으로 읽을 수 있다.

```text
목적은 결제수단별 매출 합계를 구하는 것이다.
결제수단은 cafe_order에 있고, 수량과 단가는 order_detail에 있다.
따라서 두 테이블을 order_id로 조인한다.
취소 주문은 실제 매출로 보기 어렵기 때문에 WHERE 조건으로 제외한다.
payment_method별로 묶고, quantity * unit_price의 합계를 구한다.
```

같은 내용을 SQL 절의 실행 순서로 펼치면 다음과 같다.

```text
+------+-------------------------------+------------------------------------------+
| 순서 | 절                            | 하는 일                                  |
+------+-------------------------------+------------------------------------------+
| 1    | FROM cafe_order AS o          | 주문 테이블에서 시작한다.               |
| 2    | JOIN order_detail AS od       | 주문 상세를 order_id 기준으로 붙인다.   |
| 3    | WHERE order_status <> 'CANCELED' | 취소 주문 행을 제외한다.             |
| 4    | GROUP BY payment_method       | 결제수단별로 행을 묶는다.               |
| 5    | SELECT payment_method, SUM    | 결제수단과 매출 합계를 만든다.          |
| 6    | ORDER BY total_sales DESC     | 매출 합계가 큰 순서로 정렬한다.         |
+------+-------------------------------+------------------------------------------+
```

핵심은 `SELECT`가 맨 위에 적혀 있어도, 처음부터 보여 줄 컬럼을 고르는 식으로 이해하면 안 된다는 점이다. 먼저 데이터의 범위를 만들고, 줄이고, 묶고, 계산한 뒤, 마지막에 보여 줄 모양을 정한다고 보면 된다.

```text
데이터 범위 만들기: FROM + JOIN
필요한 행만 남기기: WHERE
묶어서 계산하기: GROUP BY + 집계 함수
보여 줄 모양 정하기: SELECT
보기 좋게 정렬하기: ORDER BY + LIMIT
```

마지막으로 SQL을 읽을 때 사용할 수 있는 짧은 체크리스트를 남긴다.

| 질문 | 확인할 SQL |
| --- | --- |
| 어떤 테이블에서 출발하는가? | `FROM` |
| 다른 테이블 정보가 필요한가? | `JOIN ... ON ...` |
| 행을 걸러 내는 조건은 무엇인가? | `WHERE` |
| 여러 행을 묶어 계산하는가? | `GROUP BY`, `COUNT`, `SUM`, `AVG` |
| 그룹 결과를 다시 거르는가? | `HAVING` |
| 결과 컬럼 이름을 읽기 쉽게 바꾸는가? | `AS` |
| 결과를 어떤 순서로 보여 주는가? | `ORDER BY` |
| 일부만 보여 주는가? | `LIMIT` |

처음에는 SQL을 위에서 아래로 읽기보다, `FROM`에서 시작해 데이터가 어떻게 붙고, 줄고, 묶이고, 마지막에 어떤 모양으로 보이는지 따라가면 된다. SQL은 문법 암기보다 "데이터가 변하는 장면"을 상상하는 힘이 중요하다.
