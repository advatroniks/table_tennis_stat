import uuid

from .db_model_base import Base

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid, text


class Profile(Base):
    __tablename__ = "profiles"

    profile_id: Mapped[str] = mapped_column(
        Uuid,
        nullable=False,
        unique=True,
        server_default=text("uuid_generate_v4()"),
        default=uuid.UUID
    )

    profile_pid: Mapped[int] = mapped_column(
        primary_key=True
    )

    base: Mapped[int | None]

    left_side: Mapped[int | None]

    right_side: Mapped[int | None]

    game_style: Mapped[bool] = mapped_column(
        nullable=False,
    )



