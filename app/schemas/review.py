from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rate: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewRead(BaseModel):
    id: int
    comment: str | None
    rate: int
    user_id: int
    reviewer_id: int | None
    order_id: int | None

    model_config = ConfigDict(from_attributes=True)
