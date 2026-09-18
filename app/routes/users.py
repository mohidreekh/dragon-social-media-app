from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDep
from app.services.user_service import UserService
from app.schemas.user import (
    UserCreate,
    UserResponse,
    ProfileResponse,
    FollowResponse,
)

UserServiceDep = Annotated[UserService, Depends()]

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201
)
def add_user(
    data: UserCreate,
    service: UserServiceDep
):
    return service.create_user(data)


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: CurrentUserDep,
    service: UserServiceDep
):
    return service.get_user_profile(current_user.user_id)


@router.get("/{id}", response_model=ProfileResponse)
def get_user_profile(
    id: UUID,
    current_user: CurrentUserDep,
    service: UserServiceDep
):
    return service.get_user_profile(id)


@router.post("/{id}/follow", response_model=FollowResponse, status_code=201)
def follow_user(
    id: UUID,
    current_user: CurrentUserDep,
    service: UserServiceDep
):
    service.follow_user(follower_id=current_user.user_id, followed_id=id)
    return FollowResponse(
        message="Successfully followed user",
        follower_id=current_user.user_id,
        followed_id=id
    )


@router.delete("/{id}/follow", response_model=FollowResponse)
def unfollow_user(
    id: UUID,
    current_user: CurrentUserDep,
    service: UserServiceDep
):
    service.unfollow_user(follower_id=current_user.user_id, followed_id=id)
    return FollowResponse(
        message="Successfully unfollowed user",
        follower_id=current_user.user_id,
        followed_id=id
    )


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    current_user: CurrentUserDep,
    service: UserServiceDep,
    skip: int = 0,
    limit: int = 100
):
    return service.get_all_users(skip=skip, limit=limit)




