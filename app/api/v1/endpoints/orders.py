from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.api.v1.dependencies import get_db
from app.models.models import Order
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter()

# Создать Заказ
@router.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate, 
    db: AsyncSession = Depends(get_db)
):
    new_order = Order(
        category_id=order_data.category_id,
        title=order_data.title,
        description=order_data.description,
        price=order_data.price,
        city=order_data.city,
        user_id=order_data.user_id,
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

# Получить заказы

# Оставить заявку на выполнение

# Посмотреть заявки на заказе

# Начать чат по заказу 

# Подтвердить заявку 

# Подтвердить выполнение заказа
