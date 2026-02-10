"""Модели БД: дерево категорий, номенклатура, заказы и позиции заказа."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Category(Base):
    """
    Дерево категорий номенклатуры с неограниченной вложенностью.
    Паттерн «список смежных вершин»: parent_id ссылается на родительскую категорию.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Самоссылка: родитель и дочерние категории
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
        foreign_keys=[parent_id],
    )
    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        foreign_keys=[parent_id],
        cascade="all, delete-orphan",
    )

    # Номенклатура в этой категории
    nomenclature: Mapped[list["Nomenclature"]] = relationship(
        "Nomenclature",
        back_populates="category",
        foreign_keys="Nomenclature.category_id",
    )

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name={self.name!r}, parent_id={self.parent_id})"


class Nomenclature(Base):
    """
    Номенклатура: наименование, количество, цена.
    Связана с категорией (опционально — товар может быть без категории).
    """

    __tablename__ = "nomenclature"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_nomenclature_quantity_non_negative"),
        CheckConstraint("price >= 0", name="check_nomenclature_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category: Mapped["Category | None"] = relationship(
        "Category",
        back_populates="nomenclature",
        foreign_keys=[category_id],
    )

    # Позиции заказов с этой номенклатурой
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="nomenclature",
        foreign_keys="OrderItem.nomenclature_id",
    )

    def __repr__(self) -> str:
        return f"Nomenclature(id={self.id}, name={self.name!r}, quantity={self.quantity}, price={self.price})"


class Client(Base):
    """
    Клиент: наименование и адрес (ТЗ 1.3).
    """

    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="client",
        foreign_keys="Order.client_id",
    )

    def __repr__(self) -> str:
        return f"Client(id={self.id}, name={self.name!r})"


class Order(Base):
    """
    Заказ покупателя. Содержит позиции (OrderItem) — номенклатура и количество.
    Может быть привязан к клиенту (ТЗ 1.4).
    """

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    client: Mapped["Client | None"] = relationship(
        "Client",
        back_populates="orders",
        foreign_keys=[client_id],
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        foreign_keys="OrderItem.order_id",
    )

    def __repr__(self) -> str:
        return f"Order(id={self.id})"


class OrderItem(Base):
    """
    Позиция заказа: одна номенклатура в заказе с количеством.
    Один товар в заказе — одна строка (уникальная пара order_id + nomenclature_id).
    """

    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "nomenclature_id", name="uq_order_nomenclature"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nomenclature_id: Mapped[int] = mapped_column(
        ForeignKey("nomenclature.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
        foreign_keys=[order_id],
    )
    nomenclature: Mapped["Nomenclature"] = relationship(
        "Nomenclature",
        back_populates="order_items",
        foreign_keys=[nomenclature_id],
    )

    def __repr__(self) -> str:
        return f"OrderItem(id={self.id}, order_id={self.order_id}, nomenclature_id={self.nomenclature_id}, quantity={self.quantity})"
