-- ==========================================
-- Clothing Store Database
-- 建立服飾資料庫與六張資料表
-- ==========================================

CREATE DATABASE IF NOT EXISTS clothing_store;
USE clothing_store;

-- 1. 服飾類別
CREATE TABLE IF NOT EXISTS categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL
);

-- 2. 品牌
CREATE TABLE IF NOT EXISTS brands (
    brand_id INT PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL,
    country VARCHAR(50)
);

-- 3. 服飾商品
CREATE TABLE IF NOT EXISTS clothing (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL,
    brand_id INT NOT NULL,
    color VARCHAR(30),
    size VARCHAR(10),
    price DECIMAL(10,2) NOT NULL,
    stock_qty INT NOT NULL DEFAULT 0,
    listed_date DATE,
    image_url VARCHAR(500),
    CONSTRAINT fk_clothing_category
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
    CONSTRAINT fk_clothing_brand
        FOREIGN KEY (brand_id)
        REFERENCES brands(brand_id)
);

-- 4. 顧客
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city VARCHAR(50),
    member_level VARCHAR(20)
);

-- 5. 訂單
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10) NOT NULL,
    order_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- 6. 訂單明細
CREATE TABLE IF NOT EXISTS order_items (
    item_id VARCHAR(10) PRIMARY KEY,
    order_id VARCHAR(10) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id),
    CONSTRAINT fk_items_product
        FOREIGN KEY (product_id)
        REFERENCES clothing(product_id)
);

-- 建立完成後檢查資料庫與資料表
SELECT DATABASE();
SHOW TABLES;
