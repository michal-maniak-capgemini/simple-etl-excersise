from pydantic import BaseModel, ConfigDict


class CartDto(BaseModel):
    cart_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
