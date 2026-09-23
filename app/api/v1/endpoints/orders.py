from datetime import datetime, timezone
import select

from fastapi import APIRouter, HTTPException, status, Depends
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
        
    return new_order

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

# Посмотреть заявки на заказе

# Начать чат по заказу 

# Подтвердить заявку 

# Подтвердить выполнение заказа
