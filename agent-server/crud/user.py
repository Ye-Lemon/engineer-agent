from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_session import async_engine
from config.jwt import settings
from db.user import Base, TokenUser, User
from schemas.user import RegisterRequest, UpdateUserRequest
from utils.security import hash_password, verify_password
import jwt


async def get_user_info(db: AsyncSession, token: str):
    stmt = db.execute(select(TokenUser).where(TokenUser.token == token))
    token_record = stmt.scalar_one_or_none()
    if token_record is None or token_record.expires_at < datetime.utcnow():
        return None
    query = select(User).where(User.user_id == TokenUser.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        return await conn.run_sync(Base.metadata.create_all)


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str):
    result = await db.execute(select(User).where(User.phone == phone))
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
    expires_at = datetime.now() + timedelta(hours=settings.JWT_EXPIRATION_DAYS)
    payload = {"exp": expires_at,"sub":str(user_id)}
    jwt_token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
        )
    stmt = select(TokenUser).where(TokenUser.token == jwt_token)
    result = await db.execute(stmt)
    token_info = result.scalar_one_or_none()
    if token_info:
        token_info.token = jwt_token
        token_info.expire_time = expires_at
    else:
        token_info = TokenUser(user_id=user_id, token=jwt_token, expires_at=expires_at)
        db.add(token_info)
        await db.commit()
    return jwt_token

async def decode_jwt_token(token: str):
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORITHM,
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token 已过期")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效 token")


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
