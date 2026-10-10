from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class OrderApplicationRead(BaseModel):
    id: int
    order_id: int
    user_id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
