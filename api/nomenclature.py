"""REST-API номенклатуры (товаров): список всех товаров в БД."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_async_session
from database.models import Nomenclature
from schemas.nomenclature import NomenclatureResponse

router = APIRouter(prefix="/nomenclature", tags=["Номенклатура (товары)"])


@router.get(
    "/",
    response_model=list[NomenclatureResponse],
    summary="Список всех товаров",
    description="Возвращает все товары (номенклатуру), которые есть в БД.",
)
async def list_nomenclature(
    session: AsyncSession = Depends(get_async_session),
) -> list[NomenclatureResponse]:
    """GET-эндпоинт: отображение всех товаров, которые уже есть в БД."""
    result = await session.execute(select(Nomenclature).order_by(Nomenclature.id))
    items = result.scalars().all()
    return [NomenclatureResponse.model_validate(item) for item in items]
