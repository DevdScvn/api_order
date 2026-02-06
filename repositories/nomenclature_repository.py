"""Репозиторий для работы с номенклатурой."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Nomenclature
from repositories.base import BaseRepository


class NomenclatureRepository(BaseRepository[Nomenclature]):
    """CRUD-операции для Nomenclature."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Nomenclature)

    async def get_all(self) -> list[Nomenclature]:
        """Получить весь список номенклатуры, отсортированный по ID."""
        result = await self._session.execute(
            select(Nomenclature).order_by(Nomenclature.id)
        )
        return list(result.scalars().all())
