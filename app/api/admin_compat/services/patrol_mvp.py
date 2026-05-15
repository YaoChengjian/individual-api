from datetime import datetime, timedelta
from typing import Any

from tortoise.expressions import Q

from app.api.admin_compat.helpers import (
    build_page_payload,
    format_datetime,
    paginate_queryset,
    resolve_order_field,
)
from app.api.admin_compat.models import (
    AdminCompatEvidenceFile,
    AdminCompatInspectionEvent,
    AdminCompatInspectionReport,
    AdminCompatLawDocument,
    AdminCompatOrganization,
    AdminCompatPatrolArea,
    AdminCompatPatrolPoint,
    AdminCompatPatrolTask,
    AdminCompatPatrolTaskPoint,
    AdminCompatPatrolUserDevice,
    AdminCompatPrintRecord,
    AdminCompatPushRecord,
    AdminCompatUser,
    AdminCompatWorkOrder,
    AdminCompatWorkOrderFlow,
)
from app.api.admin_compat.schemas import (
    PatrolMvpCallbackForm,
    PatrolMvpDetectForm,
    PatrolMvpDocumentForm,
    PatrolMvpEvidenceForm,
    PatrolMvpQuery,
    PatrolMvpTaskCreateForm,
    PatrolMvpTaskForm,
    PatrolMvpTaskPointForm,
    PatrolMvpWorkOrderDraftForm,
    PatrolMvpWorkOrderForm,
)
from app.common.utils.jwt_utlis import get_password
from app.common.utils.response import fail, success

TASK_TYPE_META = {
    "FIRE_SAFETY": {"label": "消防安全", "color": "#1677FF"},
    "ENVIRONMENT": {"label": "市容环境", "color": "#16A34A"},
    "GOVERNANCE": {"label": "综合治理", "color": "#F59E0B"},
    "fire_safety": {"label": "消防安全", "color": "#1677FF"},
    "environment": {"label": "环境巡查", "color": "#16A34A"},
    "governance": {"label": "综合治理", "color": "#F59E0B"},
}

TASK_STATUS_META = {
    "DRAFT": {"label": "草稿", "color": "#94A3B8", "ripple": False},
    "DISPATCHED": {"label": "已下发", "color": "#1677FF", "ripple": True},
    "RECEIVED": {"label": "已接收", "color": "#0EA5E9", "ripple": True},
    "GOING": {"label": "前往中", "color": "#6366F1", "ripple": True},
    "INSPECTING": {"label": "巡查中", "color": "#16A34A", "ripple": True},
    "WORK_ORDER_SUBMITTED": {"label": "工单已上传", "color": "#F59E0B", "ripple": True},
    "PUSHED": {"label": "已推送第三方", "color": "#7C3AED", "ripple": True},
    "DOCUMENT_PRINTED": {"label": "文书已打印", "color": "#0891B2", "ripple": False},
    "CLOSED": {"label": "已闭环", "color": "#18A058", "ripple": False},
    "CANCELLED": {"label": "已取消", "color": "#94A3B8", "ripple": False},
    "pending": {"label": "待下发", "color": "#1677FF", "ripple": True},
    "waiting": {"label": "待执行", "color": "#7C3AED", "ripple": True},
    "running": {"label": "执行中", "color": "#16A34A", "ripple": True},
    "finished": {"label": "已完成", "color": "#18A058", "ripple": False},
    "overdue": {"label": "已逾期", "color": "#F04438", "ripple": True},
}

POINT_STATUS_META = {
    "PENDING": {"label": "待巡查", "color": "#94A3B8", "ripple": False},
    "GOING": {"label": "前往中", "color": "#6366F1", "ripple": True},
    "ARRIVED": {"label": "已到达", "color": "#1677FF", "ripple": True},
    "INSPECTING": {"label": "巡查中", "color": "#16A34A", "ripple": True},
    "RISK_DETECTED": {"label": "已发现隐患", "color": "#F59E0B", "ripple": True},
    "EVIDENCE_CAPTURED": {"label": "已取证", "color": "#0EA5E9", "ripple": True},
    "WORK_ORDER_SUBMITTED": {"label": "工单已提交", "color": "#7C3AED", "ripple": True},
    "CLOSED": {"label": "已闭环", "color": "#18A058", "ripple": False},
    "SKIPPED": {"label": "已跳过", "color": "#94A3B8", "ripple": False},
}

WORK_ORDER_STATUS_META = {
    "DRAFT": {"label": "草稿", "color": "#94A3B8", "ripple": False},
    "PENDING_SUPPLEMENT": {"label": "待补充", "color": "#F59E0B", "ripple": True},
    "LOCAL_SAVED": {"label": "本地暂存", "color": "#94A3B8", "ripple": False},
    "SUBMITTED": {"label": "已提交", "color": "#1677FF", "ripple": True},
    "PUSHING": {"label": "推送中", "color": "#6366F1", "ripple": True},
    "PUSHED": {"label": "已推送", "color": "#7C3AED", "ripple": True},
    "PUSH_FAILED": {"label": "推送失败", "color": "#F04438", "ripple": True},
    "PENDING_ACCEPT": {"label": "第三方待受理", "color": "#0EA5E9", "ripple": True},
    "PROCESSING": {"label": "处理中", "color": "#16A34A", "ripple": True},
    "DOCUMENT_GENERATED": {"label": "文书已生成", "color": "#0891B2", "ripple": False},
    "DOCUMENT_PRINTED": {"label": "文书已打印", "color": "#0F766E", "ripple": False},
    "CLOSED": {"label": "已闭环", "color": "#18A058", "ripple": False},
    "CANCELLED": {"label": "已取消", "color": "#94A3B8", "ripple": False},
    "pending_report": {"label": "待上报", "color": "#1677FF", "ripple": True},
    "processing": {"label": "处理中", "color": "#16A34A", "ripple": True},
    "finished": {"label": "已完成", "color": "#18A058", "ripple": False},
    "archived": {"label": "已归档", "color": "#0B3C8C", "ripple": False},
}

PUSH_STATUS_META = {
    "NOT_PUSHED": {"label": "未推送", "color": "#94A3B8", "ripple": False},
    "PUSHING": {"label": "推送中", "color": "#6366F1", "ripple": True},
    "PUSH_SUCCESS": {"label": "推送成功", "color": "#18A058", "ripple": False},
    "PUSH_FAILED": {"label": "推送失败", "color": "#F04438", "ripple": True},
}

DOCUMENT_STATUS_META = {
    "NOT_GENERATED": {"label": "未生成", "color": "#94A3B8", "ripple": False},
    "GENERATED": {"label": "已生成", "color": "#1677FF", "ripple": False},
    "PRINTING": {"label": "打印中", "color": "#6366F1", "ripple": True},
    "PRINTED": {"label": "已打印", "color": "#18A058", "ripple": False},
    "VOIDED": {"label": "已作废", "color": "#94A3B8", "ripple": False},
    "pending_print": {"label": "待打印", "color": "#94A3B8", "ripple": False},
    "printed": {"label": "已打印", "color": "#18A058", "ripple": False},
}

RISK_META = {
    "LOW": {"label": "低风险", "color": "#16A34A"},
    "MEDIUM": {"label": "中风险", "color": "#F59E0B"},
    "HIGH": {"label": "高风险", "color": "#F04438"},
    "low": {"label": "低风险", "color": "#16A34A"},
    "medium": {"label": "中风险", "color": "#F59E0B"},
    "high": {"label": "高风险", "color": "#F04438"},
}

DEMO_IMAGE_URL = "/mock/images/fire-passage-blocked.svg"
DEMO_MARKED_IMAGE_URL = "/mock/images/fire-passage-blocked-marked.svg"


def _now() -> datetime:
    return datetime.now()


def _fmt(value: datetime | None) -> str:
    return format_datetime(value)


def _meta(mapping: dict[str, dict[str, Any]], code: str | None) -> dict[str, Any]:
    if not code:
        return {"label": "", "color": "#94A3B8", "ripple": False}
    return mapping.get(code, {"label": code, "color": "#94A3B8", "ripple": False})


def _parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _operator_id(value: int | str | None) -> str | None:
    return None if value is None else str(value)


def _event_type_name(event_type: str) -> str:
    return {
        "FIRE_PASSAGE_BLOCKED": "消防通道堵塞",
        "GARBAGE_OVERFLOW": "垃圾满溢",
    }.get(event_type, event_type)


def _risk_name(risk_level: str) -> str:
    return _meta(RISK_META, risk_level)["label"]


async def _next_sequence(prefix: str, model, field_name: str) -> int:
    today = _now().strftime("%Y%m%d")
    startswith = f"{prefix}{today}"
    count = await model.filter(**{f"{field_name}__startswith": startswith}).count()
    return count + 1


async def _next_task_code() -> str:
    seq = await _next_sequence("RW", AdminCompatPatrolTask, "task_code")
    return f"RW{_now().strftime('%Y%m%d')}{seq:04d}"


async def _next_work_order_code(event_type: str) -> str:
    prefix = "XFS" if event_type == "FIRE_PASSAGE_BLOCKED" else "HJS"
    seq = await _next_sequence(prefix, AdminCompatWorkOrder, "work_order_code")
    return f"{prefix}{_now().strftime('%Y%m%d')}{seq:04d}"


async def _next_evidence_no() -> str:
    prefix = f"XS{_now().strftime('%Y%m%d')}-"
    count = await AdminCompatEvidenceFile.filter(evidence_no__startswith=prefix).count()
    return f"{prefix}{count + 1:03d}"


async def _next_document_no() -> str:
    seq = await AdminCompatLawDocument.filter(
        document_code__startswith=f"整责字[{_now().year}]第{_now().strftime('%m%d')}"
    ).count()
    return f"整责字[{_now().year}]第{_now().strftime('%m%d')}{seq + 1:03d}号"


async def _ensure_demo_user() -> AdminCompatUser:
    org = await AdminCompatOrganization.first()
    user = await AdminCompatUser.get_or_none(username="patrol_001")
    if not user:
        user = await AdminCompatUser.create(
            username="patrol_001",
            password=get_password("123456"),
            nickname="哼哼",
            sex="1",
            phone="13800000001",
            email="patrol_001@example.com",
            introduction="默认演示巡查员",
            organization_id=org.id if org else None,
            status=0,
            tell_pre="0752",
            tell="13800000001",
        )
    else:
        user.nickname = "哼哼"
        user.phone = user.phone or "13800000001"
        user.status = 0
        await user.save()

    device_specs = [
        ("smart_glasses", "智能眼镜", "GY-MOCK-0001"),
        ("headset", "骨传导耳机", "EJ-MOCK-0001"),
        ("badge", "电子工牌", "GP-MOCK-0001"),
        ("handheld", "手持终端", "SC-MOCK-0001"),
        ("printer", "便携打印机", "DY-MOCK-0001"),
    ]
    for device_type, device_name, device_sn in device_specs:
        device = await AdminCompatPatrolUserDevice.get_or_none(
            user_id=user.id,
            device_type=device_type,
        )
        payload = {
            "user_id": user.id,
            "user_name": "哼哼",
            "employee_no": "GW20260512001",
            "device_type": device_type,
            "device_name": device_name,
            "device_sn": device_sn,
            "online_status": "online",
            "bind_status": "bound",
        }
        if not device:
            await AdminCompatPatrolUserDevice.create(**payload)
        else:
            for key, value in payload.items():
                setattr(device, key, value)
            await device.save()
    return user


async def _demo_point() -> AdminCompatPatrolPoint | None:
    point = await AdminCompatPatrolPoint.get_or_none(point_code="XFL-3")
    if point:
        return point
    area = await AdminCompatPatrolArea.first()
    if not area:
        area = await AdminCompatPatrolArea.create(
            area_code="AREA_XFL",
            area_name="幸福里小区",
            center_lat=31.230416,
            center_lng=121.473701,
            boundary=[
                {"lat": 31.2310, "lng": 121.4728},
                {"lat": 31.2312, "lng": 121.4742},
                {"lat": 31.2301, "lng": 121.4746},
                {"lat": 31.2295, "lng": 121.4732},
            ],
            sort_number=10,
            comments="默认演示社区",
        )
    return await AdminCompatPatrolPoint.create(
        area_id=area.id,
        point_code="XFL-3",
        point_name="幸福里小区3号楼",
        point_type="FIRE_SAFETY",
        lat=area.center_lat,
        lng=area.center_lng,
        sort_number=10,
        comments="消防安全重点关注场所",
    )


def _pre_check_info(point_name: str) -> dict[str, Any]:
    return {
        "placeLevel": "消防安全重点关注场所",
        "recentEventText": "近30天内无相关上报事件",
        "householdCount": 60,
        "elderlyLivingAloneCount": 3,
        "inspectionFocus": "楼道杂物与消防设施",
        "message": (
            f"哼哼，已经到达{point_name}。该点位为消防安全重点关注场所。"
            "近30天内无相关上报事件。楼内共有住户60户，其中独居老人3户。"
            "本次重点检查楼道杂物与消防设施。现在开始巡查任务吗？"
        ),
    }


async def _record_flow(
    *,
    business_type: str,
    business_id: int,
    business_code: str | None,
    action: str,
    from_status: str | None,
    to_status: str | None,
    operator_id: str | int | None,
    operator_name: str,
    remark: str | None = None,
    event_type: str | None = None,
    extra: dict[str, Any] | None = None,
):
    await AdminCompatWorkOrderFlow.create(
        business_type=business_type,
        business_id=business_id,
        business_code=business_code,
        action=action,
        from_status=from_status,
        to_status=to_status,
        operator_id=_operator_id(operator_id),
        operator_name=operator_name,
        remark=remark,
        event_type=event_type,
        extra=extra or {},
    )


async def _set_task_status(
    task: AdminCompatPatrolTask,
    status: str,
    *,
    action: str,
    operator_id: str | int | None,
    operator_name: str,
    remark: str | None = None,
    event_type: str | None = None,
):
    from_status = task.task_status
    task.task_status = status
    await task.save()
    await _record_flow(
        business_type="TASK",
        business_id=task.id,
        business_code=task.task_code,
        action=action,
        from_status=from_status,
        to_status=status,
        operator_id=operator_id,
        operator_name=operator_name,
        remark=remark,
        event_type=event_type,
    )


async def _set_point_status(
    point_record: AdminCompatPatrolTaskPoint,
    status: str,
    *,
    action: str,
    operator_id: str | int | None,
    operator_name: str,
    remark: str | None = None,
    event_type: str | None = None,
):
    from_status = point_record.status
    point_record.status = status
    if status == "ARRIVED":
        point_record.arrived_time = _now()
    elif status == "INSPECTING":
        point_record.started_time = _now()
    elif status == "CLOSED":
        point_record.closed_time = _now()
    await point_record.save()
    await _record_flow(
        business_type="POINT",
        business_id=point_record.id,
        business_code=point_record.point_code,
        action=action,
        from_status=from_status,
        to_status=status,
        operator_id=operator_id,
        operator_name=operator_name,
        remark=remark,
        event_type=event_type,
        extra={"taskId": point_record.task_id},
    )


async def _get_task(form: PatrolMvpTaskForm) -> AdminCompatPatrolTask | None:
    if form.taskId:
        return await AdminCompatPatrolTask.get_or_none(id=form.taskId)
    if form.taskNo:
        return await AdminCompatPatrolTask.get_or_none(task_code=form.taskNo)
    return await _ensure_demo_task()


async def _get_point_record(
    task: AdminCompatPatrolTask,
    form: PatrolMvpTaskPointForm,
) -> AdminCompatPatrolTaskPoint | None:
    if form.pointRecordId:
        return await AdminCompatPatrolTaskPoint.get_or_none(
            id=form.pointRecordId,
            task_id=task.id,
        )
    if form.pointId:
        return await AdminCompatPatrolTaskPoint.get_or_none(
            task_id=task.id,
            point_id=form.pointId,
        )
    return await AdminCompatPatrolTaskPoint.filter(task_id=task.id).order_by("id").first()


async def _ensure_task_points(task: AdminCompatPatrolTask, point_ids: list[int] | None = None):
    rows = await AdminCompatPatrolTaskPoint.filter(task_id=task.id).all()
    if rows:
        return rows

    if point_ids:
        points = await AdminCompatPatrolPoint.filter(id__in=point_ids).order_by("sort_number", "id")
    else:
        demo_point = await _demo_point()
        points = [demo_point] if demo_point else []

    result = []
    for point in points:
        if not point:
            continue
        record = await AdminCompatPatrolTaskPoint.create(
            task_id=task.id,
            point_id=point.id,
            point_code=point.point_code,
            point_name=point.point_name,
            address=point.point_name,
            lat=point.lat,
            lng=point.lng,
            status="PENDING",
            pre_check=_pre_check_info(point.point_name),
        )
        result.append(record)
    if result:
        task.point_ids = [item.point_id for item in result]
        await task.save()
    return result


async def _ensure_demo_task() -> AdminCompatPatrolTask:
    user = await _ensure_demo_user()
    point = await _demo_point()
    task = await AdminCompatPatrolTask.get_or_none(task_code="RW202605120001")
    if not task:
        task = await AdminCompatPatrolTask.create(
            task_code="RW202605120001",
            task_title="幸福里小区消防安全巡查任务",
            task_type="FIRE_SAFETY",
            priority="high",
            description="演示任务：消防通道堵塞闭环处置",
            ai_focus=1,
            patrol_location="幸福里小区",
            area_ids=[],
            point_ids=[point.id] if point else [],
            plan_time=_now(),
            start_time=_now(),
            end_time=_now() + timedelta(hours=1, minutes=30),
            duration_hours=1,
            repeat_rule="none",
            executor_id=user.id,
            executor_name="哼哼",
            task_status="DISPATCHED",
            progress=0,
            exception_count=0,
            creator_id=1,
            creator_name="指挥中心操作员",
        )
        await _record_flow(
            business_type="TASK",
            business_id=task.id,
            business_code=task.task_code,
            action="任务创建",
            from_status=None,
            to_status="DRAFT",
            operator_id="admin_001",
            operator_name="指挥中心操作员",
            remark="系统创建默认演示任务",
            event_type="TASK_CREATED",
        )
        await _record_flow(
            business_type="TASK",
            business_id=task.id,
            business_code=task.task_code,
            action="任务下发",
            from_status="DRAFT",
            to_status="DISPATCHED",
            operator_id="admin_001",
            operator_name="指挥中心操作员",
            remark="任务下发至 H5 巡查端",
            event_type="TASK_DISPATCHED",
        )
    else:
        task.executor_id = user.id
        task.executor_name = "哼哼"
        await task.save()
    await _ensure_task_points(task, [point.id] if point else None)
    return task


def _point_out(point: AdminCompatPatrolTaskPoint) -> dict[str, Any]:
    status = _meta(POINT_STATUS_META, point.status)
    return {
        "pointRecordId": point.id,
        "pointId": point.point_id,
        "pointCode": point.point_code,
        "pointName": point.point_name,
        "address": point.address,
        "longitude": point.lng,
        "latitude": point.lat,
        "status": point.status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "arrivedAt": _fmt(point.arrived_time),
        "startedAt": _fmt(point.started_time),
        "closedAt": _fmt(point.closed_time),
        "preCheckInfo": point.pre_check or {},
    }


async def _task_out(task: AdminCompatPatrolTask, detail: bool = False) -> dict[str, Any]:
    await _ensure_task_points(task)
    points = await AdminCompatPatrolTaskPoint.filter(task_id=task.id).order_by("id")
    status = _meta(TASK_STATUS_META, task.task_status)
    task_type = _meta(TASK_TYPE_META, task.task_type)
    work_order = await AdminCompatWorkOrder.get_or_none(task_id=task.id)
    document = None
    if work_order:
        document = await AdminCompatLawDocument.get_or_none(work_order_id=work_order.id)
    payload = {
        "taskId": task.id,
        "taskNo": task.task_code,
        "taskCode": task.task_code,
        "title": task.task_title,
        "taskTitle": task.task_title,
        "type": task.task_type,
        "typeName": task_type["label"],
        "typeColor": task_type["color"],
        "taskType": task.task_type,
        "taskTypeName": task_type["label"],
        "patrolLocation": task.patrol_location,
        "assigneeId": "patrol_001" if task.executor_name == "哼哼" else str(task.executor_id or ""),
        "assigneeName": task.executor_name,
        "executorId": task.executor_id,
        "executorName": task.executor_name,
        "pointCount": len(points),
        "startTime": _fmt(task.start_time or task.plan_time),
        "endTime": _fmt(task.end_time),
        "planTime": _fmt(task.plan_time),
        "status": task.task_status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "taskStatus": task.task_status,
        "taskStatusName": status["label"],
        "progress": task.progress,
        "exceptionCount": task.exception_count,
        "creatorName": task.creator_name,
        "createTime": _fmt(task.create_time),
        "remark": task.description,
        "createdAt": _fmt(task.create_time),
        "updatedAt": _fmt(task.update_time),
        "currentPoint": _point_out(points[0]) if points else None,
        "points": [_point_out(item) for item in points],
        "workOrderId": work_order.id if work_order else None,
        "documentId": document.id if document else None,
    }
    if detail:
        payload["flowRecords"] = await _flow_records("TASK", task.id)
        payload["workOrder"] = _work_order_out(work_order) if work_order else None
        payload["document"] = _document_out(document) if document else None
        payload["closureSummary"] = await _closure_summary_payload(task)
    return payload


def _event_out(event: AdminCompatInspectionEvent | None) -> dict[str, Any] | None:
    if not event:
        return None
    risk = _meta(RISK_META, event.risk_level)
    return {
        "eventId": event.id,
        "eventCode": event.event_code,
        "eventTitle": event.event_title,
        "detectionId": event.id,
        "detectionNo": event.event_code,
        "eventType": event.event_type,
        "eventTypeName": event.event_type_name or _event_type_name(event.event_type),
        "riskLevel": event.risk_level,
        "riskLevelName": event.risk_level_name or risk["label"],
        "riskColor": risk["color"],
        "confidence": round(event.confidence * 100, 1) if event.confidence <= 1 else event.confidence,
        "description": event.description,
        "suggestion": "请立即拍照取证，并生成消防安全隐患工单。",
        "detectedAt": _fmt(event.detected_time),
        "imageUrl": event.image_url or DEMO_IMAGE_URL,
        "markedImageUrl": event.marked_image_url or DEMO_MARKED_IMAGE_URL,
        "bbox": event.bbox or {"x": 120, "y": 180, "width": 420, "height": 260},
        "modelName": event.model_name or "mock-ai-inspection",
        "modelVersion": event.model_version or "v1.0-demo",
        "taskId": event.task_id,
        "pointId": event.point_id,
        "pointName": event.point_name,
    }


def _evidence_out(evidence: AdminCompatEvidenceFile | None) -> dict[str, Any] | None:
    if not evidence:
        return None
    return {
        "evidenceId": evidence.id,
        "evidenceNo": evidence.evidence_no,
        "taskId": evidence.task_id,
        "pointRecordId": evidence.point_record_id,
        "detectionId": evidence.detection_id,
        "fileType": evidence.file_type,
        "fileName": evidence.file_name,
        "fileUrl": evidence.file_url,
        "capturedBy": evidence.captured_by_name,
        "capturedAt": _fmt(evidence.captured_time),
    }


def _work_order_out(order: AdminCompatWorkOrder | None) -> dict[str, Any] | None:
    if not order:
        return None
    risk = _meta(RISK_META, order.risk_level)
    status = _meta(WORK_ORDER_STATUS_META, order.status)
    push = _meta(PUSH_STATUS_META, order.push_status)
    return {
        "workOrderId": order.id,
        "workOrderNo": order.work_order_code,
        "workOrderCode": order.work_order_code,
        "title": order.title,
        "eventType": order.event_type,
        "eventTypeName": order.event_type_name or _event_type_name(order.event_type or ""),
        "riskLevel": order.risk_level,
        "riskLevelName": order.risk_level_name or risk["label"],
        "riskColor": risk["color"],
        "source": order.source,
        "reporterId": order.reporter_id,
        "reporterName": order.reporter_name,
        "reportTime": _fmt(order.report_time or order.create_time),
        "areaId": order.area_id,
        "areaName": order.area_name,
        "pointName": order.point_name,
        "locationName": order.location_name or order.point_name,
        "addressDetail": order.address_detail or order.point_name,
        "longitude": order.lng,
        "latitude": order.lat,
        "status": order.status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "pushStatus": order.push_status,
        "pushStatusName": push["label"],
        "pushStatusColor": push["color"],
        "pushStatusRipple": push.get("ripple", False),
        "thirdOrderNo": order.third_order_no or order.platform_code,
        "platformCode": order.platform_code,
        "remainingMinutes": order.remaining_minutes,
        "responsibleDepartment": order.responsible_department,
        "handlerName": order.handler_name,
        "description": order.description,
        "suggestion": order.suggestion,
        "evidenceList": order.evidence_list or [],
        "taskId": order.task_id,
        "pointRecordId": order.point_record_id,
        "detectionId": order.event_id,
        "timeline": order.timeline or [],
        "createTime": _fmt(order.create_time),
        "createdAt": _fmt(order.create_time),
        "updatedAt": _fmt(order.update_time),
    }


def _document_out(document: AdminCompatLawDocument | None) -> dict[str, Any] | None:
    if not document:
        return None
    status = _meta(DOCUMENT_STATUS_META, document.status or document.print_status)
    return {
        "documentId": document.id,
        "documentNo": document.document_code,
        "documentCode": document.document_code,
        "documentType": document.document_type,
        "documentTypeName": document.document_type_name or document.document_type,
        "documentTitle": document.document_title,
        "workOrderId": document.work_order_id,
        "targetName": document.target_name or document.checked_unit,
        "checkedUnit": document.checked_unit,
        "checkLocation": document.check_location,
        "illegalFact": document.illegal_fact,
        "legalBasis": document.legal_basis,
        "rectificationRequirement": document.rectification_requirement,
        "deadline": document.deadline,
        "reviewRequirement": document.review_requirement,
        "patrolUserName": document.inspector_name,
        "status": document.status or document.print_status,
        "statusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "printStatus": document.print_status,
        "printStatusName": status["label"],
        "content": document.content,
        "qrCode": document.qr_code,
        "qrCodeUrl": document.qr_code_url,
        "generatedAt": _fmt(document.generated_time or document.create_time),
        "printedAt": _fmt(document.printed_time),
        "createTime": _fmt(document.create_time),
    }


def _push_out(record: AdminCompatPushRecord) -> dict[str, Any]:
    status = _meta(PUSH_STATUS_META, record.push_status)
    return {
        "pushRecordId": record.id,
        "requestId": record.request_id,
        "workOrderId": record.work_order_id,
        "workOrderNo": record.work_order_code,
        "targetPlatform": record.target_platform,
        "pushStatus": record.push_status,
        "pushStatusName": status["label"],
        "statusColor": status["color"],
        "statusRipple": status.get("ripple", False),
        "thirdOrderNo": record.third_order_no,
        "requestBody": record.request_body,
        "responseBody": record.response_body,
        "errorMessage": record.error_message,
        "pushedAt": _fmt(record.pushed_time),
        "operatorName": record.operator_name,
    }


def _print_out(record: AdminCompatPrintRecord) -> dict[str, Any]:
    return {
        "printRecordId": record.id,
        "documentId": record.document_id,
        "documentNo": record.document_code,
        "printerName": record.printer_name,
        "printStatus": record.print_status,
        "operatorName": record.operator_name,
        "printedAt": _fmt(record.printed_time),
        "message": record.message,
    }


async def _flow_records(business_type: str, business_id: int) -> list[dict[str, Any]]:
    rows = await AdminCompatWorkOrderFlow.filter(
        business_type=business_type,
        business_id=business_id,
    ).order_by("create_time", "id")
    return [
        {
            "flowId": item.id,
            "businessType": item.business_type,
            "businessId": item.business_id,
            "businessCode": item.business_code,
            "action": item.action,
            "fromStatus": item.from_status,
            "toStatus": item.to_status,
            "operatorName": item.operator_name,
            "remark": item.remark,
            "eventType": item.event_type,
            "createdAt": _fmt(item.create_time),
        }
        for item in rows
    ]


async def _build_work_order_detail(order: AdminCompatWorkOrder) -> dict[str, Any]:
    event = await AdminCompatInspectionEvent.get_or_none(id=order.event_id) if order.event_id else None
    task = await AdminCompatPatrolTask.get_or_none(id=order.task_id) if order.task_id else None
    document = await AdminCompatLawDocument.get_or_none(work_order_id=order.id)
    push_records = await AdminCompatPushRecord.filter(work_order_id=order.id).order_by("-create_time")
    flows = await _flow_records("WORK_ORDER", order.id)
    if task:
        flows = [*await _flow_records("TASK", task.id), *flows]
    return {
        "workOrder": _work_order_out(order),
        "task": await _task_out(task) if task else None,
        "aiDetection": _event_out(event),
        "document": _document_out(document),
        "pushRecords": [_push_out(item) for item in push_records],
        "flowRecords": sorted(flows, key=lambda item: item["createdAt"]),
    }


async def ensure_demo():
    task = await _ensure_demo_task()
    return success(await _task_out(task, True))


async def reset_demo():
    task = await AdminCompatPatrolTask.get_or_none(task_code="RW202605120001")
    if not task:
        task = await _ensure_demo_task()
        return success(await _task_out(task, True), msg="演示任务已重置")

    work_order_ids = await AdminCompatWorkOrder.filter(task_id=task.id).values_list("id", flat=True)
    event_ids = await AdminCompatInspectionEvent.filter(task_id=task.id).values_list("id", flat=True)
    if work_order_ids:
        document_ids = await AdminCompatLawDocument.filter(work_order_id__in=work_order_ids).values_list("id", flat=True)
        if document_ids:
            await AdminCompatPrintRecord.filter(document_id__in=document_ids).delete()
        await AdminCompatLawDocument.filter(work_order_id__in=work_order_ids).delete()
        await AdminCompatPushRecord.filter(work_order_id__in=work_order_ids).delete()
        await AdminCompatWorkOrderFlow.filter(
            business_type="WORK_ORDER",
            business_id__in=work_order_ids,
        ).delete()
        await AdminCompatWorkOrder.filter(id__in=work_order_ids).delete()
    if event_ids:
        await AdminCompatEvidenceFile.filter(detection_id__in=event_ids).delete()
        await AdminCompatInspectionEvent.filter(id__in=event_ids).delete()
    await AdminCompatInspectionReport.filter(task_id=task.id).delete()
    point_record_ids = await AdminCompatPatrolTaskPoint.filter(task_id=task.id).values_list("id", flat=True)
    await AdminCompatWorkOrderFlow.filter(business_type="TASK", business_id=task.id).delete()
    if point_record_ids:
        await AdminCompatWorkOrderFlow.filter(
            business_type="POINT",
            business_id__in=point_record_ids,
        ).delete()
    await AdminCompatPatrolTaskPoint.filter(task_id=task.id).delete()

    user = await _ensure_demo_user()
    task.task_title = "幸福里小区消防安全巡查任务"
    task.task_type = "FIRE_SAFETY"
    task.priority = "high"
    task.description = "演示任务：消防通道堵塞闭环处置"
    task.ai_focus = 1
    task.patrol_location = "幸福里小区"
    task.plan_time = _now()
    task.start_time = _now()
    task.end_time = _now() + timedelta(hours=1, minutes=30)
    task.duration_hours = 1
    task.executor_id = user.id
    task.executor_name = "哼哼"
    task.task_status = "DISPATCHED"
    task.progress = 0
    task.exception_count = 0
    await task.save()
    await _ensure_task_points(task)
    await _record_flow(
        business_type="TASK",
        business_id=task.id,
        business_code=task.task_code,
        action="任务重置",
        from_status=None,
        to_status="DISPATCHED",
        operator_id="admin_001",
        operator_name="指挥中心操作员",
        remark="重置默认演示任务，方便重新跑闭环",
        event_type="TASK_DISPATCHED",
    )
    return success(await _task_out(task, True), msg="演示任务已重置")


async def create_task(form: PatrolMvpTaskCreateForm):
    start_time = _parse_time(form.startTime)
    end_time = _parse_time(form.endTime)
    if not start_time:
        return fail(1, "请选择任务开始时间")
    if not end_time:
        return fail(1, "请选择任务结束时间")
    if end_time <= start_time:
        return fail(1, "任务结束时间必须晚于开始时间")

    user = await _ensure_demo_user()
    points = await AdminCompatPatrolPoint.filter(id__in=form.pointIds).all() if form.pointIds else []
    if not points:
        point = await _demo_point()
        points = [point] if point else []
    if not points:
        return fail(1, "请至少选择一个巡查点位")

    task = await AdminCompatPatrolTask.create(
        task_code=await _next_task_code(),
        task_title=form.title.strip(),
        task_type=form.type,
        priority="high",
        description=form.remark,
        ai_focus=1,
        patrol_location="、".join({point.point_name.split("3号楼")[0] or point.point_name for point in points}),
        area_ids=list({point.area_id for point in points}),
        point_ids=[point.id for point in points],
        plan_time=start_time,
        start_time=start_time,
        end_time=end_time,
        duration_hours=max(1, int((end_time - start_time).total_seconds() // 3600)),
        repeat_rule="none",
        executor_id=user.id,
        executor_name=form.assigneeName or user.nickname,
        task_status="DRAFT",
        progress=0,
        exception_count=0,
        creator_id=1,
        creator_name="指挥中心操作员",
    )
    await _ensure_task_points(task, [point.id for point in points])
    await _record_flow(
        business_type="TASK",
        business_id=task.id,
        business_code=task.task_code,
        action="任务创建",
        from_status=None,
        to_status="DRAFT",
        operator_id="admin_001",
        operator_name="指挥中心操作员",
        remark="管理端创建巡查任务",
        event_type="TASK_CREATED",
    )
    return success(await _task_out(task, True), msg="任务已创建")


async def page_tasks(params: PatrolMvpQuery):
    await _ensure_demo_task()
    queryset = AdminCompatPatrolTask.all()
    if params.status:
        queryset = queryset.filter(task_status=params.status)
    if params.assigneeId:
        user = await AdminCompatUser.get_or_none(username=params.assigneeId)
        if user:
            queryset = queryset.filter(executor_id=user.id)
    if params.keywords:
        queryset = queryset.filter(Q(task_title__contains=params.keywords) | Q(task_code__contains=params.keywords))
    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"createdAt": "create_time", "taskNo": "task_code", "status": "task_status"},
        "-create_time",
    )
    total, rows = await paginate_queryset(queryset.order_by(order_by), params.page, params.limit)
    items = [await _task_out(item) for item in rows]
    return success(build_page_payload(items, total))


async def h5_tasks(params: PatrolMvpQuery):
    params.assigneeId = params.assigneeId or "patrol_001"
    payload = await page_tasks(params)
    return payload


async def task_detail(form: PatrolMvpTaskForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    return success(await _task_out(task, True))


async def dispatch_task(form: PatrolMvpTaskForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    if task.task_status not in ("DRAFT", "pending", "waiting", "DISPATCHED"):
        return fail(1, "当前任务状态不可下发")
    if task.task_status != "DISPATCHED":
        await _set_task_status(
            task,
            "DISPATCHED",
            action="任务下发",
            operator_id="admin_001",
            operator_name="指挥中心操作员",
            remark="任务下发至 H5 巡查端",
            event_type="TASK_DISPATCHED",
        )
    return success(await _task_out(task, True), msg="任务已下发")


async def receive_task(form: PatrolMvpTaskForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    if task.task_status != "RECEIVED":
        if task.task_status != "DISPATCHED":
            return fail(1, "当前任务不可接收")
        await _set_task_status(
            task,
            "RECEIVED",
            action="接收任务",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark=f"巡查员{form.operatorName or task.executor_name}已接收任务",
            event_type="TASK_RECEIVED",
        )
    return success(await _task_out(task, True), msg="任务已接收")


async def start_going(form: PatrolMvpTaskPointForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    point_record = await _get_point_record(task, form)
    if not point_record:
        return fail(1, "巡查点位不存在")
    if task.task_status != "GOING":
        if task.task_status != "RECEIVED":
            return fail(1, "当前任务不可开始前往")
        await _set_task_status(
            task,
            "GOING",
            action="开始前往",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark=f"开始前往{point_record.point_name}",
            event_type="PATROL_GOING",
        )
    if point_record.status != "GOING":
        await _set_point_status(
            point_record,
            "GOING",
            action="开始前往",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="点位进入前往中",
            event_type="PATROL_GOING",
        )
    return success(
        {
            **await _task_out(task, True),
            "point": _point_out(point_record),
            "speed": "1.2m/s",
            "estimatedArrival": _fmt(_now() + timedelta(minutes=3)),
        },
        msg="已开始前往",
    )


async def arrive_point(form: PatrolMvpTaskPointForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    point_record = await _get_point_record(task, form)
    if not point_record:
        return fail(1, "巡查点位不存在")
    if point_record.status != "ARRIVED":
        if point_record.status != "GOING":
            return fail(1, "当前点位不可确认到达")
        await _set_point_status(
            point_record,
            "ARRIVED",
            action="到达点位",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark=f"已到达{point_record.point_name}",
            event_type="PATROL_ARRIVED",
        )
    return success(
        {"task": await _task_out(task, True), "point": _point_out(point_record)},
        msg="已确认到达",
    )


async def start_inspection(form: PatrolMvpTaskPointForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    point_record = await _get_point_record(task, form)
    if not point_record:
        return fail(1, "巡查点位不存在")
    if point_record.status != "INSPECTING":
        if point_record.status != "ARRIVED":
            return fail(1, "请先确认到达点位")
        await _set_point_status(
            point_record,
            "INSPECTING",
            action="开始巡查",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="AI识别已开启",
            event_type="PATROL_STARTED",
        )
    if task.task_status != "INSPECTING":
        await _set_task_status(
            task,
            "INSPECTING",
            action="开始巡查",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark=f"开始巡查{point_record.point_name}",
            event_type="PATROL_STARTED",
        )
    return success(await _task_out(task, True), msg="巡查已开始")


async def mock_detect(form: PatrolMvpDetectForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    point_record = await _get_point_record(task, form)
    if not point_record:
        return fail(1, "巡查点位不存在")
    if point_record.status not in ("INSPECTING", "RISK_DETECTED", "EVIDENCE_CAPTURED"):
        return fail(1, "请先开始巡查")

    event = await AdminCompatInspectionEvent.filter(
        task_id=task.id,
        point_id=point_record.point_id,
        event_type=form.scene,
    ).order_by("-create_time").first()
    if not event:
        detected_time = _now()
        event = await AdminCompatInspectionEvent.create(
            event_code=f"det_{detected_time.strftime('%Y%m%d%H%M%S')}",
            event_title="识别到消防安全隐患：通道堵塞",
            event_type=form.scene,
            event_type_name=_event_type_name(form.scene),
            risk_level="HIGH",
            risk_level_name="高风险",
            source="AI识别",
            status="RISK_DETECTED",
            task_id=task.id,
            task_code=task.task_code,
            inspector_id=task.executor_id,
            inspector_name=task.executor_name,
            area_id=None,
            area_name="幸福里小区",
            point_id=point_record.point_id,
            point_name=point_record.point_name,
            lat=point_record.lat,
            lng=point_record.lng,
            confidence=0.96,
            description="AI识别发现消防通道被大量杂物（纸箱、旧家具）堵塞，严重影响疏散逃生。",
            image_url=DEMO_IMAGE_URL,
            marked_image_url=DEMO_MARKED_IMAGE_URL,
            bbox={"x": 120, "y": 180, "width": 420, "height": 260},
            model_name="mock-ai-inspection",
            model_version="v1.0-demo",
            detected_time=detected_time,
        )
        await _record_flow(
            business_type="TASK",
            business_id=task.id,
            business_code=task.task_code,
            action="AI识别",
            from_status=task.task_status,
            to_status=task.task_status,
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="AI识别发现消防通道堵塞隐患",
            event_type="AI_EVENT_DETECTED",
            extra={"detectionId": event.id},
        )

    if point_record.status != "RISK_DETECTED":
        await _set_point_status(
            point_record,
            "RISK_DETECTED",
            action="发现隐患",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="识别到消防安全隐患：通道堵塞",
            event_type="AI_EVENT_DETECTED",
        )
    task.exception_count = max(task.exception_count, 1)
    await task.save()
    return success(_event_out(event), msg="识别到消防安全隐患：通道堵塞")


async def capture_evidence(form: PatrolMvpEvidenceForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    point_record = await _get_point_record(task, form)
    if not point_record:
        return fail(1, "巡查点位不存在")
    event = await AdminCompatInspectionEvent.get_or_none(id=form.detectionId)
    if not event:
        return fail(1, "AI识别事件不存在")
    evidence = await AdminCompatEvidenceFile.filter(
        task_id=task.id,
        point_record_id=point_record.id,
        detection_id=event.id,
    ).order_by("-create_time").first()
    if not evidence:
        file_url = form.fileUrl or DEMO_MARKED_IMAGE_URL
        evidence = await AdminCompatEvidenceFile.create(
            evidence_no=await _next_evidence_no(),
            task_id=task.id,
            point_record_id=point_record.id,
            point_id=point_record.point_id,
            detection_id=event.id,
            file_type="IMAGE",
            file_name=file_url.rsplit("/", 1)[-1],
            file_url=file_url,
            captured_by_id=form.operatorId,
            captured_by_name=form.operatorName or task.executor_name,
            captured_time=_now(),
        )
        await _record_flow(
            business_type="TASK",
            business_id=task.id,
            business_code=task.task_code,
            action="拍照取证",
            from_status=task.task_status,
            to_status=task.task_status,
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="已拍照取证，证据已保存",
            event_type="EVIDENCE_CAPTURED",
            extra={"evidenceId": evidence.id},
        )
    if point_record.status != "EVIDENCE_CAPTURED":
        await _set_point_status(
            point_record,
            "EVIDENCE_CAPTURED",
            action="拍照取证",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="点位现场取证完成",
            event_type="EVIDENCE_CAPTURED",
        )
    return success(_evidence_out(evidence), msg="已拍照取证，证据已保存")


async def generate_work_order_draft(form: PatrolMvpWorkOrderDraftForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    point_record = await _get_point_record(task, form)
    if not point_record:
        return fail(1, "巡查点位不存在")
    event = await AdminCompatInspectionEvent.get_or_none(id=form.detectionId)
    evidence = await AdminCompatEvidenceFile.get_or_none(id=form.evidenceId)
    if not event or not evidence:
        return fail(1, "请先完成 AI 识别和拍照取证")

    order = await AdminCompatWorkOrder.filter(event_id=event.id).order_by("-create_time").first()
    if not order:
        occurred = event.detected_time or _now()
        address = "幸福里小区3号楼"
        description = (
            f"{occurred.strftime('%Y-%m-%d %H:%M')}在{address}，通过智能眼镜AI识别发现消防通道被大量杂物"
            "（纸箱、旧家具）堵塞，严重影响疏散逃生。已现场拍照取证。请相关责任单位立即处置。"
        )
        evidence_item = {
            "fileType": evidence.file_type,
            "fileName": evidence.file_name,
            "fileUrl": evidence.file_url,
        }
        order = await AdminCompatWorkOrder.create(
            work_order_code=await _next_work_order_code(event.event_type),
            title="【AI识别】幸福里小区3号楼消防通道严重堵塞",
            event_type=event.event_type,
            event_type_name=event.event_type_name or _event_type_name(event.event_type),
            risk_level=event.risk_level,
            risk_level_name=event.risk_level_name or _risk_name(event.risk_level),
            source="AI识别",
            reporter_id=task.executor_id,
            reporter_name=task.executor_name,
            area_id=event.area_id,
            area_name=event.area_name,
            point_name=point_record.point_name,
            event_id=event.id,
            task_id=task.id,
            point_record_id=point_record.id,
            location_name=point_record.point_name,
            address_detail=address,
            lat=point_record.lat,
            lng=point_record.lng,
            status="DRAFT",
            push_status="NOT_PUSHED",
            report_time=None,
            deadline_time=_now() + timedelta(hours=2),
            remaining_minutes=120,
            responsible_department="街道安监办",
            handler_name=None,
            description=description,
            suggestion="请立即拍照取证，并生成消防安全隐患工单。",
            evidence_list=[evidence_item],
            timeline=[
                {
                    "time": _now().strftime("%m-%d %H:%M"),
                    "title": "生成工单草稿",
                    "desc": "系统根据 AI 识别和取证照片生成工单草稿",
                    "status": "草稿",
                    "color": "#94A3B8",
                }
            ],
        )
        await _record_flow(
            business_type="WORK_ORDER",
            business_id=order.id,
            business_code=order.work_order_code,
            action="生成工单",
            from_status=None,
            to_status="DRAFT",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="系统自动生成工单草稿",
            event_type="WORK_ORDER_DRAFT_CREATED",
        )
        await _record_flow(
            business_type="TASK",
            business_id=task.id,
            business_code=task.task_code,
            action="生成工单",
            from_status=task.task_status,
            to_status=task.task_status,
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark=f"生成工单草稿 {order.work_order_code}",
            event_type="WORK_ORDER_DRAFT_CREATED",
            extra={"workOrderId": order.id},
        )
    return success(_work_order_out(order), msg="工单草稿已生成")


async def update_work_order(form: PatrolMvpWorkOrderForm):
    order = await _get_work_order(form)
    if not order:
        return fail(1, "工单不存在")
    if order.status not in ("DRAFT", "PENDING_SUPPLEMENT", "LOCAL_SAVED"):
        return fail(1, "当前工单状态不可编辑")
    old_status = order.status
    if form.title is not None:
        order.title = form.title.strip()
    if form.addressDetail is not None:
        order.address_detail = form.addressDetail.strip()
    if form.description is not None:
        order.description = form.description.strip()
    await order.save()
    await _record_flow(
        business_type="WORK_ORDER",
        business_id=order.id,
        business_code=order.work_order_code,
        action="暂存草稿",
        from_status=old_status,
        to_status=order.status,
        operator_id=form.operatorId,
        operator_name=form.operatorName or order.reporter_name,
        remark="巡查员更新工单草稿内容",
        event_type=None,
    )
    return success(_work_order_out(order), msg="工单草稿已保存")


async def _get_work_order(form: PatrolMvpWorkOrderForm) -> AdminCompatWorkOrder | None:
    if form.workOrderId:
        return await AdminCompatWorkOrder.get_or_none(id=form.workOrderId)
    if form.workOrderNo:
        return await AdminCompatWorkOrder.get_or_none(work_order_code=form.workOrderNo)
    return await AdminCompatWorkOrder.all().order_by("-create_time").first()


async def submit_work_order(form: PatrolMvpWorkOrderForm):
    order = await _get_work_order(form)
    if not order:
        return fail(1, "工单不存在")
    if order.status == "SUBMITTED":
        return success(_work_order_out(order), msg="工单已提交")
    if order.status not in ("DRAFT", "PENDING_SUPPLEMENT", "LOCAL_SAVED"):
        return fail(1, "当前工单不可提交")
    old_status = order.status
    order.status = "SUBMITTED"
    order.report_time = _now()
    timeline = order.timeline or []
    timeline.append(
        {
            "time": _now().strftime("%m-%d %H:%M"),
            "title": "确认上传",
            "desc": "工单上传成功，已同步至管理端工单中心",
            "status": "已提交",
            "color": "#1677FF",
        }
    )
    order.timeline = timeline
    await order.save()
    await _record_flow(
        business_type="WORK_ORDER",
        business_id=order.id,
        business_code=order.work_order_code,
        action="上传工单",
        from_status=old_status,
        to_status="SUBMITTED",
        operator_id=form.operatorId,
        operator_name=form.operatorName or order.reporter_name,
        remark="工单上传成功，已同步至管理端工单中心",
        event_type="WORK_ORDER_SUBMITTED",
    )
    if order.task_id:
        task = await AdminCompatPatrolTask.get_or_none(id=order.task_id)
        if task:
            await _set_task_status(
                task,
                "WORK_ORDER_SUBMITTED",
                action="上传工单",
                operator_id=form.operatorId,
                operator_name=form.operatorName or order.reporter_name,
                remark=f"工单 {order.work_order_code} 已上传",
                event_type="WORK_ORDER_SUBMITTED",
            )
    if order.point_record_id:
        point_record = await AdminCompatPatrolTaskPoint.get_or_none(id=order.point_record_id)
        if point_record:
            await _set_point_status(
                point_record,
                "WORK_ORDER_SUBMITTED",
                action="上传工单",
                operator_id=form.operatorId,
                operator_name=form.operatorName or order.reporter_name,
                remark="点位工单已提交",
                event_type="WORK_ORDER_SUBMITTED",
            )
    return success(_work_order_out(order), msg="工单上传成功，已同步至管理端工单中心")


async def _work_order_queryset(params: PatrolMvpQuery):
    queryset = AdminCompatWorkOrder.all()
    if params.status:
        queryset = queryset.filter(status=params.status)
    if params.keywords:
        queryset = queryset.filter(
            Q(title__contains=params.keywords)
            | Q(work_order_code__contains=params.keywords)
            | Q(address_detail__contains=params.keywords)
        )
    return queryset


async def page_work_orders(params: PatrolMvpQuery):
    await _ensure_demo_task()
    queryset = await _work_order_queryset(params)
    total, rows = await paginate_queryset(queryset.order_by("-create_time"), params.page, params.limit)
    return success(build_page_payload([_work_order_out(row) for row in rows], total))


async def work_order_detail(form: PatrolMvpWorkOrderForm):
    order = await _get_work_order(form)
    if not order:
        return fail(1, "工单不存在")
    return success(await _build_work_order_detail(order))


async def push_work_order(form: PatrolMvpWorkOrderForm):
    order = await _get_work_order(form)
    if not order:
        return fail(1, "工单不存在")
    if order.status not in ("SUBMITTED", "PUSH_FAILED", "PUSHED", "PENDING_ACCEPT"):
        return fail(1, "当前工单不可推送")
    old_status = order.status
    order.status = "PUSHING"
    order.push_status = "PUSHING"
    await order.save()

    request_id = f"req_{_now().strftime('%Y%m%d%H%M%S%f')}"
    request_body = {
        "requestId": request_id,
        "sourceSystem": "smart_patrol",
        "workOrderNo": order.work_order_code,
        "eventTitle": order.title,
        "eventType": order.event_type,
        "eventTypeName": order.event_type_name,
        "riskLevel": order.risk_level,
        "riskLevelName": order.risk_level_name,
        "description": order.description,
        "locationName": order.location_name,
        "addressDetail": order.address_detail,
        "longitude": order.lng,
        "latitude": order.lat,
        "reporterName": order.reporter_name,
        "reportTime": _fmt(order.report_time or _now()),
        "suggestedDept": order.responsible_department,
        "deadline": "2小时内现场处置",
        "evidenceList": order.evidence_list or [],
        "documentList": [],
    }

    if form.mockResult == "fail":
        response_body = {
            "success": False,
            "pushStatus": "PUSH_FAILED",
            "message": "第三方平台连接超时，请稍后重试",
        }
        order.status = "PUSH_FAILED"
        order.push_status = "PUSH_FAILED"
        msg = "推送失败，第三方平台连接超时"
    else:
        third_order_no = f"SZFNGOV{_now().strftime('%Y%m%d%H%M%S')}"
        response_body = {
            "success": True,
            "pushStatus": "PUSH_SUCCESS",
            "thirdOrderNo": third_order_no,
            "thirdStatus": "PENDING_ACCEPT",
            "message": "工单已成功上报至数字赋能基层治理平台",
        }
        order.status = "PUSHED"
        order.push_status = "PUSH_SUCCESS"
        order.third_order_no = third_order_no
        order.platform_code = third_order_no
        msg = "上报成功，工单已流转至数字赋能基层治理平台，状态：待受理。"
    timeline = order.timeline or []
    timeline.append(
        {
            "time": _now().strftime("%m-%d %H:%M"),
            "title": "一键推送",
            "desc": msg,
            "status": "推送成功" if order.push_status == "PUSH_SUCCESS" else "推送失败",
            "color": "#18A058" if order.push_status == "PUSH_SUCCESS" else "#F04438",
        }
    )
    order.timeline = timeline
    await order.save()

    push_record = await AdminCompatPushRecord.create(
        request_id=request_id,
        work_order_id=order.id,
        work_order_code=order.work_order_code,
        target_platform=form.targetPlatform,
        push_status=order.push_status,
        third_order_no=order.third_order_no,
        request_body=request_body,
        response_body=response_body,
        error_message=None if order.push_status == "PUSH_SUCCESS" else response_body["message"],
        pushed_time=_now(),
        operator_id=form.operatorId or "admin_001",
        operator_name=form.operatorName or "指挥中心操作员",
    )
    await _record_flow(
        business_type="WORK_ORDER",
        business_id=order.id,
        business_code=order.work_order_code,
        action="推送第三方",
        from_status=old_status,
        to_status=order.status,
        operator_id=form.operatorId or "admin_001",
        operator_name=form.operatorName or "指挥中心操作员",
        remark=msg,
        event_type="WORK_ORDER_PUSH_SUCCESS" if order.push_status == "PUSH_SUCCESS" else "WORK_ORDER_PUSH_FAILED",
        extra={"pushRecordId": push_record.id, "requestId": request_id},
    )
    if order.task_id and order.push_status == "PUSH_SUCCESS":
        task = await AdminCompatPatrolTask.get_or_none(id=order.task_id)
        if task:
            await _set_task_status(
                task,
                "PUSHED",
                action="推送第三方",
                operator_id=form.operatorId or "admin_001",
                operator_name=form.operatorName or "指挥中心操作员",
                remark=f"工单 {order.work_order_code} 推送成功",
                event_type="WORK_ORDER_PUSH_SUCCESS",
            )
    return success({"workOrder": _work_order_out(order), "pushRecord": _push_out(push_record)}, msg=msg)


async def page_push_records(params: PatrolMvpQuery):
    queryset = AdminCompatPushRecord.all()
    if params.keywords:
        queryset = queryset.filter(
            Q(request_id__contains=params.keywords)
            | Q(work_order_code__contains=params.keywords)
            | Q(third_order_no__contains=params.keywords)
        )
    if params.status:
        queryset = queryset.filter(push_status=params.status)
    total, rows = await paginate_queryset(queryset.order_by("-create_time"), params.page, params.limit)
    return success(build_page_payload([_push_out(row) for row in rows], total))


async def generate_document(form: PatrolMvpDocumentForm):
    order_form = PatrolMvpWorkOrderForm(workOrderId=form.workOrderId)
    order = await _get_work_order(order_form)
    if not order:
        return fail(1, "工单不存在")
    if order.push_status != "PUSH_SUCCESS":
        return fail(1, "请先推送第三方平台成功后再生成文书")
    document = await AdminCompatLawDocument.get_or_none(work_order_id=order.id)
    if not document:
        document_no = await _next_document_no()
        document = await AdminCompatLawDocument.create(
            document_code=document_no,
            document_title="责令立即整改通知书",
            document_type=form.documentType,
            document_type_name="责令立即整改通知书",
            work_order_id=order.id,
            checked_unit="幸福里小区3号楼相关责任人",
            check_location=order.address_detail or order.location_name or "",
            target_name="幸福里小区3号楼相关责任人",
            illegal_fact="占用、堵塞、封闭疏散通道，影响疏散逃生。",
            legal_basis="《中华人民共和国消防法》第二十八条、第六十条第一款第三项",
            rectification_requirement="立即清除楼梯转角平台杂物，恢复消防通道畅通。",
            deadline="现场立即整改",
            review_requirement="24小时内复查",
            status="GENERATED",
            print_status="NOT_PRINTED",
            inspector_name=order.reporter_name,
            content=(
                "经现场巡查，发现消防通道存在杂物堵塞，影响疏散逃生。"
                "现责令立即清除楼梯转角平台杂物，恢复消防通道畅通，并在24小时内接受复查。"
            ),
            qr_code=f"QR-{document_no}",
            qr_code_url=None,
            generated_time=_now(),
            printed_time=None,
        )
        await _record_flow(
            business_type="WORK_ORDER",
            business_id=order.id,
            business_code=order.work_order_code,
            action="生成文书",
            from_status=order.status,
            to_status="DOCUMENT_GENERATED",
            operator_id=form.operatorId or "admin_001",
            operator_name=form.operatorName or "指挥中心操作员",
            remark=f"生成《责令立即整改通知书》{document_no}",
            event_type="DOCUMENT_GENERATED",
            extra={"documentId": document.id},
        )
    order.status = "DOCUMENT_GENERATED"
    await order.save()
    return success(_document_out(document), msg="整改通知书已生成")


async def document_detail(form: PatrolMvpDocumentForm):
    document = None
    if form.documentId:
        document = await AdminCompatLawDocument.get_or_none(id=form.documentId)
    elif form.documentNo:
        document = await AdminCompatLawDocument.get_or_none(document_code=form.documentNo)
    elif form.workOrderId:
        document = await AdminCompatLawDocument.get_or_none(work_order_id=form.workOrderId)
    if not document:
        return fail(1, "文书不存在")
    return success(_document_out(document))


async def page_documents(params: PatrolMvpQuery):
    queryset = AdminCompatLawDocument.all()
    if params.status:
        queryset = queryset.filter(status=params.status)
    if params.keywords:
        queryset = queryset.filter(
            Q(document_title__contains=params.keywords)
            | Q(document_code__contains=params.keywords)
            | Q(checked_unit__contains=params.keywords)
        )
    total, rows = await paginate_queryset(queryset.order_by("-create_time"), params.page, params.limit)
    return success(build_page_payload([_document_out(row) for row in rows], total))


async def mock_print_document(form: PatrolMvpDocumentForm):
    detail = await document_detail(form)
    if detail["code"] != 0:
        return detail
    document = await AdminCompatLawDocument.get_or_none(id=detail["data"]["documentId"])
    if not document:
        return fail(1, "文书不存在")
    if document.status == "PRINTED":
        return success(_document_out(document), msg="文书已打印")

    document.status = "PRINTING"
    document.print_status = "PRINTING"
    await document.save()
    document.status = "PRINTED"
    document.print_status = "PRINTED"
    document.printed_time = _now()
    await document.save()

    record = await AdminCompatPrintRecord.create(
        document_id=document.id,
        document_code=document.document_code,
        printer_name=form.printerName,
        print_status="PRINTED",
        operator_id=form.operatorId,
        operator_name=form.operatorName or document.inspector_name,
        printed_time=_now(),
        message="打印完成，请取走纸质文书。",
    )
    order = await AdminCompatWorkOrder.get_or_none(id=document.work_order_id) if document.work_order_id else None
    if order:
        old_status = order.status
        order.status = "DOCUMENT_PRINTED"
        await order.save()
        await _record_flow(
            business_type="WORK_ORDER",
            business_id=order.id,
            business_code=order.work_order_code,
            action="打印文书",
            from_status=old_status,
            to_status="DOCUMENT_PRINTED",
            operator_id=form.operatorId,
            operator_name=form.operatorName or document.inspector_name,
            remark="打印完成，请取走纸质文书。",
            event_type="DOCUMENT_PRINTED",
            extra={"printRecordId": record.id},
        )
        if order.task_id:
            task = await AdminCompatPatrolTask.get_or_none(id=order.task_id)
            if task:
                await _set_task_status(
                    task,
                    "DOCUMENT_PRINTED",
                    action="打印文书",
                    operator_id=form.operatorId,
                    operator_name=form.operatorName or document.inspector_name,
                    remark=f"文书 {document.document_code} 已打印",
                    event_type="DOCUMENT_PRINTED",
                )
    return success({"document": _document_out(document), "printRecord": _print_out(record)}, msg="打印完成，请取走纸质文书。")


async def close_task(form: PatrolMvpTaskForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    if task.task_status != "CLOSED":
        if task.task_status != "DOCUMENT_PRINTED":
            return fail(1, "请先完成文书打印")
        await _set_task_status(
            task,
            "CLOSED",
            action="闭环任务",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="任务闭环完成",
            event_type="TASK_CLOSED",
        )
    point_records = await AdminCompatPatrolTaskPoint.filter(task_id=task.id).all()
    for point_record in point_records:
        if point_record.status != "CLOSED":
            await _set_point_status(
                point_record,
                "CLOSED",
                action="闭环点位",
                operator_id=form.operatorId,
                operator_name=form.operatorName or task.executor_name,
                remark="点位闭环完成",
                event_type="TASK_CLOSED",
            )
    order = await AdminCompatWorkOrder.get_or_none(task_id=task.id)
    if order and order.status != "CLOSED":
        old_status = order.status
        order.status = "CLOSED"
        await order.save()
        await _record_flow(
            business_type="WORK_ORDER",
            business_id=order.id,
            business_code=order.work_order_code,
            action="闭环工单",
            from_status=old_status,
            to_status="CLOSED",
            operator_id=form.operatorId,
            operator_name=form.operatorName or task.executor_name,
            remark="工单已闭环",
            event_type="TASK_CLOSED",
        )
    await _ensure_report(task)
    return success(await _closure_summary_payload(task), msg="任务闭环完成")


async def _ensure_report(task: AdminCompatPatrolTask):
    report = await AdminCompatInspectionReport.get_or_none(task_id=task.id)
    if report:
        return report
    order_count = await AdminCompatWorkOrder.filter(task_id=task.id).count()
    event_count = await AdminCompatInspectionEvent.filter(task_id=task.id).count()
    point_count = await AdminCompatPatrolTaskPoint.filter(task_id=task.id).count()
    printed_count = await AdminCompatLawDocument.filter(
        work_order_id__in=await AdminCompatWorkOrder.filter(task_id=task.id).values_list("id", flat=True),
        status="PRINTED",
    ).count()
    return await AdminCompatInspectionReport.create(
        report_code=f"BG{_now().strftime('%Y%m%d%H%M%S')}",
        report_title=f"{task.task_title}闭环报告",
        task_id=task.id,
        work_order_id=(await AdminCompatWorkOrder.get_or_none(task_id=task.id)).id if await AdminCompatWorkOrder.get_or_none(task_id=task.id) else None,
        report_status="generated",
        closure_rate=100,
        point_count=point_count,
        ai_detect_count=event_count,
        work_order_count=order_count,
        timeout_count=0,
        summary=f"本次任务共巡查{point_count}个点位，发现高风险消防安全隐患{event_count}起，生成工单{order_count}件，现场出具整改通知书{printed_count}份。",
        generated_time=_now(),
    )


async def _closure_summary_payload(task: AdminCompatPatrolTask) -> dict[str, Any]:
    point_count = await AdminCompatPatrolTaskPoint.filter(task_id=task.id).count()
    risk_count = await AdminCompatInspectionEvent.filter(task_id=task.id).count()
    work_order_count = await AdminCompatWorkOrder.filter(task_id=task.id).count()
    work_order_ids = await AdminCompatWorkOrder.filter(task_id=task.id).values_list("id", flat=True)
    push_success_count = await AdminCompatPushRecord.filter(
        work_order_id__in=work_order_ids,
        push_status="PUSH_SUCCESS",
    ).count() if work_order_ids else 0
    document_printed_count = await AdminCompatLawDocument.filter(
        work_order_id__in=work_order_ids,
        status="PRINTED",
    ).count() if work_order_ids else 0
    task_flows = await _flow_records("TASK", task.id)
    summary = (
        f"本次任务共巡查{point_count}个点位，发现高风险消防安全隐患{risk_count}起，"
        f"生成工单{work_order_count}件，成功推送数字赋能基层治理平台{push_success_count}件，"
        f"现场出具整改通知书{document_printed_count}份。发现到工单上传用时约2分钟，发现到文书出具用时约3分钟。"
    )
    return {
        "taskId": task.id,
        "taskNo": task.task_code,
        "taskCode": task.task_code,
        "title": task.task_title,
        "taskTitle": task.task_title,
        "taskStatus": task.task_status,
        "taskStatusName": _meta(TASK_STATUS_META, task.task_status)["label"],
        "pointCount": point_count,
        "riskCount": risk_count,
        "workOrderCount": work_order_count,
        "pushSuccessCount": push_success_count,
        "documentPrintedCount": document_printed_count,
        "timeline": [{"time": item["createdAt"], "title": item["action"], "remark": item["remark"]} for item in task_flows],
        "summaryText": summary,
    }


async def closure_summary(form: PatrolMvpTaskForm):
    task = await _get_task(form)
    if not task:
        return fail(1, "巡查任务不存在")
    return success(await _closure_summary_payload(task))


async def integration_status_callback(form: PatrolMvpCallbackForm):
    order = await AdminCompatWorkOrder.get_or_none(work_order_code=form.workOrderNo)
    if not order:
        return fail(1, "工单不存在")
    if form.thirdOrderNo:
        order.third_order_no = form.thirdOrderNo
        order.platform_code = form.thirdOrderNo
    order.handler_name = form.handlerName or order.handler_name
    order.responsible_department = form.handlerDept or order.responsible_department
    await order.save()
    await _record_flow(
        business_type="WORK_ORDER",
        business_id=order.id,
        business_code=order.work_order_code,
        action="第三方回调",
        from_status=order.status,
        to_status=order.status,
        operator_id="third_party",
        operator_name=form.handlerDept or "数字赋能基层治理平台",
        remark=form.remark or form.statusName or form.status,
        event_type=None,
        extra=form.model_dump(mode="json"),
    )
    return success({"received": True}, msg="回调已接收")
