from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=6, max_length=20)
    password: str = Field(..., min_length=8, max_length=72)


class RegisterRequest(LoginRequest):
    email: str = Field(..., min_length=3, max_length=255)
    confirm_password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    user_id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    token: str
    userinfo: UserResponse


class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=6, max_length=20)
    phone: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, min_length=3, max_length=255)
