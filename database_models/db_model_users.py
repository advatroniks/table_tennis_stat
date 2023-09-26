import uuid, datetime

from .db_model_base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid, text, String, Date

from pydantic import EmailStr


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(
        Uuid,
        nullable=False,
        default=uuid.UUID,
        server_default=text("uuid_generate_v4()"),
        unique=True
    )
    user_pid: Mapped[int] = mapped_column(
        primary_key=True
    )
    telegram_id: Mapped[int] = mapped_column(
        nullable=False,
        default=1, #
        unique=True,
    )
    user_email: Mapped[EmailStr] = mapped_column(
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(length=25),
        nullable=False,
    )
    surname: Mapped[str] = mapped_column(
        String(length=25),
        nullable=False,
    )
    birthday: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False,
    )
    city: Mapped[str] = mapped_column(
        String(length=25),
        nullable=False,
    )

