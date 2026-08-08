from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    created_at:Mapped[datetime] = mapped_column(DateTime,  default=datetime.now,comment="创建时间")
    updated_at:Mapped[datetime] = mapped_column(DateTime,  default=datetime.now,onupdate=datetime.now(),comment="更新时间")

class User(Base):
    """
    用户表
    """
    __tablename__ = "users_info"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, nullable=False, comment='用户ID')
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment='用户名')
    password: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment='密码')
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=False, comment='手机号')
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=False, comment='邮箱')


class TokenUser(Base):
    """
    令牌用户表
    """
    __tablename__ = "token_users"

    __table_args__ = (
        Index('ix_token_users_token', 'token'),
        Index('ix_token_users_user_id', 'user_id')
    )

    token_id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, nullable=False, comment='令牌ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey=User.user_id,nullable=False, comment='用户ID')
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment='令牌')
    expires: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='令牌过期时间')


