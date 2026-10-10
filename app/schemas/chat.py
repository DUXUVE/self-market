from pydantic import BaseModel, ConfigDict, Field


class ChatRead(BaseModel):
    id: int
    order_id: int
    sender_id: int

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    message_text: str = Field(min_length=1, max_length=5000)


class MessageRead(BaseModel):
    id: int
    message_text: str
    user_id: int
    chat_id: int

    model_config = ConfigDict(from_attributes=True)
