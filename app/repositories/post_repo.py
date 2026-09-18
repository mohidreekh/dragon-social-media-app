from typing import Annotated
import uuid
from sqlalchemy.orm import Session
from fastapi import Depends

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
