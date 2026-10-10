from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OperationRead(BaseModel):
    id: int
    sender_id: int
    user_id: int
    order_id: int
    hours_amount: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
