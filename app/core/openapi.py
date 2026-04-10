from enum import Enum
from functools import lru_cache
from typing import Type, Dict, Any, Callable, cast, TypeVar

from fastapi import Request, Depends
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@lru_cache(maxsize=64)
def openapi_extra(model: Type[BaseModel], in_type="query") -> Dict[str, Any]:
    """
    ✅ 自动将 BaseModel 转换为 openapi_extra["parameters"] 字段定义
    ✅ 用于 GET 请求文档展示字段描述
    ✅ 支持 path 参数注入

    in_type:
      - query : 查询参数，如 xxx?a=1&b=2
      - path : 路径参数，如 /xxx/{a}/{b}
    """
    parameters = []
    schema = model.model_json_schema()
    required_fields = set(schema.get("required", []))
    properties = schema.get("properties", {})

    for name, field in model.model_fields.items():
        field_schema = properties.get(name, {}).copy()

        # 对 enum 类型进行修正（swagger展示用）
        if isinstance(field.annotation, type) and issubclass(field.annotation, Enum):
            field_schema["enum"] = [e.value for e in field.annotation]
            field_schema["type"] = "string"

        parameters.append({
            "name": name,
            "in": in_type,
            "required": name in required_fields,
            "schema": field_schema,
            "description": field_schema.get("description", ""),
        })

    return {"parameters": parameters}


def query_model(model_cls: Type[T], param_type="query") -> Callable[[Request], T]:
    """
    ✅ 替代 Depends(BaseModel) 的注入方式
    ✅ 保留结构化参数 + 不干扰 openapi_extra 描述
    ✅ 支持 path 参数注入

    param_type:
      - query : 查询参数，如 xxx?a=1&b=2
      - path : 路径参数，如 /xxx/{a}/{b}

    """

    async def dependency(request: Request) -> T:
        return model_cls(**request.path_params) if param_type == "path" else model_cls(**request.query_params)

    return cast(Callable[[Request], T], Depends(dependency))
