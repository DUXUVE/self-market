from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Order, OrderApplication, User
from app.schemas.order import OrderApplicationRead, OrderCreate, OrderRead

router = APIRouter()


@router.post(
    "/orders",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_order = Order(
        type=order_data.type,
        category_id=order_data.category_id,
        title=order_data.title,
        description=order_data.description,
        price=order_data.price,
        city=order_data.city,
        user_id=current_user.id,
        contractor_id=None,
        desired_date=order_data.desired_date,
        creation_date=datetime.now(),
    )

    try:
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        return new_order
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    return order


@router.get("/orders", response_model=list[OrderRead])
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()


@router.post(
    "/orders/{order_id}/apply",
    response_model=OrderApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    if order.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя оставить заявку на свой заказ")
    if order.contractor_id is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="На этот заказ уже назначен исполнитель")

    existing_result = await db.execute(
        select(OrderApplication).where(
            OrderApplication.order_id == order_id,
            OrderApplication.user_id == current_user.id,
        )
    )
    if existing_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Вы уже откликнулись на этот заказ")

    application = OrderApplication(order_id=order_id, user_id=current_user.id, status="pending")
    try:
        db.add(application)
        await db.commit()
        await db.refresh(application)
        return application
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось сохранить отклик")


# Список откликов видит только заказчик, создавший заказ.
@router.get("/orders/{order_id}/applications", response_model=list[OrderApplicationRead])
async def get_order_applications(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Посмотреть отклики может только заказчик")

    applications_result = await db.execute(
        select(OrderApplication)
        .where(OrderApplication.order_id == order_id)
        .order_by(OrderApplication.created_at)
    )
    return applications_result.scalars().all()


# Исполнитель, который откликнулся, подтверждает готовность взять заказ.
@router.post("/orders/{order_id}/accept", response_model=OrderRead)
async def accept_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    if order.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказчик не может принять собственный заказ")
    if order.contractor_id is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="У заказа уже есть исполнитель")

    application_result = await db.execute(
        select(OrderApplication).where(
            OrderApplication.order_id == order_id,
            OrderApplication.user_id == current_user.id,
            OrderApplication.status == "pending",
        )
    )
    application = application_result.scalar_one_or_none()
    if application is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Сначала нужно откликнуться на заказ")

    try:
        order.contractor_id = current_user.id
        application.status = "accepted"

        other_result = await db.execute(
            select(OrderApplication).where(
                OrderApplication.order_id == order_id,
                OrderApplication.user_id != current_user.id,
                OrderApplication.status == "pending",
            )
        )
        for other_application in other_result.scalars().all():
            other_application.status = "rejected"

        await db.commit()
        await db.refresh(order)
        return order
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось принять заказ")
