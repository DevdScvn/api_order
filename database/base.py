"""Базовые настройки SQLAlchemy: движок, сессии (sync/async), создание таблиц."""

from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# По умолчанию SQLite — для разработки. Для продакшена подставьте URL PostgreSQL и т.д.
DEFAULT_DATABASE_URL = "sqlite:///./catalog.db"
DEFAULT_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./catalog.db"


def get_engine(database_url: str | None = None):
    """Создаёт и возвращает синхронный движок БД."""
    url = database_url or DEFAULT_DATABASE_URL
    return create_engine(
        url,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
        echo=False,
    )


def get_async_engine(database_url: str | None = None):
    """Создаёт и возвращает асинхронный движок БД."""
    url = database_url or DEFAULT_ASYNC_DATABASE_URL
    if url.startswith("sqlite://"):
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return create_async_engine(
        url,
        connect_args={"check_same_thread": False} if "sqlite" in url else {},
        echo=False,
    )


def get_session_factory(engine=None):
    """Фабрика синхронных сессий."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_async_session_factory(engine=None):
    """Фабрика асинхронных сессий для API."""
    if engine is None:
        engine = get_async_engine()
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )


_async_session_factory = get_async_session_factory()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость FastAPI: асинхронная сессия БД (commit при успехе, rollback при ошибке)."""
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""

    pass


def init_db(database_url: str | None = None) -> None:
    """
    Создаёт все таблицы в БД.
    Вызывать при старте приложения или отдельно для инициализации.
    """
    import database.models  # noqa: F401 — регистрируем таблицы в Base.metadata
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
