from datetime import datetime

from pydantic import BaseModel


class OrderCreate(BaseModel):
    type: bool
    category_id: int
    title: str
    description: str
    price: int
    city: str
    desired_date: datetime | None = None


class OrderRead(BaseModel):
    id: int
    type: bool
    category_id: int
    title: str
    description: str
    price: int
    city: str
    user_id: int
    contractor_id: int | None
    desired_date: datetime | None
    creation_date: datetime

    class Config:
        from_attributes = True
        