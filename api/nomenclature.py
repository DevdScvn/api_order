"""REST-API номенклатуры (товаров): список всех товаров в БД."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_async_session
from schemas.nomenclature import NomenclatureResponse
from services.nomenclature_service import list_nomenclature

router = APIRouter(prefix="/nomenclature", tags=["Номенклатура (товары)"])


@router.get(
    "/",
    response_model=list[NomenclatureResponse],
    summary="Список всех товаров",
    description="Возвращает все товары (номенклатуру), которые есть в БД.",
)
async def list_nomenclature_endpoint(
    session: AsyncSession = Depends(get_async_session),
) -> list[NomenclatureResponse]:
    """GET-эндпоинт: отображение всех товаров, которые уже есть в БД."""
    return await list_nomenclature(session)
