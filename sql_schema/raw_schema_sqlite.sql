-- Схема БД для SQLite: дерево категорий и номенклатура
-- Реляционная модель, неограниченная вложенность категорий (список смежных вершин)

-- ---------------------------------------------------------------------------
-- Дерево категорий (неограниченный уровень вложенности)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(255) NOT NULL,
    parent_id   INTEGER NULL REFERENCES categories (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories (name);
CREATE INDEX IF NOT EXISTS idx_categories_parent_id ON categories (parent_id);

-- ---------------------------------------------------------------------------
-- Номенклатура (наименование, количество, цена)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS nomenclature (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        VARCHAR(512) NOT NULL,
    quantity    NUMERIC(18, 4) NOT NULL DEFAULT 0,
    price       NUMERIC(18, 2) NOT NULL,
    category_id INTEGER NULL REFERENCES categories (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_nomenclature_name ON nomenclature (name);
CREATE INDEX IF NOT EXISTS idx_nomenclature_category_id ON nomenclature (category_id);

-- ---------------------------------------------------------------------------
-- Клиенты (наименование, адрес) — ТЗ 1.3
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clients (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    VARCHAR(255) NOT NULL,
    address VARCHAR(512) NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_clients_name ON clients (name);

-- ---------------------------------------------------------------------------
-- Заказы и позиции заказа
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NULL REFERENCES clients (id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders (client_id);

CREATE TABLE IF NOT EXISTS order_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    nomenclature_id INTEGER NOT NULL REFERENCES nomenclature (id) ON DELETE CASCADE,
    quantity       NUMERIC(18, 4) NOT NULL,
    UNIQUE (order_id, nomenclature_id)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_nomenclature_id ON order_items (nomenclature_id);
