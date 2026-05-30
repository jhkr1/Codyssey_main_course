# 카페 주문 데이터베이스로 배우는 관계형 데이터베이스

이 문서는 카페 주문 데이터베이스 미션을 이해하기 위한 학습서이다. 목표는 SQL 파일을 실행하는 것에서 끝나지 않는다. 데이터베이스의 기본 개념을 차근차근 익히고, 테이블 설계와 SQL 조회가 어떤 문제를 해결하는지 이해하는 데 목적이 있다.

## 1장. 데이터베이스를 배우는 이유

데이터베이스는 데이터를 안전하게 저장하고, 필요할 때 정확하게 꺼내기 위한 도구이다. 카페를 예로 들면 고객, 메뉴, 주문, 결제수단, 주문 상태 같은 정보가 계속 쌓인다. 이 정보를 단순한 표 하나에 모두 적을 수도 있지만, 데이터가 늘어날수록 중복과 오류가 생기기 쉽다.

예를 들어 주문 표 하나에 고객 이름, 고객 이메일, 메뉴명, 메뉴 가격, 주문일을 모두 적는다고 하자. 같은 고객이 여러 번 주문하면 이메일이 여러 행에 반복된다. 메뉴 가격이 바뀌면 과거 행과 현재 행의 가격이 섞인다. 존재하지 않는 고객 번호나 메뉴 번호가 들어가도 막기 어렵다.

관계형 데이터베이스는 이런 문제를 줄이기 위해 데이터를 여러 테이블로 나누고, 테이블 사이의 관계를 키로 연결한다. 이 미션의 핵심은 “어떤 데이터를 어디에 둘 것인가”와 “나뉜 데이터를 어떻게 다시 연결해서 읽을 것인가”이다.

## 2장. 관계형 데이터베이스란 무엇인가

관계형 데이터베이스는 데이터를 표 형태의 테이블에 저장한다. 테이블은 행과 컬럼으로 이루어진다.

| 용어 | 의미 | 예시 |
| --- | --- | --- |
| 테이블 | 같은 종류의 데이터를 모아 둔 표 | `customer` |
| 행 | 실제 데이터 한 건 | 고객 한 명 |
| 컬럼 | 행이 가지는 속성 | 이름, 이메일, 가입일 |
| 스키마 | 테이블 구조와 제약조건의 설계도 | `schema.sql` |
| 쿼리 | 데이터베이스에 내리는 명령 | `SELECT`, `INSERT` |

관계형 데이터베이스에서 중요한 점은 테이블을 나누되, 완전히 흩어지게 두지 않는다는 것이다. 각 테이블은 PK와 FK를 통해 연결된다.

## 3장. 이 미션의 도메인: 카페 주문

카페 주문은 데이터베이스 입문에 적합한 주제이다. 고객은 여러 번 주문할 수 있고, 하나의 주문에는 여러 메뉴가 들어갈 수 있으며, 메뉴는 카테고리에 속한다. 이 안에 1:N 관계, 정규화, 조인, 집계가 자연스럽게 들어 있다.

이 프로젝트는 5개 테이블로 구성된다.

| 테이블 | 역할 | 이 테이블이 필요한 이유 |
| --- | --- | --- |
| `customer` | 고객 정보 저장 | 고객 정보가 주문마다 반복되지 않게 한다. |
| `menu_category` | 메뉴 분류 저장 | 카테고리명을 메뉴마다 문자열로 반복하지 않게 한다. |
| `menu_item` | 메뉴 정보 저장 | 메뉴명, 가격, 판매 여부를 한 곳에서 관리한다. |
| `cafe_order` | 주문 한 건의 공통 정보 저장 | 주문 시각, 고객, 상태, 결제수단을 주문 단위로 관리한다. |
| `order_detail` | 주문에 포함된 메뉴 저장 | 한 주문에 여러 메뉴가 들어가는 구조를 표현한다. |

## 4장. PK: 행을 식별하는 값

PK는 Primary Key의 줄임말이며 기본키라고 부른다. 기본키는 테이블 안에서 한 행을 고유하게 식별하는 값이다.

이름만으로 고객을 식별하면 문제가 생긴다. 같은 이름의 고객이 두 명 있을 수 있기 때문이다. 이메일은 고유하게 만들 수 있지만, 이메일이 바뀌는 상황도 생각할 수 있다. 그래서 이 프로젝트에서는 `customer_id`처럼 별도의 숫자 ID를 기본키로 사용한다.

```sql
customer_id BIGINT AUTO_INCREMENT PRIMARY KEY
```

`AUTO_INCREMENT`는 새 행이 들어올 때 숫자를 자동으로 증가시킨다. 개발자가 매번 ID를 직접 정하지 않아도 되므로 실수를 줄일 수 있다.

정리하면 PK는 테이블의 각 행을 정확히 구분하기 위한 값이다. 같은 이름이나 같은 속성이 반복될 수 있으므로, 이 프로젝트에서는 `customer_id`, `menu_item_id` 같은 별도의 ID를 기본키로 두었다.

## 5장. FK: 테이블 사이를 연결하는 값

FK는 Foreign Key의 줄임말이며 외래키라고 부른다. 외래키는 다른 테이블의 기본키를 참조하는 컬럼이다.

예를 들어 `cafe_order.customer_id`는 `customer.customer_id`를 참조한다. 이 말은 “이 주문은 어떤 고객의 주문인가”를 고객 테이블과 연결해서 표현한다는 뜻이다.

```sql
CONSTRAINT fk_cafe_order_customer
  FOREIGN KEY (customer_id)
  REFERENCES customer(customer_id)
```

외래키가 중요한 이유는 참조 무결성을 지켜 주기 때문이다. 고객 테이블에 없는 `customer_id = 999`로 주문을 넣으려고 하면 데이터베이스가 거부한다. 애플리케이션 코드가 실수하더라도 데이터베이스가 마지막으로 막아 주는 것이다.

정리하면 FK는 테이블 사이의 관계를 표현하고, 존재하지 않는 부모 데이터를 참조하지 못하게 막는 장치이다. 이 프로젝트에서는 주문이 반드시 존재하는 고객을 참조하고, 주문 상세가 반드시 존재하는 주문과 메뉴를 참조하도록 FK를 사용했다.

## 6장. 1:N 관계

1:N 관계는 한쪽 데이터 하나가 다른 쪽 데이터 여러 개와 연결되는 관계이다. 고객과 주문을 예로 들면, 고객 한 명은 여러 번 주문할 수 있다. 그러나 주문 한 건은 보통 한 명의 고객에게 속한다.

```text
customer 1 ---- N cafe_order
```

이때 외래키는 보통 N쪽 테이블에 들어간다. 주문 테이블에 `customer_id`를 넣으면 각 주문이 어떤 고객에게 속하는지 표현할 수 있다.

이 프로젝트에는 다음 1:N 관계가 있다.

| 관계 | 설명 |
| --- | --- |
| `menu_category` 1:N `menu_item` | 하나의 카테고리에 여러 메뉴가 속한다. |
| `customer` 1:N `cafe_order` | 한 고객은 여러 주문을 할 수 있다. |
| `cafe_order` 1:N `order_detail` | 한 주문에는 여러 메뉴가 들어갈 수 있다. |
| `menu_item` 1:N `order_detail` | 하나의 메뉴는 여러 주문 상세에 등장할 수 있다. |

## 7장. 정규화: 왜 테이블을 나누는가

정규화는 중복을 줄이고 데이터 불일치를 막기 위해 테이블을 적절히 나누는 과정이다. 정규화의 목적은 테이블을 많이 만드는 것이 아니라, 한 종류의 사실을 한 곳에서 관리하는 것이다.

나쁜 설계는 주문 테이블 하나에 고객 이메일, 메뉴명, 카테고리명, 메뉴 가격을 모두 반복 저장하는 방식이다. 이 경우 다음 문제가 생긴다.

| 문제 | 설명 |
| --- | --- |
| 삽입 이상 | 아직 주문이 없는 메뉴나 고객 정보를 자연스럽게 저장하기 어렵다. |
| 수정 이상 | 고객 이메일이 바뀌면 여러 주문 행을 모두 수정해야 한다. |
| 삭제 이상 | 주문을 삭제했더니 메뉴나 고객 정보까지 사라질 수 있다. |

이 프로젝트에서는 데이터를 다음처럼 나누었다.

| 데이터 | 저장 위치 |
| --- | --- |
| 고객 이름, 이메일, 전화번호 | `customer` |
| 메뉴 카테고리명 | `menu_category` |
| 메뉴명, 현재 가격, 판매 여부 | `menu_item` |
| 주문 시각, 결제수단, 주문상태 | `cafe_order` |
| 주문 당시 수량과 단가 | `order_detail` |

단, `order_detail.unit_price`는 일부러 따로 저장한다. `menu_item.price`와 비슷해 보이지만 의미가 다르다. `menu_item.price`는 현재 판매 가격이고, `order_detail.unit_price`는 주문 당시 적용된 가격이다. 메뉴 가격이 나중에 바뀌어도 과거 주문 금액은 바뀌면 안 된다.

이것은 무분별한 중복이 아니라 이력 보존을 위한 의도적인 설계이다.

## 8장. 데이터 타입

데이터 타입은 컬럼에 어떤 종류의 값이 들어갈 수 있는지를 정한다. 타입을 정하면 데이터베이스가 잘못된 형태의 값을 어느 정도 막을 수 있다.

| 타입 | 사용 위치 | 의미 |
| --- | --- | --- |
| `BIGINT` | ID 컬럼 | 큰 정수를 저장한다. |
| `VARCHAR(50)` | 이름, 이메일 | 길이가 변하는 문자열을 저장한다. |
| `DATETIME` | 가입일, 주문 시각 | 날짜와 시간을 함께 저장한다. |
| `DECIMAL(10, 2)` | 가격 | 소수점이 있는 정확한 숫자를 저장한다. |
| `BOOLEAN` | 판매 여부 | 참 또는 거짓을 저장한다. |
| `ENUM` | 주문 상태, 결제수단 | 정해진 값 중 하나만 저장한다. |

가격에 `FLOAT`가 아니라 `DECIMAL`을 사용한 점도 중요하다. 금액은 반올림 오차가 생기면 안 되므로 정확한 십진수 타입인 `DECIMAL`이 적합하다.

## 9장. NULL과 NOT NULL

`NULL`은 값이 없음을 의미한다. 숫자 0이나 빈 문자열과 다르다. 아직 모르는 값, 입력되지 않은 값, 해당되지 않는 값을 표현할 때 사용한다.

그러나 모든 컬럼이 `NULL`을 허용하면 중요한 데이터가 빠진 채 저장될 수 있다. 그래서 반드시 필요한 값에는 `NOT NULL`을 붙인다.

```sql
name VARCHAR(50) NOT NULL
```

고객 이름이 없는 고객, 주문 시각이 없는 주문은 이 미션의 데이터로 의미가 약하다. 따라서 `customer.name`, `cafe_order.ordered_at` 같은 컬럼은 `NOT NULL`로 둔다.

## 10장. 제약조건

제약조건은 테이블에 들어갈 수 있는 데이터를 제한하는 규칙이다. 좋은 데이터베이스 설계는 애플리케이션 코드만 믿지 않고, 데이터베이스 자체에도 규칙을 둔다.

| 제약조건 | 사용 예 | 막는 문제 |
| --- | --- | --- |
| `PRIMARY KEY` | `customer_id` | 같은 행을 구분할 수 없는 문제 |
| `FOREIGN KEY` | `cafe_order.customer_id` | 존재하지 않는 부모 데이터 참조 |
| `NOT NULL` | `customer.name` | 필수 값 누락 |
| `UNIQUE` | `customer.email` | 중복 이메일 |
| `CHECK` | `price > 0` | 음수 가격, 0원 메뉴 |

제약조건의 핵심은 데이터를 믿을 수 있게 만드는 데 있다. 좋은 데이터베이스는 잘못된 데이터가 들어온 뒤에 고치는 것이 아니라, 잘못된 데이터가 처음부터 들어오기 어렵게 설계된다.

## 11장. 삭제 규칙: CASCADE와 RESTRICT

외래키에는 부모 데이터가 삭제될 때 자식 데이터를 어떻게 처리할지 정하는 규칙이 붙을 수 있다.

`ON DELETE CASCADE`는 부모 행이 삭제될 때 자식 행도 함께 삭제한다. 이 프로젝트에서는 주문이 삭제되면 해당 주문의 상세도 함께 삭제되도록 `order_detail.order_id`에 사용했다.

`ON DELETE RESTRICT`는 자식 행이 있으면 부모 행 삭제를 막는다. 예를 들어 어떤 메뉴가 과거 주문 상세에 사용되었다면, 그 메뉴를 함부로 삭제하면 과거 주문을 해석하기 어려워진다. 그래서 `order_detail.menu_item_id`가 참조하는 메뉴 삭제는 제한한다.

정리하면 생명주기가 같은 데이터는 `CASCADE`를 고려하고, 기록 보존이 중요한 데이터는 `RESTRICT`를 고려한다.

## 12장. SELECT

`SELECT`는 데이터를 조회하는 명령이다. 기본 구조는 다음과 같다.

```sql
SELECT 컬럼
FROM 테이블
WHERE 조건
ORDER BY 정렬기준
LIMIT 개수;
```

각 절의 역할은 분명하다.

| 절 | 역할 |
| --- | --- |
| `SELECT` | 어떤 컬럼을 볼지 정한다. |
| `FROM` | 어느 테이블에서 가져올지 정한다. |
| `WHERE` | 어떤 행만 남길지 정한다. |
| `ORDER BY` | 결과를 어떤 기준으로 정렬할지 정한다. |
| `LIMIT` | 몇 개만 볼지 정한다. |

## 13장. JOIN

정규화로 테이블을 나누었기 때문에, 실제 조회에서는 다시 연결해야 한다. 이때 사용하는 문법이 `JOIN`이다.

카페 주문 데이터베이스를 예로 들면, `cafe_order`에는 고객 이름이 직접 저장되어 있지 않다. 주문 테이블에는 `customer_id`만 있고, 고객 이름은 `customer` 테이블에 있다. 주문 목록에 고객 이름을 함께 보여 주려면 두 테이블을 연결해야 한다.

```sql
SELECT o.order_id, c.name, o.ordered_at
FROM cafe_order AS o
INNER JOIN customer AS c ON o.customer_id = c.customer_id;
```

`ON o.customer_id = c.customer_id`는 두 테이블을 어떤 기준으로 붙일지 정하는 조건이다. JOIN을 읽을 때는 “어떤 테이블을 기준으로 시작하는가”, “어떤 테이블을 붙이는가”, “무슨 컬럼끼리 같은 행으로 볼 것인가”를 차례대로 확인한다.

## 13.1 JOIN의 기본 그림

두 테이블을 원 두 개로 생각하면 JOIN의 차이를 더 쉽게 볼 수 있다. 왼쪽 원은 기준 테이블 A, 오른쪽 원은 연결할 테이블 B이다.

```text
      A 테이블              B 테이블
   ┌─────────┐          ┌─────────┐
   │    A    │          │    B    │
   │  ┌──────┼──────────┼──────┐  │
   │  │ 겹침 │          │ 겹침 │  │
   │  └──────┼──────────┼──────┘  │
   └─────────┘          └─────────┘
```

JOIN 종류는 이 그림에서 어느 부분을 결과에 남길지의 차이이다.

| JOIN 종류 | 결과에 남는 부분 | 카페 DB에서의 예 |
| --- | --- | --- |
| `INNER JOIN` | A와 B가 서로 매칭되는 부분 | 고객 정보가 있는 주문만 조회 |
| `LEFT JOIN` | A 전체와 B의 매칭 부분 | 주문이 없는 고객까지 포함해 조회 |
| `RIGHT JOIN` | B 전체와 A의 매칭 부분 | 오른쪽 테이블을 기준으로 모두 보존 |
| `FULL OUTER JOIN` | A와 B의 모든 행 | 양쪽의 미매칭 데이터까지 모두 조회 |
| `CROSS JOIN` | A와 B의 모든 조합 | 모든 고객과 모든 메뉴 조합 만들기 |
| `SELF JOIN` | 같은 테이블을 자기 자신과 연결 | 같은 테이블 안에서 비교하기 |

## 13.2 INNER JOIN

`INNER JOIN`은 양쪽 테이블에 매칭되는 데이터가 있는 행만 보여 준다. 가장 기본적인 JOIN이다.

```text
A: customer
B: cafe_order

INNER JOIN 결과
┌───────────────┐
│ A와 B의 겹침 │
└───────────────┘
```

예를 들어 주문 목록에 고객 이름을 붙일 때 사용할 수 있다.

```sql
SELECT o.order_id, c.name AS customer_name, o.order_status
FROM cafe_order AS o
INNER JOIN customer AS c ON o.customer_id = c.customer_id;
```

이 쿼리는 주문과 고객이 연결되는 행만 보여 준다. `cafe_order.customer_id`가 `customer.customer_id`를 참조하므로, 정상적인 데이터라면 모든 주문은 고객과 연결된다.

## 13.3 LEFT JOIN

`LEFT JOIN`은 왼쪽 테이블의 행을 모두 보존한다. 오른쪽 테이블에 연결되는 데이터가 없으면 오른쪽 컬럼은 `NULL`로 채워진다.

```text
LEFT JOIN 결과
┌───────────────┬───────────────┐
│ A만 있는 부분 │ A와 B의 겹침  │
└───────────────┴───────────────┘
```

주문이 없는 고객까지 보고 싶을 때는 `customer`를 왼쪽에 둔다.

```sql
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```

이 쿼리는 주문이 없는 고객도 결과에 남긴다. 주문이 없는 고객은 `o.order_id`가 `NULL`이므로 `COUNT(o.order_id)` 결과가 0이 된다.

`LEFT JOIN`은 “없는 것을 찾는 쿼리”에서 자주 쓰인다. 예를 들어 주문 이력이 없는 고객을 찾을 때 사용할 수 있다.

```sql
SELECT c.customer_id, c.name
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

## 13.4 RIGHT JOIN

`RIGHT JOIN`은 오른쪽 테이블의 행을 모두 보존한다. `LEFT JOIN`과 방향만 반대이다.

```text
RIGHT JOIN 결과
┌───────────────┬───────────────┐
│ A와 B의 겹침  │ B만 있는 부분 │
└───────────────┴───────────────┘
```

예를 들어 다음 쿼리는 오른쪽 테이블인 `customer`를 기준으로 모든 고객을 보존한다.

```sql
SELECT c.customer_id, c.name, o.order_id
FROM cafe_order AS o
RIGHT JOIN customer AS c ON o.customer_id = c.customer_id;
```

하지만 실무에서는 `RIGHT JOIN`보다 `LEFT JOIN`을 더 자주 사용한다. 기준으로 삼고 싶은 테이블을 왼쪽에 두면 쿼리를 읽기 쉽기 때문이다. 위 쿼리는 다음 `LEFT JOIN`과 같은 의도로 읽을 수 있다.

```sql
SELECT c.customer_id, c.name, o.order_id
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id;
```

## 13.5 FULL OUTER JOIN

`FULL OUTER JOIN`은 양쪽 테이블의 모든 행을 보존한다. 매칭되는 행은 붙여서 보여 주고, 한쪽에만 있는 행은 반대쪽 컬럼을 `NULL`로 채운다.

```text
FULL OUTER JOIN 결과
┌───────────────┬───────────────┬───────────────┐
│ A만 있는 부분 │ A와 B의 겹침  │ B만 있는 부분 │
└───────────────┴───────────────┴───────────────┘
```

PostgreSQL은 `FULL OUTER JOIN`을 지원한다.

```sql
SELECT *
FROM customer AS c
FULL OUTER JOIN cafe_order AS o ON c.customer_id = o.customer_id;
```

MySQL은 `FULL OUTER JOIN` 문법을 직접 지원하지 않는다. MySQL에서 비슷한 결과가 필요하면 `LEFT JOIN`과 `RIGHT JOIN`을 `UNION`으로 합쳐 표현한다.

```sql
SELECT c.customer_id, c.name, o.order_id
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id
UNION
SELECT c.customer_id, c.name, o.order_id
FROM customer AS c
RIGHT JOIN cafe_order AS o ON c.customer_id = o.customer_id;
```

다만 이 프로젝트의 데이터 구조에서는 주문이 반드시 존재하는 고객을 참조하도록 FK가 걸려 있으므로, 고객 없이 주문만 존재하는 경우는 원칙적으로 생기지 않는다.

## 13.6 CROSS JOIN

`CROSS JOIN`은 두 테이블의 모든 조합을 만든다. 연결 조건이 없기 때문에 결과 행 수는 두 테이블 행 수를 곱한 값이 된다.

```text
A가 10행이고 B가 10행이면
CROSS JOIN 결과는 100행이다.
```

예를 들어 모든 고객과 모든 메뉴의 조합을 만들 수 있다.

```sql
SELECT c.name AS customer_name, mi.name AS menu_name
FROM customer AS c
CROSS JOIN menu_item AS mi;
```

이 쿼리는 실제 주문을 의미하지 않는다. “각 고객에게 모든 메뉴를 추천 후보로 만든다”처럼 모든 조합이 필요한 상황에서 사용할 수 있다. 행 수가 급격히 늘어날 수 있으므로 주의해야 한다.

## 13.7 SELF JOIN

`SELF JOIN`은 같은 테이블을 자기 자신과 연결하는 방식이다. 별도의 JOIN 종류라기보다, 같은 테이블에 서로 다른 별칭을 붙여 두 테이블처럼 사용하는 방법이다.

이 프로젝트의 테이블 구조에는 직원-상사 관계처럼 자기 자신을 참조하는 대표 예시는 없다. 그래도 개념을 이해하기 위해 고객 가입일을 서로 비교하는 예를 만들 수 있다.

```sql
SELECT newer.name AS newer_customer, older.name AS older_customer
FROM customer AS newer
INNER JOIN customer AS older ON newer.joined_at > older.joined_at;
```

이 쿼리는 한 고객보다 먼저 가입한 다른 고객들을 찾는다. 같은 `customer` 테이블을 `newer`와 `older`라는 두 이름으로 나누어 읽는 것이 핵심이다.

## 13.8 JOIN을 선택하는 기준

JOIN을 고를 때는 문법 이름부터 외우기보다 “어떤 행을 잃으면 안 되는가”를 먼저 생각해야 한다.

| 원하는 결과 | 적합한 JOIN |
| --- | --- |
| 양쪽에 모두 존재하는 데이터만 필요하다 | `INNER JOIN` |
| 왼쪽 테이블의 모든 행이 필요하다 | `LEFT JOIN` |
| 오른쪽 테이블의 모든 행이 필요하다 | `RIGHT JOIN` |
| 양쪽 테이블의 모든 행이 필요하다 | `FULL OUTER JOIN` |
| 모든 조합이 필요하다 | `CROSS JOIN` |
| 같은 테이블 안에서 행끼리 비교해야 한다 | `SELF JOIN` |

이 미션에서 가장 중요하게 쓰는 조인은 `INNER JOIN`과 `LEFT JOIN`이다. `INNER JOIN`은 연결된 주문, 고객, 메뉴 정보를 함께 볼 때 사용하고, `LEFT JOIN`은 주문이 없는 고객처럼 “연결되지 않은 데이터”까지 확인할 때 사용한다.

## 14장. GROUP BY

`GROUP BY`는 여러 행을 그룹으로 묶고, 그룹별 계산을 할 때 사용한다. 예를 들어 주문 상태별 주문 수, 결제수단별 매출, 고객별 평균 주문 금액을 계산할 수 있다.

자주 쓰는 집계 함수는 다음과 같다.

| 함수 | 의미 |
| --- | --- |
| `COUNT(*)` | 행 개수를 센다. |
| `SUM()` | 합계를 구한다. |
| `AVG()` | 평균을 구한다. |
| `MIN()` | 최솟값을 구한다. |
| `MAX()` | 최댓값을 구한다. |

집계 쿼리에서는 “무엇을 기준으로 묶는가”와 “무엇을 계산하는가”를 구분해야 한다. 결제수단별 매출이라면 기준은 결제수단이고, 계산 대상은 `quantity * unit_price`의 합계이다.

## 15장. 서브쿼리

서브쿼리는 쿼리 안에 들어 있는 또 다른 쿼리이다. 어떤 결과를 먼저 구하고, 그 결과를 바깥 쿼리에서 조건으로 사용할 때 쓴다.

예를 들어 주문 이력이 없는 고객을 찾을 때는 주문 테이블에 등장한 고객 ID 목록을 먼저 구한 뒤, 그 목록에 없는 고객을 찾을 수 있다.

```sql
SELECT customer_id, name, email
FROM customer
WHERE customer_id NOT IN (
  SELECT customer_id
  FROM cafe_order
);
```

같은 문제는 `LEFT JOIN`으로도 풀 수 있다. 중요한 것은 한 가지 문제를 여러 방식으로 표현할 수 있다는 점이다.

## 16장. UPDATE와 DELETE

`UPDATE`는 기존 데이터를 수정한다.

```sql
UPDATE cafe_order
SET order_status = 'PAID'
WHERE order_id = 9;
```

`DELETE`는 기존 데이터를 삭제한다.

```sql
DELETE FROM cafe_order
WHERE order_id = 5 AND order_status = 'CANCELED';
```

두 명령은 실제 데이터를 바꾸므로 항상 `WHERE` 조건을 확인해야 한다. 조건 없이 실행하면 테이블의 모든 행이 수정되거나 삭제될 수 있다.

## 17장. 인덱스와 EXPLAIN

인덱스는 데이터를 더 빨리 찾기 위한 자료구조이다. 책의 찾아보기처럼, 테이블 전체를 처음부터 끝까지 읽지 않고 필요한 위치를 빠르게 찾도록 돕는다.

이 프로젝트에서는 주문일 기준 조회와 정렬이 자주 일어난다고 보고 `ordered_at`에 인덱스를 만들었다.

```sql
CREATE INDEX idx_cafe_order_ordered_at ON cafe_order(ordered_at);
```

인덱스는 조회 성능에 도움을 줄 수 있지만 공짜는 아니다. 데이터를 추가, 수정, 삭제할 때 인덱스도 함께 갱신해야 하며 저장 공간도 사용한다. 따라서 자주 검색, 정렬, 조인에 쓰이는 컬럼을 중심으로 신중하게 만든다.

`EXPLAIN`은 쿼리를 실제로 실행하기 전에 DBMS가 어떤 방식으로 실행할지 보여 주는 명령이다. 인덱스를 만들었다면 실행 계획에서 그 인덱스가 사용되는지 확인할 수 있다.

## 18장. MySQL과 PostgreSQL의 차이

MySQL과 PostgreSQL은 모두 관계형 데이터베이스 관리 시스템이다. 둘 다 테이블, 행, 컬럼, PK, FK, JOIN, GROUP BY 같은 관계형 데이터베이스의 핵심 개념을 지원한다. 따라서 이 미션에서 배운 설계 개념은 MySQL뿐 아니라 PostgreSQL에도 대부분 그대로 적용된다.

차이는 같은 SQL을 사용하더라도 세부 문법, 데이터 타입, 기능 철학, 기본 동작에서 나타난다.

| 구분 | MySQL | PostgreSQL |
| --- | --- | --- |
| 성격 | 널리 쓰이는 범용 RDBMS이다. 웹 서비스에서 많이 사용된다. | 표준 SQL 준수와 확장 기능이 강한 RDBMS이다. |
| 자동 증가 ID | `AUTO_INCREMENT`를 사용한다. | 보통 `SERIAL`, `BIGSERIAL`, 또는 `GENERATED AS IDENTITY`를 사용한다. |
| 문자열 타입 | `VARCHAR`, `TEXT` 등을 사용한다. | `VARCHAR`, `TEXT` 등을 사용하며 `TEXT` 사용이 자연스럽다. |
| 불리언 타입 | `BOOLEAN`을 쓸 수 있지만 내부적으로는 숫자처럼 처리된다. | `BOOLEAN` 타입이 명확하다. |
| ENUM | `ENUM('A', 'B')`를 컬럼에 직접 선언할 수 있다. | 별도 enum 타입을 만들거나 `CHECK` 제약조건을 사용한다. |
| 현재 시각 | `CURRENT_TIMESTAMP`를 사용한다. | `CURRENT_TIMESTAMP`, `now()` 등을 사용한다. |
| 실행 계획 | `EXPLAIN`을 사용한다. | `EXPLAIN`, `EXPLAIN ANALYZE`를 자주 사용한다. |
| JSON | JSON 기능을 지원한다. | `JSONB`가 강력하여 JSON 검색과 인덱싱에 많이 사용된다. |
| 엄격함 | 설정에 따라 타입 변환을 비교적 유연하게 처리할 수 있다. | 타입과 SQL 규칙을 더 엄격하게 검사하는 편이다. |

이 프로젝트의 `schema.sql`은 MySQL 기준으로 작성되어 있다. 예를 들어 다음 문법은 MySQL 스타일이다.

```sql
customer_id BIGINT AUTO_INCREMENT PRIMARY KEY
```

PostgreSQL에서는 보통 다음처럼 쓸 수 있다.

```sql
customer_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

또 MySQL의 `ENUM` 컬럼은 다음처럼 작성되어 있다.

```sql
order_status ENUM('ORDERED', 'PAID', 'CANCELED', 'COMPLETED')
```

PostgreSQL에서는 별도 타입을 만들거나 `CHECK` 제약조건으로 표현할 수 있다.

```sql
order_status VARCHAR(20) CHECK (
  order_status IN ('ORDERED', 'PAID', 'CANCELED', 'COMPLETED')
)
```

중요한 점은 MySQL과 PostgreSQL의 차이를 “어느 하나가 무조건 더 좋다”로 이해하지 않는 것이다. 둘 다 좋은 데이터베이스이고, 프로젝트의 요구사항, 팀의 경험, 운영 환경, 필요한 기능에 따라 선택한다.

이 미션에서는 MySQL을 사용한다. 이유는 Docker로 실행하기 쉽고, 입문자가 테이블 생성, FK, JOIN, GROUP BY, 인덱스를 실습하기에 충분하기 때문이다. 다만 개념 자체는 PostgreSQL에서도 그대로 이어진다.

따라서 이 장의 핵심은 분명하다. MySQL과 PostgreSQL은 서로 다른 DBMS이지만, 관계형 데이터베이스의 기본 사고방식은 공유한다. 이 프로젝트의 SQL 파일은 MySQL 문법으로 작성되어 있으나, 테이블을 나누고 키로 연결한 뒤 SQL로 다시 읽는 설계 원리는 PostgreSQL에서도 그대로 이어진다.

## 19장. 정리

이 프로젝트는 카페 주문 데이터를 여러 테이블로 나누어 저장한다. 고객, 메뉴 카테고리, 메뉴, 주문, 주문 상세는 각각 의미와 변경 이유가 다르다. 하나의 큰 테이블에 모두 넣으면 고객 이메일, 메뉴명, 카테고리명, 가격이 주문마다 반복되고, 데이터가 바뀔 때 불일치가 생기기 쉽다.

테이블을 나눈 뒤에는 PK와 FK로 관계를 표현한다. PK는 각 행을 식별하고, FK는 존재하는 데이터만 참조하도록 제한한다. 이 구조 덕분에 주문은 고객과 연결되고, 주문 상세는 주문 및 메뉴와 연결된다.

주문과 주문 상세를 분리한 이유는 하나의 주문에 여러 메뉴가 들어갈 수 있기 때문이다. 주문 시각, 고객, 주문 상태, 결제수단은 주문 한 건의 공통 정보이고, 메뉴, 수량, 단가는 주문 안의 각 메뉴마다 달라지는 정보이다.

`order_detail.unit_price`는 주문 당시 단가를 보존하기 위해 따로 저장한다. 메뉴의 현재 가격이 바뀌어도 과거 주문 금액과 매출 계산이 바뀌면 안 되기 때문이다. 이처럼 좋은 설계는 중복을 줄이는 것뿐 아니라, 시간이 지나도 데이터의 의미가 흔들리지 않도록 만드는 일이다.

SQL은 나누어 저장된 데이터를 다시 읽기 위한 언어이다. `SELECT`는 필요한 데이터를 꺼내고, `JOIN`은 테이블을 연결하며, `GROUP BY`는 여러 행을 묶어 지표를 만든다. `UPDATE`와 `DELETE`는 데이터를 직접 바꾸므로 조건을 신중히 확인해야 한다. 인덱스는 조회를 빠르게 할 수 있지만, 쓰기 비용과 저장 공간을 함께 고려해야 한다.

## 20장. 맺음말

관계형 데이터베이스는 데이터를 의미 있는 테이블로 나누고, PK와 FK로 연결한 뒤, SQL로 다시 조합하여 필요한 답을 얻는 체계이다.
