"""
Подключение к БД: асинхронный движок и сессии.

DatabaseHelper инкапсулирует engine и session_factory.
get_session — зависимость FastAPI с автоматическим commit/rollback транзакции.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from settings.config import settings


class DatabaseHelper:
    """
    Хелпер для работы с асинхронной БД.

    - Создаёт engine и session_factory при инициализации
    - get_session() — генератор сессии с commit при успехе, rollback при ошибке
    - dispose() — корректное закрытие пула соединений при остановке приложения
    """

    def __init__(
        self,
        url: str,
        *,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        async_url = self._to_async_url(url)
        connect_args = (
            {"check_same_thread": False}
            if "sqlite" in async_url
            else {}
        )
        self.engine: AsyncEngine = create_async_engine(
            async_url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size if "sqlite" not in async_url else 1,
            max_overflow=max_overflow if "sqlite" not in async_url else 0,
            connect_args=connect_args,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = (
            async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        )

    @staticmethod
    def _to_async_url(url: str) -> str:
        """Преобразует sync URL в async (sqlite+aiosqlite, postgresql+asyncpg)."""
        if url.startswith("sqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    async def dispose(self) -> None:
        """Закрывает пул соединений. Вызывать при shutdown приложения."""
        await self.engine.dispose()

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Зависимость FastAPI: сессия БД с управлением транзакцией.

        - При успешном завершении обработчика — commit
        - При исключении — rollback, исключение пробрасывается дальше
        """
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


db_helper = DatabaseHelper(
    url=settings.database_url,
    echo=settings.database_echo,
    echo_pool=False,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
)
