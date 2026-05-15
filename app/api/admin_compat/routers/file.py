from fastapi import APIRouter, Body, File, Form, Request, UploadFile

from app.api.admin_compat.deps import CompatAuthRoute, get_admin_user_from_request
from app.api.admin_compat.schemas import FileRecordQuery
from app.api.admin_compat.services import file as file_service
from app.common.decorators.log import log_api
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/file", route_class=CompatAuthRoute)


@router.post("/upload", summary="上传文件", tags=["管理台兼容层-文件"])
@log_api
async def upload_file(request: Request, file: UploadFile = File(...)):
    return JsonResponse(
        await file_service.upload_file(file, get_admin_user_from_request(request))
    )


@router.post("/upload/base64", summary="上传 base64 文件", tags=["管理台兼容层-文件"])
@log_api
async def upload_base64_file(
    request: Request,
    base64: str = Form(...),
    fileName: str | None = Form(None),
):
    return JsonResponse(
        await file_service.upload_base64_file(
            base64, fileName, get_admin_user_from_request(request)
        )
    )


@router.post("/page", summary="分页查询文件", tags=["管理台兼容层-文件"])
async def page_files(params: FileRecordQuery, request: Request):
    return JsonResponse(
        await file_service.page_files(params, get_admin_user_from_request(request))
    )


@router.post("/list", summary="查询文件列表", tags=["管理台兼容层-文件"])
async def list_files(
    request: Request,
    params: FileRecordQuery = Body(default_factory=FileRecordQuery),
):
    return JsonResponse(
        await file_service.list_files(params, get_admin_user_from_request(request))
    )


@router.post("/remove/{file_id}", summary="删除文件", tags=["管理台兼容层-文件"])
@log_api
async def remove_file(file_id: int, request: Request):
    return JsonResponse(
        await file_service.remove_file(file_id, get_admin_user_from_request(request))
    )


@router.post("/remove/batch", summary="批量删除文件", tags=["管理台兼容层-文件"])
@log_api
async def remove_files(file_ids: list[int], request: Request):
    return JsonResponse(
        await file_service.remove_files(file_ids, get_admin_user_from_request(request))
    )
