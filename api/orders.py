"""REST-API заказов: добавление товара в заказ."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_helper import db_helper
from exceptions import (
    InsufficientStockError,
    NomenclatureNotFoundError,
    OrderNotFoundError,
)
from schemas.order import AddItemToOrderRequest, ErrorDetail, OrderItemResponse
from services.order_service import add_product_to_order

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post(
    "/items",
    response_model=OrderItemResponse,
    responses={
        400: {
            "description": "Товара нет в наличии в запрошенном количестве",
            "model": ErrorDetail,
        },
        404: {
            "description": "Заказ или номенклатура не найдены",
            "model": ErrorDetail,
        },
    },
    summary="Добавить товар в заказ",
    description=(
        "Принимает ID заказа, ID номенклатуры и количество. "
        "Если товар уже есть в заказе — количество увеличивается (новая позиция не создаётся). "
        "Если товара нет в наличии — возвращается ошибка 400."
    ),
)
async def add_item_to_order(
    body: AddItemToOrderRequest,
    session: AsyncSession = Depends(db_helper.get_session),
) -> OrderItemResponse:
    """
    **Добавление товара в заказ.**

    - **order_id** — ID заказа (должен существовать).
    - **nomenclature_id** — ID номенклатуры (товара).
    - **quantity** — количество (строго больше 0).

    При повторном добавлении той же номенклатуры в тот же заказ количество суммируется.
    """
    try:
        item = await add_product_to_order(
            session=session,
            order_id=body.order_id,
            nomenclature_id=body.nomenclature_id,
            quantity=body.quantity,
        )
        return OrderItemResponse.model_validate(item)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NomenclatureNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Товара нет в наличии в нужном количестве. Доступно: {e.available}, запрошено: {e.requested}",
        )
