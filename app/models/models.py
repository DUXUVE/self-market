from datetime import datetime
from typing import List, Optional
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    phone_number: Mapped[str] = mapped_column(String(31), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_link: Mapped[str] = mapped_column(String(1023), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    reviews: Mapped[List["Review"]] = relationship(back_populates="user")
    
    orders_as_owner: Mapped[List["Order"]] = relationship(
        "Order", foreign_keys="[Order.user_id]", back_populates="owner"
    )
    orders_as_contractor: Mapped[List["Order"]] = relationship(
        "Order", foreign_keys="[Order.contractor_id]", back_populates="contractor"
    )
    
    chats: Mapped[List["Chat"]] = relationship(back_populates="sender")
    messages: Mapped[List["Message"]] = relationship(back_populates="user")
    
    operations_as_sender: Mapped[List["Operation"]] = relationship(
        "Operation", foreign_keys="[Operation.sender_id]", back_populates="sender"
    )
    operations_as_user: Mapped[List["Operation"]] = relationship(
        "Operation", foreign_keys="[Operation.user_id]", back_populates="user_rel"
    )


class Review(Base):
    __tablename__ = "review" 
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rate: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="reviews")


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    orders: Mapped[List["Order"]] = relationship(back_populates="category")


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    contractor_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=True)
    desired_date: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    creation_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    category: Mapped["Category"] = relationship(back_populates="orders")
    owner: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="orders_as_owner")
    contractor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[contractor_id], back_populates="orders_as_contractor")
    chats: Mapped[List["Chat"]] = relationship(back_populates="order")
    operations: Mapped[List["Operation"]] = relationship(back_populates="order")


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("order.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="chats")
    sender: Mapped["User"] = relationship(back_populates="chats")
    messages: Mapped[List["Message"]] = relationship(back_populates="chat")


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="messages")
    chat: Mapped["Chat"] = relationship(back_populates="messages")


class Operation(Base):
    __tablename__ = "operation"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("order.id"), nullable=False)
    hours_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id], back_populates="operations_as_sender")
    user_rel: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="operations_as_user")
    order: Mapped["Order"] = relationship(back_populates="operations")
    