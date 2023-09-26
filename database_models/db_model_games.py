import uuid

from .db_model_base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Uuid, text, ForeignKey, INTEGER
from sqlalchemy.dialects.postgresql import ARRAY


class Games(Base):
    __tablename__ = "games"

    game_id: Mapped[str] = mapped_column(
        Uuid,
        unique=True,
        nullable=False,
        default=uuid.UUID,
        server_default=text("uuid_generate_v4()")
    )
    game_pid: Mapped[int] = mapped_column(
        primary_key=True
    )
    player_1: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"),
    )
    player_2: Mapped[str] = mapped_column(
        ForeignKey("users.user_id")
    )
    score_player_1: Mapped[list] = mapped_column(
        ARRAY(
            item_type=INTEGER,
            dimensions=7
        )
    )
    score_player_2: Mapped[list] = mapped_column(
        ARRAY(
            item_type=INTEGER,
            dimensions=7
        )
    )