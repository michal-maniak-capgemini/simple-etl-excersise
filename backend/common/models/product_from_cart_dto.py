from pydantic import BaseModel


class ProductFromCartDto(BaseModel):
    cart_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True
