from pydantic import BaseModel, ConfigDict


class ProductDto(BaseModel):
    title: str
    description: str
    category: str
    price: float
    product_id: int

    model_config = ConfigDict(
        from_attributes=True
    )
