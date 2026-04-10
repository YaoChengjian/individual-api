import time

from app.common.constants import RedisKey
from app.common.utils.redis_utils import RedisUtil


def _fmt_seconds(secs: int) -> str:
    if secs >= 86400:
        return f'{secs // 86400}天'
    if secs >= 3600:
        return f'{secs // 3600}小时'
    if secs >= 60:
        return f'{secs // 60}分钟'
    return f'{secs}秒'


class LoginThrottle:
    FAIL_EXPIRE_SEC = 24 * 60 * 60  # 失败计数窗口

    @staticmethod
    def _fail_key(uid: int, user_type: str = 'web') -> str:
        key_fix = RedisKey.web_login_fail_count if user_type == 'web' else RedisKey.sys_login_fail_count
        return f'{key_fix}{uid}'

    @staticmethod
    def _lock_key(uid: int, user_type: str = 'web') -> str:
        key_fix = RedisKey.web_login_lock if user_type == 'web' else RedisKey.sys_login_lock
        return f'{key_fix}{uid}'

    @classmethod
    async def is_locked(cls, uid: int, user_type: str = 'web') -> int:
        """返回剩余锁定秒数（未锁定返回 0）"""
        ttl = await RedisUtil.ttl(cls._lock_key(uid, user_type))
        return ttl if ttl and ttl > 0 else 0

    @staticmethod
    def _lock_seconds_for_count(count: int) -> int:
        """
        阈值说明（到达阈值即生效）：
        3次 → 5分钟；4次 → 10分钟；5次 → 30分钟；≥6次 → 24小时
        """
        if count >= 6:
            return 24 * 60 * 60
        if count == 5:
            return 30 * 60
        if count == 4:
            return 10 * 60
        if count == 3:
            return 5 * 60
        return 0

    @classmethod
    async def record_failure_and_maybe_lock(cls, uid: int, user_type: str = 'web') -> tuple[int, int]:
        """
        失败 +1，并根据累计次数决定是否加锁。
        返回：(当前次数, 本次锁定秒数[可能为0])
        """
        # 计数 + TTL 窗口；如你的 RedisUtil 不支持 incr(expire=..)，请分步设置 expire
        count = await RedisUtil.incr(cls._fail_key(uid, user_type), expire=cls.FAIL_EXPIRE_SEC)
        try:
            count = int(count)
        except Exception:
            count = 1

        lock_sec = cls._lock_seconds_for_count(count)
        if lock_sec > 0:
            await RedisUtil.set(cls._lock_key(uid, user_type), '1', expire=lock_sec)
        return count, lock_sec

    @classmethod
    async def reset(cls, uid: int, user_type: str = 'web'):
        await RedisUtil.delete(cls._fail_key(uid, user_type))
        await RedisUtil.delete(cls._lock_key(uid, user_type))
