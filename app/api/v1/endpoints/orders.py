from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Order, OrderApplication, Operation, User
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
    if order_data.price <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Цена должна быть больше нуля")

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
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось создать заказ")


@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
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


# Исполнитель принимает заказ; стоимость в часах переводится в минуты и замораживается.
@router.post("/orders/{order_id}/accept", response_model=OrderRead)
async def accept_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order_result = await db.execute(
            select(Order).where(Order.id == order_id).with_for_update()
        )
        order = order_result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
        if order.user_id == current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заказчик не может принять собственный заказ")
        if order.contractor_id is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="У заказа уже есть исполнитель")
        if order.price <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Цена заказа должна быть больше нуля")

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

        customer_result = await db.execute(
            select(User).where(User.id == order.user_id).with_for_update()
        )
        customer = customer_result.scalar_one_or_none()
        if customer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказчик не найден")

        price_minutes = order.price * 60
        if customer.balance_minutes < price_minutes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно минут. Нужно: {price_minutes}, доступно: {customer.balance_minutes}",
            )

        # Не допускаем повторного списания, если для заказа уже есть операция оплаты.
        operation_result = await db.execute(
            select(Operation).where(Operation.order_id == order_id)
        )
        if operation_result.scalars().first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Для этого заказа уже создана операция оплаты")

        customer.balance_minutes -= price_minutes
        order.contractor_id = current_user.id
        application.status = "accepted"
        db.add(Operation(
            sender_id=customer.id,
            user_id=current_user.id,
            order_id=order.id,
            hours_amount=order.price,
            status="frozen",
        ))

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
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось принять заказ и заморозить минуты")


# Исполнитель сообщает, что выполнил заказ. Деньги пока остаются замороженными.
@router.post("/orders/{order_id}/complete", response_model=OrderRead)
async def mark_order_complete(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order_result = await db.execute(select(Order).where(Order.id == order_id).with_for_update())
        order = order_result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
        if order.contractor_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Отметить выполнение может только назначенный исполнитель")

        operation_result = await db.execute(
            select(Operation).where(Operation.order_id == order_id, Operation.status == "frozen")
        )
        operation = operation_result.scalar_one_or_none()
        if operation is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Для заказа нет замороженной оплаты")
        operation.status = "awaiting_confirmation"
        await db.commit()
        await db.refresh(order)
        return order
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось отметить заказ выполненным")


# Заказчик подтверждает выполнение: замороженные минуты поступают исполнителю.
@router.post("/orders/{order_id}/confirm", response_model=OrderRead)
async def confirm_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        order_result = await db.execute(select(Order).where(Order.id == order_id).with_for_update())
        order = order_result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
        if order.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Подтвердить выполнение может только заказчик")
        if order.contractor_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="У заказа нет исполнителя")

        operation_result = await db.execute(
            select(Operation).where(
                Operation.order_id == order_id,
                Operation.status == "awaiting_confirmation",
            ).with_for_update()
        )
        operation = operation_result.scalar_one_or_none()
        if operation is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Исполнитель ещё не отметил заказ выполненным")

        contractor_result = await db.execute(
            select(User).where(User.id == order.contractor_id).with_for_update()
        )
        contractor = contractor_result.scalar_one_or_none()
        if contractor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Исполнитель не найден")

        contractor.balance_minutes += operation.hours_amount * 60
        operation.status = "completed"
        await db.commit()
        await db.refresh(order)
        return order
    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не удалось подтвердить заказ и перевести минуты")
