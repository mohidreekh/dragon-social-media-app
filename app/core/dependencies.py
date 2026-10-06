from fastapi import Cookie
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security.jwt import decode_access_token
from app.db.session import get_db
from app.models.user import User, UserStatus

# Common Database Session Dependency for any Service / Repository
SessionDep = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def get_current_user(
    token_from_header: Annotated[str | None, Depends(oauth2_scheme)] = None,
    access_token: Annotated[str | None, Cookie()] = None,
    db: SessionDep = None,
) -> User:
    token = token_from_header or access_token
    print("TOKEN:", token)

    if not token or token in ("null", "undefined"):
        raise UnauthorizedException("Not authenticated")

    payload = decode_access_token(token)

    user_id_str: str | None = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException("Invalid user ID format in token")

    stmt = select(User).where(User.user_id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")

    if user.status == UserStatus.BANNED:
        raise UnauthorizedException("User account is banned")

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]