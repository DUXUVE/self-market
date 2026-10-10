from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):
    category_id: int
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    price: int = Field(gt=0, description="Стоимость услуги в часах")


class ServiceUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, gt=0, description="Стоимость услуги в часах")


class ServiceRead(BaseModel):
    id: int
    user_id: int
    category_id: int
    title: str
    description: str
    price: int

    model_config = ConfigDict(from_attributes=True)
