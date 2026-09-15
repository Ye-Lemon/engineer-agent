from typing import Optional
from pydantic import BaseModel,Field,ConfigDict


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=6, max_length=20)
    password: str = Field(..., min_length=8, max_length=72)


class RegisterRequest(LoginRequest):
    username: str = Field(..., min_length=6, max_length=20)
    email: str = Field(..., min_length=3, max_length=255)
    confirm_password: str = Field(..., min_length=8, max_length=72)


class UserResponse(BaseModel):
    user_id: int
    username: str
    phone: Optional[str] = None
    email: Optional[str] = None

    # 模型类配置
    model_config = ConfigDict(
        from_attributes=True  # 模型类属性映射（允许从ORM对象属性中取值）
    )


class AuthResponse(BaseModel):
    token: str
    userinfo: UserResponse=Field(alias="userInfo")

    # 模型类配置
    model_config = ConfigDict(
        populate_by_name= True, # alias / 字段名兼容
        from_attributes=True  # 模型类属性映射（允许从ORM对象属性中取值）
    )


class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=6, max_length=20)
    phone: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, min_length=3, max_length=255)

class UserUpdatePassword(BaseModel):
    old_password: str = Field(...,min_length=8,max_length=12,alias="oldpassword",description='旧密码')
    new_password: str = Field(...,min_length=8,max_length=12,alias="newpassword",description='新密码')
