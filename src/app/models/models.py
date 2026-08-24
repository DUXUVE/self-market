from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column 


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    phone_number: Mapped[str] = mapped_column(String(31), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_link: Mapped[str] = mapped_column(String(1023), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
