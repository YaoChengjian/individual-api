# app/common/utils/redis_utils.py
import json
from typing import Optional, Any, Union

from app.core.redis import get_redis_client


class RedisUtil:
    # ----------------------
    # 基础序列化/反序列化
    # ----------------------
    @staticmethod
    def _deserialize(data: Optional[Union[str, bytes]]) -> Optional[Any]:
        """
        将 Redis 中取出的原始值反序列化为 Python 对象：
        - 如果是我们 set() 写入的包装JSON，返回 wrapper["data"]
        - 如果是纯数字字符串（例如 INCR 产生的 '42'），json.loads 会返回 int
        - 其他非JSON数据，原样返回（bytes/str）
        """
        if data is None:
            return None
        try:
            wrapper = json.loads(data)
            if isinstance(wrapper, dict) and "__type__" in wrapper:
                return wrapper["data"]
            return wrapper  # e.g. "42" -> 42
        except json.JSONDecodeError:
            return data

    @staticmethod
    async def set(key: str, value: Any, expire: Optional[int] = None) -> None:
        """
        自动识别类型并保存：
        - 原始类型（str/int/float/bool）标记为 primitive
        - 复杂结构（dict/list/自定义）标记为 json
        """
        redis_client = get_redis_client()
        if isinstance(value, (str, int, float, bool)):
            wrapper = {"__type__": "primitive", "data": value}
        else:
            wrapper = {"__type__": "json", "data": value}
        await redis_client.set(key, json.dumps(wrapper, ensure_ascii=False), ex=expire)

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        获取并自动反序列化为原始类型或 JSON 对象
        """
        redis_client = get_redis_client()
        data = await redis_client.get(key)
        return RedisUtil._deserialize(data)

    @staticmethod
    async def delete(key: str) -> int:
        redis_client = get_redis_client()
        return await redis_client.delete(key)

    @staticmethod
    async def exists(key: str) -> bool:
        redis_client = get_redis_client()
        return await redis_client.exists(key) == 1

    @staticmethod
    async def delete_by_prefix(prefix: str) -> int:
        """
        删除所有以指定前缀开头的 key
        返回删除的数量
        """
        redis_client = get_redis_client()
        cursor = b"0"
        deleted_count = 0
        pattern = f"{prefix}*"

        while cursor:
            cursor, keys = await redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                deleted_count += await redis_client.delete(*keys)
            if cursor == 0 or cursor == b"0":
                break

        return deleted_count

    # ----------------------
    # 新增：一次性获取并删除（原子）
    # ----------------------
    @staticmethod
    async def getdel(key: str) -> Optional[Any]:
        """
        原子性 GET+DEL，优先使用 Redis 6.2+ 的 GETDEL。
        如客户端/服务端不支持，则尝试 execute_command，再退回 Lua，最后兜底非原子 get+del。
        """
        redis_client = get_redis_client()
        value = None

        # 1) 优先客户端方法
        try:
            if hasattr(redis_client, "getdel"):
                value = await redis_client.getdel(key)  # redis-py 4.2+
            else:
                # 2) 直接发 GETDEL 命令（部分客户端有但未暴露方法）
                try:
                    value = await redis_client.execute_command("GETDEL", key)
                except Exception:
                    # 3) 回退 Lua 原子脚本
                    script = (
                        "local v = redis.call('GET', KEYS[1]); "
                        "if v then redis.call('DEL', KEYS[1]) end; "
                        "return v"
                    )
                    value = await redis_client.eval(script, 1, key)
        except Exception:
            # 4) 最后兜底：非原子（尽量避免，只在极端情况下使用）
            value = await redis_client.get(key)
            if value is not None:
                await redis_client.delete(key)

        return RedisUtil._deserialize(value)

    # ----------------------
    # 新增：自增计数（可选过期）
    # ----------------------
    @staticmethod
    async def incr(key: str, expire: Optional[int] = None) -> int:
        """
        失败计数等场景：
        - 第一次 INCR 置 1 时设置过期
        - 若键已存在但无 TTL（ttl == -1），也补上过期
        返回：当前计数（int）
        """
        redis_client = get_redis_client()
        val = await redis_client.incr(key)
        if expire is not None:
            if val == 1:
                await redis_client.expire(key, expire)
            else:
                ttl = await redis_client.ttl(key)
                if ttl == -1:  # 无过期
                    await redis_client.expire(key, expire)
        return int(val)

    # ----------------------
    # 新增：TTL/EXPIRE
    # ----------------------
    @staticmethod
    async def ttl(key: str) -> int:
        """
        返回 TTL（秒）：
        -2: key 不存在；-1: 无过期；>=0: 剩余秒数
        """
        redis_client = get_redis_client()
        ttl = await redis_client.ttl(key)
        return int(ttl) if ttl is not None else -2

    @staticmethod
    async def expire(key: str, seconds: int) -> bool:
        """
        为已有 key 设置过期时间（秒）
        返回 True/False 表示是否设置成功
        """
        redis_client = get_redis_client()
        res = await redis_client.expire(key, seconds)
        return res == 1
