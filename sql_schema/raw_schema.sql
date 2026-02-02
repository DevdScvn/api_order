-- Схема БД: дерево категорий и номенклатура
-- Реляционная модель, неограниченная вложенность категорий (список смежных вершин)
-- Совместимо с PostgreSQL; для SQLite уберите или замените SERIAL/BIGSERIAL на INTEGER

-- ---------------------------------------------------------------------------
-- Дерево категорий (неограниченный уровень вложенности)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    parent_id   INTEGER NULL REFERENCES categories (id) ON DELETE SET NULL,
    CONSTRAINT categories_parent_fk FOREIGN KEY (parent_id) REFERENCES categories (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (name);
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories (parent_id);

COMMENT ON TABLE categories IS 'Дерево категорий номенклатуры с неограниченной вложенностью';
COMMENT ON COLUMN categories.parent_id IS 'Родительская категория; NULL для корневого уровня';

-- ---------------------------------------------------------------------------
-- Номенклатура (наименование, количество, цена)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nomenclature (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(512) NOT NULL,
    quantity    NUMERIC(18, 4) NOT NULL DEFAULT 0,
    price       NUMERIC(18, 2) NOT NULL,
    category_id INTEGER NULL REFERENCES categories (id) ON DELETE SET NULL,
    CONSTRAINT nomenclature_category_fk FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_nomenclature_name ON nomenclature (name);
CREATE INDEX IF NOT EXISTS idx_nomenclature_category_id ON nomenclature (category_id);

COMMENT ON TABLE nomenclature IS 'Номенклатура: наименование, количество, цена';
COMMENT ON COLUMN nomenclature.category_id IS 'Категория товара; NULL допустимо';

-- ---------------------------------------------------------------------------
-- Клиенты (наименование, адрес) — ТЗ 1.3
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clients (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(255) NOT NULL,
    address VARCHAR(512) NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_clients_name ON clients (name);

COMMENT ON TABLE clients IS 'Клиенты: наименование и адрес';

-- ---------------------------------------------------------------------------
-- Заказы и позиции заказа
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id        SERIAL PRIMARY KEY,
    client_id INTEGER NULL REFERENCES clients (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders (client_id);

COMMENT ON TABLE orders IS 'Заказ; позиции в order_items';

CREATE TABLE IF NOT EXISTS order_items (
    id          SERIAL PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    nomenclature_id INTEGER NOT NULL REFERENCES nomenclature (id) ON DELETE CASCADE,
    quantity    NUMERIC(18, 4) NOT NULL,
    CONSTRAINT uq_order_nomenclature UNIQUE (order_id, nomenclature_id)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_nomenclature_id ON order_items (nomenclature_id);

COMMENT ON TABLE order_items IS 'Позиция заказа: номенклатура и количество; один товар в заказе — одна строка';
