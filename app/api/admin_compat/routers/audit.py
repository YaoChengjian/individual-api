from fastapi import APIRouter, Body, Request

from app.api.admin_compat.deps import CompatAuthRoute, get_admin_user_from_request
from app.api.admin_compat.schemas import AuditLogQuery
from app.api.admin_compat.services import audit as audit_service
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/system/audit-log", route_class=CompatAuthRoute)


@router.post("/page", summary="分页查询审计日志", tags=["管理台兼容层-审计日志"])
async def page_audit_logs(params: AuditLogQuery, request: Request):
    return JsonResponse(
        await audit_service.page_audit_logs(params, get_admin_user_from_request(request))
    )


@router.post("/list", summary="查询审计日志列表", tags=["管理台兼容层-审计日志"])
async def list_audit_logs(
    request: Request,
    params: AuditLogQuery = Body(default_factory=AuditLogQuery),
):
    return JsonResponse(
        await audit_service.list_audit_logs(params, get_admin_user_from_request(request))
    )
