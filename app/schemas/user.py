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

    class Config:
        from_attributes = True
        