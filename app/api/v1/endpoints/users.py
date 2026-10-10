from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_active_user, get_current_user, get_db
from app.models.models import Operation, Review, Service, User as UserModel
from app.schemas.user import User as UserSchema, UserPublic, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


async def add_rating_summary(db: AsyncSession, user: UserModel) -> dict:
    result = await db.execute(
        select(func.avg(Review.rate), func.count(Review.id)).where(
            Review.user_id == user.id
        )
    )
    average, count = result.one()

    hours_result = await db.execute(
        select(func.coalesce(func.sum(Operation.hours_amount), 0)).where(
            Operation.user_id == user.id,
            Operation.status == "completed",
        )
    )
    total_hours = hours_result.scalar_one()

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
        "total_hours_worked": int(total_hours),
    }


@router.get("/me", response_model=UserSchema)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Возвращает личный профиль текущего пользователя со статистикой."""
    return await add_rating_summary(db, current_user)


@router.patch("/me", response_model=UserSchema)
async def update_users_me(
    profile_data: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновляет данные личного профиля текущего пользователя."""
    changes = profile_data.model_dump(exclude_unset=True)

    for field, value in changes.items():
        if value is not None:
            setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)
    return await add_rating_summary(db, current_user)


@router.get("/search", response_model=list[UserPublic])
async def search_helpers(
    city: str | None = None,
    category_id: int | None = None,
    min_rating: float | None = Query(default=None, ge=0, le=5),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Ищет пользователей с услугами по категории, городу и минимальному рейтингу."""
    # В результатах поиска должны быть именно исполнители, у которых есть услуги.
    query = select(UserModel).where(
        UserModel.id.in_(select(Service.user_id)),
        UserModel.id != current_user.id,
    ).order_by(UserModel.id)

    if city and city.strip():
        query = query.where(UserModel.city.ilike(f"%{city.strip()}%"))

    if category_id is not None:
        query = query.where(
            UserModel.id.in_(
                select(Service.user_id).where(Service.category_id == category_id)
            )
        )

    result = await db.execute(query)
    users = result.scalars().all()

    profiles = []
    for user in users:
        profile = await add_rating_summary(db, user)
        if min_rating is not None and profile["rating_average"] < min_rating:
            continue

        first_service_query = select(Service).where(Service.user_id == user.id)
        if category_id is not None:
            first_service_query = first_service_query.where(
                Service.category_id == category_id
            )
        first_service_result = await db.execute(
            first_service_query.order_by(Service.id).limit(1)
        )
        first_service = first_service_result.scalar_one_or_none()
        profile["first_service"] = (
            {
                "id": first_service.id,
                "title": first_service.title,
                "category_id": first_service.category_id,
                "price": first_service.price,
            }
            if first_service is not None
            else None
        )
        profiles.append(profile)

    return profiles


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Возвращает публичную информацию о пользователе и его рейтинг без телефона и баланса."""
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return await add_rating_summary(db, user)
