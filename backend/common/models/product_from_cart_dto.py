from pydantic import BaseModel, ConfigDict


class ProductFromCartDto(BaseModel):
    cart_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)
