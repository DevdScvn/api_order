"""Общие фикстуры для тестов FastAPI-приложения."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path
from typing import Any
import sys

import pytest
from fastapi import FastAPI
from httpx import AsyncClient


# Обеспечиваем, что корень проекта (где лежит main.py) есть в sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app as fastapi_app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Отдельный event loop для pytest с async-тестами."""
    loop = asyncio.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Приложение FastAPI для API-тестов."""
    return fastapi_app


@pytest.fixture()
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    """HTTP-клиент для интеграционных/API-тестов."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
