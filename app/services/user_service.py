from uuid import UUID
from typing import Annotated

from fastapi import Depends

from app.core.exceptions import ConflictException, NotFoundException, UnauthorizedException
from app.core.security.password import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import LastPostResponse, ProfileResponse, UserCreate, UserLogin


class UserService:
    def __init__(self, repo: Annotated[UserRepository, Depends()]) -> None:
        self.repo = repo

    def create_user(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise ConflictException("Email already exists")

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
            profile_image=data.profile_image,
        )
        return self.repo.create(user)

    def login(self, data: UserLogin) -> User:
        user = self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid credentials")
        return user

    def get_user_by_id(self, id: UUID) -> User:
        user = self.repo.get_by_id(id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def get_user_profile(self, id: UUID) -> ProfileResponse:
        user = self.get_user_by_id(id)

        last_post_obj = self.repo.get_last_post(id)
        last_post = LastPostResponse.model_validate(last_post_obj) if last_post_obj else None

        return ProfileResponse(
            id=user.user_id,
            username=user.username,
            profile_image=user.profile_image,
            followers_count=self.repo.get_followers_count(id),
            following_count=self.repo.get_following_count(id),
            last_post=last_post,
        )

    def follow_user(self, follower_id: UUID, followed_id: UUID) -> None:
        if follower_id == followed_id:
            raise ConflictException("You cannot follow yourself")
        self.get_user_by_id(follower_id)
        self.get_user_by_id(followed_id)
        if self.repo.is_following(follower_id, followed_id):
            raise ConflictException("Already following this user")
        self.repo.follow_user(follower_id, followed_id)

    def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self.repo.get_all(skip=skip, limit=limit)
