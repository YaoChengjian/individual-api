import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from jose import JWTError, jwt
from tortoise.expressions import Q

from app.api.admin_compat.constants import MAX_UPLOAD_MB, UPLOAD_SUFFIXES
from app.api.admin_compat.helpers import build_page_payload, build_file_url, format_datetime, paginate_queryset
from app.api.admin_compat.models import (
    AdminCompatInspectionEvent,
    AdminCompatDictionary,
    AdminCompatDictionaryData,
    AdminCompatPatrolArea,
    AdminCompatPatrolPoint,
    AdminCompatPatrolTask,
    AdminCompatUser,
    AdminCompatWorkOrder,
    AdminCompatWorkOrderFlow,
)
from app.api.admin_compat.schemas import (
    AppTaskDetailForm,
    AppTaskQuery,
    AppWorkOrderPushItem,
    H5PrintedWorkOrderForm,
    H5LoginForm,
    H5TaskForm,
    H5TaskQuery,
    H5WorkOrderBatchForm,
)
from app.common.utils.jwt_utlis import ALGORITHM, SECRET_KEY, create_token, verify_password
from app.common.utils.file_utils import FileUtils
from app.common.utils.response import fail, success

TOKEN_EXPIRE_DAYS = 7
ACTIVE_TASK_STATUSES = ("waiting", "running", "finished", "overdue")
APP_WORK_ORDER_SOURCE = "App智能巡查"
PRINTED_WORK_ORDER_STATUS = "PRINTED"

TASK_STATUS_META = {
    "waiting": {"label": "待执行", "color": "#1677ff", "ripple": True},
    "running": {"label": "执行中", "color": "#18a058", "ripple": True},
    "finished": {"label": "已完成", "color": "#18a058", "ripple": False},
    "overdue": {"label": "已逾期", "color": "#f04438", "ripple": True},
}

WORK_ORDER_STATUS_META = {
    "pending_report": {"label": "待处理", "color": "#f59e0b", "ripple": True},
    "processed": {"label": "已处理", "color": "#18a058", "ripple": False},
    "processing": {"label": "处理中", "color": "#722ed1", "ripple": True},
    "finished": {"label": "已完成", "color": "#18a058", "ripple": False},
    "archived": {"label": "已归档", "color": "#0b3c8c", "ripple": False},
    "overdue": {"label": "已超时", "color": "#f04438", "ripple": True},
}

RISK_META = {
    "low": {"label": "低风险", "color": "#18a058"},
    "medium": {"label": "中风险", "color": "#f59e0b"},
    "high": {"label": "高风险", "color": "#f04438"},
    "major": {"label": "重大风险", "color": "#a8071a"},
}


def _meta(mapping: dict[str, dict[str, Any]], code: str | None) -> dict[str, Any]:
    if not code:
        return {"label": "", "color": "#8b95a5", "ripple": False}
    return mapping.get(code, {"label": code, "color": "#8b95a5", "ripple": False})


async def _dictionary_name_map(dict_code: str) -> dict[str, str]:
    dictionary = await AdminCompatDictionary.get_or_none(dict_code=dict_code)
    if not dictionary:
        return {}
    rows = await AdminCompatDictionaryData.filter(dict_id=dictionary.id).all()
    return {item.dict_data_code: item.dict_data_name for item in rows}


def _create_mobile_token(user: AdminCompatUser) -> str:
    return create_token(
        {
            "user_id": user.id,
            "username": user.username,
            "token_type": "h5_patrol",
        },
        expires_delta=timedelta(days=TOKEN_EXPIRE_DAYS),
    )


def decode_mobile_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("token_type") != "h5_patrol":
            return None
        int(payload.get("user_id"))
        return payload
    except (JWTError, TypeError, ValueError):
        return None


async def resolve_mobile_user(token: str) -> AdminCompatUser | None:
    payload = decode_mobile_token(token)
    if not payload:
        return None
    return await AdminCompatUser.get_or_none(id=int(payload["user_id"]), status=0)


async def login(form: H5LoginForm):
    username = form.username.strip()
    user = await AdminCompatUser.get_or_none(username=username)
    if not user or not verify_password(form.password, user.password):
        return fail(1001, "账号或密码错误")
    if user.status != 0:
        return fail(1005, "账号已冻结")
    token = _create_mobile_token(user)
    return success(
        {
            "accessToken": token,
            "user": {
                "userId": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "avatar": user.avatar,
                "phone": user.phone,
            },
        },
        msg="登录成功",
    )


def _task_queryset(params: H5TaskQuery | AppTaskQuery, executor_id: int | None = None):
    queryset = AdminCompatPatrolTask.all()
    if executor_id:
        queryset = queryset.filter(executor_id=executor_id)
    if getattr(params, "executorId", None):
        queryset = queryset.filter(executor_id=params.executorId)
    if getattr(params, "taskStatus", None):
        queryset = queryset.filter(task_status=params.taskStatus)
    else:
        queryset = queryset.filter(task_status__in=ACTIVE_TASK_STATUSES)
    if getattr(params, "keywords", None):
        keyword = params.keywords.strip()
        if keyword:
            queryset = queryset.filter(
                Q(task_title__contains=keyword)
                | Q(task_code__contains=keyword)
                | Q(patrol_location__contains=keyword)
            )
    return queryset


async def _task_point_out(point: AdminCompatPatrolPoint) -> dict[str, Any]:
    area = await AdminCompatPatrolArea.get_or_none(id=point.area_id)
    return {
        "pointId": point.id,
        "areaId": point.area_id,
        "areaName": area.area_name if area else "",
        "pointCode": point.point_code,
        "pointName": point.point_name,
        "pointType": point.point_type,
        "lat": point.lat,
        "lng": point.lng,
        "address": point.comments or point.point_name,
    }


def _work_order_out(order: AdminCompatWorkOrder, selected: bool = False) -> dict[str, Any]:
    status = _meta(WORK_ORDER_STATUS_META, order.status)
    risk = _meta(RISK_META, order.risk_level)
    return {
        "workOrderId": order.id,
        "workOrderCode": order.work_order_code,
        "title": order.title,
        "taskId": order.task_id,
        "eventId": order.event_id,
        "eventType": order.event_type,
        "eventTypeName": order.event_type_name or order.event_type or "智能巡查事件",
        "riskLevel": order.risk_level,
        "riskLevelName": order.risk_level_name or risk["label"],
        "riskColor": risk["color"],
        "status": order.status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "source": order.source,
        "reporterId": order.reporter_id,
        "reporterName": order.reporter_name,
        "locationName": order.location_name or order.point_name or order.area_name,
        "addressDetail": order.address_detail,
        "lat": order.lat,
        "lng": order.lng,
        "description": order.description,
        "suggestion": order.suggestion,
        "evidenceList": order.evidence_list or [],
        "reportTime": format_datetime(order.report_time),
        "printStatus": order.push_status,
        "printed": order.push_status == PRINTED_WORK_ORDER_STATUS,
        "documentContent": (order.timeline or [{}])[-1].get("documentContent") if order.timeline else "",
        "noticeNumber": (order.timeline or [{}])[-1].get("noticeNumber") if order.timeline else "",
        "fileUrl": (order.timeline or [{}])[-1].get("fileUrl") if order.timeline else "",
        "selected": selected,
    }


async def _task_out(
    task: AdminCompatPatrolTask,
    detail: bool = False,
    type_names: dict[str, str] | None = None,
    priority_names: dict[str, str] | None = None,
    repeat_rule_names: dict[str, str] | None = None,
) -> dict[str, Any]:
    status = _meta(TASK_STATUS_META, task.task_status)
    type_names = type_names if type_names is not None else await _dictionary_name_map("patrol_task_type")
    priority_names = priority_names if priority_names is not None else await _dictionary_name_map("patrol_task_priority")
    repeat_rule_names = repeat_rule_names if repeat_rule_names is not None else await _dictionary_name_map("patrol_task_repeat_rule")
    task_type_name = type_names.get(task.task_type, task.task_type)
    priority_name = priority_names.get(task.priority, task.priority)
    repeat_rule_name = repeat_rule_names.get(task.repeat_rule, task.repeat_rule)
    point_ids = task.point_ids or []
    points = await AdminCompatPatrolPoint.filter(id__in=point_ids).order_by("sort_number", "id") if point_ids else []
    work_orders = []
    if task.task_status != "waiting":
        work_orders = await AdminCompatWorkOrder.filter(
            task_id=task.id,
            source=APP_WORK_ORDER_SOURCE,
        ).order_by("-create_time").all()
    selected_ids = {order.id for order in work_orders}
    payload = {
        "taskId": task.id,
        "taskCode": task.task_code,
        "taskNo": task.task_code,
        "taskTitle": task.task_title,
        "title": task.task_title,
        "taskType": task.task_type,
        "type": task.task_type,
        "typeName": task_type_name,
        "taskTypeName": task_type_name,
        "priority": task.priority,
        "priorityName": priority_name,
        "description": task.description,
        "aiFocus": bool(task.ai_focus),
        "patrolLocation": task.patrol_location,
        "planTime": format_datetime(task.plan_time),
        "startTime": format_datetime(task.start_time or task.plan_time),
        "endTime": format_datetime(task.end_time),
        "durationHours": task.duration_hours,
        "repeatRule": task.repeat_rule,
        "repeatRuleName": repeat_rule_name,
        "executorId": task.executor_id,
        "executorName": task.executor_name,
        "assigneeId": str(task.executor_id or ""),
        "assigneeName": task.executor_name,
        "status": task.task_status,
        "taskStatus": task.task_status,
        "statusName": status["label"],
        "taskStatusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "progress": task.progress,
        "exceptionCount": task.exception_count,
        "pointCount": len(point_ids),
        "workOrderCount": len(work_orders),
        "createTime": format_datetime(task.create_time),
    }
    if detail:
        payload["points"] = [await _task_point_out(point) for point in points]
        payload["currentPoint"] = payload["points"][0] if payload["points"] else None
        payload["areaIds"] = task.area_ids or []
        payload["pointIds"] = point_ids
        payload["workOrders"] = [_work_order_out(order, order.id in selected_ids) for order in work_orders]
        payload["route"] = [
            {"lat": item["lat"], "lng": item["lng"], "name": item["pointName"]}
            for item in payload["points"]
        ]
    return payload


async def page_h5_tasks(params: H5TaskQuery, current_user: AdminCompatUser | None = None):
    type_names = await _dictionary_name_map("patrol_task_type")
    priority_names = await _dictionary_name_map("patrol_task_priority")
    repeat_rule_names = await _dictionary_name_map("patrol_task_repeat_rule")
    total, tasks = await paginate_queryset(
        _task_queryset(params, executor_id=current_user.id if current_user else None).order_by("-create_time"),
        params.page,
        params.limit,
    )
    return success(
        build_page_payload(
            [
                await _task_out(
                    task,
                    type_names=type_names,
                    priority_names=priority_names,
                    repeat_rule_names=repeat_rule_names,
                )
                for task in tasks
            ],
            total,
        )
    )


async def list_dictionary_data(dict_code: str):
    dictionary = await AdminCompatDictionary.get_or_none(dict_code=dict_code)
    if not dictionary:
        return success([])
    rows = await AdminCompatDictionaryData.filter(dict_id=dictionary.id).order_by(
        "sort_number",
        "id",
    )
    return success(
        [
            {
                "dictDataId": item.id,
                "dictId": item.dict_id,
                "dictCode": dict_code,
                "dictDataCode": item.dict_data_code,
                "dictDataName": item.dict_data_name,
                "color": item.color,
                "ripple": item.ripple,
                "sortNumber": item.sort_number,
                "comments": item.comments,
            }
            for item in rows
        ]
    )


async def app_task_page(params: AppTaskQuery):
    type_names = await _dictionary_name_map("patrol_task_type")
    priority_names = await _dictionary_name_map("patrol_task_priority")
    repeat_rule_names = await _dictionary_name_map("patrol_task_repeat_rule")
    executor_id = params.executorId
    if not executor_id and params.username:
        user = await AdminCompatUser.get_or_none(username=params.username.strip())
        executor_id = user.id if user else None
    total, tasks = await paginate_queryset(
        _task_queryset(params, executor_id=executor_id).order_by("-create_time"),
        params.page,
        params.limit,
    )
    return success(
        build_page_payload(
            [
                await _task_out(
                    task,
                    type_names=type_names,
                    priority_names=priority_names,
                    repeat_rule_names=repeat_rule_names,
                )
                for task in tasks
            ],
            total,
        )
    )


async def _get_task(form: H5TaskForm | AppTaskDetailForm):
    if form.taskId:
        return await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    if form.taskCode:
        return await AdminCompatPatrolTask.get_or_none(task_code=form.taskCode)
    return None


async def h5_task_detail(form: H5TaskForm, current_user: AdminCompatUser | None = None):
    task = await _get_task(form)
    if not task or (current_user and task.executor_id != current_user.id):
        return fail(1, "巡查任务不存在")
    return success(await _task_out(task, detail=True))


async def app_task_detail(form: AppTaskDetailForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    return success(await _task_out(task, detail=True))


async def _record_task_flow(
    task: AdminCompatPatrolTask,
    action: str,
    from_status: str | None,
    to_status: str,
    operator_id: int | None,
    operator_name: str,
    remark: str,
):
    await AdminCompatWorkOrderFlow.create(
        business_type="TASK",
        business_id=task.id,
        business_code=task.task_code,
        action=action,
        from_status=from_status,
        to_status=to_status,
        operator_id=str(operator_id) if operator_id is not None else None,
        operator_name=operator_name,
        remark=remark,
        event_type=action,
        extra={},
    )


async def start_task(form: H5TaskForm, current_user: AdminCompatUser | None = None):
    task = await _get_task(form)
    if not task or (current_user and task.executor_id != current_user.id):
        return fail(1, "巡查任务不存在")
    if task.task_status == "finished":
        return fail(1, "任务已完成，不能再次开始")
    if task.task_status == "running":
        return success(await _task_out(task, detail=True), msg="任务已在执行中")
    if task.executor_id:
        running = await AdminCompatPatrolTask.filter(
            executor_id=task.executor_id,
            task_status="running",
        ).exclude(id=task.id).first()
        if running:
            return fail(1, f"当前已有执行中的任务：{running.task_title}")
    if task.task_status != "waiting":
        return fail(1, "当前任务状态不可开始")
    old_status = task.task_status
    task.task_status = "running"
    task.progress = max(task.progress, 10)
    await task.save()
    operator_id = current_user.id if current_user else task.executor_id
    operator_name = (
        (current_user.nickname or current_user.username)
        if current_user
        else (task.executor_name or "H5演示端")
    )
    await _record_task_flow(
        task,
        "开始巡查",
        old_status,
        task.task_status,
        operator_id,
        operator_name,
        "移动端点击开始任务",
    )
    return success(await _task_out(task, detail=True), msg="任务已开始")


async def finish_task(form: H5TaskForm, current_user: AdminCompatUser | None = None):
    task = await _get_task(form)
    if not task or (current_user and task.executor_id != current_user.id):
        return fail(1, "巡查任务不存在")
    if task.task_status != "running":
        return fail(1, "只有执行中的任务可以结束")
    old_status = task.task_status
    task.task_status = "finished"
    task.progress = 100
    await task.save()
    operator_id = current_user.id if current_user else task.executor_id
    operator_name = (
        (current_user.nickname or current_user.username)
        if current_user
        else (task.executor_name or "H5演示端")
    )
    await _record_task_flow(
        task,
        "结束巡查",
        old_status,
        task.task_status,
        operator_id,
        operator_name,
        "移动端点击结束任务",
    )
    return success(await _task_out(task, detail=True), msg="任务已结束")


async def task_work_orders(form: H5TaskForm, current_user: AdminCompatUser | None = None):
    task = await _get_task(form)
    if not task or (current_user and task.executor_id != current_user.id):
        return fail(1, "巡查任务不存在")
    if task.task_status == "waiting":
        return success([])
    queryset = AdminCompatWorkOrder.filter(task_id=task.id, source=APP_WORK_ORDER_SOURCE)
    if current_user:
        queryset = queryset.filter(reporter_id=current_user.id)
    orders = await queryset.order_by("-create_time").all()
    selected_ids = {order.id for order in orders if order.task_id == task.id}
    return success([_work_order_out(order, order.id in selected_ids) for order in orders])


async def bind_task_work_orders(form: H5WorkOrderBatchForm, current_user: AdminCompatUser | None = None):
    task = await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    if not task or (current_user and task.executor_id != current_user.id):
        return fail(1, "巡查任务不存在")
    if task.task_status != "running":
        return fail(1, "请先开始巡查，再推送工单")
    order_ids = sorted(set(form.workOrderIds))
    if not order_ids:
        return fail(1, "请选择工单")
    orders = await AdminCompatWorkOrder.filter(id__in=order_ids, source=APP_WORK_ORDER_SOURCE).all()
    if len(orders) != len(order_ids):
        return fail(1, "部分工单不存在")
    for order in orders:
        order.task_id = task.id
        if current_user:
            order.reporter_id = current_user.id
            order.reporter_name = current_user.nickname or current_user.username
        elif task.executor_id:
            order.reporter_id = task.executor_id
            order.reporter_name = task.executor_name
        await order.save()
    task.exception_count = max(task.exception_count, len(orders))
    if task.task_status == "running":
        task.progress = max(task.progress, 70)
    await task.save()
    return success([_work_order_out(order, True) for order in orders], msg="工单已关联")


def _parse_report_time(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d %H:%M:%S", "%m-%d %H:%M"):
        try:
            parsed = datetime.strptime(value, fmt)
            if "%Y" not in fmt:
                parsed = parsed.replace(year=datetime.now().year)
            return parsed
        except ValueError:
            continue
    return datetime.now()


def _risk_code_from_name(name: str | None) -> str:
    text = name or ""
    if "高" in text:
        return "high"
    if "中" in text:
        return "medium"
    if "低" in text:
        return "low"
    return "medium"


def _normalize_image_base64(value: str | None) -> str | None:
    if not value:
        return None
    image_base64 = value.strip()
    return image_base64 or None


def _build_app_evidence_list(item: AppWorkOrderPushItem, image_base64: str | None) -> list[dict[str, Any]]:
    evidence_list = [dict(evidence) for evidence in (item.evidenceList or [])]
    if image_base64:
        evidence_list.insert(
            0,
            {
                "fileType": "image",
                "fileName": f"app-work-order-{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg",
                "imageBase64": image_base64,
            },
        )
    return evidence_list


async def upload_h5_print_file(file):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_UPLOAD_MB * 1024 * 1024:
        return fail(1, f"文件不能大于{MAX_UPLOAD_MB}MB")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix and suffix not in UPLOAD_SUFFIXES:
        return fail(1, "不支持该文件类型")

    save_info = await FileUtils.get_save_filepath(FileUtils.upload_dir, suffix or ".pdf")
    with open(save_info["save_path"], "wb") as target:
        shutil.copyfileobj(file.file, target)

    file_path = save_info["db_path"]
    return success(
        {
            "path": file_path,
            "filePath": file_path,
            "url": build_file_url(file_path),
            "fileName": file.filename,
            "length": file_size,
        }
    )


async def save_printed_work_orders(form: H5PrintedWorkOrderForm):
    task = await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    if not task:
        return fail(1, "巡查任务不存在")
    if not form.workOrders:
        return fail(1, "请选择需要打印的工单")

    now = datetime.now()
    saved: list[dict[str, Any]] = []
    for index, item in enumerate(form.workOrders, start=1):
        work_order_code = item.workOrderCode or f"H5-PRINT-{task.id}-{now.strftime('%Y%m%d%H%M%S')}-{index:03d}"
        order = None
        if item.workOrderId and item.workOrderId > 0:
            order = await AdminCompatWorkOrder.get_or_none(id=item.workOrderId, task_id=task.id)
        if not order:
            order = await AdminCompatWorkOrder.get_or_none(work_order_code=work_order_code)
        payload = {
            "title": item.title or "H5 打印工单",
            "event_type": "H5_PRINTED_WORK_ORDER",
            "event_type_name": item.eventTypeName or "智能巡查事件",
            "risk_level": _risk_code_from_name(item.riskLevelName),
            "risk_level_name": item.riskLevelName or "一般",
            "source": APP_WORK_ORDER_SOURCE,
            "reporter_id": task.executor_id,
            "reporter_name": item.reporterName or task.executor_name or "H5巡查员",
            "area_id": None,
            "area_name": task.patrol_location or "",
            "point_name": item.locationName,
            "event_id": None,
            "task_id": task.id,
            "point_record_id": None,
            "location_name": item.locationName,
            "address_detail": item.addressDetail,
            "status": "processed",
            "push_status": PRINTED_WORK_ORDER_STATUS,
            "report_time": _parse_report_time(item.reportTime),
            "deadline_time": now + timedelta(hours=2),
            "remaining_minutes": 120,
            "responsible_department": "待分派",
            "handler_name": "",
            "description": item.description,
            "suggestion": item.suggestion,
            "evidence_list": item.evidenceList,
            "timeline": [
                {
                    "time": now.strftime("%m-%d %H:%M"),
                    "title": "H5打印",
                    "desc": "移动端确认打印整改提醒告知书，工单已处理",
                    "status": "已处理",
                    "color": "#18a058",
                    "noticeNumber": form.noticeNumber,
                    "documentContent": form.documentContent,
                    "fileUrl": form.fileUrl,
                }
            ],
        }
        if order:
            for key, value in payload.items():
                setattr(order, key, value)
            await order.save()
        else:
            order = await AdminCompatWorkOrder.create(
                work_order_code=work_order_code,
                **payload,
            )
        saved.append(_work_order_out(order, True))

    task.exception_count = max(task.exception_count, len(saved))
    if task.task_status == "running":
        task.progress = max(task.progress, 70)
    await task.save()
    return success({"count": len(saved), "list": saved}, msg="打印工单已回传")


async def app_push_work_orders(items: list[AppWorkOrderPushItem]):
    created = []
    for index, item in enumerate(items, start=1):
        task = None
        if item.taskId:
            task = await AdminCompatPatrolTask.get_or_none(id=item.taskId)
        elif item.taskCode:
            task = await AdminCompatPatrolTask.get_or_none(task_code=item.taskCode)
        if not task:
            return fail(1, f"第{index}条工单未匹配到巡查任务")
        if task.task_status != "running":
            return fail(1, f"任务{task.task_code}未开始巡查，不能推送工单")

        reporter = None
        if item.reporterId:
            reporter = await AdminCompatUser.get_or_none(id=item.reporterId)
        elif task and task.executor_id:
            reporter = await AdminCompatUser.get_or_none(id=task.executor_id)

        point = await AdminCompatPatrolPoint.get_or_none(id=item.pointId) if item.pointId else None
        now = datetime.now()
        image_base64 = _normalize_image_base64(item.imageBase64 or item.imageUrl)
        evidence_list = _build_app_evidence_list(item, image_base64)
        event_code = f"APP-EVT-{now.strftime('%Y%m%d%H%M%S')}-{index:03d}"
        order_code = f"APP-WO-{now.strftime('%Y%m%d%H%M%S')}-{index:03d}"
        event = await AdminCompatInspectionEvent.create(
            event_code=event_code,
            event_title=item.eventTitle or item.title or "App 智能巡查事件",
            event_type=item.eventType,
            event_type_name=item.eventTypeName,
            risk_level=item.riskLevel,
            risk_level_name=item.riskLevelName,
            source=APP_WORK_ORDER_SOURCE,
            status="work_order_created",
            task_id=task.id if task else None,
            task_code=task.task_code if task else item.taskCode,
            inspector_id=reporter.id if reporter else item.reporterId,
            inspector_name=(reporter.nickname if reporter else item.reporterName) or "App巡查员",
            area_id=point.area_id if point else None,
            area_name="",
            point_id=point.id if point else item.pointId,
            point_name=(point.point_name if point else item.pointName) or item.locationName or "智能巡查点位",
            lat=item.lat if item.lat is not None else (point.lat if point else 0),
            lng=item.lng if item.lng is not None else (point.lng if point else 0),
            confidence=item.confidence or 0,
            description=item.description,
            image_url=image_base64,
            detected_time=now,
        )
        order = await AdminCompatWorkOrder.create(
            work_order_code=order_code,
            title=item.title or item.eventTitle or "App 智能巡查推送工单",
            event_type=item.eventType,
            event_type_name=item.eventTypeName,
            risk_level=item.riskLevel,
            risk_level_name=item.riskLevelName,
            source=APP_WORK_ORDER_SOURCE,
            reporter_id=reporter.id if reporter else item.reporterId,
            reporter_name=(reporter.nickname if reporter else item.reporterName) or "App巡查员",
            area_id=point.area_id if point else None,
            area_name="",
            point_name=(point.point_name if point else item.pointName),
            event_id=event.id,
            task_id=task.id if task else None,
            point_record_id=None,
            location_name=item.locationName or item.pointName,
            address_detail=item.addressDetail,
            lat=item.lat if item.lat is not None else (point.lat if point else None),
            lng=item.lng if item.lng is not None else (point.lng if point else None),
            status="pending_report",
            push_status="NOT_PUSHED",
            report_time=now,
            deadline_time=now + timedelta(hours=2),
            remaining_minutes=120,
            responsible_department="待分派",
            handler_name="",
            description=item.description,
            suggestion=item.suggestion,
            evidence_list=evidence_list,
            timeline=[
                {
                    "time": now.strftime("%m-%d %H:%M"),
                    "title": "App推送",
                    "desc": "App 智能巡查推送工单",
                    "status": "待上报",
                    "color": "#1677ff",
                }
            ],
        )
        if task:
            task.exception_count = max(task.exception_count, 1)
            if task.task_status == "running":
                task.progress = max(task.progress, 70)
            await task.save()
        created.append(_work_order_out(order, True))
    return success({"count": len(created), "list": created}, msg="工单已接收")
