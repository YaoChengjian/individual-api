import asyncio
import math
from inspect import iscoroutinefunction, signature, Parameter
from typing import TypeVar, Callable, Awaitable, Optional, Any, Type, Tuple, Dict

from pydantic import BaseModel, ValidationError
from tortoise.queryset import QuerySet

from app.common.exceptions.exception import TipsError
from app.common.schema import RespListModel, BasePageModel
from app.core.db_models import BaseOrmModel

T = TypeVar("T")
S = TypeVar('S')


def _filter_kwargs_for_callable(func: Callable[..., Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据 func 的签名过滤 kwargs，只保留可接收的键。
    若 func 含有 **kwargs 则直接原样返回。
    """
    sig = signature(func)
    params = sig.parameters

    # 有 **kwargs，直接全量通过
    if any(p.kind == Parameter.VAR_KEYWORD for p in params.values()):
        return kwargs

    allowed = {k: v for k, v in kwargs.items() if k in params}
    return allowed


async def _ormFuncToModel(
        orm: BaseOrmModel,
        model: Type[BaseModel],
        func: Callable[..., Awaitable[dict]],
        func_args: Tuple[Any, ...] = (),
        func_kwargs: Optional[Dict[str, Any]] = None,
) -> BaseModel:
    """
    把 orm 和 func 返回的 dict 转换为 pydantic 模型
    支持向 func 传递可选参数（args/kwargs），并自动过滤无关 kwargs
    """
    func_kwargs = func_kwargs or {}

    try:
        obj = model.model_validate(orm)
    except ValidationError as e:
        # 精确提示缺失字段
        for err in e.errors():
            if err.get('type') == 'missing':
                missing_field = err['loc'][0]
                model_name = model.__name__
                raise TipsError(
                    f"字段 '{missing_field}' 缺失：在构造 {model_name} 时未能从 ORM 对象中获取该字段的值。"
                    f"建议为该字段设置默认值，如：`{missing_field}: Optional[...] = None`"
                )
        # 其他校验错误直接抛出
        raise

    # 过滤 kwargs 后再调用
    filtered_kwargs = _filter_kwargs_for_callable(func, func_kwargs)
    extra = await func(orm, *func_args, **filtered_kwargs)

    if not isinstance(extra, dict):
        raise TipsError("paginate：func 必须返回 dict，用于合并到 Pydantic 模型中。")

    return obj.model_copy(update=extra)


async def paginate(
        queryset: QuerySet[T],
        page_query: BasePageModel,
        model: Optional[Type[S]] = None,
        func: Optional[Callable[..., Awaitable[dict]]] = None,
        *,
        func_args: Tuple[Any, ...] = (),
        func_kwargs: Optional[Dict[str, Any]] = None,
) -> RespListModel[S]:
    """
    常规通用分页查询

    :param queryset: orm 的 QuerySet
    :param page_query: 分页查询参数
    :param model: 返回的 pydantic 模型
    :param func: 异步函数，签名示例：async def f(orm, *, user_id: int, lang: str) -> dict
    :param func_args: 位置参数，将在 orm 之后按顺序传入 func
    :param func_kwargs: 关键字参数，自动按 func 的签名过滤多余项
    """
    if func and not iscoroutinefunction(func):
        raise ValueError('paginate：func 参数必须是异步函数！')

    total = await queryset.count()
    raw_items = await queryset.offset((page_query.page - 1) * page_query.page_size).limit(page_query.page_size)

    if func and model:
        items = await asyncio.gather(*[
            _ormFuncToModel(i, model, func, func_args=func_args, func_kwargs=func_kwargs)
            for i in raw_items
        ])
    elif model:
        items = [model.model_validate(item) for item in raw_items]
    else:
        items = raw_items

    page_count = math.ceil(total / page_query.page_size)
    return RespListModel[S](list=items, page_count=page_count, data_count=total)


# 使用样例

# 1. 不传 func_args 和 func_kwargs
"""

async def enrich_minimal(orm) -> dict:
    return {"extra": 1}

await paginate(qs, page_query, model=OutModel, func=enrich_minimal)
"""

# 2. 传 func_kwargs
"""
async def enrich_with_ctx(orm, *, user_id: int, lang: str) -> dict:
    return {"is_owner": orm.user_id == user_id, "lang": lang}

await paginate(
    qs, page_query,
    model=OutModel,
    func=enrich_with_ctx,
    func_kwargs={"user_id": 42, "lang": "zh-CN", "unused": "will_be_ignored"}
)
"""
# 3. 传 func_args
"""
async def enrich_with_pos(orm, feature_flag: bool) -> dict:
    return {"enabled": feature_flag}

await paginate(qs, page_query, model=OutModel, func=enrich_with_pos, func_args=(True,))

"""