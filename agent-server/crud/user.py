from datetime import datetime, timedelta
import secrets
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_session import async_engine
from db.user import Base, TokenUser, User
from schema.user import RegisterRequest, UpdateUserRequest
from utils.security import hash_password, verify_password


async def create_tables() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, request: RegisterRequest) -> User:
    user = User(
        username=request.username,
        email=request.email,
        password=hash_password(request.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await get_user_by_username(db, username)
    if user is None or not verify_password(password, user.password):
        return None
    return user


async def create_access_token(db: AsyncSession, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    result = await db.execute(select(TokenUser).where(TokenUser.user_id == user_id))
    token_record = result.scalar_one_or_none()
    if token_record is None:
        db.add(TokenUser(user_id=user_id, token=token, expires_at=expires_at))
    else:
        token_record.token = token
        token_record.expires_at = expires_at
    await db.commit()
    return token


async def get_user_by_token(db: AsyncSession, token: str) -> Optional[User]:
    result = await db.execute(
        select(User)
        .join(TokenUser, TokenUser.user_id == User.user_id)
        .where(TokenUser.token == token, TokenUser.expires_at > datetime.utcnow())
    )
    return result.scalar_one_or_none()


async def revoke_token(db: AsyncSession, token: str) -> None:
    await db.execute(delete(TokenUser).where(TokenUser.token == token))
    await db.commit()


async def update_user(db: AsyncSession, user: User, changes: UpdateUserRequest) -> User:
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user
