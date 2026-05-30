# `queries.sql` 쿼리 해설서

이 문서는 `queries.sql`에 들어 있는 SQL을 하나씩 읽기 위한 해설서이다. SQL을 외우는 것보다 중요한 일은 쿼리가 어떤 질문에 답하고 있는지 이해하는 것이다. 데이터베이스 쿼리는 결국 “데이터에게 묻는 질문”이다.

## 1. 쿼리를 읽는 기본 순서

SQL은 보통 `SELECT`부터 적지만, 실제로 이해할 때는 다음 순서로 읽으면 쉽다.

1. `FROM`: 어느 테이블에서 시작하는가.
2. `JOIN`: 어떤 테이블을 연결하는가.
3. `WHERE`: 어떤 행만 남기는가.
4. `GROUP BY`: 어떤 기준으로 묶는가.
5. `SELECT`: 어떤 컬럼이나 계산 결과를 보여 주는가.
6. `ORDER BY`: 어떤 순서로 정렬하는가.
7. `LIMIT`: 몇 개만 보여 주는가.

이 순서로 읽으면 긴 쿼리도 덜 어렵다.

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

## 8. 쿼리 07: 완료된 주문의 상세 내역 조회

```sql
SELECT c.name AS customer_name, mc.name AS category_name, mi.name AS menu_name,
       od.quantity, od.quantity * od.unit_price AS line_total
FROM order_detail AS od
INNER JOIN cafe_order AS o ON od.order_id = o.order_id
INNER JOIN customer AS c ON o.customer_id = c.customer_id
INNER JOIN menu_item AS mi ON od.menu_item_id = mi.menu_item_id
INNER JOIN menu_category AS mc ON mi.category_id = mc.category_id
WHERE o.order_status = 'COMPLETED'
ORDER BY c.name, mi.name;
```

이 쿼리는 여러 테이블을 연결하는 대표 예시이다. 주문 상세에서 시작해 주문, 고객, 메뉴, 카테고리까지 연결한다.

연결 흐름은 다음과 같다.

```text
order_detail -> cafe_order -> customer
order_detail -> menu_item -> menu_category
```

`WHERE o.order_status = 'COMPLETED'`는 완료된 주문만 남긴다. 취소되었거나 아직 처리 중인 주문은 제외한다.

이 쿼리를 이해하면 정규화된 테이블을 다시 조합하는 감각을 익힐 수 있다.

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

## 12. 쿼리 11: 고객별 평균 주문 금액

```sql
SELECT c.customer_id, c.name,
       ROUND(AVG(order_totals.order_total), 2) AS average_order_amount
FROM customer AS c
INNER JOIN (
  SELECT o.order_id, o.customer_id, SUM(od.quantity * od.unit_price) AS order_total
  FROM cafe_order AS o
  INNER JOIN order_detail AS od ON o.order_id = od.order_id
  WHERE o.order_status <> 'CANCELED'
  GROUP BY o.order_id, o.customer_id
) AS order_totals ON c.customer_id = order_totals.customer_id
GROUP BY c.customer_id, c.name
ORDER BY average_order_amount DESC;
```

이 쿼리는 고객별 평균 주문 금액을 구한다. 조금 길지만 두 단계로 나누면 이해하기 쉽다.

첫 번째 단계는 서브쿼리이다.

```text
주문별 총액을 먼저 구한다.
```

주문 하나에는 여러 주문 상세가 있을 수 있으므로, 먼저 `order_id`별로 `SUM(quantity * unit_price)`를 계산한다.

두 번째 단계는 바깥 쿼리이다.

```text
주문별 총액을 고객별로 평균 낸다.
```

`AVG(order_totals.order_total)`은 고객이 가진 여러 주문 총액의 평균을 계산한다. `ROUND(..., 2)`는 소수점 둘째 자리까지 반올림한다.

이 쿼리의 핵심은 “평균 주문 금액”을 바로 구하는 것이 아니라, 먼저 “주문 한 건의 총액”을 구한 뒤 평균을 낸다는 점이다.

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

## 16. 쿼리 15: 인덱스 사용 계획 확인

```sql
EXPLAIN
SELECT order_id, customer_id, order_status, ordered_at
FROM cafe_order
WHERE ordered_at >= '2026-03-04 00:00:00'
ORDER BY ordered_at;
```

이 쿼리는 실제 데이터를 조회하기보다 실행 계획을 확인한다.

`EXPLAIN`은 MySQL이 쿼리를 어떤 방식으로 실행할지 보여 준다. 이 프로젝트에서는 `ordered_at`에 인덱스를 만들었으므로, 날짜 조건과 정렬에서 인덱스가 사용될 수 있는지 확인한다.

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

## 19. 보너스 C: FK 무결성 테스트

```sql
-- INSERT INTO cafe_order (customer_id, order_status, ordered_at, payment_method)
-- VALUES (999, 'ORDERED', '2026-03-10 10:00:00', 'CARD');
```

이 쿼리는 주석 처리되어 있다. 주석을 해제하면 실패해야 정상이다.

이유는 `customer_id = 999`인 고객이 `customer` 테이블에 없기 때문이다. `cafe_order.customer_id`는 `customer.customer_id`를 참조하는 FK이므로, 존재하지 않는 고객의 주문은 저장될 수 없다.

이 예시는 FK가 단순한 장식이 아니라 실제로 잘못된 데이터를 막는 규칙임을 보여 준다.

## 20. 쿼리 읽기 순서

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
