from pydantic import BaseModel


class ProductDto(BaseModel):
    title: str
    description: str
    category: str
    price: float
    product_id: int

    class Config:
        from_attributes = True
