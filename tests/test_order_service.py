"""Unit-тесты для сервиса добавления товара в заказ."""

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import InsufficientStockError, NomenclatureNotFoundError, OrderNotFoundError
from services.order_service import add_product_to_order


@pytest.fixture()
def session() -> AsyncSession:
    """Фикстура-заглушка сессии БД."""
    return MagicMock(spec=AsyncSession)


@pytest.mark.asyncio
async def test_add_product_to_order_order_not_found(session: AsyncSession) -> None:
    """Если заказа нет – выбрасывается OrderNotFoundError."""
    with patch("services.order_service.OrderRepository") as order_repo_cls, patch(
        "services.order_service.NomenclatureRepository"
    ), patch("services.order_service.OrderItemRepository"):
        order_repo = order_repo_cls.return_value
        order_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(OrderNotFoundError):
            await add_product_to_order(
                session=session,
                order_id=1,
                nomenclature_id=10,
                quantity=Decimal("1"),
            )


@pytest.mark.asyncio
async def test_add_product_to_order_nomenclature_not_found(
    session: AsyncSession,
) -> None:
    """Если номенклатура не найдена – NomenclatureNotFoundError."""
    with patch("services.order_service.OrderRepository") as order_repo_cls, patch(
        "services.order_service.NomenclatureRepository"
    ) as nom_repo_cls, patch("services.order_service.OrderItemRepository"):
        order_repo = order_repo_cls.return_value
        order_repo.get_by_id = AsyncMock(return_value=object())

        nom_repo = nom_repo_cls.return_value
        nom_repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(NomenclatureNotFoundError):
            await add_product_to_order(
                session=session,
                order_id=1,
                nomenclature_id=10,
                quantity=Decimal("1"),
            )


@pytest.mark.asyncio
async def test_add_product_to_order_insufficient_stock(session: AsyncSession) -> None:
    """Если товара не хватает – InsufficientStockError."""
    nomenclature = MagicMock()
    nomenclature.quantity = Decimal("3")

    existing_item = MagicMock()
    existing_item.quantity = Decimal("2")

    with patch("services.order_service.OrderRepository") as order_repo_cls, patch(
        "services.order_service.NomenclatureRepository"
    ) as nom_repo_cls, patch(
        "services.order_service.OrderItemRepository"
    ) as item_repo_cls:
        order_repo = order_repo_cls.return_value
        order_repo.get_by_id = AsyncMock(return_value=object())

        nom_repo = nom_repo_cls.return_value
        nom_repo.get_by_id = AsyncMock(return_value=nomenclature)

        item_repo = item_repo_cls.return_value
        item_repo.get_by_order_and_nomenclature = AsyncMock(return_value=existing_item)

        with pytest.raises(InsufficientStockError) as exc:
            await add_product_to_order(
                session=session,
                order_id=1,
                nomenclature_id=10,
                quantity=Decimal("5"),
            )

        assert exc.value.available == Decimal("3")
        assert exc.value.requested == Decimal("7")


@pytest.mark.asyncio
async def test_add_product_to_order_update_existing_item(session: AsyncSession) -> None:
    """Если позиция уже есть – обновляется количество через update_quantity."""
    nomenclature = MagicMock()
    nomenclature.quantity = Decimal("10")

    existing_item = MagicMock()
    existing_item.quantity = Decimal("2")

    updated_item = MagicMock()

    with patch("services.order_service.OrderRepository") as order_repo_cls, patch(
        "services.order_service.NomenclatureRepository"
    ) as nom_repo_cls, patch(
        "services.order_service.OrderItemRepository"
    ) as item_repo_cls:
        order_repo = order_repo_cls.return_value
        order_repo.get_by_id = AsyncMock(return_value=object())

        nom_repo = nom_repo_cls.return_value
        nom_repo.get_by_id = AsyncMock(return_value=nomenclature)

        item_repo = item_repo_cls.return_value
        item_repo.get_by_order_and_nomenclature = AsyncMock(return_value=existing_item)
        item_repo.update_quantity = AsyncMock(return_value=updated_item)

        result = await add_product_to_order(
            session=session,
            order_id=1,
            nomenclature_id=10,
            quantity=Decimal("3"),
        )

        assert result is updated_item
        item_repo.update_quantity.assert_awaited_once()


@pytest.mark.asyncio
async def test_add_product_to_order_create_new_item(session: AsyncSession) -> None:
    """Если позиции нет – создаётся новая через create."""
    nomenclature = MagicMock()
    nomenclature.quantity = Decimal("10")

    created_item: Any = MagicMock()

    with patch("services.order_service.OrderRepository") as order_repo_cls, patch(
        "services.order_service.NomenclatureRepository"
    ) as nom_repo_cls, patch(
        "services.order_service.OrderItemRepository"
    ) as item_repo_cls:
        order_repo = order_repo_cls.return_value
        order_repo.get_by_id = AsyncMock(return_value=object())

        nom_repo = nom_repo_cls.return_value
        nom_repo.get_by_id = AsyncMock(return_value=nomenclature)

        item_repo = item_repo_cls.return_value
        item_repo.get_by_order_and_nomenclature = AsyncMock(return_value=None)
        item_repo.create = AsyncMock(return_value=created_item)

        result = await add_product_to_order(
            session=session,
            order_id=1,
            nomenclature_id=10,
            quantity=Decimal("3"),
        )

        assert result is created_item
        item_repo.create.assert_awaited_once_with(1, 10, Decimal("3"))

