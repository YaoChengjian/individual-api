from app.api.admin_compat.helpers import build_page_payload, paginate_queryset, resolve_order_field
from app.api.admin_compat.models import AdminCompatUserMessage
from app.api.admin_compat.schemas import (
    CurrentAdminUser,
    UserMessageQuery,
    UserMessageRemoveForm,
    UserMessageStatusUpdateForm,
    UserMessageUnread,
)
from app.api.admin_compat.services.common import build_message_out
from app.common.utils.response import fail, success


async def list_unread_user_messages(current_user: CurrentAdminUser):
    messages = await AdminCompatUserMessage.filter(
        user_id=current_user.user_id,
        status=0,
    ).order_by("-message_time")
    notices = []
    letters = []
    todos = []
    for message in messages:
        payload = build_message_out(message)
        if message.message_type == "notice":
            notices.append(payload)
        elif message.message_type == "letter":
            letters.append(payload)
        elif message.message_type == "todo":
            todos.append(payload)

    return success(
        UserMessageUnread(notices=notices, letters=letters, todos=todos),
        msg="获取成功",
    )


async def page_user_messages(params: UserMessageQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatUserMessage.filter(
        user_id=current_user.user_id,
        message_type=params.messageType,
    )
    if params.title:
        queryset = queryset.filter(title__contains=params.title)
    if params.keywords:
        queryset = queryset.filter(title__contains=params.keywords)
    if params.status in (0, 1):
        queryset = queryset.filter(status=params.status)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"time": "message_time", "status": "status", "title": "title"},
        "-message_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [build_message_out(item).model_dump(mode="json") for item in data]
    return success(build_page_payload(items, total))


async def update_user_message_status(
    form: UserMessageStatusUpdateForm,
    current_user: CurrentAdminUser,
):
    if not form.ids:
        return fail(1, "请选择消息")

    await AdminCompatUserMessage.filter(
        id__in=form.ids,
        user_id=current_user.user_id,
        message_type=form.messageType,
    ).update(status=1)
    return success(msg="操作成功")


async def remove_user_messages(
    form: UserMessageRemoveForm,
    current_user: CurrentAdminUser,
):
    if not form.ids:
        return fail(1, "请选择消息")

    await AdminCompatUserMessage.filter(
        id__in=form.ids,
        user_id=current_user.user_id,
    ).delete()
    return success(msg="删除成功")
