# API Заказов

REST-API на **FastAPI**, **SQLAlchemy**, **Pydantic**. Асинхронные эндпоинты, контейнеризация (Docker).

## Эндпоинты API

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/orders/items` | Добавить товар в заказ |
| GET | `/api/nomenclature/` | Список всей номенклатуры |
| GET | `/api/categories/` | Плоский список категорий |
| GET | `/api/categories/tree` | Дерево категорий с количеством товаров |

## Сервис «Добавление товара в заказ» (ТЗ п.3)

- **Метод**: `POST /api/orders/items`
- **Тело запроса**: `order_id`, `nomenclature_id`, `quantity`
- Если товар уже есть в заказе — **количество увеличивается** (новая позиция не создаётся).
- Если товара **нет в наличии** в нужном количестве — возвращается ошибка **400** с текстом.

### Пример запроса

```bash
curl -X POST "http://localhost:8000/api/orders/items" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 1, "nomenclature_id": 1, "quantity": 2}'
```

### Документация API

- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

## Запуск

### Локально (uv)

```bash
uv sync
cp .env.example .env   # опционально: настройка через переменные окружения
uv run python scripts/init_db.py      # создание таблиц
uv run python scripts/seed_test_data.py  # тестовые данные (дерево категорий как на картинке)
uv run uvicorn main:app --reload
```

URL БД и порт настраиваются через `.env` (см. `.env.example`). По умолчанию — SQLite `./catalog.db`, порт 8000.

> **Важно:** при изменении схемы БД (добавление таблиц) удалите `catalog.db` и заново выполните `init_db` и `seed_test_data`.

### Docker

```bash
docker compose up --build
```

API будет доступен на **http://localhost:8000**. База SQLite монтируется в `./catalog.db`.

## Стек

- **FastAPI** — REST-API, async-эндпоинты, автодокументация
- **SQLAlchemy 2 (async)** — модели и сессии БД
- **Pydantic + pydantic-settings** — валидация и конфигурация из `.env`
- **Docker / docker-compose** — контейнеризация

## Структура работы с БД

- `database/db_helper.py` — `DatabaseHelper`: engine, session_factory, `get_session()` (с commit/rollback), `dispose()` при shutdown
- `database/base.py` — `Base`, sync engine для скриптов (`init_db`, `seed_test_data`)
- Конфигурация: `settings/config.py`, переменные `DATABASE_URL`, `RUN_HOST`, `RUN_PORT` и др.
