from fastapi import APIRouter, Request

from app.api.admin_compat.deps import CompatAuthRoute, get_admin_user_from_request
from app.api.admin_compat.schemas import (
    UserMessageQuery,
    UserMessageRemoveForm,
    UserMessageStatusUpdateForm,
)
from app.api.admin_compat.services import message as message_service
from app.common.decorators.log import log_api
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/user/message", route_class=CompatAuthRoute)


@router.post("/unread/list", summary="查询未处理消息", tags=["管理台兼容层-消息"])
async def list_unread_user_messages(request: Request):
    return JsonResponse(
        await message_service.list_unread_user_messages(
            get_admin_user_from_request(request)
        )
    )


@router.post("/page", summary="分页查询用户消息", tags=["管理台兼容层-消息"])
async def page_user_messages(params: UserMessageQuery, request: Request):
    return JsonResponse(
        await message_service.page_user_messages(
            params, get_admin_user_from_request(request)
        )
    )


@router.post("/status/update", summary="更新消息状态", tags=["管理台兼容层-消息"])
@log_api
async def update_user_message_status(
    form: UserMessageStatusUpdateForm,
    request: Request,
):
    return JsonResponse(
        await message_service.update_user_message_status(
            form, get_admin_user_from_request(request)
        )
    )


@router.post("/remove", summary="删除消息", tags=["管理台兼容层-消息"])
@log_api
async def remove_user_messages(form: UserMessageRemoveForm, request: Request):
    return JsonResponse(
        await message_service.remove_user_messages(
            form, get_admin_user_from_request(request)
        )
    )
