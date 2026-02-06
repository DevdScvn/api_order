"""Репозиторий для работы с категориями."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Category, Nomenclature
from repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """CRUD-операции для Category."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Category)

    async def get_all_flat(self) -> list[Category]:
        """Получить плоский список всех категорий, отсортированный по parent_id и name."""
        result = await self._session.execute(
            select(Category).order_by(Category.parent_id.nullsfirst(), Category.name)
        )
        return list(result.scalars().all())

    async def get_roots(self) -> list[Category]:
        """Получить корневые категории (без родителя)."""
        result = await self._session.execute(
            select(Category).where(Category.parent_id.is_(None)).order_by(Category.name)
        )
        return list(result.scalars().all())

    async def get_children(self, parent_id: int) -> list[Category]:
        """Получить дочерние категории по parent_id."""
        result = await self._session.execute(
            select(Category).where(Category.parent_id == parent_id).order_by(Category.name)
        )
        return list(result.scalars().all())

    async def count_nomenclature_in_category(self, category_id: int) -> int:
        """Подсчитать количество товаров в категории."""
        result = await self._session.execute(
            select(func.count(Nomenclature.id)).where(
                Nomenclature.category_id == category_id
            )
        )
        return result.scalar() or 0
