"""Unit-тесты сервиса номенклатуры."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.nomenclature import NomenclatureResponse
from services.nomenclature_service import list_nomenclature


class FakeNomenclature:
    def __init__(
        self,
        id: int,
        name: str,
        quantity: int | Decimal,
        price: int | Decimal,
        category_id: int | None = None,
    ):
        self.id = id
        self.name = name
        self.quantity = Decimal(quantity)
        self.price = Decimal(price)
        self.category_id = category_id


@pytest.fixture()
def session() -> AsyncSession:
    return MagicMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_list_nomenclature_uses_repository_and_maps_to_schema(
    session: AsyncSession,
) -> None:
    """Проверяем, что список номенклатуры берётся из репозитория и мапится в Pydantic-схемы."""
    fake_item = FakeNomenclature(
        id=1,
        name="Товар",
        quantity=10,
        price="99.90",
        category_id=2,
    )

    with patch("services.nomenclature_service.NomenclatureRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_all = AsyncMock(return_value=[fake_item])

        result = await list_nomenclature(session)

        repo_cls.assert_called_once_with(session)
        repo.get_all.assert_awaited_once()

        assert len(result) == 1
        assert isinstance(result[0], NomenclatureResponse)
        assert result[0].id == 1
        assert result[0].name == "Товар"

