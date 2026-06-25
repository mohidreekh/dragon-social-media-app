from typing import Annotated
from fastapi import APIRouter

from app.core.dependencies import UserServiceDep
from app.services.user_service import UserService
from app.core.dependencies import get_user_service
from app.schemas.user import (
    UserCreate,
    UserResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse
)
def add_user(
    data: UserCreate,
    service: UserServiceDep
):
    return service.create_user(data)