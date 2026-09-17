import redis.asyncio as redis
import dotenv
import os

dotenv.load_dotenv()
REDIS_URL=os.getenv("REDIS_URL")

redis_client: redis.Redis = redis.from_url(
    REDIS_URL,
    decode_responses=True,     # 返回 str，不是 bytes
    max_connections=20,        # 连接池上限
    protocol=2,                # 如果服务器 < 6.0 或报 HELLO 错误，保留这行
)


async def close_redis() -> None:
    """应用关闭时调用"""
    await redis_client.aclose()


async def ping_redis() -> bool:
    """健康检查"""
    try:
        return await redis_client.ping()
    except Exception:
        return False