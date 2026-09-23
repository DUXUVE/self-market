from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate 
from app.services.user_service import authenticate_user
from app.core.security import create_access_token
from app.models.models import User
from app.core.security import get_password_hash

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Логин пользователя.
    Принимает username и password (form-data), возвращает JWT токен.
    """
    # Проверяем пользователя
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаём токен
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(access_token=access_token, token_type="bearer")

async def create_user(db: AsyncSession =Depends(get_db), user: UserCreate=Depends()) -> User:
    # по номеру телефона проверяет зарегестрирован пользователь/нет
    result = await db.execute(select(User).where(User.phone_number == user.phone_number))
    exists = result.scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже зарегестрирован.",
        )
    
    # модель пользователя 
    new_user = User(
        phone_number=user.phone_number,
        hashed_password=get_password_hash(user.password),
        name=user.name,
        city=user.city,
        description=user.description
    )
    
    # добавляет в бд 
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/register") 
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)): 
    phone_number = payload.phone_number
    
    # проверяет через create_user
    user = await create_user(db, payload) 
    return user
