import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, AliasChoices

class PostCreate(BaseModel):
    body: str = Field(..., description="text required")
    image: str | None = Field(default=None, description="optional_url")
    location: str | None = Field(default=None, description="optional")
    status: str = Field(default="published", description="status")

class PostResponse(BaseModel):
    id: str = Field(validation_alias=AliasChoices("id", "post_id"))
    status: str
    created_at: datetime = Field(validation_alias=AliasChoices("created_at", "created"))

    model_config = {"from_attributes": True}
