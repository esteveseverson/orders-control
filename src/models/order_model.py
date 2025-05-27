from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import table_registry


class OrderStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'canceled'


@table_registry.mapped_as_dataclass
class Order:
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey('clients.id'), nullable=False
    )
    total: Mapped[int] = mapped_column(nullable=False)
    items: Mapped[list['OrderItem']] = relationship(
        back_populates='order', cascade='all, delete-orphan'
    )
    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )


@table_registry.mapped_as_dataclass
class OrderItem:
    __tablename__ = 'order_items'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey('orders.id'), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id'), nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[int] = mapped_column(nullable=False)

    order: Mapped['Order'] = relationship(back_populates='items')
