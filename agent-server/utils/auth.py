from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_session import get_db
from crud.user import get_user_by_token
from db.user import User


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication")

    user = await get_user_by_token(db, token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")
    return user
