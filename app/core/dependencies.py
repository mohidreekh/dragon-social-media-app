from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService


SessionDep = Annotated[
    Session,
    Depends(get_db)
]


def get_user_repository(
    db: SessionDep
):
    return UserRepository(db)


def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repo)


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service)
]