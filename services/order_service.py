"""Сервис добавления товара в заказ."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Nomenclature, Order, OrderItem


class OrderNotFoundError(Exception):
    """Заказ не найден."""

    pass


class NomenclatureNotFoundError(Exception):
    """Номенклатура не найдена."""

    pass


class InsufficientStockError(Exception):
    """Товара нет в наличии в нужном количестве."""

    def __init__(self, available: Decimal, requested: Decimal):
        self.available = available
        self.requested = requested
        super().__init__(f"Недостаточно товара в наличии: доступно {available}, запрошено {requested}")


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
    # Проверяем существование заказа
    order_result = await session.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalar_one_or_none()
    if order is None:
        raise OrderNotFoundError(f"Заказ с ID {order_id} не найден")

    # Проверяем существование номенклатуры и остаток
    nom_result = await session.execute(
        select(Nomenclature).where(Nomenclature.id == nomenclature_id)
    )
    nomenclature = nom_result.scalar_one_or_none()
    if nomenclature is None:
        raise NomenclatureNotFoundError(f"Номенклатура с ID {nomenclature_id} не найдена")

    # Текущее количество этой номенклатуры уже в заказе
    existing_result = await session.execute(
        select(OrderItem).where(
            OrderItem.order_id == order_id,
            OrderItem.nomenclature_id == nomenclature_id,
        )
    )
    existing_item = existing_result.scalar_one_or_none()
    current_in_order = existing_item.quantity if existing_item else Decimal("0")
    total_required = current_in_order + quantity

    # Проверка наличия на складе (nomenclature.quantity — остаток)
    available = nomenclature.quantity
    if available < total_required:
        raise InsufficientStockError(available=available, requested=total_required)

    if existing_item:
        existing_item.quantity = total_required
        await session.flush()
        await session.refresh(existing_item)
        return existing_item

    new_item = OrderItem(
        order_id=order_id,
        nomenclature_id=nomenclature_id,
        quantity=quantity,
    )
    session.add(new_item)
    await session.flush()
    await session.refresh(new_item)
    return new_item
