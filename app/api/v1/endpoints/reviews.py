from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Operation, Order, Review, User
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post(
    "/orders/{order_id}",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_review(
    order_id: int,
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Заказчик оставляет отзыв исполнителю после подтверждённого заказа."""
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Оставить отзыв может только заказчик",
        )
    if order.contractor_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У заказа нет исполнителя",
        )

    operation_result = await db.execute(
        select(Operation).where(
            Operation.order_id == order_id,
            Operation.status == "completed",
        )
    )
    if operation_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отзыв можно оставить после завершения заказа",
        )

    existing_result = await db.execute(
        select(Review).where(Review.order_id == order_id)
    )
    if existing_result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="На этот заказ уже оставлен отзыв",
        )

    review = Review(
        comment=review_data.comment,
        rate=review_data.rate,
        user_id=order.contractor_id,
        reviewer_id=current_user.id,
        order_id=order.id,
    )
    try:
        db.add(review)
        await db.commit()
        await db.refresh(review)
        return review
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось сохранить отзыв",
        )


@router.get("/users/{user_id}", response_model=list[ReviewRead])
async def get_user_reviews(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает отзывы, оставленные о выбранном пользователе."""
    user_result = await db.execute(select(User).where(User.id == user_id))
    if user_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    result = await db.execute(
        select(Review)
        .where(Review.user_id == user_id)
        .order_by(Review.id.desc())
    )
    return result.scalars().all()
