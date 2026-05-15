from fastapi import APIRouter, Body

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
from app.api.admin_compat.services import patrol_mvp as patrol_mvp_service
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/patrol-mvp")


@router.post("/ensure-demo", summary="初始化智能单兵巡查演示数据", tags=["智能单兵巡查闭环"])
async def ensure_demo():
    return JsonResponse(await patrol_mvp_service.ensure_demo())


@router.post("/reset-demo", summary="重置智能单兵巡查演示数据", tags=["智能单兵巡查闭环"])
async def reset_demo():
    return JsonResponse(await patrol_mvp_service.reset_demo())


@router.post("/task/create", summary="创建巡查任务", tags=["智能单兵巡查闭环"])
async def create_task(form: PatrolMvpTaskCreateForm):
    return JsonResponse(await patrol_mvp_service.create_task(form))


@router.post("/task/page", summary="分页查询巡查任务", tags=["智能单兵巡查闭环"])
async def page_tasks(params: PatrolMvpQuery = Body(default_factory=PatrolMvpQuery)):
    return JsonResponse(await patrol_mvp_service.page_tasks(params))


@router.post("/h5/tasks", summary="H5 查询我的巡查任务", tags=["智能单兵巡查闭环"])
async def h5_tasks(params: PatrolMvpQuery = Body(default_factory=PatrolMvpQuery)):
    return JsonResponse(await patrol_mvp_service.h5_tasks(params))


@router.post("/task/detail", summary="查询巡查任务详情", tags=["智能单兵巡查闭环"])
async def task_detail(form: PatrolMvpTaskForm):
    return JsonResponse(await patrol_mvp_service.task_detail(form))


@router.post("/task/dispatch", summary="下发巡查任务", tags=["智能单兵巡查闭环"])
async def dispatch_task(form: PatrolMvpTaskForm):
    return JsonResponse(await patrol_mvp_service.dispatch_task(form))


@router.post("/task/receive", summary="H5 接收任务", tags=["智能单兵巡查闭环"])
async def receive_task(form: PatrolMvpTaskForm):
    return JsonResponse(await patrol_mvp_service.receive_task(form))


@router.post("/task/start-going", summary="H5 开始前往", tags=["智能单兵巡查闭环"])
async def start_going(form: PatrolMvpTaskPointForm):
    return JsonResponse(await patrol_mvp_service.start_going(form))


@router.post("/task/arrive", summary="H5 确认到达点位", tags=["智能单兵巡查闭环"])
async def arrive_point(form: PatrolMvpTaskPointForm):
    return JsonResponse(await patrol_mvp_service.arrive_point(form))


@router.post("/task/start-inspection", summary="H5 开始巡查", tags=["智能单兵巡查闭环"])
async def start_inspection(form: PatrolMvpTaskPointForm):
    return JsonResponse(await patrol_mvp_service.start_inspection(form))


@router.post("/ai/mock-detect", summary="触发 AI 模拟识别", tags=["智能单兵巡查闭环"])
async def mock_detect(form: PatrolMvpDetectForm):
    return JsonResponse(await patrol_mvp_service.mock_detect(form))


@router.post("/evidence/capture", summary="创建取证记录", tags=["智能单兵巡查闭环"])
async def capture_evidence(form: PatrolMvpEvidenceForm):
    return JsonResponse(await patrol_mvp_service.capture_evidence(form))


@router.post("/work-order/generate-draft", summary="生成工单草稿", tags=["智能单兵巡查闭环"])
async def generate_work_order_draft(form: PatrolMvpWorkOrderDraftForm):
    return JsonResponse(await patrol_mvp_service.generate_work_order_draft(form))


@router.post("/work-order/update", summary="更新工单草稿", tags=["智能单兵巡查闭环"])
async def update_work_order(form: PatrolMvpWorkOrderForm):
    return JsonResponse(await patrol_mvp_service.update_work_order(form))


@router.post("/work-order/submit", summary="提交工单", tags=["智能单兵巡查闭环"])
async def submit_work_order(form: PatrolMvpWorkOrderForm):
    return JsonResponse(await patrol_mvp_service.submit_work_order(form))


@router.post("/work-order/page", summary="分页查询工单", tags=["智能单兵巡查闭环"])
async def page_work_orders(params: PatrolMvpQuery = Body(default_factory=PatrolMvpQuery)):
    return JsonResponse(await patrol_mvp_service.page_work_orders(params))


@router.post("/work-order/detail", summary="查询工单详情", tags=["智能单兵巡查闭环"])
async def work_order_detail(form: PatrolMvpWorkOrderForm):
    return JsonResponse(await patrol_mvp_service.work_order_detail(form))


@router.post("/work-order/push", summary="一键推送第三方平台 mock", tags=["智能单兵巡查闭环"])
async def push_work_order(form: PatrolMvpWorkOrderForm):
    return JsonResponse(await patrol_mvp_service.push_work_order(form))


@router.post("/push-record/page", summary="分页查询推送日志", tags=["智能单兵巡查闭环"])
async def page_push_records(params: PatrolMvpQuery = Body(default_factory=PatrolMvpQuery)):
    return JsonResponse(await patrol_mvp_service.page_push_records(params))


@router.post("/document/generate", summary="生成整改通知书", tags=["智能单兵巡查闭环"])
async def generate_document(form: PatrolMvpDocumentForm):
    return JsonResponse(await patrol_mvp_service.generate_document(form))


@router.post("/document/detail", summary="查询文书详情", tags=["智能单兵巡查闭环"])
async def document_detail(form: PatrolMvpDocumentForm):
    return JsonResponse(await patrol_mvp_service.document_detail(form))


@router.post("/document/page", summary="分页查询文书", tags=["智能单兵巡查闭环"])
async def page_documents(params: PatrolMvpQuery = Body(default_factory=PatrolMvpQuery)):
    return JsonResponse(await patrol_mvp_service.page_documents(params))


@router.post("/document/mock-print", summary="H5 模拟打印文书", tags=["智能单兵巡查闭环"])
async def mock_print_document(form: PatrolMvpDocumentForm):
    return JsonResponse(await patrol_mvp_service.mock_print_document(form))


@router.post("/task/close", summary="闭环任务", tags=["智能单兵巡查闭环"])
async def close_task(form: PatrolMvpTaskForm):
    return JsonResponse(await patrol_mvp_service.close_task(form))


@router.post("/task/closure-summary", summary="查询任务闭环摘要", tags=["智能单兵巡查闭环"])
async def closure_summary(form: PatrolMvpTaskForm):
    return JsonResponse(await patrol_mvp_service.closure_summary(form))


@router.post("/integration/work-orders/status-callback", summary="第三方工单状态回调预留", tags=["智能单兵巡查闭环"])
async def integration_status_callback(form: PatrolMvpCallbackForm):
    return JsonResponse(await patrol_mvp_service.integration_status_callback(form))
