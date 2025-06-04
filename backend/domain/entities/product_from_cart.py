from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.sqlite_database import Base


class ProductFromCart(Base):
    __tablename__ = "products_from_carts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    cart_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("carts.cart_id"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.product_id"), nullable=False, index=True
    )
    quantity: Mapped[int]

    def __repr__(self) -> str:
        return (
            f"<ProductFromCart(id={self.id}, cart_id={self.cart_id}, "
            f"product_id={self.product_id}, quantity={self.quantity})>"
        )
