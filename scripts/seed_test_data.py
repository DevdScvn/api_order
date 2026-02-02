#!/usr/bin/env python3
"""
Тестовые данные по дереву категорий (как на картинках):
- Бытовая техника
  - Стиральные машины (0)
  - Холодильники (2)
    - однокамерные (0)
    - двухкамерные (0)
  - Телевизоры (0)
- Компьютеры
  - Ноутбуки (2)
    - 17" (0)
    - 19" (0)
  - Моноблоки (0)

Числа — количество товаров в категории (напрямую или в подкатегориях).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from database import get_session_factory, init_db
from database.models import Category, Client, Nomenclature, Order


def seed_data(session) -> None:
    """Создаёт дерево категорий, номенклатуру, клиентов и заказы."""
    # --- Дерево категорий ---
    cat_result = session.execute(select(Category).limit(1))
    if cat_result.scalar_one_or_none() is not None:
        print("Категории уже есть, пропускаем")
        return

    # Корневые
    bt = Category(name="Бытовая техника", parent_id=None)
    comp = Category(name="Компьютеры", parent_id=None)
    session.add_all([bt, comp])
    session.flush()

    # Бытовая техника -> подкатегории
    стиральные = Category(name="Стиральные машины", parent_id=bt.id)
    холодильники = Category(name="Холодильники", parent_id=bt.id)
    телевизоры = Category(name="Телевизоры", parent_id=bt.id)
    session.add_all([стиральные, холодильники, телевизоры])
    session.flush()

    # Холодильники -> подкатегории
    однокамерные = Category(name="однокамерные", parent_id=холодильники.id)
    двухкамерные = Category(name="двухкамерные", parent_id=холодильники.id)
    session.add_all([однокамерные, двухкамерные])
    session.flush()

    # Компьютеры -> подкатегории
    ноутбуки = Category(name="Ноутбуки", parent_id=comp.id)
    моноблоки = Category(name="Моноблоки", parent_id=comp.id)
    session.add_all([ноутбуки, моноблоки])
    session.flush()

    # Ноутбуки -> подкатегории
    n17 = Category(name='17"', parent_id=ноутбуки.id)
    n19 = Category(name='19"', parent_id=ноутбуки.id)
    session.add_all([n17, n19])
    session.flush()

    # --- Номенклатура (количество как на картинке) ---
    # Бытовая техника: 3 — 1 в Стиральные + 2 в Холодильники (однокамерные, двухкамерные)
    # Холодильники: 2 — по 1 в однокамерные и двухкамерные
    # Компьютеры: 2 — 2 в Ноутбуки (17", 19")
    # Ноутбуки: 2 — по 1 в 17" и 19"

    nomenclature = [
        # Стиральные машины (1)
        Nomenclature(
            name="Стиральная машина Samsung",
            quantity=5,
            price=35000,
            category_id=стиральные.id,
        ),
        # однокамерные (1)
        Nomenclature(
            name="Холодильник однокамерный Атлант",
            quantity=3,
            price=18000,
            category_id=однокамерные.id,
        ),
        # двухкамерные (1)
        Nomenclature(
            name="Холодильник двухкамерный LG",
            quantity=4,
            price=45000,
            category_id=двухкамерные.id,
        ),
        # 17" (1)
        Nomenclature(
            name='Ноутбук 17" ASUS',
            quantity=2,
            price=65000,
            category_id=n17.id,
        ),
        # 19" (1)
        Nomenclature(
            name='Ноутбук 19" Dell',
            quantity=3,
            price=72000,
            category_id=n19.id,
        ),
    ]
    session.add_all(nomenclature)
    session.flush()

    # --- Клиенты ---
    clients = [
        Client(name="ООО Рога и копыта", address="г. Москва, ул. Ленина, 1"),
        Client(name="ИП Иванов", address="г. Санкт-Петербург, Невский пр., 10"),
    ]
    session.add_all(clients)
    session.flush()

    # --- Заказы ---
    order1 = Order(client_id=clients[0].id)
    session.add(order1)
    session.flush()
    print(
        "Создано: дерево категорий, 5 товаров, 2 клиента, заказ id=1. "
        "Пример: POST /api/orders/items {\"order_id\": 1, \"nomenclature_id\": 1, \"quantity\": 2}"
    )


if __name__ == "__main__":
    init_db()
    session_factory = get_session_factory()
    with session_factory() as session:
        seed_data(session)
        session.commit()
    print("Готово.")
