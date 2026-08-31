from pydantic import BaseModel, PhoneNumber

class UserCreate:
    phone_number: PhoneNumber
    password: str
    name: str
    city: str
    description: str | None

class User:
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True
