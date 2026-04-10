from typing import Optional

import redis.asyncio as redis
from app.config import ConfigClass

redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("❌ Redis 未初始化")
    return redis_client


async def init_redis() -> None:
    """
    初始化 Redis 客户端，保存为全局变量 redis_client
    """
    global redis_client
    redis_client = redis.Redis(
        host=ConfigClass.redis.host,
        port=ConfigClass.redis.port,
        db=ConfigClass.redis.db,
        password=ConfigClass.redis.password or None,
        decode_responses=True,
    )
    try:
        await redis_client.ping()

    except Exception as e:
        raise RuntimeError("❌ Redis 初始化失败，请检查连接配置") from e


async def close_redis() -> None:
    """
    关闭 Redis 客户端连接
    """
    if redis_client:
        await redis_client.close()
