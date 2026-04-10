# app/core/task_wrappers.py
import asyncio
import inspect
import functools
from typing import Callable, Any
from app.core.db import init_db, close_db  # 复用你现成的函数


def with_tortoise(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    方案A装饰器：每次调用时
    1) 新建事件循环
    2) 在同一循环内 init_db -> 执行业务(支持异步/同步) -> close_db
    3) 返回业务结果
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        async def _runner():
            await init_db()
            try:
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                return result
            finally:
                await close_db()

        return asyncio.run(_runner())

    return _wrapper
