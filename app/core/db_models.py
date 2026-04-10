import uuid

from tortoise import fields
from tortoise.exceptions import ConfigurationError
from tortoise.models import Model
from tortoise.queryset import QuerySet

from app.core.db import LOGIC_DELETE_ENABLED


class BaseQuerySet(QuerySet):
    def __init__(self, model):
        super().__init__(model)

    def all(self):
        # 强制使用 filter 来实现自动 is_delete=False
        return self.filter()

    def filter(self, *args, **kwargs):
        if "is_delete" not in kwargs:
            kwargs["is_delete"] = False
        return super().filter(*args, **kwargs)

    async def get_or_none(self, *args, **kwargs):
        if "is_delete" not in kwargs:
            kwargs["is_delete"] = False
        return await super().get_or_none(*args, **kwargs)

    async def delete(self, *, force_flag: bool = False):
        if force_flag or not LOGIC_DELETE_ENABLED:
            return await super().delete()
        return await self.update(is_delete=True)


# ✅ 类属性包装器，用于惰性初始化 QuerySet
class LazyManager:
    def __get__(self, instance, owner):
        if not getattr(owner._meta, "db", None):
            raise ConfigurationError(f"Model {owner.__name__} 未初始化完成，不能访问 objects")
        return BaseQuerySet(owner)


def generate_uuid():
    """生成一个32位长度的字符串UUID"""
    return uuid.uuid4().hex


class BaseOrmModel(Model):
    id = fields.CharField(max_length=32, pk=True, default=generate_uuid, description="主键 ID")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")
    is_delete = fields.BooleanField(default=False, description="逻辑删除标志")

    # ✅ 用 LazyManager 注入惰性类属性
    objects = LazyManager()

    class Meta:
        abstract = True

    async def safe_delete(self):
        """安全删除：按配置执行逻辑删除或物理删除"""
        if LOGIC_DELETE_ENABLED:
            self.is_delete = True
            await self.save(update_fields=['is_delete', 'update_time'])
        else:
            await self.delete()

    async def force_delete(self):
        """强制物理删除"""
        await super().delete()


class BaseViewModel(Model):
    class Meta:
        abstract = True

    async def save(self, *args, **kwargs):  # 防误写
        raise RuntimeError("v_user_recency is read-only")

    async def delete(self, *args, **kwargs):
        raise RuntimeError("v_user_recency is read-only")
