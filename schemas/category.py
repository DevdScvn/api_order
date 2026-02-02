"""Схемы для дерева категорий."""

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    """Ответ: категория из БД."""

    id: int
    name: str = Field(..., description="Наименование категории")
    parent_id: int | None = Field(None, description="ID родительской категории")

    model_config = {"from_attributes": True}


class CategoryTreeItem(BaseModel):
    """Элемент дерева категорий с вложенными дочерними."""

    id: int
    name: str
    parent_id: int | None
    children: list["CategoryTreeItem"] = Field(default_factory=list)
    item_count: int = Field(0, description="Количество товаров в этой категории (напрямую)")

    model_config = {"from_attributes": True}


# Для рекурсивной схемы
CategoryTreeItem.model_rebuild()
