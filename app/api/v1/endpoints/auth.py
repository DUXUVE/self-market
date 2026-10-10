
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_db
from app.core.security import create_access_token, get_password_hash
from app.models.models import User
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.services.user_service import authenticate_user, get_user_by_phone, normalize_phone_number


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Вход пользователя по номеру телефона и паролю."""

    user = await authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.phone_number}
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


async def create_user(
    db: AsyncSession,
    user_data: UserCreate,
) -> User:
    """Создаёт нового пользователя."""

    existing_user = await get_user_by_phone(
        db,
        str(user_data.phone_number),
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже зарегистрирован.",
        )

    user = User(
        phone_number=normalize_phone_number(str(user_data.phone_number)),
        hashed_password=get_password_hash(user_data.password),
        name=user_data.name,
        city=user_data.city,
        description=user_data.description or "",
        balance_minutes=120,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/register")
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Регистрация нового пользователя."""

    user = await create_user(db, payload)

    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "name": user.name,
        "city": user.city,
        "avatar_link": user.avatar_link,
        "description": user.description,
        "balance_minutes": user.balance_minutes,
    }
