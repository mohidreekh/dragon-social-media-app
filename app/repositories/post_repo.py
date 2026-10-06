import uuid

from sqlalchemy import select

from app.models.post import Post, PostStatus
from app.core.dependencies import SessionDep
from app.schemas.post import PostCreate


class PostRepository:
    def __init__(self, db: SessionDep):
        self.db = db

    def create_post(self, data: PostCreate, user_id: uuid.UUID) -> Post:
        status_val = data.status.upper() if data.status else "PUBLIC"
        try:
            status_enum = PostStatus(status_val)
        except ValueError:
            status_enum = PostStatus.PUBLIC

        post = Post(
            post_id=f"post_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            body=data.body,
            image=data.image,
            location=data.location,
            status=status_enum,
        )
        self.db.add(post)
        self.db.flush()
        self.db.refresh(post)
        return post

    def get_posts(self, user_id: uuid.UUID, skip: int = 0, limit: int = 10) -> list[Post]:
        stmt = select(Post).where(Post.user_id == user_id).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_post_by_id(self, post_id: str) -> Post | None:
        stmt = select(Post).where(Post.post_id == post_id)
        return self.db.execute(stmt).scalar_one_or_none()
