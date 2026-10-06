from app.schemas.user import ProfileResponse
from fastapi import Response
from fastapi import responses
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
    response: Response,
    service: UserServiceDep
):
    user = service.create_user(data)
    access_token = create_access_token(subject=user.user_id)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLogin,
    response: Response,
    service: UserServiceDep
):
    user = service.login(data)
    access_token = create_access_token(subject=user.user_id)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=ProfileResponse)
def get_current_user_info(current_user: CurrentUserDep, service: UserServiceDep):
    print("ME ENDPOINT CALLED")
    return service.get_user_profile(current_user.user_id)

