from datetime import datetime

from app.common.utils.jwt_utlis import get_password

from .constants import (
    DEFAULT_ADMIN_NICKNAME,
    DEFAULT_ADMIN_PASSWORD,
    DEFAULT_ADMIN_USERNAME,
    SEED_DICTIONARIES,
    SEED_INSPECTION_EVENTS,
    SEED_INSPECTION_REPORTS,
    SEED_LAW_DOCUMENTS,
    SEED_MENUS,
    SEED_MESSAGES,
    SEED_ORGANIZATIONS,
    SEED_PATROL_AREAS,
    SEED_PATROL_POINTS,
    SEED_PATROL_TASKS,
    SEED_PATROL_USER_DEVICES,
    SEED_ROLES,
    SEED_WORK_ORDERS,
)
from .models import (
    AdminCompatDictionary,
    AdminCompatDictionaryData,
    AdminCompatInspectionEvent,
    AdminCompatInspectionReport,
    AdminCompatLawDocument,
    AdminCompatMenu,
    AdminCompatOrganization,
    AdminCompatPatrolArea,
    AdminCompatPatrolPoint,
    AdminCompatPatrolTask,
    AdminCompatPatrolUserDevice,
    AdminCompatRole,
    AdminCompatRoleMenu,
    AdminCompatUser,
    AdminCompatUserMessage,
    AdminCompatUserRole,
    AdminCompatWorkOrder,
)


def _parse_seed_datetime(value):
    if not value or isinstance(value, datetime):
        return value
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return value


async def ensure_seed_data():
    """
    启动时补齐管理台当前需要的基础数据。
    """

    await _ensure_organizations()
    await _ensure_dictionaries()
    await _cleanup_removed_menus()
    menu_id_map = await _ensure_menus()
    admin_user = await _ensure_admin_user()
    patrol_user = await _ensure_patrol_demo_user()
    await _cleanup_removed_roles()
    roles = await _ensure_roles()
    await _ensure_admin_role_bindings(admin_user.id, roles, menu_id_map)
    await _ensure_patrol_area_points()
    await _ensure_patrol_user_devices()
    await _ensure_patrol_tasks(admin_user.id, admin_user.nickname, patrol_user.id, patrol_user.nickname)
    await AdminCompatPatrolTask.filter(task_status="pending").update(task_status="waiting")
    await AdminCompatPatrolTask.exclude(task_status__in=["waiting", "running", "finished", "overdue"]).delete()
    await _ensure_closed_loop_data(admin_user.id, admin_user.nickname)
    await _ensure_messages(admin_user.id)


async def _ensure_organizations():
    for item in SEED_ORGANIZATIONS:
        exists = await AdminCompatOrganization.get_or_none(
            organization_code=item["organization_code"]
        )
        if exists:
            exists.organization_name = item["organization_name"]
            exists.organization_full_name = item["organization_full_name"]
            exists.organization_type = item["organization_type"]
            exists.sort_number = item["sort_number"]
            exists.comments = item["comments"]
            await exists.save()
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
        else:
            dict_obj.dict_name = item["dict_name"]
            dict_obj.sort_number = item["sort_number"]
            dict_obj.comments = item["comments"]
            await dict_obj.save()
        for detail in item["items"]:
            exists = await AdminCompatDictionaryData.get_or_none(
                dict_id=dict_obj.id,
                dict_data_code=detail["dict_data_code"],
            )
            if exists:
                exists.dict_data_name = detail["dict_data_name"]
                exists.sort_number = detail["sort_number"]
                exists.comments = detail.get("comments")
                exists.color = detail.get("color")
                exists.ripple = detail.get("ripple", 0)
                await exists.save()
                continue
            await AdminCompatDictionaryData.create(
                dict_id=dict_obj.id,
                dict_data_code=detail["dict_data_code"],
                dict_data_name=detail["dict_data_name"],
                sort_number=detail["sort_number"],
                comments=detail.get("comments"),
                color=detail.get("color"),
                ripple=detail.get("ripple", 0),
            )
        if item["dict_code"] == "patrol_task_status":
            await AdminCompatDictionaryData.filter(
                dict_id=dict_obj.id,
                dict_data_code="pending",
            ).delete()


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


REMOVED_MENU_PATH_PREFIXES = (
    "/form",
    "/list",
    "/result",
    "/exception",
    "/iframe",
    "/example",
    "/dashboard/workplace",
    "/dashboard/analysis",
    "/system/tenant",
    "/system/member",
)

REMOVED_MENU_EXACT_PATHS = (
    "/dashboard",
    "https://eleadmin.com/goods/26",
)


async def _cleanup_removed_menus():
    menu_ids: set[int] = set()
    for path_prefix in REMOVED_MENU_PATH_PREFIXES:
        menus = await AdminCompatMenu.filter(path=path_prefix).all()
        menu_ids.update(menu.id for menu in menus)
        menus = await AdminCompatMenu.filter(path__startswith=f"{path_prefix}/").all()
        menu_ids.update(menu.id for menu in menus)

    for path in REMOVED_MENU_EXACT_PATHS:
        menus = await AdminCompatMenu.filter(path=path).all()
        menu_ids.update(menu.id for menu in menus)

    for menu_id in sorted(menu_ids):
        if await AdminCompatMenu.get_or_none(id=menu_id):
            await _delete_menu_tree(menu_id)


async def _delete_menu_tree(menu_id: int):
    child_ids = await AdminCompatMenu.filter(parent_id=menu_id).values_list("id", flat=True)
    for child_id in child_ids:
        await _delete_menu_tree(child_id)
    await AdminCompatRoleMenu.filter(menu_id=menu_id).delete()
    await AdminCompatMenu.filter(id=menu_id).delete()


async def _ensure_admin_user() -> AdminCompatUser:
    org = await AdminCompatOrganization.first()
    user = await AdminCompatUser.get_or_none(username=DEFAULT_ADMIN_USERNAME)
    if user:
        user.password = get_password(DEFAULT_ADMIN_PASSWORD)
        user.nickname = user.nickname or DEFAULT_ADMIN_NICKNAME
        user.organization_id = user.organization_id or (org.id if org else None)
        user.status = 0
        await user.save()
    return user


async def _ensure_patrol_demo_user() -> AdminCompatUser:
    org = await AdminCompatOrganization.first()
    user = await AdminCompatUser.get_or_none(username="patrol_001")
    payload = {
        "password": get_password("123456"),
        "nickname": "张三",
        "sex": "1",
        "phone": "13800000001",
        "email": "patrol_001@example.com",
        "introduction": "移动端默认巡查员",
        "organization_id": org.id if org else None,
        "status": 0,
        "tell_pre": "0752",
        "tell": "13800000001",
    }
    if user:
        await user.update_from_dict(payload)
        await user.save()
        return user
    return await AdminCompatUser.create(username="patrol_001", **payload)

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


async def _cleanup_removed_roles():
    removed_role_codes = ("tenant_owner", "tenant_admin", "tenant_user", "tenant_auditor")
    role_ids = await AdminCompatRole.filter(
        role_code__in=removed_role_codes,
    ).values_list("id", flat=True)
    if not role_ids:
        return
    await AdminCompatRoleMenu.filter(role_id__in=role_ids).delete()
    await AdminCompatUserRole.filter(role_id__in=role_ids).delete()
    await AdminCompatRole.filter(id__in=role_ids).delete()


async def _ensure_roles() -> dict[str, AdminCompatRole]:
    role_map: dict[str, AdminCompatRole] = {}
    for item in SEED_ROLES:
        role = await AdminCompatRole.get_or_none(role_code=item["role_code"])
        if not role:
            role = await AdminCompatRole.create(**item)
        else:
            role.role_name = item["role_name"]
            role.is_system_role = item["is_system_role"]
            role.comments = item["comments"]
            await role.save()
        role_map[role.role_code] = role
    return role_map


async def _ensure_admin_role_bindings(
    user_id: int,
    role_map: dict[str, AdminCompatRole],
    menu_id_map: dict[str, int],
):
    admin_role = role_map["admin"]
    if not await AdminCompatUserRole.get_or_none(user_id=user_id, role_id=admin_role.id):
        await AdminCompatUserRole.create(user_id=user_id, role_id=admin_role.id)

    await _ensure_role_menu_bindings(role_map, menu_id_map)


async def _ensure_role_menu_bindings(
    role_map: dict[str, AdminCompatRole],
    menu_id_map: dict[str, int],
):
    all_keys = list(menu_id_map.keys())
    role_menu_keys = {
        "admin": all_keys,
        "operator": [key for key in all_keys if not key.startswith("system-")],
        "viewer": [key for key in all_keys if key.startswith("dashboard-") or key.startswith("user-")],
    }

    for role_code, menu_keys in role_menu_keys.items():
        role = role_map.get(role_code)
        if not role:
            continue
        menu_ids = [menu_id_map[key] for key in menu_keys if key in menu_id_map]
        for menu_id in menu_ids:
            exists = await AdminCompatRoleMenu.get_or_none(role_id=role.id, menu_id=menu_id)
            if not exists:
                await AdminCompatRoleMenu.create(role_id=role.id, menu_id=menu_id)


async def _ensure_patrol_tasks(
    admin_user_id: int,
    admin_nickname: str,
    patrol_user_id: int | None = None,
    patrol_nickname: str | None = None,
):
    area_map = {area.area_code: area for area in await AdminCompatPatrolArea.all()}
    point_map = {point.point_code: point for point in await AdminCompatPatrolPoint.all()}

    for item in SEED_PATROL_TASKS:
        task = await AdminCompatPatrolTask.get_or_none(task_code=item["task_code"])
        area_codes = item.get("area_codes") or []
        point_codes = item.get("point_codes") or []
        payload = {
            **{
                key: value
                for key, value in item.items()
                if key not in {"area_codes", "point_codes"}
            },
            "executor_id": item.get("executor_id") or patrol_user_id or admin_user_id,
            "executor_name": item.get("executor_name") or patrol_nickname or admin_nickname,
            "creator_id": item.get("creator_id") or admin_user_id,
            "creator_name": item.get("creator_name") or admin_nickname,
        }
        if area_codes:
            payload["area_ids"] = [
                area_map[code].id for code in area_codes if code in area_map
            ]
        if point_codes:
            payload["point_ids"] = [
                point_map[code].id for code in point_codes if code in point_map
            ]
        for datetime_key in ("plan_time", "start_time", "end_time"):
            payload[datetime_key] = _parse_seed_datetime(payload.get(datetime_key))
        if not task:
            await AdminCompatPatrolTask.create(**payload)
            continue

        for key, value in payload.items():
            setattr(task, key, value)
        await task.save()


async def _ensure_patrol_area_points():
    seed_area_codes = {item["area_code"] for item in SEED_PATROL_AREAS}
    seed_point_codes = {item["point_code"] for item in SEED_PATROL_POINTS}
    await AdminCompatPatrolPoint.exclude(point_code__in=seed_point_codes).delete()
    await AdminCompatPatrolArea.exclude(area_code__in=seed_area_codes).delete()

    area_id_map: dict[str, int] = {}
    for item in SEED_PATROL_AREAS:
        area = await AdminCompatPatrolArea.get_or_none(area_code=item["area_code"])
        if not area:
            area = await AdminCompatPatrolArea.create(**item)
        else:
            for key, value in item.items():
                setattr(area, key, value)
            await area.save()
        area_id_map[item["area_code"]] = area.id

    for item in SEED_PATROL_POINTS:
        area_code = item["area_code"]
        area_id = area_id_map.get(area_code)
        if not area_id:
            continue
        payload = {key: value for key, value in item.items() if key != "area_code"}
        payload["area_id"] = area_id
        point = await AdminCompatPatrolPoint.get_or_none(point_code=item["point_code"])
        if not point:
            await AdminCompatPatrolPoint.create(**payload)
            continue
        for key, value in payload.items():
            setattr(point, key, value)
        await point.save()


async def _ensure_patrol_user_devices():
    for item in SEED_PATROL_USER_DEVICES:
        username = item.get("username")
        user = await AdminCompatUser.get_or_none(username=username)
        if not user:
            continue
        payload = {key: value for key, value in item.items() if key != "username"}
        payload["user_id"] = user.id
        device = await AdminCompatPatrolUserDevice.get_or_none(
            user_id=user.id,
            device_type=payload["device_type"],
        )
        if not device:
            await AdminCompatPatrolUserDevice.create(**payload)
            continue
        for key, value in payload.items():
            setattr(device, key, value)
        await device.save()


async def _ensure_closed_loop_data(admin_user_id: int, admin_nickname: str):
    area_map = {area.area_code: area for area in await AdminCompatPatrolArea.all()}
    point_map = {point.point_code: point for point in await AdminCompatPatrolPoint.all()}
    task_map = {task.task_code: task for task in await AdminCompatPatrolTask.all()}

    event_id_map: dict[str, int] = {}
    for item in SEED_INSPECTION_EVENTS:
        point = point_map.get(item.get("point_code"))
        area = area_map.get(item.get("area_code"))
        task = task_map.get(item.get("task_code"))
        payload = {
            key: value
            for key, value in item.items()
            if key not in {"area_code", "point_code"}
        }
        payload.update(
            {
                "area_id": area.id if area else None,
                "area_name": area.area_name if area else item.get("area_name", "幸福里小区"),
                "point_id": point.id if point else None,
                "point_name": point.point_name if point else item.get("point_name", "重点点位"),
                "lat": point.lat if point else item.get("lat", 23.1372),
                "lng": point.lng if point else item.get("lng", 113.2621),
                "task_id": task.id if task else None,
                "inspector_id": item.get("inspector_id") or admin_user_id,
                "inspector_name": item.get("inspector_name") or admin_nickname,
            }
        )
        payload["detected_time"] = _parse_seed_datetime(payload.get("detected_time"))
        event = await AdminCompatInspectionEvent.get_or_none(
            event_code=item["event_code"]
        )
        if not event:
            event = await AdminCompatInspectionEvent.create(**payload)
        else:
            for key, value in payload.items():
                setattr(event, key, value)
            await event.save()
        event_id_map[item["event_code"]] = event.id

    work_order_id_map: dict[str, int] = {}
    for item in SEED_WORK_ORDERS:
        event_id = event_id_map.get(item.get("event_code"))
        task = task_map.get(item.get("task_code"))
        area = area_map.get(item.get("area_code"))
        payload = {
            key: value
            for key, value in item.items()
            if key not in {"event_code", "task_code", "area_code"}
        }
        payload.update(
            {
                "event_id": event_id,
                "task_id": task.id if task else None,
                "area_id": area.id if area else None,
                "area_name": area.area_name if area else item.get("area_name", "幸福里小区"),
                "reporter_id": item.get("reporter_id") or admin_user_id,
                "reporter_name": item.get("reporter_name") or admin_nickname,
            }
        )
        payload["deadline_time"] = _parse_seed_datetime(payload.get("deadline_time"))
        order = await AdminCompatWorkOrder.get_or_none(
            work_order_code=item["work_order_code"]
        )
        if not order:
            order = await AdminCompatWorkOrder.create(**payload)
        else:
            for key, value in payload.items():
                setattr(order, key, value)
            await order.save()
        work_order_id_map[item["work_order_code"]] = order.id

    for item in SEED_INSPECTION_REPORTS:
        task = task_map.get(item.get("task_code"))
        work_order_id = work_order_id_map.get(item.get("work_order_code"))
        payload = {
            key: value
            for key, value in item.items()
            if key not in {"task_code", "work_order_code"}
        }
        payload.update(
            {
                "task_id": task.id if task else None,
                "work_order_id": work_order_id,
            }
        )
        payload["generated_time"] = _parse_seed_datetime(payload.get("generated_time"))
        payload["archive_time"] = _parse_seed_datetime(payload.get("archive_time"))
        report = await AdminCompatInspectionReport.get_or_none(
            report_code=item["report_code"]
        )
        if not report:
            await AdminCompatInspectionReport.create(**payload)
            continue
        for key, value in payload.items():
            setattr(report, key, value)
        await report.save()

    for item in SEED_LAW_DOCUMENTS:
        work_order_id = work_order_id_map.get(item.get("work_order_code"))
        payload = {key: value for key, value in item.items() if key != "work_order_code"}
        payload["work_order_id"] = work_order_id
        document = await AdminCompatLawDocument.get_or_none(
            document_code=item["document_code"]
        )
        if not document:
            await AdminCompatLawDocument.create(**payload)
            continue
        for key, value in payload.items():
            setattr(document, key, value)
        await document.save()


async def _ensure_messages(user_id: int):
    for item in SEED_MESSAGES:
        exists = await AdminCompatUserMessage.filter(
            user_id=user_id,
            message_type=item["message_type"],
            title=item["title"],
        ).first()
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
