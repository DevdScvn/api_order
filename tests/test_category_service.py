"""Unit-тесты сервиса категорий."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.category import CategoryResponse, CategoryTreeItem
from services.category_service import get_category_tree, list_categories


@pytest.fixture()
def session() -> AsyncSession:
    return MagicMock(spec=AsyncSession)


class FakeCategory:
    def __init__(self, id: int, name: str, parent_id: int | None = None):
        self.id = id
        self.name = name
        self.parent_id = parent_id


@pytest.mark.asyncio
async def test_list_categories_uses_repository_and_maps_to_schema(
    session: AsyncSession,
) -> None:
    """Проверяем, что список категорий берётся из репозитория и мапится в Pydantic-схемы."""
    fake_category = FakeCategory(id=1, name="Root", parent_id=None)

    with patch("services.category_service.CategoryRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_all_flat = AsyncMock(return_value=[fake_category])

        result = await list_categories(session)

        repo_cls.assert_called_once_with(session)
        repo.get_all_flat.assert_awaited_once()

        assert len(result) == 1
        assert isinstance(result[0], CategoryResponse)
        assert result[0].id == 1
        assert result[0].name == "Root"


@pytest.mark.asyncio
async def test_get_category_tree_builds_recursive_tree(session: AsyncSession) -> None:
    """Проверяем построение дерева категорий и подсчёт товаров (2 запроса: все категории + счётчики)."""
    root = FakeCategory(id=1, name="Root", parent_id=None)
    child = FakeCategory(id=2, name="Child", parent_id=1)

    with patch("services.category_service.CategoryRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_all_flat = AsyncMock(return_value=[root, child])
        repo.get_nomenclature_counts_by_category = AsyncMock(
            return_value={1: 5, 2: 2}
        )

        tree = await get_category_tree(session)

        repo_cls.assert_called_once_with(session)
        repo.get_all_flat.assert_awaited_once()
        repo.get_nomenclature_counts_by_category.assert_awaited_once()

        assert len(tree) == 1
        root_node = tree[0]
        assert isinstance(root_node, CategoryTreeItem)
        assert root_node.id == 1
        assert root_node.item_count == 5
        assert len(root_node.children) == 1
        child_node = root_node.children[0]
        assert child_node.id == 2
        assert child_node.item_count == 2

