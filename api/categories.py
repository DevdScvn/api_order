"""REST-API дерева категорий номенклатуры."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_helper import db_helper
from schemas.category import CategoryResponse, CategoryTreeItem
from services.category_service import get_category_tree, list_categories

router = APIRouter(prefix="/categories", tags=["Каталог / Дерево категорий"])


@router.get(
    "/",
    response_model=list[CategoryResponse],
    summary="Список всех категорий",
    description="Возвращает все категории (плоский список).",
)
async def list_categories_endpoint(
    session: AsyncSession = Depends(db_helper.get_session),
) -> list[CategoryResponse]:
    """GET: плоский список категорий."""
    return await list_categories(session)


@router.get(
    "/tree",
    response_model=list[CategoryTreeItem],
    summary="Дерево категорий",
    description="Возвращает иерархическое дерево категорий с количеством товаров в каждой.",
)
async def category_tree_endpoint(
    session: AsyncSession = Depends(db_helper.get_session),
) -> list[CategoryTreeItem]:
    """GET: дерево категорий с подсчётом товаров (как на картинке)."""
    return await get_category_tree(session)
