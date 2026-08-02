from typing import Annotated
from uuid import UUID
from fastapi import APIRouter

from app.core.dependencies import UserServiceDep
from app.services.user_service import UserService
from app.core.dependencies import get_user_service
from app.schemas.user import (
    UserCreate,
    UserResponse,
    ProfileResponse,
    FollowRequest,
    FollowResponse,
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


@router.get("/{id}", response_model=ProfileResponse)
def get_user_profile(id: UUID, service: UserServiceDep):
    return service.get_user_profile(id)


@router.post("/{id}/follow", response_model=FollowResponse, status_code=201)
def follow_user(
    id: UUID,
    data: FollowRequest,
    service: UserServiceDep
):
    service.follow_user(follower_id=data.follower_id, followed_id=id)
    return FollowResponse(
        message="Successfully followed user",
        follower_id=data.follower_id,
        followed_id=id
    )


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    service: UserServiceDep,
    skip: int = 0,
    limit: int = 100
):
    return service.get_all_users(skip=skip, limit=limit)



