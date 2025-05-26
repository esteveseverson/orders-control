from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from . import table_registry

@table_registry.mapped_as_dataclass
class Product:
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    barcode: Mapped[str] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    expiration: Mapped[datetime] = mapped_column(nullable=False)
    image: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now(), onupdate=func.now()
    )