from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=2, max_length=1000)
    guest_name: Optional[str] = Field(None, max_length=100)
    guest_email: Optional[EmailStr] = None


class CommentModerate(BaseModel):
    is_approved: Optional[bool] = None
    is_flagged: Optional[bool] = None


class CommentOut(BaseModel):
    id: int
    content: str
    guest_name: Optional[str] = None
    is_approved: bool
    is_flagged: bool
    created_at: datetime
    user: Optional[UserOut] = None
    post_id: int

    model_config = {"from_attributes": True}


class CommentAdminOut(CommentOut):
    guest_email: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
