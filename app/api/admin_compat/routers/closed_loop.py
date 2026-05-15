from fastapi import APIRouter, Body

from app.api.admin_compat.deps import CompatAuthRoute
from app.api.admin_compat.schemas import ClosedLoopIdForm, ClosedLoopQuery, WorkOrderActionForm
from app.api.admin_compat.services import closed_loop as closed_loop_service
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/closed-loop", route_class=CompatAuthRoute)


@router.post("/dashboard/summary", summary="闭环驾驶舱统计", tags=["管理台兼容层-闭环业务"])
async def dashboard_summary():
    return JsonResponse(await closed_loop_service.dashboard_summary())


@router.post("/dashboard/map-points", summary="闭环地图点位", tags=["管理台兼容层-闭环业务"])
async def map_points():
    return JsonResponse(await closed_loop_service.map_points())


@router.post("/activity/timeline", summary="闭环流转动态", tags=["管理台兼容层-闭环业务"])
async def activity_timeline():
    return JsonResponse(await closed_loop_service.activity_timeline())


@router.post("/work-order/page", summary="分页查询事件工单", tags=["管理台兼容层-闭环业务"])
async def page_work_orders(params: ClosedLoopQuery):
    return JsonResponse(await closed_loop_service.page_work_orders(params))


@router.post("/work-order/list", summary="查询事件工单列表", tags=["管理台兼容层-闭环业务"])
async def list_work_orders(params: ClosedLoopQuery = Body(default_factory=ClosedLoopQuery)):
    return JsonResponse(await closed_loop_service.list_work_orders(params))


@router.post("/work-order/detail", summary="查询事件工单详情", tags=["管理台兼容层-闭环业务"])
async def work_order_detail(form: ClosedLoopIdForm):
    return JsonResponse(await closed_loop_service.work_order_detail(form))


@router.post("/work-order/action", summary="事件工单操作", tags=["管理台兼容层-闭环业务"])
async def work_order_action(form: WorkOrderActionForm):
    return JsonResponse(await closed_loop_service.work_order_action(form))


@router.post("/report/page", summary="分页查询闭环报告", tags=["管理台兼容层-闭环业务"])
async def page_reports(params: ClosedLoopQuery):
    return JsonResponse(await closed_loop_service.page_reports(params))


@router.post("/report/list", summary="查询闭环报告列表", tags=["管理台兼容层-闭环业务"])
async def list_reports(params: ClosedLoopQuery = Body(default_factory=ClosedLoopQuery)):
    return JsonResponse(await closed_loop_service.list_reports(params))


@router.post("/report/detail", summary="查询闭环报告详情", tags=["管理台兼容层-闭环业务"])
async def report_detail(form: ClosedLoopIdForm):
    return JsonResponse(await closed_loop_service.report_detail(form))


@router.post("/report/archive", summary="归档闭环报告", tags=["管理台兼容层-闭环业务"])
async def archive_report(form: ClosedLoopIdForm):
    return JsonResponse(await closed_loop_service.archive_report(form))


@router.post("/document/page", summary="分页查询文书", tags=["管理台兼容层-闭环业务"])
async def page_documents(params: ClosedLoopQuery):
    return JsonResponse(await closed_loop_service.page_documents(params))


@router.post("/document/list", summary="查询文书列表", tags=["管理台兼容层-闭环业务"])
async def list_documents(params: ClosedLoopQuery = Body(default_factory=ClosedLoopQuery)):
    return JsonResponse(await closed_loop_service.list_documents(params))


@router.post("/personnel/devices", summary="巡查员与设备状态", tags=["管理台兼容层-闭环业务"])
async def personnel_devices():
    return JsonResponse(await closed_loop_service.personnel_devices())
