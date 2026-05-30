-- cafe_order_db 실습에 사용할 샘플 데이터이다.
-- schema.sql을 먼저 실행한 뒤 이 파일을 실행한다.

USE cafe_order_db;

INSERT INTO customer (name, email, phone, joined_at) VALUES
('Kim Minjun', 'minjun.kim@example.com', '010-1000-0001', '2026-01-03 10:12:00'),
('Lee Seoyeon', 'seoyeon.lee@example.com', '010-1000-0002', '2026-01-05 14:20:00'),
('Park Jiho', 'jiho.park@example.com', '010-1000-0003', '2026-01-08 09:30:00'),
('Choi Yuna', 'yuna.choi@example.com', '010-1000-0004', '2026-01-12 16:40:00'),
('Jung Haein', 'haein.jung@example.com', '010-1000-0005', '2026-01-17 11:05:00'),
('Kang Doyun', 'doyun.kang@example.com', '010-1000-0006', '2026-02-01 13:11:00'),
('Yoon Harin', 'harin.yoon@example.com', '010-1000-0007', '2026-02-04 18:22:00'),
('Lim Siwoo', 'siwoo.lim@example.com', '010-1000-0008', '2026-02-09 08:15:00'),
('Han Jisoo', 'jisoo.han@example.com', '010-1000-0009', '2026-02-14 12:44:00'),
('Oh Eunwoo', 'eunwoo.oh@example.com', '010-1000-0010', '2026-02-20 15:31:00');

INSERT INTO menu_category (name, description) VALUES
('Coffee', 'Espresso based drinks'),
('Non Coffee', 'Tea, chocolate, and ade drinks'),
('Dessert', 'Cakes, cookies, and bakery items'),
('Sandwich', 'Meal style sandwiches'),
('Seasonal', 'Limited season menu'),
('Bottle Drink', 'Ready-to-drink bottled beverages'),
('Bean', 'Coffee beans for home brewing'),
('Merchandise', 'Cafe goods and tumblers'),
('Breakfast', 'Morning sets and light meals'),
('Smoothie', 'Fruit and yogurt blended drinks');

INSERT INTO menu_item (category_id, name, price, is_available) VALUES
(1, 'Americano', 4500.00, TRUE),
(1, 'Cafe Latte', 5200.00, TRUE),
(1, 'Vanilla Latte', 5800.00, TRUE),
(1, 'Cold Brew', 5500.00, TRUE),
(2, 'Milk Tea', 5600.00, TRUE),
(2, 'Lemon Ade', 5900.00, TRUE),
(3, 'Cheesecake', 6800.00, TRUE),
(3, 'Chocolate Cookie', 3200.00, TRUE),
(4, 'Ham Cheese Sandwich', 7600.00, TRUE),
(5, 'Strawberry Cream Latte', 6500.00, FALSE);

INSERT INTO cafe_order (customer_id, order_status, ordered_at, payment_method) VALUES
(1, 'COMPLETED', '2026-03-01 09:10:00', 'CARD'),
(2, 'COMPLETED', '2026-03-01 12:30:00', 'MOBILE'),
(3, 'PAID', '2026-03-02 14:05:00', 'CARD'),
(4, 'COMPLETED', '2026-03-03 08:55:00', 'CASH'),
(5, 'CANCELED', '2026-03-03 18:20:00', 'CARD'),
(1, 'COMPLETED', '2026-03-04 10:15:00', 'MOBILE'),
(6, 'PAID', '2026-03-04 13:40:00', 'CARD'),
(7, 'COMPLETED', '2026-03-05 11:25:00', 'CARD'),
(8, 'ORDERED', '2026-03-06 16:00:00', 'CASH'),
(9, 'COMPLETED', '2026-03-07 19:10:00', 'MOBILE');

INSERT INTO order_detail (order_id, menu_item_id, quantity, unit_price) VALUES
(1, 1, 2, 4500.00),
(1, 8, 1, 3200.00),
(2, 2, 1, 5200.00),
(2, 7, 2, 6800.00),
(3, 3, 1, 5800.00),
(4, 9, 1, 7600.00),
(5, 6, 1, 5900.00),
(6, 4, 2, 5500.00),
(7, 5, 1, 5600.00),
(8, 1, 1, 4500.00),
(9, 7, 1, 6800.00),
(10, 2, 2, 5200.00);
