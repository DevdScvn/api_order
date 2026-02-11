"""Конфигурация приложения через переменные окружения."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig:
    """Параметры подключения к БД."""

    def __init__(
        self,
        url: str,
        *,
        echo: bool = False,
        echo_pool: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self.url = url
        self.echo = echo
        self.echo_pool = echo_pool
        self.pool_size = pool_size
        self.max_overflow = max_overflow

    @property
    def async_url(self) -> str:
        """URL для асинхронного движка (sqlite -> sqlite+aiosqlite)."""
        if self.url.startswith("sqlite://"):
            return self.url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        if self.url.startswith("postgresql://"):
            return self.url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.url


class RunConfig:
    """Параметры запуска приложения."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.host = host
        self.port = port


class Settings(BaseSettings):
    """Главные настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = "sqlite:///./catalog.db"
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    run_host: str = "127.0.0.1"
    run_port: int = 8000

    @property
    def db(self) -> DatabaseConfig:
        return DatabaseConfig(
            url=self.database_url,
            echo=self.database_echo,
            pool_size=self.database_pool_size,
            max_overflow=self.database_max_overflow,
        )

    @property
    def run(self) -> RunConfig:
        return RunConfig(host=self.run_host, port=self.run_port)


settings = Settings()
