from pydantic import BaseModel


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

    class Config:
        from_attributes = True
