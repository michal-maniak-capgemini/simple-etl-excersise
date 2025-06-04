from pydantic import BaseModel, ConfigDict


class UserDto(BaseModel):
    first_name: str
    last_name: str
    email: str
    age: int
    birth_date: str
    street: str
    city: str
    country: str
    user_id: int

    model_config = ConfigDict(
        from_attributes=True
    )
