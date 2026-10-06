import uuid
from enum import Enum
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PostStatus(str, Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"



class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=True
    )

    body: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    image: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    status: Mapped[PostStatus] = mapped_column(
        ENUM(PostStatus, name="poststatus"),
        nullable=False,
        default=PostStatus.PUBLIC
    )

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )