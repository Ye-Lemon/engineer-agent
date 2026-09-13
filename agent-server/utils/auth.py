from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_session import get_db
from crud.user import get_user_info


def auth_user_info(
        authorization: str = Header(...,alias='Authorization'),
        db: AsyncSession = Depends(get_db)
):
    token = authorization.split(" ")[1]
    result = get_user_info(db,token)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="令牌过期或不存在")
    return result
