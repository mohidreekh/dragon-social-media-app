from typing import Annotated
from uuid import UUID
from fastapi import Depends

from app.core.exceptions import BadRequestException
from app.models.post import Post
from app.repositories.post_repo import PostRepository
from app.schemas.post import PostCreate


class PostService:
    def __init__(self, repo: Annotated[PostRepository, Depends()]) -> None:
        self.repo = repo

    def create_post(self, data: PostCreate, user_id: UUID) -> Post:
        if not data.body or not data.body.strip():
            raise BadRequestException("Body is required")
        return self.repo.create_post(data, user_id=user_id)

