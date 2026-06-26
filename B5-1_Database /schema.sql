-- 카페 주문 관리 데이터베이스의 스키마이다.
-- DBMS는 MySQL 8.x를 기준으로 한다.
-- AUTO_INCREMENT, ENUM, ENGINE=InnoDB와 같은 MySQL 문법을 사용한다.

DROP DATABASE IF EXISTS cafe_order_db;
CREATE DATABASE cafe_order_db
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE cafe_order_db;

CREATE TABLE customer (
  customer_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  phone VARCHAR(20) UNIQUE,
  joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE menu_category (
  category_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  description VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE menu_item (
  menu_item_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  category_id BIGINT NOT NULL,
  name VARCHAR(80) NOT NULL UNIQUE,
  price DECIMAL(10, 2) NOT NULL,
  is_available BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT fk_menu_item_category
    FOREIGN KEY (category_id)
    REFERENCES menu_category(category_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT chk_menu_item_price
    CHECK (price > 0)
) ENGINE=InnoDB;

CREATE TABLE cafe_order (
  order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_status ENUM('ORDERED', 'PAID', 'CANCELED', 'COMPLETED') NOT NULL DEFAULT 'ORDERED',
  ordered_at DATETIME NOT NULL,
  payment_method ENUM('CARD', 'CASH', 'MOBILE') NOT NULL,
  CONSTRAINT fk_cafe_order_customer
    FOREIGN KEY (customer_id)
    REFERENCES customer(customer_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE order_detail (
  order_detail_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  menu_item_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10, 2) NOT NULL,
  CONSTRAINT fk_order_detail_order
    FOREIGN KEY (order_id)
    REFERENCES cafe_order(order_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT fk_order_detail_menu_item
    FOREIGN KEY (menu_item_id)
    REFERENCES menu_item(menu_item_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,
  CONSTRAINT chk_order_detail_quantity
    CHECK (quantity > 0),
  CONSTRAINT chk_order_detail_unit_price
    CHECK (unit_price > 0)
) ENGINE=InnoDB;
