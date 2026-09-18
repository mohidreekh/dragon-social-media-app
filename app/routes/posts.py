from typing import Annotated
from fastapi import APIRouter, Depends

from app.core.dependencies import CurrentUserDep
from app.services.post_service import PostService
from app.schemas.post import PostCreate, PostResponse

PostServiceDep = Annotated[PostService, Depends()]

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post(
    "/",
    response_model=PostResponse,
    status_code=201
)
def create_post(
    data: PostCreate,
    current_user: CurrentUserDep,
    service: PostServiceDep
):
    return service.create_post(data, user_id=current_user.user_id)

