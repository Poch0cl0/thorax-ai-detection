from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None
    role: str = "clinician"


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    role: str
    roles: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}


class UserBriefRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    roles: list[str] = Field(default_factory=list)

