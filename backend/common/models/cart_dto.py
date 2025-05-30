from pydantic import BaseModel


class CartDto(BaseModel):
    cart_id: int
    user_id: int

    class Config:
        from_attributes = True
