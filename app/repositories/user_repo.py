from uuid import UUID

from sqlalchemy import delete, func, select

from app.models.follow import Follow
from app.models.post import Post
from app.models.user import User
from app.core.dependencies import SessionDep


class UserRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def get_by_id(self, id: UUID) -> User | None:
        stmt = select(User).where(User.user_id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_followers_count(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(Follow).where(Follow.followed_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_following_count(self, user_id: UUID) -> int:
        stmt = select(func.count()).select_from(Follow).where(Follow.follower_id == user_id)
        return self.db.execute(stmt).scalar_one()

    def get_last_post(self, user_id: UUID) -> Post | None:
        stmt = (
            select(Post)
            .where(Post.user_id == user_id)
            .order_by(Post.created.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def is_following(self, follower_id: UUID, followed_id: UUID) -> bool:
        stmt = select(Follow).where(
            Follow.follower_id == follower_id,
            Follow.followed_id == followed_id,
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def follow_user(self, follower_id: UUID, followed_id: UUID) -> Follow:
        follow = Follow(follower_id=follower_id, followed_id=followed_id)
        self.db.add(follow)
        self.db.flush()
        self.db.refresh(follow)
        return follow

    def unfollow_user(self, follower_id: UUID, followed_id: UUID) -> None:
        stmt = delete(Follow).where(
            Follow.follower_id == follower_id,
            Follow.followed_id == followed_id,
        )
        self.db.execute(stmt)
        self.db.flush()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        stmt = select(User).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())
