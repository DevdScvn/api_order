"""Сервис добавления товара в заказ."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import OrderItem
from exceptions import (
    InsufficientStockError,
    NomenclatureNotFoundError,
    OrderNotFoundError,
)
from repositories import (
    NomenclatureRepository,
    OrderItemRepository,
    OrderRepository,
)


async def add_product_to_order(
    session: AsyncSession,
    order_id: int,
    nomenclature_id: int,
    quantity: Decimal,
) -> OrderItem:
    """
    Добавляет товар в заказ по REST-API контракту.

    - Если позиция с данной номенклатурой уже есть в заказе — увеличивает количество.
    - Если позиции нет — создаёт новую.
    - Если товара нет в наличии в нужном количестве — выбрасывает InsufficientStockError.

    :param session: асинхронная сессия БД
    :param order_id: ID заказа
    :param nomenclature_id: ID номенклатуры
    :param quantity: количество
    :return: созданная или обновлённая позиция заказа (OrderItem)
    """
    order_repo = OrderRepository(session)
    nom_repo = NomenclatureRepository(session)
    item_repo = OrderItemRepository(session)

    order = await order_repo.get_by_id(order_id)
    if order is None:
        raise OrderNotFoundError(f"Заказ с ID {order_id} не найден")

    nomenclature = await nom_repo.get_by_id(nomenclature_id)
    if nomenclature is None:
        raise NomenclatureNotFoundError(
            f"Номенклатура с ID {nomenclature_id} не найдена"
        )

    existing_item = await item_repo.get_by_order_and_nomenclature(
        order_id, nomenclature_id
    )
    current_in_order = existing_item.quantity if existing_item else Decimal("0")
    total_required = current_in_order + quantity

    available = nomenclature.quantity
    if available < total_required:
        raise InsufficientStockError(available=available, requested=total_required)

    if existing_item:
        return await item_repo.update_quantity(existing_item, total_required)

    return await item_repo.create(order_id, nomenclature_id, quantity)
