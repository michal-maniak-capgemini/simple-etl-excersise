from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.sqlite_database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    title: Mapped[str]
    description: Mapped[str]
    category: Mapped[str]
    price: Mapped[float]
    product_id: Mapped[int] = mapped_column(unique=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, title={self.title}, description={self.description}, "
            f"category={self.category}, price={self.price}, product_id={self.product_id})>"
        )
