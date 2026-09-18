from typing import Annotated
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models.user import User
from app.models.follow import Follow
from app.models.post import Post
from app.core.dependencies import SessionDep

class UserRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def get_by_id(self, id: UUID):
        return (
            self.db.query(User)
            .filter(User.user_id == id)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_followers_count(self, user_id: UUID) -> int:
        return (
            self.db.query(Follow)
            .filter(Follow.followed_id == user_id)
            .count()
        )

    def get_following_count(self, user_id: UUID) -> int:
        return (
            self.db.query(Follow)
            .filter(Follow.follower_id == user_id)
            .count()
        )

    def get_last_post(self, user_id: UUID) -> Post | None:
        return (
            self.db.query(Post)
            .filter(Post.user_id == user_id)
            .order_by(Post.created.desc())
            .first()
        )

    def is_following(self, follower_id: UUID, followed_id: UUID) -> bool:
        return (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
            .first()
            is not None
        )

    def follow_user(self, follower_id: UUID, followed_id: UUID) -> Follow:
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        self.db.add(follow)
        self.db.flush()
        self.db.refresh(follow)
        return follow

    def unfollow_user(self, follower_id: UUID, followed_id: UUID) -> None:
        self.db.query(Follow).filter(
            Follow.follower_id == follower_id,
            Follow.followed_id == followed_id,
        ).delete()
        self.db.flush()
        
    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        return (
            self.db.query(User)
            .offset(skip)
            .limit(limit)
            .all()
        )



