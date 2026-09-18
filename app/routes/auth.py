from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDep
from app.core.security.jwt import create_access_token
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.user_service import UserService

UserServiceDep = Annotated[UserService, Depends()]

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    data: UserCreate,
    service: UserServiceDep
):
    user = service.create_user(data)
    access_token = create_access_token(subject=user.user_id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    service: UserServiceDep
):
    user = service.login(data)
    access_token = create_access_token(subject=user.user_id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: CurrentUserDep):
    return current_user
