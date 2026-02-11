"""
Базовые классы SQLAlchemy: Base для моделей, sync-движок для скриптов.

Асинхронные сессии и API — в database.db_helper.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from settings.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


def get_engine(database_url: str | None = None):
    """Синхронный движок БД (для init_db, seed, миграций)."""
    url = database_url or settings.database_url
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
        echo=settings.database_echo,
    )


def get_session_factory(engine=None):
    """Фабрика синхронных сессий (для скриптов init_db, seed_test_data)."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(database_url: str | None = None) -> None:
    """
    Создаёт все таблицы в БД.

    Вызывать при старте приложения или в скриптах инициализации.
    """
    import database.models  # noqa: F401 — регистрируем таблицы в Base.metadata
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
