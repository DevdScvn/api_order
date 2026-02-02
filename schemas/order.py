"""Схемы для заказов и добавления товара в заказ."""

from decimal import Decimal

from pydantic import BaseModel, Field


class AddItemToOrderRequest(BaseModel):
    """Тело запроса: добавление товара в заказ."""

    order_id: int = Field(..., description="ID заказа", gt=0)
    nomenclature_id: int = Field(..., description="ID номенклатуры (товара)", gt=0)
    quantity: Decimal = Field(..., description="Количество", gt=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_id": 1,
                    "nomenclature_id": 1,
                    "quantity": 2.5,
                }
            ]
        }
    }


class OrderItemResponse(BaseModel):
    """Ответ: позиция заказа после добавления/обновления."""

    id: int
    order_id: int
    nomenclature_id: int
    quantity: Decimal

    model_config = {"from_attributes": True}


class ErrorDetail(BaseModel):
    """Детали ошибки API."""

    detail: str = Field(..., description="Описание ошибки")
    code: str | None = Field(None, description="Код ошибки")
