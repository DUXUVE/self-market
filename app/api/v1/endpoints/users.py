from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user, get_current_user, get_db
from app.models.models import Review, User as UserModel
from app.schemas.user import User as UserSchema

router = APIRouter(prefix="/users", tags=["users"])


async def add_rating_summary(db: AsyncSession, user: UserModel) -> dict:
    result = await db.execute(
        select(func.avg(Review.rate), func.count(Review.id)).where(
            Review.user_id == user.id
        )
    )
    average, count = result.one()
    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "name": user.name,
        "city": user.city,
        "avatar_link": user.avatar_link,
        "description": user.description,
        "balance_minutes": user.balance_minutes,
        "rating_average": round(float(average), 2) if average is not None else 0.0,
        "reviews_count": count,
    }


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает профиль текущего пользователя со средним рейтингом и числом отзывов."""
    return await add_rating_summary(db, current_user)


@router.get("/{user_id}", response_model=UserSchema)
async def read_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Возвращает публичную информацию о пользователе и его рейтинг."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return await add_rating_summary(db, user)
