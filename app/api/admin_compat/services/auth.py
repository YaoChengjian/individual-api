import base64

from fastapi import Request

from app.api.admin_compat.constants import DEFAULT_ADMIN_PASSWORD
from app.api.admin_compat.deps import (
    clear_admin_access_token,
    create_admin_access_token,
    get_admin_user_from_request,
    get_login_lock_ttl,
    record_login_failure,
    reset_login_failures,
    save_admin_access_token,
)
from app.api.admin_compat.helpers import get_request_ip, parse_user_agent
from app.api.admin_compat.models import AdminCompatLoginRecord, AdminCompatUser
from app.api.admin_compat.schemas import (
    CaptchaResult,
    LoginForm,
    LoginResult,
    UpdatePasswordForm,
    UpdateUserProfileForm,
)
from app.api.admin_compat.services.common import build_user_out
from app.common.utils.captcha_utils import CaptchaService
from app.common.utils.jwt_utlis import get_password, verify_password
from app.common.utils.response import fail, success

_LAST_CAPTCHA_TEXT: str | None = None


async def get_captcha():
    global _LAST_CAPTCHA_TEXT

    # 兼容层直接返回验证码文本给前端调试，因此这里额外避免连续两次生成相同内容，
    # 让“点击刷新验证码”在页面上有更明显的变化感知。
    code = CaptchaService.build_code(exclude=_LAST_CAPTCHA_TEXT).lower()
    _LAST_CAPTCHA_TEXT = code
    image = base64.b64encode(CaptchaService._build_image(code)).decode()
    return success(
        CaptchaResult(base64=f"data:image/png;base64,{image}", text=code),
        msg="获取成功",
    )


async def login(form: LoginForm, request: Request):
    user = await AdminCompatUser.get_or_none(username=form.username.strip())
    if not user:
        await _create_login_record(
            request=request,
            login_type=1,
            comments="用户名或密码错误",
            username=form.username.strip(),
        )
        return fail(1001, "用户名或密码错误")

    locked_ttl = await get_login_lock_ttl(user.id)
    if locked_ttl > 0:
        return fail(1010, f"账号已锁定，请稍后再试")

    if user.status != 0:
        await _create_login_record(
            request=request,
            login_type=1,
            comments="账号已冻结",
            user=user,
        )
        return fail(1005, "账号已冻结")

    if not verify_password(form.password, user.password):
        _count, lock_seconds = await record_login_failure(user.id)
        comments = "用户名或密码错误"
        if lock_seconds > 0:
            comments = f"账号已锁定，请 {lock_seconds} 秒后重试"
        await _create_login_record(
            request=request,
            login_type=1,
            comments=comments,
            user=user,
        )
        return fail(1001, comments)

    token = create_admin_access_token(user.id, user.username)
    await save_admin_access_token(user.id, token)
    await reset_login_failures(user.id)
    await _create_login_record(request=request, login_type=0, comments="登录成功", user=user)

    return success(
        LoginResult(access_token=token, user=await build_user_out(user, include_authorities=True)),
        msg="登录成功",
    )


async def logout(request: Request):
    current_user = get_admin_user_from_request(request)
    await clear_admin_access_token(current_user.user_id)
    user = await AdminCompatUser.get_or_none(id=current_user.user_id)
    if user:
        await _create_login_record(
            request=request,
            login_type=2,
            comments="退出登录",
            user=user,
        )
    return success(msg="退出成功")


async def get_user_info(request: Request):
    current_user = get_admin_user_from_request(request)
    user = await AdminCompatUser.get_or_none(id=current_user.user_id)
    if not user:
        return fail(1004, "账户不存在")
    return success(await build_user_out(user, include_authorities=True), msg="获取成功")


async def update_password(request: Request, form: UpdatePasswordForm):
    current_user = get_admin_user_from_request(request)
    user = await AdminCompatUser.get_or_none(id=current_user.user_id)
    if not user:
        return fail(1004, "账户不存在")
    if not verify_password(form.oldPassword, user.password):
        return fail(1, "旧密码不正确")

    new_password = form.password.strip()
    if form.password != new_password or not (5 <= len(new_password) <= 18):
        return fail(1, "密码必须为5-18位非空白字符")

    user.password = get_password(new_password)
    await user.save(update_fields=["password", "update_time"])
    return success(msg="密码修改成功")


async def update_user_info(request: Request, form: UpdateUserProfileForm):
    current_user = get_admin_user_from_request(request)
    user = await AdminCompatUser.get_or_none(id=current_user.user_id)
    if not user:
        return fail(1004, "账户不存在")

    updates = {}
    if form.nickname is not None:
        updates["nickname"] = form.nickname.strip()
    if form.avatar is not None:
        updates["avatar"] = form.avatar
    if form.sex is not None:
        updates["sex"] = form.sex
    if form.email is not None:
        updates["email"] = form.email.strip()
    if form.introduction is not None:
        updates["introduction"] = form.introduction
    if form.address is not None:
        updates["address"] = form.address
    if form.tellPre is not None:
        updates["tell_pre"] = form.tellPre
    if form.tell is not None:
        updates["tell"] = form.tell

    if "nickname" in updates and not updates["nickname"]:
        return fail(1, "昵称不能为空")

    await user.update_from_dict(updates)
    await user.save()
    return success(await build_user_out(user, include_authorities=True), msg="保存成功")


async def _create_login_record(
    request: Request,
    login_type: int,
    comments: str,
    user: AdminCompatUser | None = None,
    username: str | None = None,
):
    ua_info = parse_user_agent(request.headers.get("user-agent"))
    await AdminCompatLoginRecord.create(
        user_id=user.id if user else None,
        username=user.username if user else username,
        nickname=user.nickname if user else None,
        os=ua_info["os"],
        device=ua_info["device"],
        browser=ua_info["browser"],
        ip=get_request_ip(request),
        login_type=login_type,
        comments=comments,
    )


async def reset_default_admin_password():
    """
    为了方便本地调试，兼容层默认管理员密码始终保持为 admin。
    """

    user = await AdminCompatUser.get_or_none(username="admin")
    if not user:
        return
    user.password = get_password(DEFAULT_ADMIN_PASSWORD)
    await user.save(update_fields=["password", "update_time"])
