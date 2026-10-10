from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Operation, Order, User
from app.schemas.wallet import OperationRead

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/operations", response_model=list[OperationRead])
async def get_wallet_operations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Возвращает историю операций с именами участников и названием заказа."""
    sender = aliased(User)
    receiver = aliased(User)

    result = await db.execute(
        select(
            Operation,
            sender.name.label("sender_name"),
            receiver.name.label("receiver_name"),
            Order.title.label("order_title"),
        )
        .join(sender, Operation.sender_id == sender.id)
        .join(receiver, Operation.user_id == receiver.id)
        .join(Order, Operation.order_id == Order.id)
        .where(
            or_(
                Operation.sender_id == current_user.id,
                Operation.user_id == current_user.id,
            )
        )
        .order_by(Operation.created_at.desc(), Operation.id.desc())
    )

    operations = []
    for operation, sender_name, receiver_name, order_title in result.all():
        operations.append(
            {
                "id": operation.id,
                "sender_id": operation.sender_id,
                "user_id": operation.user_id,
                "order_id": operation.order_id,
                "hours_amount": operation.hours_amount,
                "status": operation.status,
                "created_at": operation.created_at,
                "sender_name": sender_name,
                "receiver_name": receiver_name,
                "order_title": order_title,
            }
        )

    return operations
