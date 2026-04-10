from datetime import datetime

from app.common.utils.jwt_utlis import get_password

from .constants import (
    DEFAULT_ADMIN_NICKNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    SEED_DICTIONARIES,
    SEED_MENUS,
    SEED_MESSAGES,
    SEED_ORGANIZATIONS,
)
from .models import (
    AdminCompatDictionary,
    AdminCompatDictionaryData,
    AdminCompatMenu,
    AdminCompatOrganization,
    AdminCompatRole,
    AdminCompatRoleMenu,
    AdminCompatUser,
    AdminCompatUserMessage,
    AdminCompatUserRole,
)


async def ensure_seed_data():
    """
    启动时补齐管理台当前需要的基础数据。

    这里不仅保证账号、角色、字典可用，也会把前端页面对应的菜单树和按钮权限
    同步到数据库里，方便联调时直接看到完整导航。
    """

    await _ensure_organizations()
    await _ensure_dictionaries()
    menu_id_map = await _ensure_menus()
    admin_user = await _ensure_admin_user()
    admin_role = await _ensure_admin_role()
    await _ensure_admin_role_bindings(admin_user.id, admin_role.id, menu_id_map)
    await _ensure_messages(admin_user.id)


async def _ensure_organizations():
    for item in SEED_ORGANIZATIONS:
        exists = await AdminCompatOrganization.get_or_none(
            organization_code=item["organization_code"]
        )
        if exists:
            continue
        await AdminCompatOrganization.create(**item)


async def _ensure_dictionaries():
    for item in SEED_DICTIONARIES:
        dict_obj = await AdminCompatDictionary.get_or_none(dict_code=item["dict_code"])
        if not dict_obj:
            dict_obj = await AdminCompatDictionary.create(
                dict_code=item["dict_code"],
                dict_name=item["dict_name"],
                sort_number=item["sort_number"],
                comments=item["comments"],
            )
        for detail in item["items"]:
            exists = await AdminCompatDictionaryData.get_or_none(
                dict_id=dict_obj.id,
                dict_data_code=detail["dict_data_code"],
            )
            if exists:
                continue
            await AdminCompatDictionaryData.create(
                dict_id=dict_obj.id,
                dict_data_code=detail["dict_data_code"],
                dict_data_name=detail["dict_data_name"],
                sort_number=detail["sort_number"],
                comments=detail.get("comments"),
            )


async def _ensure_menus() -> dict[str, int]:
    menu_id_map: dict[str, int] = {}
    pending = list(SEED_MENUS)
    while pending:
        next_round = []
        progressed = False
        for item in pending:
            parent_key = item["parent_key"]
            if parent_key and parent_key not in menu_id_map:
                next_round.append(item)
                continue

            parent_id = menu_id_map.get(parent_key, 0)
            lookup = (
                {"authority": item["authority"]}
                if item["menu_type"] == 1 and item["authority"]
                else {"path": item["path"]}
            )
            menu = await AdminCompatMenu.get_or_none(**lookup)
            if not menu:
                menu = await AdminCompatMenu.create(
                    parent_id=parent_id,
                    title=item["title"],
                    path=item["path"],
                    component=item["component"],
                    menu_type=item["menu_type"],
                    sort_number=item["sort_number"],
                    authority=item["authority"],
                    icon=item["icon"],
                    hide=item["hide"],
                    meta=item["meta"],
                    open_type=item["open_type"],
                    redirect=item.get("redirect"),
                )
            else:
                menu.parent_id = parent_id
                menu.title = item["title"]
                menu.component = item["component"]
                menu.menu_type = item["menu_type"]
                menu.sort_number = item["sort_number"]
                menu.authority = item["authority"]
                menu.icon = item["icon"]
                menu.hide = item["hide"]
                menu.meta = item["meta"]
                menu.open_type = item["open_type"]
                menu.redirect = item.get("redirect")
                await menu.save()
            menu_id_map[item["key"]] = menu.id
            progressed = True

        if not progressed:
            raise RuntimeError("菜单种子数据存在无法解析的父子关系")
        pending = next_round

    return menu_id_map


async def _ensure_admin_user() -> AdminCompatUser:
    org = await AdminCompatOrganization.first()
    user = await AdminCompatUser.get_or_none(username=DEFAULT_ADMIN_USERNAME)
    if user:
        # 兼容开发阶段反复启动，默认账号密码保持可用。
        user.password = get_password(DEFAULT_ADMIN_PASSWORD)
        user.nickname = user.nickname or DEFAULT_ADMIN_NICKNAME
        user.organization_id = user.organization_id or (org.id if org else None)
        user.status = 0
        await user.save()
        return user

    return await AdminCompatUser.create(
        username=DEFAULT_ADMIN_USERNAME,
        password=get_password(DEFAULT_ADMIN_PASSWORD),
        nickname=DEFAULT_ADMIN_NICKNAME,
        sex="1",
        phone="13800138000",
        email="admin@example.com",
        introduction="系统初始化管理员账号",
        organization_id=org.id if org else None,
        status=0,
        tell_pre="0752",
        tell="1234567",
    )


async def _ensure_admin_role() -> AdminCompatRole:
    role = await AdminCompatRole.get_or_none(role_code="admin")
    if role:
        return role
    return await AdminCompatRole.create(
        role_code="admin",
        role_name="超级管理员",
        comments="系统初始化角色",
    )


async def _ensure_admin_role_bindings(user_id: int, role_id: int, menu_id_map: dict[str, int]):
    if not await AdminCompatUserRole.get_or_none(user_id=user_id, role_id=role_id):
        await AdminCompatUserRole.create(user_id=user_id, role_id=role_id)

    for menu_id in menu_id_map.values():
        exists = await AdminCompatRoleMenu.get_or_none(role_id=role_id, menu_id=menu_id)
        if not exists:
            await AdminCompatRoleMenu.create(role_id=role_id, menu_id=menu_id)


async def _ensure_messages(user_id: int):
    for item in SEED_MESSAGES:
        exists = await AdminCompatUserMessage.get_or_none(
            user_id=user_id,
            message_type=item["message_type"],
            title=item["title"],
        )
        if exists:
            continue
        await AdminCompatUserMessage.create(
            user_id=user_id,
            message_type=item["message_type"],
            title=item["title"],
            content=item.get("content"),
            status=item.get("status", 0),
            avatar=item.get("avatar"),
            icon=item.get("icon"),
            color=item.get("color"),
            message_time=datetime.now(),
        )
