from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class OrderCreate(BaseModel):
    category_id: int
    title: str
    description: str
    price: int
    city: str
    user_id: int
    desired_date: Optional[datetime] = None

class OrderRead(BaseModel):
    id: int
    category_id: int
    title: str
    description: str
    price: int
    city: str
    user_id: int
    contractor_id: Optional[int]
    desired_date: Optional[datetime]
    creation_date: datetime

    class Config:
        from_attributes = True
