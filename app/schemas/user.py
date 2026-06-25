"""
Pydantic schemas for User endpoints.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


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
    created: datetime
    updated: datetime

    model_config = {"from_attributes": True}
