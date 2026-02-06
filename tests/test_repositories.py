"""Быстрые unit-тесты для репозиториев, проверяющие их основные методы."""

from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import BaseRepository
from repositories.category_repository import CategoryRepository
from repositories.nomenclature_repository import NomenclatureRepository
from repositories.order_item_repository import OrderItemRepository
from repositories.order_repository import OrderRepository


def test_order_repository_inherits_base_repository() -> None:
    """OrderRepository должен быть наследником BaseRepository с правильной моделью."""
    session = MagicMock(spec=AsyncSession)
    repo = OrderRepository(session)
    assert isinstance(repo, BaseRepository)


def test_order_item_repository_inherits_base_repository() -> None:
    """OrderItemRepository наследуется от BaseRepository."""
    session = MagicMock(spec=AsyncSession)
    repo = OrderItemRepository(session)
    assert isinstance(repo, BaseRepository)


def test_nomenclature_repository_inherits_base_repository() -> None:
    """NomenclatureRepository наследуется от BaseRepository."""
    session = MagicMock(spec=AsyncSession)
    repo = NomenclatureRepository(session)
    assert isinstance(repo, BaseRepository)


def test_category_repository_inherits_base_repository() -> None:
    """CategoryRepository наследуется от BaseRepository."""
    session = MagicMock(spec=AsyncSession)
    repo = CategoryRepository(session)
    assert isinstance(repo, BaseRepository)

