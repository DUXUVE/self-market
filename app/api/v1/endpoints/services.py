from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Category, Service, User
from app.schemas.service import ServiceCreate, ServiceRead, ServiceUpdate

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создаёт карточку услуги для текущего пользователя."""
    category_result = await db.execute(
        select(Category).where(Category.id == service_data.category_id)
    )
    if category_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Категория не найдена",
        )

    service = Service(
        user_id=current_user.id,
        category_id=service_data.category_id,
        title=service_data.title,
        description=service_data.description,
        price=service_data.price,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("", response_model=list[ServiceRead])
async def get_services(
    user_id: int | None = None,
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает карточки услуг; можно отфильтровать по владельцу и категории."""
    query = select(Service).order_by(Service.id.desc())
    if user_id is not None:
        query = query.where(Service.user_id == user_id)
    if category_id is not None:
        query = query.where(Service.category_id == category_id)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Возвращает одну карточку услуги."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена",
        )
    return service


@router.patch("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Изменяет только свою карточку услуги."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена",
        )
    if service.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно изменять только свои услуги",
        )

    changes = service_data.model_dump(exclude_unset=True)
    if "category_id" in changes and changes["category_id"] is not None:
        category_result = await db.execute(
            select(Category).where(Category.id == changes["category_id"])
        )
        if category_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория не найдена",
            )
    for field, value in changes.items():
        if value is not None:
            setattr(service, field, value)

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаляет только свою карточку услуги."""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена",
        )
    if service.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Можно удалять только свои услуги",
        )

    await db.delete(service)
    await db.commit()
