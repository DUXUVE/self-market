from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from phonenumbers import PhoneNumberFormat, format_number, parse

from app.core.security import verify_password, get_password_hash
from app.models.models import User


def normalize_phone_number(phone_number: str) -> str:
    """Приводит номер телефона к единому формату."""
    phone = parse(phone_number, None)
    return format_number(phone, PhoneNumberFormat.RFC3966)


async def get_user_by_phone(
    db: AsyncSession,
    phone_number: str,
) -> User | None:
    """Ищет пользователя по номеру телефона."""

    normalized_phone = normalize_phone_number(phone_number)

    result = await db.execute(
        select(User).where(User.phone_number == normalized_phone)
    )

    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession,
    phone_number: str,
    password: str,
) -> User | None:
    """Проверяет номер телефона и пароль пользователя."""

    user = await get_user_by_phone(db, phone_number)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
