from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserCreate(BaseModel):
    phone_number: PhoneNumber
    password: str
    name: str
    city: str
    description: str | None = None


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=255)
    avatar_link: str | None = Field(default=None, max_length=1023)
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
    total_hours_worked: int = 0

    class Config:
        from_attributes = True
