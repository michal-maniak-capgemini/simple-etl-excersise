from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.sqlite_database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    )
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    age: Mapped[int]
    birth_date: Mapped[str]
    street: Mapped[str]
    city: Mapped[str]
    country: Mapped[str]
    user_id: Mapped[int]

    def __repr__(self) -> str:
        return (
            f"<User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
            f"email={self.email}, age={self.age}, birth_date={self.birth_date}, "
            f"street={self.street}, city={self.city}, country={self.country}, "
            f"user_id={self.user_id})>"
        )
