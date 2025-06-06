from pydantic import BaseModel, ConfigDict


class MostOrderedCategoryDto(BaseModel):
    user_id: int
    category_name: str
    total_orders: int

    model_config = ConfigDict(from_attributes=True)
