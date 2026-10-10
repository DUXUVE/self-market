from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db
from app.models.models import Chat, Message, Order, OrderApplication, User
from app.schemas.chat import ChatRead, MessageCreate, MessageRead

router = APIRouter(prefix="/chats", tags=["chats"])


async def get_chat_for_participant(
    chat_id: int,
    current_user: User,
    db: AsyncSession,
) -> Chat:
    """Проверяет, что пользователь имеет доступ к чату."""
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден",
        )

    order_result = await db.execute(select(Order).where(Order.id == chat.order_id))
    order = order_result.scalar_one_or_none()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    if order.user_id == current_user.id:
        return chat

    if chat.sender_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому чату",
        )

    if order.contractor_id == current_user.id:
        return chat

    application_result = await db.execute(
        select(OrderApplication).where(
            OrderApplication.order_id == order.id,
            OrderApplication.user_id == current_user.id,
            OrderApplication.status == "pending",
        )
    )
    if application_result.scalar_one_or_none() is not None and order.contractor_id is None:
        return chat

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="У вас нет доступа к этому чату",
    )


@router.post(
    "/orders/{order_id}",
    response_model=ChatRead,
    status_code=status.HTTP_200_OK,
)
async def get_or_create_order_chat(
    order_id: int,
    participant_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Открывает отдельный чат заказчика с выбранным исполнителем."""
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalar_one_or_none()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заказ не найден",
        )

    if order.user_id == current_user.id:
        # Заказчик должен выбрать конкретного откликнувшегося исполнителя.
        target_user_id = participant_id or order.contractor_id
        if target_user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Укажите participant_id — ID исполнителя, откликнувшегося на заказ",
            )
        if target_user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя открыть чат с самим собой",
            )
        if order.contractor_id is not None and order.contractor_id != target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У заказа уже выбран другой исполнитель",
            )
        application_result = await db.execute(
            select(OrderApplication).where(
                OrderApplication.order_id == order_id,
                OrderApplication.user_id == target_user_id,
                OrderApplication.status.in_(["pending", "accepted"]),
            )
        )
        if order.contractor_id != target_user_id and application_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не откликался на этот заказ",
            )
    else:
        if participant_id is not None and participant_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Исполнитель может открыть только свой чат",
            )
        is_contractor = order.contractor_id == current_user.id
        application_result = await db.execute(
            select(OrderApplication).where(
                OrderApplication.order_id == order_id,
                OrderApplication.user_id == current_user.id,
                OrderApplication.status == "pending",
            )
        )
        is_applicant = application_result.scalar_one_or_none() is not None
        if not is_contractor and not is_applicant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Чат доступен только участникам заказа",
            )
        if order.contractor_id is not None and not is_contractor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У заказа уже выбран другой исполнитель",
            )
        target_user_id = current_user.id

    chat_result = await db.execute(
        select(Chat).where(
            Chat.order_id == order_id,
            Chat.sender_id == target_user_id,
        )
    )
    chat = chat_result.scalar_one_or_none()
    if chat is not None:
        return chat

    chat = Chat(order_id=order_id, sender_id=target_user_id)
    db.add(chat)
    try:
        await db.commit()
        await db.refresh(chat)
        return chat
    except Exception:
        await db.rollback()
        chat_result = await db.execute(
            select(Chat).where(
                Chat.order_id == order_id,
                Chat.sender_id == target_user_id,
            )
        )
        chat = chat_result.scalar_one_or_none()
        if chat is not None:
            return chat
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось открыть чат",
        )

@router.get("", response_model=list[ChatRead])
async def get_my_chats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Возвращает чаты заказов, к которым имеет доступ текущий пользователь."""
    owned_orders = select(Order.id).where(
        (Order.user_id == current_user.id) | (Order.contractor_id == current_user.id)
    )
    applied_orders = select(OrderApplication.order_id).where(
        OrderApplication.user_id == current_user.id
    )
    result = await db.execute(
        select(Chat)
        .where((Chat.order_id.in_(owned_orders)) | (Chat.order_id.in_(applied_orders)))
        .order_by(Chat.id.desc())
    )
    chats = result.scalars().all()

    accessible = []
    for chat in chats:
        order_result = await db.execute(select(Order).where(Order.id == chat.order_id))
        order = order_result.scalar_one_or_none()
        if order is None:
            continue
        if order.contractor_id is not None and order.contractor_id != current_user.id:
            if order.user_id != current_user.id:
                continue
        accessible.append(chat)
    return accessible


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def get_chat_messages(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Читает сообщения доступного пользователю чата."""
    chat = await get_chat_for_participant(chat_id, current_user, db)
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat.id)
        .order_by(Message.id)
    )
    return result.scalars().all()


@router.post(
    "/{chat_id}/messages",
    response_model=MessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def send_chat_message(
    chat_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отправляет сообщение в чат заказа."""
    chat = await get_chat_for_participant(chat_id, current_user, db)
    message_text = message_data.message_text.strip()
    if not message_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Сообщение не должно быть пустым",
        )

    message = Message(
        message_text=message_text,
        user_id=current_user.id,
        chat_id=chat.id,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
