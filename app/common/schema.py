from datetime import datetime
from typing import Any, Dict, List, Generic, TypeVar, Optional

from pydantic import BaseModel, Field, model_serializer

T = TypeVar("T")


class NoneSchema(BaseModel):
    """
    用于处理没有数据的情况
    """
    pass


class IdSchema(BaseModel):
    id: str = Field(..., description="ID")


# 通用VO基类模型
# 1. 支持从ORM对象直接转换为VO对象(from_attributes=True)
# 2. 支持拓展ORM中没有的字段
# 3. 自动处理datetime类型的JSON序列化
# 4. 所有VO模型都应继承此类
class BaseVoModel(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")
        }

    def extra(self, **data: Any) -> Dict[str, Any]:
        result = self.model_dump(mode='json')
        result.update(data)
        return result

    # 统一输出加工：把所有 None 变为 ""
    # @model_serializer(mode="wrap")
    # def _serialize(self, serializer):
    #     data = serializer(self)
    #
    #     def replace_none(obj):
    #         if obj is None:
    #             return ""
    #         if isinstance(obj, list):
    #             return [replace_none(i) for i in obj]
    #         if isinstance(obj, dict):
    #             return {k: replace_none(v) for k, v in obj.items()}
    #         return obj
    #
    #     return replace_none(data)


class FileMod(BaseModel):
    file_name: str = Field(..., description="文件名称")
    file_path: str = Field(..., description="文件路径")


class FileVo(BaseVoModel):
    file_name: str = Field(..., description="文件名称")
    file_path: str = Field(..., description="文件路径")


# 通用分页参数模型
class BasePageModel(BaseModel):
    page: int = Field(1, description="页码", ge=1)
    page_size: int = Field(10, description="每页记录数", ge=1)


class RespListSimp(BaseVoModel, Generic[T]):
    list: List[T] = Field(..., description="当前页数据")


class RespListModel(BaseVoModel, Generic[T]):
    list: List[T] = Field(..., description="当前页数据")
    page_count: int = Field(..., description="总页数")
    data_count: int = Field(..., description="总数据条数")


class WebCurUser(BaseModel):
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    name: str = Field(..., description="姓名")
    phone: Optional[str] = Field(None, description="手机号")
    is_cert: Optional[bool] = Field(None, description="是否认证")


class CurUser(BaseModel):
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    name: str = Field(..., description="姓名")
    phone: Optional[str] = Field(None, description="手机号")
    status: Optional[int] = Field(None, description="状态.0：停用；1：正常")
    is_superuser: bool = Field(..., description="是否超级管理员")
