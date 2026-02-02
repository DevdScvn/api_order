#!/usr/bin/env python3
"""Создание таблиц БД через SQLAlchemy (для разработки)."""

import sys
from pathlib import Path

# Корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import init_db

if __name__ == "__main__":
    # По умолчанию SQLite в корне проекта
    init_db()
    print("Таблицы созданы: catalog.db")
