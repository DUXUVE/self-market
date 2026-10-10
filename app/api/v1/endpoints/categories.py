from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.models.models import Category


router = APIRouter()


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """Возвращает список категорий."""

    result = await db.execute(select(Category))
    categories = result.scalars().all()

    return [
        {
            "id": category.id,
            "title": category.title,
        }
        for category in categories
    ]
