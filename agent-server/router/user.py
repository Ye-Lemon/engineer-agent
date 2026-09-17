from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status, UploadFile,File
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_session import get_db
from crud.user import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_username,
    revoke_token,
    update_user,
)
from db.user import User
from schemas.user import AuthResponse, LoginRequest, RegisterRequest, UpdateUserRequest, UserResponse
from utils.auth import auth_user_info
from utils.response import success_response

router = APIRouter(prefix="/api/v1/auth", tags=["用户系统"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(db, request.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    user = await create_user(db, request)
    data = UserResponse.model_validate(user)
    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="用户注册成功",
        data=data,
    )


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.username, request.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名未注册")
    token = await create_access_token(db,user.user_id)
    data = AuthResponse(token=token, userinfo=UserResponse.model_validate(user))
    return success_response(message="登录成功", data=data)


@router.get("/info")
async def get_info(current_user: User = Depends(auth_user_info)):
    return success_response(
        message="已获取用户信息",
        data=UserResponse.model_validate(current_user),
    )

@router.post("/info")
async def update_info(
    request: UpdateUserRequest,
    current_user: User = Depends(auth_user_info),
    db: AsyncSession = Depends(get_db),
):
    user = await update_user(db, current_user, request)
    return success_response(message="用户信息已更新", data=UserResponse.model_validate(user))

@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() == "bearer" and token:
        await revoke_token(db, token)
    return success_response(message="退出成功")



