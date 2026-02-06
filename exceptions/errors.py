"""Классы исключений приложения."""

from decimal import Decimal


class OrderNotFoundError(Exception):
    """Заказ не найден."""

    pass


class NomenclatureNotFoundError(Exception):
    """Номенклатура не найдена."""

    pass


class InsufficientStockError(Exception):
    """Товара нет в наличии в нужном количестве."""

    def __init__(self, available: Decimal, requested: Decimal):
        self.available = available
        self.requested = requested
        super().__init__(
            f"Недостаточно товара в наличии: доступно {available}, запрошено {requested}"
        )
