from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Operation, User
from app.schemas.wallet import OperationRead

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/operations", response_model=list[OperationRead])
async def get_wallet_operations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Возвращает историю операций текущего пользователя."""
    result = await db.execute(
        select(Operation)
        .where(
            or_(
                Operation.sender_id == current_user.id,
                Operation.user_id == current_user.id,
            )
        )
        .order_by(Operation.created_at.desc(), Operation.id.desc())
    )
    return result.scalars().all()
