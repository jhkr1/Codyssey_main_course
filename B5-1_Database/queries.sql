-- cafe_order_db에서 실습할 핵심 SQL 쿼리 모음이다.
-- schema.sql과 sample_data.sql을 먼저 실행한 뒤 이 파일을 실행한다.

USE cafe_order_db;

-- 01. 기본 SELECT: 판매 중이고 6,000원 미만인 메뉴를 조회한다.
SELECT menu_item_id, name, price
FROM menu_item
WHERE is_available = TRUE AND price < 6000
ORDER BY price ASC;

-- 02. ORDER BY와 LIMIT: 최신 주문 5건을 조회한다.
SELECT order_id, customer_id, order_status, ordered_at, payment_method
FROM cafe_order
ORDER BY ordered_at DESC
LIMIT 5;

-- 03. LIKE 패턴 검색: example.com 이메일을 사용하는 고객을 조회한다.
SELECT customer_id, name, email, joined_at
FROM customer
WHERE email LIKE '%@example.com'
ORDER BY joined_at ASC;

-- 04. IN 조건: 아직 확인이 필요한 주문 상태를 조회한다.
SELECT order_id, customer_id, order_status, ordered_at
FROM cafe_order
WHERE order_status IN ('ORDERED', 'CANCELED')
ORDER BY ordered_at;

-- 05. INNER JOIN: 주문 목록에 고객 이름을 함께 표시한다.
SELECT o.order_id, c.name AS customer_name, o.order_status, o.ordered_at
FROM cafe_order AS o
INNER JOIN customer AS c ON o.customer_id = c.customer_id
ORDER BY o.order_id;

-- 06. INNER JOIN: 주문 상세에 메뉴명과 줄 금액을 함께 표시한다.
SELECT od.order_detail_id, od.order_id, mi.name AS menu_name,
       od.quantity, od.unit_price, od.quantity * od.unit_price AS line_total
FROM order_detail AS od
INNER JOIN menu_item AS mi ON od.menu_item_id = mi.menu_item_id
ORDER BY od.order_detail_id;

-- 07. INNER JOIN: 메뉴 목록에 카테고리명을 함께 표시한다.
SELECT mi.menu_item_id, mi.name AS menu_name, mc.name AS category_name, mi.price
FROM menu_item AS mi
INNER JOIN menu_category AS mc ON mi.category_id = mc.category_id
ORDER BY mi.menu_item_id;

-- 08. LEFT JOIN: 주문이 없는 고객까지 포함하여 고객별 주문 수를 조회한다.
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM customer AS c
LEFT JOIN cafe_order AS o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY order_count ASC, c.customer_id;

-- 09. COUNT 집계: 주문 상태별 주문 수를 계산한다.
SELECT order_status, COUNT(*) AS order_count
FROM cafe_order
GROUP BY order_status
ORDER BY order_count DESC;

-- 10. SUM 집계: 취소 주문을 제외하고 결제수단별 매출을 계산한다.
SELECT o.payment_method, SUM(od.quantity * od.unit_price) AS total_sales
FROM cafe_order AS o
INNER JOIN order_detail AS od ON o.order_id = od.order_id
WHERE o.order_status <> 'CANCELED'
GROUP BY o.payment_method
ORDER BY total_sales DESC;

-- 11. AVG 집계: 카테고리별 평균 메뉴 가격을 계산한다.
SELECT mc.name AS category_name, ROUND(AVG(mi.price), 2) AS average_menu_price
FROM menu_category AS mc
INNER JOIN menu_item AS mi ON mc.category_id = mi.category_id
GROUP BY mc.category_id, mc.name
ORDER BY average_menu_price DESC;

-- 12. 서브쿼리: 주문 이력이 없는 고객을 조회한다.
SELECT customer_id, name, email
FROM customer
WHERE customer_id NOT IN (
  SELECT customer_id
  FROM cafe_order
)
ORDER BY customer_id;

-- 13. UPDATE: 특정 주문의 상태를 결제 완료로 변경한다.
UPDATE cafe_order
SET order_status = 'PAID'
WHERE order_id = 9;

SELECT order_id, order_status
FROM cafe_order
WHERE order_id = 9;

-- 14. DELETE: 취소 주문을 삭제하고 ON DELETE CASCADE 동작을 확인한다.
DELETE FROM cafe_order
WHERE order_id = 5 AND order_status = 'CANCELED';

SELECT COUNT(*) AS remaining_order_rows
FROM cafe_order
WHERE order_id = 5;

SELECT COUNT(*) AS remaining_order_detail_rows
FROM order_detail
WHERE order_id = 5;

-- 15. 인덱스 생성과 확인: 주문 시각 검색/정렬을 빠르게 하기 위해 ordered_at에 인덱스를 만든다.
CREATE INDEX idx_cafe_order_ordered_at ON cafe_order(ordered_at);

EXPLAIN
SELECT order_id, customer_id, order_status, ordered_at
FROM cafe_order
WHERE ordered_at >= '2026-03-04 00:00:00'
ORDER BY ordered_at;

-- Bonus A. JOIN 방식: Coffee 카테고리에 속한 메뉴를 조회한다.
SELECT mi.menu_item_id, mi.name, mi.price
FROM menu_item AS mi
INNER JOIN menu_category AS mc ON mi.category_id = mc.category_id
WHERE mc.name = 'Coffee'
ORDER BY mi.price;

-- Bonus B. 서브쿼리 방식: Coffee 카테고리에 속한 메뉴를 조회한다.
SELECT menu_item_id, name, price
FROM menu_item
WHERE category_id = (
  SELECT category_id
  FROM menu_category
  WHERE name = 'Coffee'
)
ORDER BY price;

-- Bonus C. FK 무결성 테스트: customer_id 999가 존재하지 않으므로 주석을 해제하면 실패해야 한다.
-- INSERT INTO cafe_order (customer_id, order_status, ordered_at, payment_method)
-- VALUES (999, 'ORDERED', '2026-03-10 10:00:00', 'CARD');
