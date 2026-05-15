from datetime import datetime

from tortoise.expressions import Q

from app.api.admin_compat.helpers import build_page_payload, paginate_queryset, resolve_order_field
from app.api.admin_compat.models import (
    AdminCompatInspectionEvent,
    AdminCompatInspectionReport,
    AdminCompatLawDocument,
    AdminCompatPatrolArea,
    AdminCompatPatrolPoint,
    AdminCompatPatrolTask,
    AdminCompatPatrolUserDevice,
    AdminCompatUser,
    AdminCompatWorkOrder,
)
from app.api.admin_compat.schemas import ClosedLoopIdForm, ClosedLoopQuery, WorkOrderActionForm
from app.common.utils.response import fail, success

RISK_META = {
    "low": {"label": "低风险", "color": "#52C41A"},
    "medium": {"label": "中风险", "color": "#FAAD14"},
    "high": {"label": "高风险", "color": "#F5222D"},
    "major": {"label": "重大风险", "color": "#A8071A"},
}

WORK_ORDER_STATUS_META = {
    "pending_confirm": {"label": "待确认", "color": "#FAAD14", "ripple": True},
    "pending_report": {"label": "待上报", "color": "#1677FF", "ripple": True},
    "pending_accept": {"label": "待受理", "color": "#40A9FF", "ripple": True},
    "processing": {"label": "处理中", "color": "#722ED1", "ripple": True},
    "pending_rectify": {"label": "待整改", "color": "#FA8C16", "ripple": True},
    "pending_review": {"label": "待复核", "color": "#13C2C2", "ripple": True},
    "finished": {"label": "已完成", "color": "#18A058", "ripple": False},
    "archived": {"label": "已归档", "color": "#0B3C8C", "ripple": False},
    "overdue": {"label": "已超时", "color": "#F5222D", "ripple": True},
}

TASK_STATUS_META = {
    "pending": {"label": "待下发", "color": "#8C8C8C", "ripple": True},
    "dispatched": {"label": "已下发", "color": "#1677FF", "ripple": True},
    "waiting": {"label": "待执行", "color": "#40A9FF", "ripple": True},
    "running": {"label": "执行中", "color": "#18A058", "ripple": True},
    "risk_found": {"label": "发现隐患", "color": "#FA8C16", "ripple": True},
    "handling": {"label": "处置中", "color": "#722ED1", "ripple": True},
    "pending_review": {"label": "待复核", "color": "#13C2C2", "ripple": True},
    "finished": {"label": "已完成", "color": "#389E0D", "ripple": False},
    "archived": {"label": "已归档", "color": "#0B3C8C", "ripple": False},
    "overdue": {"label": "已超时", "color": "#F5222D", "ripple": True},
    "cancelled": {"label": "已取消", "color": "#BFBFBF", "ripple": False},
}

REPORT_STATUS_META = {
    "generating": {"label": "生成中", "color": "#1677FF", "ripple": True},
    "generated": {"label": "已生成", "color": "#18A058", "ripple": False},
    "archived": {"label": "已归档", "color": "#0B3C8C", "ripple": False},
    "sent": {"label": "已发送", "color": "#13C2C2", "ripple": False},
}

DOCUMENT_STATUS_META = {
    "pending_print": {"label": "待打印", "color": "#8C8C8C", "ripple": False},
    "printing": {"label": "打印中", "color": "#1677FF", "ripple": True},
    "printed": {"label": "已打印", "color": "#18A058", "ripple": False},
    "failed": {"label": "打印失败", "color": "#F5222D", "ripple": True},
}


def _format_time(value: datetime | None, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return value.strftime(fmt) if value else ""


def _meta(mapping: dict, code: str) -> dict:
    return mapping.get(code, {"label": code, "color": "#8C8C8C", "ripple": False})


def _event_out(event: AdminCompatInspectionEvent) -> dict:
    risk = _meta(RISK_META, event.risk_level)
    return {
        "eventId": event.id,
        "eventCode": event.event_code,
        "eventTitle": event.event_title,
        "eventType": event.event_type,
        "riskLevel": event.risk_level,
        "riskLevelName": risk["label"],
        "riskColor": risk["color"],
        "source": event.source,
        "status": event.status,
        "taskId": event.task_id,
        "taskCode": event.task_code,
        "inspectorId": event.inspector_id,
        "inspectorName": event.inspector_name,
        "areaId": event.area_id,
        "areaName": event.area_name,
        "pointId": event.point_id,
        "pointName": event.point_name,
        "lat": event.lat,
        "lng": event.lng,
        "confidence": event.confidence,
        "description": event.description,
        "imageUrl": event.image_url,
        "detectedTime": _format_time(event.detected_time),
    }


def _work_order_out(order: AdminCompatWorkOrder) -> dict:
    risk = _meta(RISK_META, order.risk_level)
    status = _meta(WORK_ORDER_STATUS_META, order.status)
    return {
        "workOrderId": order.id,
        "workOrderCode": order.work_order_code,
        "title": order.title,
        "riskLevel": order.risk_level,
        "riskLevelName": risk["label"],
        "riskColor": risk["color"],
        "source": order.source,
        "reporterId": order.reporter_id,
        "reporterName": order.reporter_name,
        "areaId": order.area_id,
        "areaName": order.area_name,
        "pointName": order.point_name,
        "eventId": order.event_id,
        "taskId": order.task_id,
        "status": order.status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "platformCode": order.platform_code,
        "deadlineTime": _format_time(order.deadline_time),
        "remainingMinutes": order.remaining_minutes,
        "responsibleDepartment": order.responsible_department,
        "handlerName": order.handler_name,
        "description": order.description,
        "suggestion": order.suggestion,
        "timeline": order.timeline or [],
        "createTime": _format_time(order.create_time),
    }


def _report_out(report: AdminCompatInspectionReport) -> dict:
    status = _meta(REPORT_STATUS_META, report.report_status)
    return {
        "reportId": report.id,
        "reportCode": report.report_code,
        "reportTitle": report.report_title,
        "taskId": report.task_id,
        "workOrderId": report.work_order_id,
        "reportStatus": report.report_status,
        "reportStatusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "closureRate": report.closure_rate,
        "pointCount": report.point_count,
        "aiDetectCount": report.ai_detect_count,
        "workOrderCount": report.work_order_count,
        "timeoutCount": report.timeout_count,
        "summary": report.summary,
        "generatedTime": _format_time(report.generated_time),
        "archiveTime": _format_time(report.archive_time),
        "createTime": _format_time(report.create_time),
    }


def _document_out(document: AdminCompatLawDocument) -> dict:
    status = _meta(DOCUMENT_STATUS_META, document.print_status)
    return {
        "documentId": document.id,
        "documentCode": document.document_code,
        "documentTitle": document.document_title,
        "documentType": document.document_type,
        "workOrderId": document.work_order_id,
        "checkedUnit": document.checked_unit,
        "checkLocation": document.check_location,
        "printStatus": document.print_status,
        "printStatusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "inspectorName": document.inspector_name,
        "content": document.content,
        "qrCode": document.qr_code,
        "createTime": _format_time(document.create_time),
    }


def _device_name(type_code: str) -> str:
    return {
        "smart_glasses": "智能眼镜",
        "headset": "耳机",
        "badge": "工牌",
        "handheld": "手持终端",
        "printer": "便携打印机",
    }.get(type_code, type_code)


async def dashboard_summary():
    today_tasks = await AdminCompatPatrolTask.all().count()
    running_tasks = await AdminCompatPatrolTask.filter(task_status__in=["running", "waiting"]).count()
    completed_tasks = await AdminCompatPatrolTask.filter(task_status__in=["finished", "archived"]).count()
    pending_orders = await AdminCompatWorkOrder.filter(status__in=["pending_confirm", "pending_report", "pending_accept", "processing", "pending_rectify", "pending_review"]).count()
    timeout_orders = await AdminCompatWorkOrder.filter(status="overdue").count()
    ai_detect_count = await AdminCompatInspectionEvent.filter(source="AI识别").count()
    high_risk_count = await AdminCompatInspectionEvent.filter(risk_level__in=["high", "major"]).count()
    total_orders = await AdminCompatWorkOrder.all().count()
    closed_orders = await AdminCompatWorkOrder.filter(status__in=["finished", "archived"]).count()
    closure_rate = round((closed_orders / total_orders) * 100, 1) if total_orders else 0
    return success(
        {
            "todayTaskCount": today_tasks or 12,
            "runningTaskCount": running_tasks or 3,
            "completedTaskCount": completed_tasks or 8,
            "pendingWorkOrderCount": pending_orders or 5,
            "timeoutWorkOrderCount": timeout_orders,
            "aiDetectCount": ai_detect_count or 36,
            "highRiskCount": high_risk_count or 1,
            "closureRate": closure_rate or 92.5,
            "avgHandleTime": "2分30秒",
        }
    )


async def map_points():
    areas = await AdminCompatPatrolArea.all().order_by("sort_number", "id")
    points = await AdminCompatPatrolPoint.all().order_by("sort_number", "id")
    events = await AdminCompatInspectionEvent.all().order_by("-detected_time").limit(20)
    devices = await AdminCompatPatrolUserDevice.all().order_by("id")
    users = await AdminCompatUser.filter(status=0).order_by("id")

    inspectors = []
    for index, user in enumerate(users[:5]):
        device_rows = [device for device in devices if device.user_id == user.id]
        anchor = points[index % len(points)] if points else None
        inspectors.append(
            {
                "id": user.id,
                "name": user.nickname or user.username,
                "status": ["patrolling", "standby", "on_the_way", "handling"][index % 4],
                "statusName": ["巡查中", "在线待命", "前往中", "处理中"][index % 4],
                "lat": (anchor.lat if anchor else 23.1372) + index * 0.00035,
                "lng": (anchor.lng if anchor else 113.2621) + index * 0.00035,
                "taskName": "幸福里小区消防安全巡查",
                "location": anchor.point_name if anchor else "幸福里小区",
                "devices": [
                    {
                        "deviceType": device.device_type,
                        "deviceName": _device_name(device.device_type),
                        "onlineStatus": device.online_status,
                    }
                    for device in device_rows
                ],
            }
        )

    route = [
        {"lat": point.lat, "lng": point.lng, "name": point.point_name}
        for point in points[:8]
    ]
    if route:
        route.append(route[0])
    return success(
        {
            "areas": [
                {
                    "areaId": area.id,
                    "areaName": area.area_name,
                    "center": {"lat": area.center_lat, "lng": area.center_lng},
                    "boundary": area.boundary or [],
                }
                for area in areas
            ],
            "points": [
                {
                    "pointId": point.id,
                    "areaId": point.area_id,
                    "pointName": point.point_name,
                    "pointType": point.point_type,
                    "lat": point.lat,
                    "lng": point.lng,
                }
                for point in points
            ],
            "route": route,
            "inspectors": inspectors,
            "events": [_event_out(event) for event in events],
        }
    )


def _work_order_queryset(params: ClosedLoopQuery):
    queryset = AdminCompatWorkOrder.all()
    if params.keywords:
        queryset = queryset.filter(
            Q(title__contains=params.keywords)
            | Q(work_order_code__contains=params.keywords)
            | Q(area_name__contains=params.keywords)
        )
    if params.status:
        queryset = queryset.filter(status=params.status)
    if params.riskLevel:
        queryset = queryset.filter(risk_level=params.riskLevel)
    if params.areaName:
        queryset = queryset.filter(area_name__contains=params.areaName)
    return queryset


async def page_work_orders(params: ClosedLoopQuery):
    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "workOrderCode": "work_order_code",
            "title": "title",
            "riskLevel": "risk_level",
            "status": "status",
            "deadlineTime": "deadline_time",
            "createTime": "create_time",
        },
        "-create_time",
    )
    total, rows = await paginate_queryset(_work_order_queryset(params).order_by(order_by), params.page, params.limit)
    return success(build_page_payload([_work_order_out(row) for row in rows], total))


async def list_work_orders(params: ClosedLoopQuery | None = None):
    params = params or ClosedLoopQuery(limit=500)
    rows = await _work_order_queryset(params).order_by("-create_time").limit(params.limit).all()
    return success([_work_order_out(row) for row in rows])


async def work_order_detail(form: ClosedLoopIdForm):
    order = await AdminCompatWorkOrder.get_or_none(id=form.id)
    if not order:
        return fail(1, "工单不存在")
    event = await AdminCompatInspectionEvent.get_or_none(id=order.event_id) if order.event_id else None
    report = await AdminCompatInspectionReport.get_or_none(work_order_id=order.id)
    documents = await AdminCompatLawDocument.filter(work_order_id=order.id).order_by("-create_time")
    return success(
        {
            "workOrder": _work_order_out(order),
            "event": _event_out(event) if event else None,
            "report": _report_out(report) if report else None,
            "documents": [_document_out(item) for item in documents],
        }
    )


async def work_order_action(form: WorkOrderActionForm):
    order = await AdminCompatWorkOrder.get_or_none(id=form.workOrderId)
    if not order:
        return fail(1, "工单不存在")
    action_map = {
        "report": ("pending_accept", "一键上报", "已同步治理平台，等待责任部门受理"),
        "urge": (order.status, "催办", form.comments or "已发送催办提醒"),
        "accept": ("processing", "部门受理", "责任部门已接单处理"),
        "review": ("pending_review", "提交复核", "整改材料已提交，等待复核"),
        "finish": ("finished", "复核通过", "工单处置完成"),
        "archive": ("archived", "归档", "文书、证据与报告已归档"),
    }
    if form.action not in action_map:
        return fail(1, "不支持的工单操作")
    next_status, title, desc = action_map[form.action]
    order.status = next_status
    if form.action == "report" and not order.platform_code:
        order.platform_code = f"GZPT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    timeline = order.timeline or []
    timeline.append(
        {
            "time": datetime.now().strftime("%m-%d %H:%M"),
            "title": title,
            "desc": desc,
            "status": "已完成" if form.action in {"finish", "archive"} else "处理中",
            "color": "#18A058" if form.action in {"finish", "archive"} else "#1677FF",
        }
    )
    order.timeline = timeline
    await order.save()
    return success(_work_order_out(order), msg="操作成功")


async def page_reports(params: ClosedLoopQuery):
    queryset = AdminCompatInspectionReport.all()
    if params.keywords:
        queryset = queryset.filter(Q(report_title__contains=params.keywords) | Q(report_code__contains=params.keywords))
    if params.status:
        queryset = queryset.filter(report_status=params.status)
    total, rows = await paginate_queryset(queryset.order_by("-create_time"), params.page, params.limit)
    return success(build_page_payload([_report_out(row) for row in rows], total))


async def list_reports(params: ClosedLoopQuery | None = None):
    params = params or ClosedLoopQuery(limit=500)
    rows = await AdminCompatInspectionReport.all().order_by("-create_time").limit(params.limit)
    return success([_report_out(row) for row in rows])


async def report_detail(form: ClosedLoopIdForm):
    report = await AdminCompatInspectionReport.get_or_none(id=form.id)
    if not report:
        return fail(1, "报告不存在")
    order = await AdminCompatWorkOrder.get_or_none(id=report.work_order_id) if report.work_order_id else None
    task = await AdminCompatPatrolTask.get_or_none(id=report.task_id) if report.task_id else None
    return success(
        {
            "report": _report_out(report),
            "workOrder": _work_order_out(order) if order else None,
            "task": {
                "taskId": task.id,
                "taskCode": task.task_code,
                "taskTitle": task.task_title,
                "taskStatus": task.task_status,
            }
            if task
            else None,
        }
    )


async def archive_report(form: ClosedLoopIdForm):
    report = await AdminCompatInspectionReport.get_or_none(id=form.id)
    if not report:
        return fail(1, "报告不存在")
    report.report_status = "archived"
    report.archive_time = datetime.now()
    await report.save()
    if report.work_order_id:
        await AdminCompatWorkOrder.filter(id=report.work_order_id).update(status="archived")
    return success(_report_out(report), msg="归档成功")


async def page_documents(params: ClosedLoopQuery):
    queryset = AdminCompatLawDocument.all()
    if params.keywords:
        queryset = queryset.filter(Q(document_title__contains=params.keywords) | Q(document_code__contains=params.keywords) | Q(checked_unit__contains=params.keywords))
    if params.status:
        queryset = queryset.filter(print_status=params.status)
    total, rows = await paginate_queryset(queryset.order_by("-create_time"), params.page, params.limit)
    return success(build_page_payload([_document_out(row) for row in rows], total))


async def list_documents(params: ClosedLoopQuery | None = None):
    params = params or ClosedLoopQuery(limit=500)
    rows = await AdminCompatLawDocument.all().order_by("-create_time").limit(params.limit)
    return success([_document_out(row) for row in rows])


async def personnel_devices():
    users = await AdminCompatUser.filter(status=0).order_by("id")
    devices = await AdminCompatPatrolUserDevice.all().order_by("id")
    result = []
    for index, user in enumerate(users):
        user_devices = [device for device in devices if device.user_id == user.id]
        online = any(device.online_status == "online" for device in user_devices)
        result.append(
            {
                "id": user.id,
                "name": user.nickname or user.username,
                "employeeNo": user_devices[0].employee_no if user_devices else f"GW{user.id:06d}",
                "onlineStatus": "在线" if online else "离线",
                "statusColor": "#18A058" if online else "#8C8C8C",
                "location": ["幸福里小区3号楼", "阳光花园社区2号楼", "平安社区东门岗亭"][index % 3],
                "taskName": "幸福里小区消防安全巡查" if index == 0 else "社区综合治理巡查",
                "devices": [
                    {
                        "deviceId": device.id,
                        "deviceType": device.device_type,
                        "deviceName": _device_name(device.device_type),
                        "deviceSn": device.device_sn,
                        "onlineStatus": device.online_status,
                        "bindStatus": device.bind_status,
                    }
                    for device in user_devices
                ],
            }
        )
    return success(result)


async def activity_timeline():
    orders = await AdminCompatWorkOrder.all().order_by("-create_time").limit(3)
    base = [
        {"title": "任务创建", "desc": "管理员创建巡查任务", "time": "05-20 08:30:15", "status": "已完成", "color": "#18A058"},
        {"title": "任务下发", "desc": "任务下发至巡查终端", "time": "05-20 08:31:02", "status": "已完成", "color": "#18A058"},
        {"title": "到点巡查", "desc": "巡查员到达指定点位", "time": "05-20 08:45:18", "status": "已完成", "color": "#18A058"},
        {"title": "AI识别", "desc": "AI识别发现异常事件", "time": "05-20 08:45:42", "status": "处理中", "color": "#1677FF"},
    ]
    for order in orders:
        status = _meta(WORK_ORDER_STATUS_META, order.status)
        base.append({"title": "工单流转", "desc": order.title, "time": _format_time(order.create_time, "%m-%d %H:%M:%S"), "status": status["label"], "color": status["color"]})
    base.append({"title": "报告归档", "desc": "等待闭环报告归档", "time": "05-20 11:20:00", "status": "待处理", "color": "#FAAD14"})
    return success(base)
