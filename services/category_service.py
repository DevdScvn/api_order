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
    """Получить дерево категорий с подсчётом товаров в каждой (2 запроса вместо N)."""
    repo = CategoryRepository(session)
    all_categories = await repo.get_all_flat()
    counts_by_category = await repo.get_nomenclature_counts_by_category()

    # Группируем по parent_id, дочерние отсортированы по name (порядок из get_all_flat)
    children_by_parent: dict[int | None, list[Category]] = {}
    for cat in all_categories:
        children_by_parent.setdefault(cat.parent_id, []).append(cat)
    for key in children_by_parent:
        children_by_parent[key].sort(key=lambda c: c.name)

    def build_node(cat: Category) -> CategoryTreeItem:
        children = children_by_parent.get(cat.id, [])
        return CategoryTreeItem(
            id=cat.id,
            name=cat.name,
            parent_id=cat.parent_id,
            children=[build_node(child) for child in children],
            item_count=counts_by_category.get(cat.id, 0),
        )

    roots = children_by_parent.get(None, [])
    return [build_node(r) for r in roots]
