from fastapi import Request
from fastapi.routing import APIRoute
from jose import JWTError, jwt

from app.common.utils.jwt_utlis import ALGORITHM, SECRET_KEY, create_token
from app.common.utils.redis_utils import RedisUtil
from app.common.utils.response import JsonResponse, fail

from .constants import (
    LOGIN_FAIL_EXPIRE_SECONDS,
    LOGIN_FAIL_PREFIX,
    LOGIN_LOCK_PREFIX,
    LOGIN_TOKEN_PREFIX,
    TOKEN_EXPIRE_SECONDS,
)
from .helpers import make_log_user_context
from .models import AdminCompatRole, AdminCompatUser, AdminCompatUserRole
from .schemas import CurrentAdminUser


def _fmt_seconds(seconds: int) -> str:
    if seconds >= 3600:
        return f"{seconds // 3600}小时"
    if seconds >= 60:
        return f"{seconds // 60}分钟"
    return f"{seconds}秒"


def create_admin_access_token(user_id: int, username: str) -> str:
    return create_token(
        {
            "user_id": user_id,
            "username": username,
            "token_type": "admin_compat",
        }
    )


async def save_admin_access_token(user_id: int, token: str):
    await RedisUtil.set(
        f"{LOGIN_TOKEN_PREFIX}{user_id}",
        token,
        expire=TOKEN_EXPIRE_SECONDS,
    )


async def clear_admin_access_token(user_id: int):
    await RedisUtil.delete(f"{LOGIN_TOKEN_PREFIX}{user_id}")


async def get_login_lock_ttl(user_id: int) -> int:
    ttl = await RedisUtil.ttl(f"{LOGIN_LOCK_PREFIX}{user_id}")
    return ttl if ttl and ttl > 0 else 0


def _lock_seconds_for_count(count: int) -> int:
    if count >= 6:
        return 24 * 60 * 60
    if count == 5:
        return 30 * 60
    if count == 4:
        return 10 * 60
    if count == 3:
        return 5 * 60
    return 0


async def record_login_failure(user_id: int) -> tuple[int, int]:
    count = await RedisUtil.incr(
        f"{LOGIN_FAIL_PREFIX}{user_id}",
        expire=LOGIN_FAIL_EXPIRE_SECONDS,
    )
    lock_seconds = _lock_seconds_for_count(int(count))
    if lock_seconds > 0:
        await RedisUtil.set(
            f"{LOGIN_LOCK_PREFIX}{user_id}",
            "1",
            expire=lock_seconds,
        )
    return int(count), lock_seconds


async def reset_login_failures(user_id: int):
    await RedisUtil.delete(f"{LOGIN_FAIL_PREFIX}{user_id}")
    await RedisUtil.delete(f"{LOGIN_LOCK_PREFIX}{user_id}")


class CompatAuthRoute(APIRoute):
    """
    管理台兼容层自己的鉴权路由。
    """

    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def handler(request: Request):
            auth_header = request.headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                return JsonResponse(fail(code=1002, msg="Token无效或已过期"))

            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                if payload.get("token_type") != "admin_compat":
                    return JsonResponse(fail(code=1002, msg="Token无效或已过期"))

                user_id = int(payload.get("user_id"))
            except (JWTError, TypeError, ValueError):
                return JsonResponse(fail(code=1002, msg="Token无效或已过期"))

            redis_token = await RedisUtil.get(f"{LOGIN_TOKEN_PREFIX}{user_id}")
            if redis_token != token:
                return JsonResponse(fail(code=1002, msg="Token无效或已过期"))

            user = await AdminCompatUser.get_or_none(id=user_id)
            if not user:
                return JsonResponse(fail(code=1004, msg="账户不存在"))
            if user.status != 0:
                return JsonResponse(fail(code=1005, msg="账号已冻结"))

            locked_ttl = await get_login_lock_ttl(user.id)
            if locked_ttl > 0:
                return JsonResponse(
                    fail(code=1010, msg=f"账号已锁定，请 {_fmt_seconds(locked_ttl)} 后重试")
                )

            current_user = CurrentAdminUser(
                user_id=user.id,
                username=user.username,
                nickname=user.nickname,
                status=user.status,
                organization_id=user.organization_id,
            )
            request.state.admin_user = current_user
            request.state.cur_user = make_log_user_context(
                user.id, user.username, user.nickname
            )

            return await original_handler(request)

        return handler


def get_admin_user_from_request(request: Request) -> CurrentAdminUser:
    current_user = getattr(request.state, "admin_user", None)
    if current_user:
        return current_user
    raise RuntimeError("当前请求未完成兼容层鉴权")


async def get_current_role_codes(current_user: CurrentAdminUser) -> set[str]:
    relations = await AdminCompatUserRole.filter(user_id=current_user.user_id).all()
    role_ids = sorted({item.role_id for item in relations})

    if not role_ids:
        return set()
    roles = await AdminCompatRole.filter(id__in=role_ids).all()
    return {role.role_code for role in roles}
