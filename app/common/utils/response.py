from typing import Any, List, Type, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar('T')
S = TypeVar('S')


def _normalize_data(data: Any) -> Any:
    """
    把 Pydantic 模型转为 dict
    """

    if isinstance(data, BaseModel):
        return data.model_dump(mode='json')
    return data


# ✅ services.py 中使用：返回标准响应结构（不返回 JSONResponse）
def success(data: Any = None, msg: str = "成功", code: int = 0) -> dict:
    return {
        "code": code,
        "message": msg,
        "data": _normalize_data(data),
    }


def fail(code: int = 99, msg: str = "", data: Any = None) -> dict:
    return {
        "code": code,
        "message": msg,
        "data": data,
    }


# ✅ views.py 中使用：把结构化结果包装成 JSON 响应
def JsonResponse(result: dict, status_code: int = 200):
    return JSONResponse(status_code=status_code, content=result)


def to_voList(orm_list: List[T], model: Type[S]) -> List[S]:
    """
    将 ORM list 转为 Pydantic list
    """
    return [model.model_validate(obj) for obj in orm_list]
