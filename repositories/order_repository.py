"""Репозиторий для работы с заказами."""

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Order
from repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """CRUD-операции для Order."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Order)
