"""Схемы для номенклатуры (товаров)."""

from decimal import Decimal

from pydantic import BaseModel, Field


class NomenclatureResponse(BaseModel):
    """Ответ: один товар (номенклатура) из БД."""

    id: int
    name: str = Field(..., description="Наименование")
    quantity: Decimal = Field(..., description="Остаток на складе")
    price: Decimal = Field(..., description="Цена")
    category_id: int | None = Field(None, description="ID категории")

    model_config = {"from_attributes": True}
