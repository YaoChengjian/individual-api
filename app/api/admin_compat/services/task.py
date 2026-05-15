from datetime import datetime, timedelta

from app.api.admin_compat.helpers import build_page_payload, paginate_queryset, resolve_order_field
from app.api.admin_compat.models import (
    AdminCompatDictionary,
    AdminCompatDictionaryData,
    AdminCompatInspectionEvent,
    AdminCompatPatrolArea,
    AdminCompatPatrolPoint,
    AdminCompatPatrolTask,
    AdminCompatPatrolUserDevice,
    AdminCompatUser,
    AdminCompatWorkOrder,
)
from app.api.admin_compat.schemas import (
    CurrentAdminUser,
    PatrolAreaForm,
    PatrolPointForm,
    PatrolPointRemoveForm,
    PatrolTaskCreateForm,
    PatrolTaskDetailForm,
    PatrolTaskWorkOrderQuery,
    PatrolTaskQuery,
    PatrolTaskTourForm,
    PatrolTaskUpdateForm,
)
from app.common.utils.redis_utils import RedisUtil
from app.common.utils.response import fail, success

TOUR_REDIS_PREFIX = "admin-compat:tour:"
PRINTED_WORK_ORDER_STATUS = "PRINTED"

WORK_ORDER_STATUS_META = {
    "pending_report": {"label": "待处理", "color": "#f59e0b", "ripple": True},
    "processed": {"label": "已处理", "color": "#18a058", "ripple": False},
    "processing": {"label": "处理中", "color": "#722ed1", "ripple": True},
    "finished": {"label": "已完成", "color": "#18a058", "ripple": False},
}


def _work_order_time(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _normalize_image_src(value: str | None) -> str:
    if not value:
        return ""
    image_src = value.strip()
    if not image_src:
        return ""
    if image_src.startswith(("data:", "http://", "https://", "/")):
        return image_src
    return f"data:image/jpeg;base64,{image_src}"


async def _extract_work_order_image(order: AdminCompatWorkOrder) -> str:
    for evidence in order.evidence_list or []:
        if not isinstance(evidence, dict):
            continue
        image_value = (
            evidence.get("imageBase64")
            or evidence.get("imageUrl")
            or evidence.get("base64")
            or evidence.get("fileUrl")
            or evidence.get("url")
        )
        if image_value:
            return _normalize_image_src(str(image_value))
    if order.event_id:
        event = await AdminCompatInspectionEvent.get_or_none(id=order.event_id)
        if event:
            return _normalize_image_src(event.marked_image_url or event.image_url)
    return ""


async def _build_printed_work_order(order: AdminCompatWorkOrder) -> dict:
    timeline = order.timeline or []
    print_meta = timeline[-1] if timeline else {}
    status = WORK_ORDER_STATUS_META.get(
        order.status,
        {"label": order.status, "color": "#8b95a5", "ripple": False},
    )
    return {
        "workOrderId": order.id,
        "workOrderCode": order.work_order_code,
        "title": order.title,
        "taskId": order.task_id,
        "eventTypeName": order.event_type_name or order.event_type,
        "riskLevelName": order.risk_level_name,
        "reporterName": order.reporter_name,
        "locationName": order.location_name or order.point_name or order.area_name,
        "addressDetail": order.address_detail,
        "description": order.description,
        "suggestion": order.suggestion,
        "status": order.status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status["ripple"],
        "reportTime": _work_order_time(order.report_time),
        "printedAt": _work_order_time(order.update_time or order.create_time),
        "noticeNumber": print_meta.get("noticeNumber"),
        "documentContent": print_meta.get("documentContent"),
        "fileUrl": print_meta.get("fileUrl"),
        "imageBase64": await _extract_work_order_image(order),
        "evidenceList": order.evidence_list or [],
    }


async def _dictionary_name_map(dict_code: str) -> dict[str, str]:
    dictionary = await AdminCompatDictionary.get_or_none(dict_code=dict_code)
    if not dictionary:
        return {}
    rows = await AdminCompatDictionaryData.filter(dict_id=dictionary.id).all()
    return {item.dict_data_code: item.dict_data_name for item in rows}


async def _task_name_maps() -> tuple[dict[str, str], dict[str, str]]:
    return (
        await _dictionary_name_map("patrol_task_type"),
        await _dictionary_name_map("patrol_task_status"),
    )


def _format_time(value: datetime | None) -> str:
    if not value:
        return ""
    return value.strftime("%Y-%m-%d %H:%M")


def _build_task_out(
    task: AdminCompatPatrolTask,
    type_names: dict[str, str],
    status_names: dict[str, str],
) -> dict:
    return {
        "taskId": task.id,
        "taskCode": task.task_code,
        "taskTitle": task.task_title,
        "taskType": task.task_type,
        "taskTypeName": type_names.get(task.task_type, task.task_type),
        "priority": task.priority,
        "description": task.description,
        "aiFocus": bool(task.ai_focus),
        "patrolLocation": task.patrol_location,
        "areaIds": task.area_ids or [],
        "pointIds": task.point_ids or [],
        "planTime": _format_time(task.plan_time),
        "startTime": _format_time(task.start_time or task.plan_time),
        "endTime": _format_time(task.end_time),
        "durationHours": task.duration_hours,
        "repeatRule": task.repeat_rule,
        "executorId": task.executor_id,
        "executorName": task.executor_name,
        "taskStatus": task.task_status,
        "taskStatusName": status_names.get(task.task_status, task.task_status),
        "progress": task.progress,
        "exceptionCount": task.exception_count,
        "creatorName": task.creator_name,
        "createTime": _format_time(task.create_time),
    }


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _task_queryset(params: PatrolTaskQuery):
    queryset = AdminCompatPatrolTask.all()
    if params.taskTitle:
        queryset = queryset.filter(task_title__contains=params.taskTitle)
    if params.taskType:
        queryset = queryset.filter(task_type=params.taskType)
    if params.taskStatus:
        queryset = queryset.filter(task_status=params.taskStatus)
    if params.patrolLocation:
        queryset = queryset.filter(patrol_location__contains=params.patrolLocation)
    if params.executorId:
        queryset = queryset.filter(executor_id=params.executorId)
    if start := _parse_time(params.timeStart):
        queryset = queryset.filter(plan_time__gte=start)
    if end := _parse_time(params.timeEnd):
        end = end.replace(hour=23, minute=59, second=59) if len(params.timeEnd or "") <= 10 else end
        queryset = queryset.filter(plan_time__lte=end)
    return queryset


async def page_tasks(params: PatrolTaskQuery):
    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "taskCode": "task_code",
            "taskTitle": "task_title",
            "taskType": "task_type",
            "patrolLocation": "patrol_location",
            "planTime": "plan_time",
            "executorName": "executor_name",
            "taskStatus": "task_status",
            "progress": "progress",
            "exceptionCount": "exception_count",
            "creatorName": "creator_name",
            "createTime": "create_time",
        },
        "-create_time",
    )
    total, tasks = await paginate_queryset(
        _task_queryset(params).order_by(order_by),
        params.page,
        params.limit,
    )
    type_names, status_names = await _task_name_maps()
    items = [_build_task_out(task, type_names, status_names) for task in tasks]
    return success(build_page_payload(items, total))


async def list_tasks(params: PatrolTaskQuery | None = None):
    params = params or PatrolTaskQuery(limit=500)
    tasks = await _task_queryset(params).order_by("-create_time").limit(params.limit).all()
    type_names, status_names = await _task_name_maps()
    return success([_build_task_out(task, type_names, status_names) for task in tasks])


async def task_detail(form: PatrolTaskDetailForm):
    task = None
    if form.taskId:
        task = await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    elif form.taskCode:
        task = await AdminCompatPatrolTask.get_or_none(task_code=form.taskCode)
    if not task:
        return fail(1, "巡查任务不存在")

    type_names, status_names = await _task_name_maps()
    task_out = _build_task_out(task, type_names, status_names)
    areas = (await list_patrol_areas())["data"]
    points = (await list_patrol_points(task.area_ids or []))["data"]
    executors = (await list_patrol_executors())["data"]
    return success(
        {
            "task": task_out,
            "areas": areas,
            "points": points,
            "executors": executors,
        }
    )


async def printed_work_orders(form: PatrolTaskDetailForm):
    queryset = await _printed_work_order_queryset(form)
    if queryset is None:
        return fail(1, "巡查任务不存在")
    rows = await queryset.order_by("-update_time", "-create_time").all()
    return success([await _build_printed_work_order(row) for row in rows])


async def page_printed_work_orders(params: PatrolTaskWorkOrderQuery):
    queryset = await _printed_work_order_queryset(params)
    if queryset is None:
        return fail(1, "巡查任务不存在")
    total, rows = await paginate_queryset(
        queryset.order_by("-update_time", "-create_time"),
        params.page,
        params.limit,
    )
    return success(build_page_payload([await _build_printed_work_order(row) for row in rows], total))


async def _printed_work_order_queryset(form: PatrolTaskDetailForm | PatrolTaskWorkOrderQuery):
    task = None
    if form.taskId:
        task = await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    elif form.taskCode:
        task = await AdminCompatPatrolTask.get_or_none(task_code=form.taskCode)
    if not task:
        return None
    return AdminCompatWorkOrder.filter(
        task_id=task.id,
        push_status=PRINTED_WORK_ORDER_STATUS,
    )


async def task_summary(params: PatrolTaskQuery | None = None):
    params = params or PatrolTaskQuery(limit=500)
    queryset = _task_queryset(params)
    return success(
        {
            "pending": 0,
            "waiting": await queryset.filter(task_status="waiting").count(),
            "running": await queryset.filter(task_status="running").count(),
            "finished": await queryset.filter(task_status="finished").count(),
            "overdue": await queryset.filter(task_status="overdue").count(),
        }
    )


def _build_area_out(area: AdminCompatPatrolArea) -> dict:
    return {
        "areaId": area.id,
        "areaCode": area.area_code,
        "areaName": area.area_name,
        "center": {"lat": area.center_lat, "lng": area.center_lng},
        "boundary": area.boundary or [],
        "sortNumber": area.sort_number,
        "comments": area.comments,
    }


def _coord_to_dict(coord) -> dict[str, float]:
    return {"lat": coord.lat, "lng": coord.lng}


def _build_point_out(point: AdminCompatPatrolPoint) -> dict:
    return {
        "pointId": point.id,
        "areaId": point.area_id,
        "pointCode": point.point_code,
        "pointName": point.point_name,
        "pointType": point.point_type,
        "lat": point.lat,
        "lng": point.lng,
        "sortNumber": point.sort_number,
        "comments": point.comments,
    }


def _build_device_out(device: AdminCompatPatrolUserDevice) -> dict:
    return {
        "deviceId": device.id,
        "userId": device.user_id,
        "userName": device.user_name,
        "employeeNo": device.employee_no,
        "deviceType": device.device_type,
        "deviceName": device.device_name,
        "deviceSn": device.device_sn,
        "onlineStatus": device.online_status,
        "bindStatus": device.bind_status,
    }


async def list_patrol_areas():
    areas = await AdminCompatPatrolArea.all().order_by("sort_number", "id")
    return success([_build_area_out(area) for area in areas])


async def list_patrol_points(area_ids: list[int] | None = None):
    queryset = AdminCompatPatrolPoint.all()
    if area_ids:
        queryset = queryset.filter(area_id__in=area_ids)
    points = await queryset.order_by("sort_number", "id")
    return success([_build_point_out(point) for point in points])


async def save_patrol_area(form: PatrolAreaForm):
    if len(form.boundary) < 3:
        return fail(1, "请至少绘制3个边界点")

    boundary = [_coord_to_dict(coord) for coord in form.boundary]
    payload = {
        "area_name": form.areaName.strip(),
        "center_lat": form.center.lat,
        "center_lng": form.center.lng,
        "boundary": boundary,
        "comments": form.comments,
    }
    if form.areaId:
        area = await AdminCompatPatrolArea.get_or_none(id=form.areaId)
        if not area:
            return fail(1, "巡查区域不存在")
        for key, value in payload.items():
            setattr(area, key, value)
        await area.save()
        return success(_build_area_out(area), msg="区域已更新")

    area = await AdminCompatPatrolArea.create(
        area_code=f"AREA{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        sort_number=99,
        **payload,
    )
    return success(_build_area_out(area), msg="区域已保存")


async def add_patrol_point(form: PatrolPointForm):
    area_id = form.areaId
    if not area_id:
        area = await AdminCompatPatrolArea.first()
        area_id = area.id if area else None
    if not area_id:
        return fail(1, "请先选择社区")

    payload = {
        "area_id": area_id,
        "point_name": form.pointName.strip(),
        "point_type": form.pointType or "key_point",
        "lat": form.lat,
        "lng": form.lng,
    }
    if form.pointId:
        point = await AdminCompatPatrolPoint.get_or_none(id=form.pointId)
        if not point:
            return fail(1, "巡查点位不存在")
        for key, value in payload.items():
            setattr(point, key, value)
        await point.save()
        return success(_build_point_out(point), msg="点位已更新")

    point = await AdminCompatPatrolPoint.create(
        area_id=area_id,
        point_code=f"POINT{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        sort_number=99,
        **{key: value for key, value in payload.items() if key != "area_id"},
    )
    return success(_build_point_out(point), msg="添加成功")


async def remove_patrol_point(form: PatrolPointRemoveForm):
    deleted = await AdminCompatPatrolPoint.filter(id=form.pointId).delete()
    if not deleted:
        return fail(1, "巡查点位不存在")
    return success(msg="删除成功")


async def list_patrol_executors():
    users = await AdminCompatUser.filter(status=0).order_by("id")
    if not users:
        return success([])
    devices = await AdminCompatPatrolUserDevice.filter(
        user_id__in=[user.id for user in users],
    ).order_by("id")
    devices_by_user: dict[int, list[dict]] = {}
    for device in devices:
        devices_by_user.setdefault(device.user_id, []).append(_build_device_out(device))

    result = []
    for user in users:
        user_devices = devices_by_user.get(user.id, [])
        employee_no = user_devices[0]["employeeNo"] if user_devices else f"GW{user.id:06d}"
        result.append(
            {
                "userId": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "employeeNo": employee_no,
                "avatar": user.avatar,
                "status": user.status,
                "devices": user_devices,
            }
        )
    return success(result)


async def get_task_create_options():
    areas = (await list_patrol_areas())["data"]
    points = (await list_patrol_points())["data"]
    executors = (await list_patrol_executors())["data"]
    return success({"areas": areas, "points": points, "executors": executors})


def _join_area_names(areas: list[AdminCompatPatrolArea]) -> str:
    if not areas:
        return ""
    return "、".join(area.area_name for area in areas[:3])


async def create_task(form: PatrolTaskCreateForm, current_user: CurrentAdminUser):
    error, payload = await _prepare_task_payload(form)
    if error:
        return error

    task = await AdminCompatPatrolTask.create(
        task_code=f"RWD{datetime.now().strftime('%Y%m%d%H%M%S')}",
        **payload,
        task_status="waiting",
        progress=0,
        exception_count=0,
        creator_id=current_user.user_id,
        creator_name=current_user.nickname,
    )
    type_names, status_names = await _task_name_maps()
    return success(_build_task_out(task, type_names, status_names), msg="保存成功")


async def _prepare_task_payload(form: PatrolTaskCreateForm):
    start_time = _parse_time(form.startTime)
    end_time = _parse_time(form.endTime)
    if not start_time:
        return fail(1, "请选择任务开始时间"), None
    if not end_time:
        return fail(1, "请选择任务结束时间"), None
    if end_time <= start_time:
        return fail(1, "任务结束时间必须晚于开始时间"), None
    if form.durationHours < 1:
        return fail(1, "预计时长不能小于1小时"), None
    actual_hours = (end_time - start_time).total_seconds() / 3600
    if form.durationHours > actual_hours:
        return fail(1, "预计时长不能超过开始到结束的时间范围"), None
    description = form.description.strip()
    if not description:
        return fail(1, "请输入任务说明"), None
    if not form.areaIds:
        return fail(1, "请选择巡查社区"), None
    if not form.pointIds:
        return fail(1, "请至少选择一个巡查点位"), None

    executor = await AdminCompatUser.get_or_none(id=form.executorId, status=0)
    if not executor:
        return fail(1, "执行人不存在或已停用"), None

    areas = await AdminCompatPatrolArea.filter(id__in=form.areaIds).order_by("sort_number", "id")
    points = await AdminCompatPatrolPoint.filter(id__in=form.pointIds).all()
    valid_point_ids = [point.id for point in points]
    if not valid_point_ids:
        return fail(1, "巡查点位不存在"), None

    return None, {
        "task_title": form.taskTitle.strip(),
        "task_type": form.taskType,
        "priority": form.priority,
        "description": description,
        "ai_focus": 1 if form.aiFocus else 0,
        "patrol_location": _join_area_names(areas),
        "area_ids": [area.id for area in areas],
        "point_ids": valid_point_ids,
        "plan_time": start_time,
        "start_time": start_time,
        "end_time": end_time,
        "duration_hours": form.durationHours,
        "repeat_rule": form.repeatRule,
        "executor_id": executor.id,
        "executor_name": executor.nickname or executor.username,
    }


async def update_task(form: PatrolTaskUpdateForm, current_user: CurrentAdminUser):
    task = await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    if not task:
        return fail(1, "巡查任务不存在")
    if task.task_status != "waiting":
        return fail(1, "当前任务状态不可编辑")

    error, payload = await _prepare_task_payload(form)
    if error:
        return error

    for key, value in payload.items():
        setattr(task, key, value)
    task.task_status = "waiting"
    await task.save()

    type_names, status_names = await _task_name_maps()
    return success(_build_task_out(task, type_names, status_names), msg="修改成功")


def _tour_key(current_user: CurrentAdminUser, tour_key: str) -> str:
    safe_key = tour_key.strip() or "task-management"
    return f"{TOUR_REDIS_PREFIX}{current_user.user_id}:{safe_key}:{datetime.now().strftime('%Y%m%d')}"


def _seconds_until_tomorrow() -> int:
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(60, int((tomorrow - now).total_seconds()))


async def get_tour_status(form: PatrolTaskTourForm, current_user: CurrentAdminUser):
    hidden = await RedisUtil.exists(_tour_key(current_user, form.tourKey))
    return success({"hidden": hidden})


async def hide_tour_today(form: PatrolTaskTourForm, current_user: CurrentAdminUser):
    await RedisUtil.set(_tour_key(current_user, form.tourKey), True, expire=_seconds_until_tomorrow())
    return success(msg="今日不再提示")
