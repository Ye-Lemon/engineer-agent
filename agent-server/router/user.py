from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_session import get_db
from crud.user import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_email,
    get_user_by_username,
    revoke_token,
    update_user,
)
from db.user import User
from schema.user import AuthResponse, LoginRequest, RegisterRequest, UpdateUserRequest, UserResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=422, detail="Passwords do not match")
    if await get_user_by_username(db, request.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await get_user_by_email(db, request.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        user = await create_user(db, request)
        return success_response(
            message="Registration successful",
            data=UserResponse.model_validate(user),
            status_code=status.HTTP_201_CREATED,
        )
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists") from error


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, request.username, request.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = await create_access_token(db, user.user_id)
    data = AuthResponse(token=token, userinfo=UserResponse.model_validate(user))
    return success_response(message="Login successful", data=data)


@router.get("/info")
async def get_info(current_user: User = Depends(get_current_user)):
    return success_response(message="User information retrieved", data=UserResponse.model_validate(current_user))


@router.patch("/info")
async def update_info(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await update_user(db, current_user, request)
    return success_response(message="User information updated", data=UserResponse.model_validate(user))


@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() == "bearer" and token:
        await revoke_token(db, token)
    return success_response(message="Logout successful")
