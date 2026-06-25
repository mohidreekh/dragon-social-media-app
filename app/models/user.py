import uuid
import enum as py_enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base



class UserRole(str, py_enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserStatus(str, py_enum.Enum):
    ACTIVE = "ACTIVE"
    BANNED = "BANNED"


role_enum = ENUM("ADMIN", "USER", name="userrole", create_type=False)
status_enum = ENUM("ACTIVE", "BANNED", name="userstatus", create_type=False)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    hashed_password: Mapped[str] = mapped_column(String(255))


    profile_image: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    role: Mapped[UserRole] = mapped_column(role_enum, default=UserRole.USER, nullable=False)

    status: Mapped[UserStatus] = mapped_column(status_enum, default=UserStatus.ACTIVE, nullable=False)
    
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