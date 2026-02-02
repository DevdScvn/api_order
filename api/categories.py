"""REST-API дерева категорий номенклатуры."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.base import get_async_session
from database.models import Category, Nomenclature
from schemas.category import CategoryResponse, CategoryTreeItem

router = APIRouter(prefix="/categories", tags=["Каталог / Дерево категорий"])


@router.get(
    "/",
    response_model=list[CategoryResponse],
    summary="Список всех категорий",
    description="Возвращает все категории (плоский список).",
)
async def list_categories(
    session: AsyncSession = Depends(get_async_session),
) -> list[CategoryResponse]:
    """GET: плоский список категорий."""
    result = await session.execute(
        select(Category).order_by(Category.parent_id.nullsfirst(), Category.name)
    )
    items = result.scalars().all()
    return [CategoryResponse.model_validate(c) for c in items]


@router.get(
    "/tree",
    response_model=list[CategoryTreeItem],
    summary="Дерево категорий",
    description="Возвращает иерархическое дерево категорий с количеством товаров в каждой.",
)
async def category_tree(
    session: AsyncSession = Depends(get_async_session),
) -> list[CategoryTreeItem]:
    """GET: дерево категорий с подсчётом товаров (как на картинке)."""
    result = await session.execute(
        select(Category).where(Category.parent_id.is_(None)).order_by(Category.name)
    )
    roots = result.scalars().all()

    async def build_node(cat: Category) -> CategoryTreeItem:
        # Количество товаров напрямую в этой категории
        count_result = await session.execute(
            select(func.count(Nomenclature.id)).where(Nomenclature.category_id == cat.id)
        )
        count = count_result.scalar() or 0

        # Рекурсивно строим детей
        children_result = await session.execute(
            select(Category).where(Category.parent_id == cat.id).order_by(Category.name)
        )
        children = children_result.scalars().all()
        child_items = [await build_node(c) for c in children]

        return CategoryTreeItem(
            id=cat.id,
            name=cat.name,
            parent_id=cat.parent_id,
            children=child_items,
            item_count=count,
        )

    return [await build_node(r) for r in roots]
