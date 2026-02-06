"""Сервис работы с номенклатурой."""

from sqlalchemy.ext.asyncio import AsyncSession

from repositories import NomenclatureRepository
from schemas.nomenclature import NomenclatureResponse


async def list_nomenclature(session: AsyncSession) -> list[NomenclatureResponse]:
    """Получить список всех товаров (номенклатуры)."""
    repo = NomenclatureRepository(session)
    items = await repo.get_all()
    return [NomenclatureResponse.model_validate(item) for item in items]
