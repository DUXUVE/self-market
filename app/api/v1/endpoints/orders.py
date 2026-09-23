from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Order, User
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter()

# Создать Заказ
@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_order = Order(
        category_id=order_data.category_id,
        title=order_data.title,
        description=order_data.description,
        price=order_data.price,
        city=order_data.city,
        user_id=current_user.id,
        contractor_id=None,
        desired_date=order_data.desired_date,
        creation_date=datetime.now(timezone.utc)
    )
    
    try:
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        return new_order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Получить заказ
@router.get("/orders/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    return order

# Получить заказы
@router.get("/orders", response_model=list[OrderRead])
async def get_orders(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Order)
    )

    orders = result.scalars().all()

    return orders

# Оставить заявку на выполнение
@router.post("/orders/{order_id}/apply", response_model=OrderRead)
async def apply_to_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    if order.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя оставить заявку на свой заказ",
        )

    if order.contractor_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="На этот заказ уже назначен исполнитель",
        )

    order.contractor_id = current_user.id

    try:
        await db.commit()
        await db.refresh(order)
        return order
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

# Посмотреть заявки на заказе
@router.get("/orders/{order_id}/applications", response_model=list[OrderResponseRead])
async def get_order_applications(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Проверяем, что заказ существует
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    # Доступ к заявкам имеет только владелец заказа
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к заявкам этого заказа",
        )

    # Получаем все заявки по заказу
    result = await db.execute(
        select(OrderResponse).where(OrderResponse.order_id == order_id)
    )
    applications = result.scalars().all()

    return applications

# Начать чат по заказу 

# Подтвердить заявку 

# Подтвердить выполнение заказа
