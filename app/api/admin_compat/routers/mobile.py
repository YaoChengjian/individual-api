from fastapi import APIRouter, Body, File, Request, UploadFile

from app.api.admin_compat.schemas import (
    AppTaskDetailForm,
    AppTaskQuery,
    AppWorkOrderPushItem,
    H5DictionaryQuery,
    H5LoginForm,
    H5TaskForm,
    H5TaskQuery,
    H5WorkOrderBatchForm,
)
from app.api.admin_compat.services import mobile as mobile_service
from app.common.utils.response import JsonResponse

h5_router = APIRouter(prefix="/h5")
app_router = APIRouter(prefix="/app")


async def _current_h5_user(request: Request):
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return await mobile_service.resolve_mobile_user(auth_header.split(" ", 1)[1].strip())


@h5_router.post("/login", summary="H5 巡查员登录", tags=["H5巡查端"])
async def h5_login(form: H5LoginForm):
    return JsonResponse(await mobile_service.login(form))


@h5_router.post("/dictionary/list", summary="H5 查询字典数据", tags=["H5巡查端"])
async def h5_dictionary_list(form: H5DictionaryQuery):
    return JsonResponse(await mobile_service.list_dictionary_data(form.dictCode))


@h5_router.post("/task/page", summary="H5 巡查任务列表", tags=["H5巡查端"])
async def h5_task_page(request: Request, params: H5TaskQuery = Body(default_factory=H5TaskQuery)):
    return JsonResponse(await mobile_service.page_h5_tasks(params))


@h5_router.post("/task/detail", summary="H5 巡查任务详情", tags=["H5巡查端"])
async def h5_task_detail(request: Request, form: H5TaskForm):
    return JsonResponse(await mobile_service.h5_task_detail(form))


@h5_router.post("/task/start", summary="H5 开始巡查任务", tags=["H5巡查端"])
async def h5_task_start(request: Request, form: H5TaskForm):
    return JsonResponse(await mobile_service.start_task(form))


@h5_router.post("/task/finish", summary="H5 结束巡查任务", tags=["H5巡查端"])
async def h5_task_finish(request: Request, form: H5TaskForm):
    return JsonResponse(await mobile_service.finish_task(form))


@h5_router.post("/task/work-orders", summary="H5 查询任务关联工单", tags=["H5巡查端"])
async def h5_task_work_orders(request: Request, form: H5TaskForm):
    return JsonResponse(await mobile_service.task_work_orders(form))


@h5_router.post("/task/work-orders/bind", summary="H5 多选关联任务工单", tags=["H5巡查端"])
async def h5_task_work_orders_bind(request: Request, form: H5WorkOrderBatchForm):
    return JsonResponse(await mobile_service.bind_task_work_orders(form))


@h5_router.post("/upload", summary="H5 上传打印文书", tags=["H5巡查端"])
async def h5_upload_print_file(file: UploadFile = File(...)):
    return JsonResponse(await mobile_service.upload_h5_print_file(file))


@app_router.post("/task/page", summary="App 巡查任务列表", tags=["App接口"])
async def app_task_page(params: AppTaskQuery = Body(default_factory=AppTaskQuery)):
    return JsonResponse(await mobile_service.app_task_page(params))


@app_router.post("/task/detail", summary="App 巡查任务详情", tags=["App接口"])
async def app_task_detail(form: AppTaskDetailForm):
    return JsonResponse(await mobile_service.app_task_detail(form))


@app_router.post("/work-order/push", summary="App 智能巡查推送工单", tags=["App接口"])
async def app_work_order_push(items: list[AppWorkOrderPushItem]):
    return JsonResponse(await mobile_service.app_push_work_orders(items))
