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
    is_active: bool = True

    class Config:
        from_attributes = True


class UserInDB(User):
    username: str
    email: str
    hashed_password: str