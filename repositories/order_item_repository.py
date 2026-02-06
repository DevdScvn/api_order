"""Репозиторий для работы с позициями заказа."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import OrderItem
from repositories.base import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    """CRUD-операции для OrderItem."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, OrderItem)

    async def get_by_order_and_nomenclature(
        self, order_id: int, nomenclature_id: int
    ) -> OrderItem | None:
        """Найти позицию заказа по order_id и nomenclature_id."""
        result = await self._session.execute(
            select(OrderItem).where(
                OrderItem.order_id == order_id,
                OrderItem.nomenclature_id == nomenclature_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self, order_id: int, nomenclature_id: int, quantity: Decimal
    ) -> OrderItem:
        """Создать новую позицию заказа."""
        item = OrderItem(
            order_id=order_id,
            nomenclature_id=nomenclature_id,
            quantity=quantity,
        )
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def update_quantity(self, item: OrderItem, quantity: Decimal) -> OrderItem:
        """Обновить количество в позиции заказа."""
        item.quantity = quantity
        await self._session.flush()
        await self._session.refresh(item)
        return item
