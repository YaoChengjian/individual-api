from datetime import datetime
from typing import Any

from fastapi import Request

from app.api.admin_compat.helpers import build_page_payload, paginate_queryset, resolve_order_field
from app.api.admin_compat.models import AdminCompatAuditLog
from app.api.admin_compat.schemas import AuditLogQuery, CurrentAdminUser
from app.api.admin_compat.services.common import build_audit_log_out
from app.common.utils.response import success


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


async def record_audit_log(
    *,
    current_user: CurrentAdminUser | None = None,
    audit_type: str,
    summary: str,
    target_type: str | None = None,
    target_id: Any | None = None,
    before: Any | None = None,
    after: Any | None = None,
    risk_level: str = "low",
    request: Request | None = None,
    actor_name: str | None = None,
):
    await AdminCompatAuditLog.create(
        actor_user_id=current_user.user_id if current_user else None,
        actor_name=actor_name or (current_user.nickname if current_user else None),
        audit_type=audit_type,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        summary=summary,
        before_json=before,
        after_json=after,
        risk_level=risk_level,
        ip=request.client.host if request and request.client else None,
        trace_id=request.headers.get("x-request-id") if request else None,
    )


async def page_audit_logs(params: AuditLogQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatAuditLog.all()

    if params.auditType:
        queryset = queryset.filter(audit_type__contains=params.auditType)
    if params.actorName:
        queryset = queryset.filter(actor_name__contains=params.actorName)
    if params.riskLevel:
        queryset = queryset.filter(risk_level=params.riskLevel)
    if params.targetType:
        queryset = queryset.filter(target_type=params.targetType)
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "id": "id",
            "auditType": "audit_type",
            "actorName": "actor_name",
            "riskLevel": "risk_level",
            "createTime": "create_time",
        },
        "-create_time",
    )
    queryset = queryset.order_by(order_by)
    total, records = await paginate_queryset(queryset, params.page, params.limit)
    return success(
        build_page_payload(
            [build_audit_log_out(item).model_dump(mode="json") for item in records],
            total,
        )
    )


async def list_audit_logs(params: AuditLogQuery | None, current_user: CurrentAdminUser):
    params = params or AuditLogQuery(limit=500)
    queryset = AdminCompatAuditLog.all()
    if params.auditType:
        queryset = queryset.filter(audit_type__contains=params.auditType)
    if params.actorName:
        queryset = queryset.filter(actor_name__contains=params.actorName)
    if params.riskLevel:
        queryset = queryset.filter(risk_level=params.riskLevel)
    if params.targetType:
        queryset = queryset.filter(target_type=params.targetType)
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)

    records = await queryset.order_by("-create_time").all()
    return success([build_audit_log_out(item).model_dump(mode="json") for item in records])
