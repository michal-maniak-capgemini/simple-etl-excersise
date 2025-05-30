from pydantic import BaseModel


class MostOrderedCategoryDto(BaseModel):
    user_id: int
    category_name: str
    total_orders: int

    class Config:
        from_attributes = True
