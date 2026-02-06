"""Сервис работы с категориями."""

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Category
from repositories import CategoryRepository
from schemas.category import CategoryResponse, CategoryTreeItem


async def list_categories(session: AsyncSession) -> list[CategoryResponse]:
    """Получить плоский список всех категорий."""
    repo = CategoryRepository(session)
    items = await repo.get_all_flat()
    return [CategoryResponse.model_validate(c) for c in items]


async def get_category_tree(session: AsyncSession) -> list[CategoryTreeItem]:
    """Получить дерево категорий с подсчётом товаров в каждой."""
    repo = CategoryRepository(session)
    roots = await repo.get_roots()

    async def build_node(cat: Category) -> CategoryTreeItem:
        count = await repo.count_nomenclature_in_category(cat.id)
        children = await repo.get_children(cat.id)
        child_items = [await build_node(c) for c in children]
        return CategoryTreeItem(
            id=cat.id,
            name=cat.name,
            parent_id=cat.parent_id,
            children=child_items,
            item_count=count,
        )

    return [await build_node(r) for r in roots]
