from pathlib import Path

from app.api.admin_compat.constants import MAX_UPLOAD_MB, UPLOAD_SUFFIXES
from app.api.admin_compat.helpers import (
    build_page_payload,
    decode_base64_payload,
    guess_content_type,
    paginate_queryset,
    resolve_order_field,
)
from app.api.admin_compat.models import AdminCompatFileRecord, AdminCompatUser
from app.api.admin_compat.schemas import CurrentAdminUser, FileRecordQuery
from app.api.admin_compat.services.common import build_file_record_out, build_file_records_out
from app.common.utils.file_utils import FileUtils
from app.common.utils.response import fail, success
from app.config import ConfigClass


async def upload_file(file, current_user: CurrentAdminUser):
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    payload = await FileUtils.upload_file(
        file,
        limit_type=UPLOAD_SUFFIXES,
        limit_mb=MAX_UPLOAD_MB,
    )
    record = await AdminCompatFileRecord.create(
        name=payload["file_name"],
        path=payload["file_path"],
        length=file_size,
        content_type=file.content_type,
        create_user_id=current_user.user_id,
    )
    return success((await build_file_record_out(record)).model_dump(mode="json"))


async def upload_base64_file(base64_data: str, file_name: str | None, current_user: CurrentAdminUser):
    content, content_type = decode_base64_payload(base64_data)
    suffix = Path(file_name or "upload.bin").suffix or ".bin"
    save_info = await FileUtils.get_save_filepath(FileUtils.upload_dir, suffix)
    with open(save_info["save_path"], "wb") as target:
        target.write(content)

    record = await AdminCompatFileRecord.create(
        name=file_name or Path(save_info["db_path"]).name,
        path=save_info["db_path"],
        length=len(content),
        content_type=guess_content_type(file_name, content_type),
        create_user_id=current_user.user_id,
    )
    return success((await build_file_record_out(record)).model_dump(mode="json"))


async def page_files(params: FileRecordQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatFileRecord.all()
    if params.name:
        queryset = queryset.filter(name__contains=params.name)
    if params.path:
        queryset = queryset.filter(path__contains=params.path)
    if params.createNickname:
        user_ids = await AdminCompatUser.filter(
            nickname__contains=params.createNickname
        ).values_list("id", flat=True)
        queryset = queryset.filter(create_user_id__in=user_ids)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "createTime": "create_time",
            "length": "length",
            "name": "name",
            "path": "path",
        },
        "-create_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [item.model_dump(mode="json") for item in await build_file_records_out(data)]
    return success(build_page_payload(items, total))


async def list_files(params: FileRecordQuery | None = None, current_user: CurrentAdminUser | None = None):
    params = params or FileRecordQuery(limit=500)
    queryset = AdminCompatFileRecord.all()
    if params.name:
        queryset = queryset.filter(name__contains=params.name)
    if params.path:
        queryset = queryset.filter(path__contains=params.path)
    if params.createNickname:
        user_ids = await AdminCompatUser.filter(
            nickname__contains=params.createNickname
        ).values_list("id", flat=True)
        queryset = queryset.filter(create_user_id__in=user_ids)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"createTime": "create_time", "length": "length", "name": "name"},
        "-create_time",
    )
    data = await queryset.order_by(order_by).all()
    return success([item.model_dump(mode="json") for item in await build_file_records_out(data)])


async def remove_file(file_id: int, current_user: CurrentAdminUser):
    record = await AdminCompatFileRecord.get_or_none(
        id=file_id,
    )
    if not record:
        return fail(1, "文件不存在")
    await _delete_file_record(record)
    return success(msg="删除成功")


async def remove_files(file_ids: list[int], current_user: CurrentAdminUser):
    if not file_ids:
        return fail(1, "请选择要删除的文件")
    data = await AdminCompatFileRecord.filter(
        id__in=file_ids,
    ).all()
    for record in data:
        await _delete_file_record(record)
    return success(msg="批量删除成功")


async def _delete_file_record(record: AdminCompatFileRecord):
    absolute_path = Path(ConfigClass.BASE_DIR) / record.path.lstrip("/")
    FileUtils.force_delete(str(absolute_path))
    await record.delete()
