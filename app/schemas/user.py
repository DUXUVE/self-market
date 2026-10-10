from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserCreate(BaseModel):
    phone_number: PhoneNumber
    password: str
    name: str
    city: str
    description: str | None = None


class User(BaseModel):
    id: int
    phone_number: str
    name: str
    city: str
    avatar_link: str | None = None
    description: str | None = None
    balance_minutes: int = 0
    rating_average: float = 0.0
    reviews_count: int = 0

    class Config:
        from_attributes = True
        