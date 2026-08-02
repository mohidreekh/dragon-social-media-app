"""
Pydantic schemas for User endpoints.
"""

import uuid
from datetime import datetime

from pydantic import AliasChoices, BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    profile_image: str


class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None



class UserResponse(BaseModel):
    user_id: uuid.UUID
    username: str | None
    profile_image: str | None
    
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}


class LastPostResponse(BaseModel):
    id: str = Field(validation_alias=AliasChoices("id", "post_id"))
    body: str
    image: str | None = None
    location: str | None = None
    status: str
    created_at: datetime = Field(validation_alias=AliasChoices("created_at", "created"))

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    id: uuid.UUID = Field(validation_alias=AliasChoices("id", "user_id"))
    username: str
    profile_image: str | None = None
    followers_count: int = 0
    following_count: int = 0
    last_post: LastPostResponse | None = None

    model_config = {"from_attributes": True}


UserProfileResponse = ProfileResponse


class FollowRequest(BaseModel):
    follower_id: uuid.UUID


class FollowResponse(BaseModel):
    message: str
    follower_id: uuid.UUID
    followed_id: uuid.UUID


