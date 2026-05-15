from fastapi import APIRouter, Request

from app.api.admin_compat.deps import CompatAuthRoute
from app.api.admin_compat.services import auth as auth_service
from app.api.admin_compat.schemas import (
    LoginForm,
    RegisterForm,
    UpdatePasswordForm,
    UpdateUserProfileForm,
)
from app.common.decorators.log import log_api
from app.common.utils.response import JsonResponse

public_router = APIRouter()
protected_router = APIRouter(route_class=CompatAuthRoute)


@public_router.post("/captcha", summary="获取登录验证码", tags=["管理台兼容层-认证"])
async def get_captcha():
    return JsonResponse(await auth_service.get_captcha())


@public_router.post("/login", summary="账号登录", tags=["管理台兼容层-认证"])
async def login(form: LoginForm, request: Request):
    return JsonResponse(await auth_service.login(form, request))


@public_router.post("/register", summary="账号注册", tags=["管理台兼容层-认证"])
async def register(form: RegisterForm):
    return JsonResponse(await auth_service.register(form))


@protected_router.post("/logout", summary="退出登录", tags=["管理台兼容层-认证"])
async def logout(request: Request):
    return JsonResponse(await auth_service.logout(request))


@protected_router.post("/auth/user/info", summary="获取当前用户信息", tags=["管理台兼容层-认证"])
async def get_user_info(request: Request):
    return JsonResponse(await auth_service.get_user_info(request))


@protected_router.post("/auth/password/update", summary="修改当前用户密码", tags=["管理台兼容层-认证"])
@log_api
async def update_password(form: UpdatePasswordForm, request: Request):
    return JsonResponse(await auth_service.update_password(request, form))


@protected_router.post("/auth/user/update", summary="修改当前用户资料", tags=["管理台兼容层-认证"])
@log_api
async def update_user_info(form: UpdateUserProfileForm, request: Request):
    return JsonResponse(await auth_service.update_user_info(request, form))
