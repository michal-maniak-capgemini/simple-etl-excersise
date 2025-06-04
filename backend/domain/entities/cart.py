from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.sqlite_database import Base


class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    cart_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.user_id"), nullable=False, index=True
    )

    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, cart_id={self.cart_id}, user_id={self.user_id})>"
