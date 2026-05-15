from fastapi import APIRouter, Body

from fastapi import Request

from app.api.admin_compat.deps import CompatAuthRoute, get_admin_user_from_request
from app.api.admin_compat.schemas import (
    PatrolAreaForm,
    PatrolPointForm,
    PatrolPointRemoveForm,
    PatrolTaskCreateForm,
    PatrolTaskDetailForm,
    PatrolTaskQuery,
    PatrolTaskTourForm,
    PatrolTaskUpdateForm,
    PatrolTaskWorkOrderQuery,
    H5TaskForm,
)
from app.api.admin_compat.services import task as task_service
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/task", route_class=CompatAuthRoute)


@router.post("/page", summary="分页查询巡查任务", tags=["管理台兼容层-任务管理"])
async def page_tasks(params: PatrolTaskQuery):
    return JsonResponse(await task_service.page_tasks(params))


@router.post("/list", summary="查询巡查任务列表", tags=["管理台兼容层-任务管理"])
async def list_tasks(params: PatrolTaskQuery = Body(default_factory=PatrolTaskQuery)):
    return JsonResponse(await task_service.list_tasks(params))


@router.post("/summary", summary="查询巡查任务统计", tags=["管理台兼容层-任务管理"])
async def task_summary(params: PatrolTaskQuery = Body(default_factory=PatrolTaskQuery)):
    return JsonResponse(await task_service.task_summary(params))


@router.post("/detail", summary="查询巡查任务详情", tags=["管理台兼容层-任务管理"])
async def task_detail(form: PatrolTaskDetailForm):
    return JsonResponse(await task_service.task_detail(form))


@router.post("/work-orders/printed", summary="查询巡查任务已打印工单", tags=["管理台兼容层-任务管理"])
async def task_printed_work_orders(form: H5TaskForm):
    return JsonResponse(await task_service.printed_work_orders(form))


@router.post("/work-orders/printed/page", summary="分页查询巡查任务已打印工单", tags=["管理台兼容层-任务管理"])
async def page_task_printed_work_orders(params: PatrolTaskWorkOrderQuery):
    return JsonResponse(await task_service.page_printed_work_orders(params))


@router.post("/create-options", summary="查询新建巡查任务表单数据", tags=["管理台兼容层-任务管理"])
async def get_task_create_options():
    return JsonResponse(await task_service.get_task_create_options())


@router.post("/area/list", summary="查询巡查社区面", tags=["管理台兼容层-任务管理"])
async def list_patrol_areas():
    return JsonResponse(await task_service.list_patrol_areas())


@router.post("/area/save", summary="保存巡查社区面", tags=["管理台兼容层-任务管理"])
async def save_patrol_area(form: PatrolAreaForm):
    return JsonResponse(await task_service.save_patrol_area(form))


@router.post("/point/list", summary="查询巡查点位", tags=["管理台兼容层-任务管理"])
async def list_patrol_points(area_ids: list[int] = Body(default_factory=list)):
    return JsonResponse(await task_service.list_patrol_points(area_ids))


@router.post("/point/add", summary="新增巡查点位", tags=["管理台兼容层-任务管理"])
async def add_patrol_point(form: PatrolPointForm):
    return JsonResponse(await task_service.add_patrol_point(form))


@router.post("/point/remove", summary="删除巡查点位", tags=["管理台兼容层-任务管理"])
async def remove_patrol_point(form: PatrolPointRemoveForm):
    return JsonResponse(await task_service.remove_patrol_point(form))


@router.post("/executor/list", summary="查询巡查员与设备", tags=["管理台兼容层-任务管理"])
async def list_patrol_executors():
    return JsonResponse(await task_service.list_patrol_executors())


@router.post("/add", summary="新增巡查任务", tags=["管理台兼容层-任务管理"])
async def create_task(form: PatrolTaskCreateForm, request: Request):
    return JsonResponse(
        await task_service.create_task(form, get_admin_user_from_request(request))
    )


@router.post("/update", summary="编辑巡查任务", tags=["管理台兼容层-任务管理"])
async def update_task(form: PatrolTaskUpdateForm, request: Request):
    return JsonResponse(
        await task_service.update_task(form, get_admin_user_from_request(request))
    )


@router.post("/tour/status", summary="查询任务管理引导状态", tags=["管理台兼容层-任务管理"])
async def get_tour_status(
    request: Request,
    form: PatrolTaskTourForm = Body(default_factory=PatrolTaskTourForm),
):
    return JsonResponse(
        await task_service.get_tour_status(form, get_admin_user_from_request(request))
    )


@router.post("/tour/hide-today", summary="今日不再提示任务管理引导", tags=["管理台兼容层-任务管理"])
async def hide_tour_today(
    request: Request,
    form: PatrolTaskTourForm = Body(default_factory=PatrolTaskTourForm),
):
    return JsonResponse(
        await task_service.hide_tour_today(form, get_admin_user_from_request(request))
    )
