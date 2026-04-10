from fastapi import APIRouter, Body, File, Request, UploadFile

from app.api.admin_compat.deps import CompatAuthRoute, get_admin_user_from_request
from app.api.admin_compat.schemas import (
    DictionaryDataForm,
    DictionaryDataQuery,
    DictionaryForm,
    DictionaryQuery,
    ExistenceCheckForm,
    LoginRecordQuery,
    MenuForm,
    MenuQuery,
    OperationRecordQuery,
    OrganizationForm,
    OrganizationQuery,
    RoleForm,
    RoleQuery,
    UserFileForm,
    UserFileQuery,
    UserForm,
    UserPasswordResetForm,
    UserQuery,
    UserStatusUpdateForm,
)
from app.api.admin_compat.services import system as system_service
from app.common.decorators.log import log_api
from app.common.utils.response import JsonResponse

router = APIRouter(prefix="/system", route_class=CompatAuthRoute)


@router.post("/role/page", summary="分页查询角色", tags=["管理台兼容层-系统管理"])
async def page_roles(params: RoleQuery):
    return JsonResponse(await system_service.page_roles(params))


@router.post("/role/list", summary="查询角色列表", tags=["管理台兼容层-系统管理"])
async def list_roles(params: RoleQuery = Body(default_factory=RoleQuery)):
    return JsonResponse(await system_service.list_roles(params))


@router.post("/role/add", summary="新增角色", tags=["管理台兼容层-系统管理"])
@log_api
async def add_role(form: RoleForm):
    return JsonResponse(await system_service.add_role(form))


@router.post("/role/update", summary="修改角色", tags=["管理台兼容层-系统管理"])
@log_api
async def update_role(form: RoleForm):
    return JsonResponse(await system_service.update_role(form))


@router.post("/role/remove/{role_id}", summary="删除角色", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_role(role_id: int):
    return JsonResponse(await system_service.remove_role(role_id))


@router.post("/role/remove/batch", summary="批量删除角色", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_roles(role_ids: list[int]):
    return JsonResponse(await system_service.remove_roles(role_ids))


@router.post("/role-menu/list/{role_id}", summary="查询角色菜单", tags=["管理台兼容层-系统管理"])
async def list_role_menus(role_id: int):
    return JsonResponse(await system_service.list_role_menus(role_id))


@router.post("/role-menu/update/{role_id}", summary="更新角色菜单", tags=["管理台兼容层-系统管理"])
@log_api
async def update_role_menus(role_id: int, menu_ids: list[int]):
    return JsonResponse(await system_service.update_role_menus(role_id, menu_ids))


@router.post("/user/page", summary="分页查询用户", tags=["管理台兼容层-系统管理"])
async def page_users(params: UserQuery):
    return JsonResponse(await system_service.page_users(params))


@router.post("/user/list", summary="查询用户列表", tags=["管理台兼容层-系统管理"])
async def list_users(params: UserQuery = Body(default_factory=UserQuery)):
    return JsonResponse(await system_service.list_users(params))


@router.post("/user/detail/{user_id}", summary="查询用户详情", tags=["管理台兼容层-系统管理"])
async def get_user_detail(user_id: int):
    return JsonResponse(await system_service.get_user_detail(user_id))


@router.post("/user/add", summary="新增用户", tags=["管理台兼容层-系统管理"])
@log_api
async def add_user(form: UserForm):
    return JsonResponse(await system_service.add_user(form))


@router.post("/user/update", summary="修改用户", tags=["管理台兼容层-系统管理"])
@log_api
async def update_user(form: UserForm):
    return JsonResponse(await system_service.update_user(form))


@router.post("/user/remove/{user_id}", summary="删除用户", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_user(user_id: int, request: Request):
    return JsonResponse(
        await system_service.remove_user(user_id, get_admin_user_from_request(request))
    )


@router.post("/user/remove/batch", summary="批量删除用户", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_users(user_ids: list[int], request: Request):
    return JsonResponse(
        await system_service.remove_users(user_ids, get_admin_user_from_request(request))
    )


@router.post("/user/status/update", summary="更新用户状态", tags=["管理台兼容层-系统管理"])
@log_api
async def update_user_status(form: UserStatusUpdateForm, request: Request):
    return JsonResponse(
        await system_service.update_user_status(form, get_admin_user_from_request(request))
    )


@router.post("/user/password/update", summary="重置用户密码", tags=["管理台兼容层-系统管理"])
@log_api
async def update_user_password(form: UserPasswordResetForm):
    return JsonResponse(await system_service.update_user_password(form))


@router.post("/user/import", summary="导入用户", tags=["管理台兼容层-系统管理"])
@log_api
async def import_users(file: UploadFile = File(...)):
    return JsonResponse(await system_service.import_users(file))


@router.post("/user/existence", summary="检查用户字段是否存在", tags=["管理台兼容层-系统管理"])
async def check_user_existence(form: ExistenceCheckForm):
    return JsonResponse(await system_service.check_user_existence(form))


@router.post("/menu/page", summary="分页查询菜单", tags=["管理台兼容层-系统管理"])
async def page_menus(params: MenuQuery):
    return JsonResponse(await system_service.page_menus(params))


@router.post("/menu/list", summary="查询菜单列表", tags=["管理台兼容层-系统管理"])
async def list_menus(params: MenuQuery = Body(default_factory=MenuQuery)):
    return JsonResponse(await system_service.list_menus(params))


@router.post("/menu/add", summary="新增菜单", tags=["管理台兼容层-系统管理"])
@log_api
async def add_menu(form: MenuForm):
    return JsonResponse(await system_service.add_menu(form))


@router.post("/menu/update", summary="修改菜单", tags=["管理台兼容层-系统管理"])
@log_api
async def update_menu(form: MenuForm):
    return JsonResponse(await system_service.update_menu(form))


@router.post("/menu/remove/{menu_id}", summary="删除菜单", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_menu(menu_id: int):
    return JsonResponse(await system_service.remove_menu(menu_id))


@router.post("/organization/page", summary="分页查询机构", tags=["管理台兼容层-系统管理"])
async def page_organizations(params: OrganizationQuery):
    return JsonResponse(await system_service.page_organizations(params))


@router.post("/organization/list", summary="查询机构列表", tags=["管理台兼容层-系统管理"])
async def list_organizations(params: OrganizationQuery = Body(default_factory=OrganizationQuery)):
    return JsonResponse(await system_service.list_organizations(params))


@router.post("/organization/tree", summary="查询机构树", tags=["管理台兼容层-系统管理"])
async def list_organizations_tree(
    params: OrganizationQuery = Body(default_factory=OrganizationQuery),
):
    return JsonResponse(await system_service.list_organizations_tree(params))


@router.post("/organization/add", summary="新增机构", tags=["管理台兼容层-系统管理"])
@log_api
async def add_organization(form: OrganizationForm):
    return JsonResponse(await system_service.add_organization(form))


@router.post("/organization/update", summary="修改机构", tags=["管理台兼容层-系统管理"])
@log_api
async def update_organization(form: OrganizationForm):
    return JsonResponse(await system_service.update_organization(form))


@router.post("/organization/remove/{organization_id}", summary="删除机构", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_organization(organization_id: int):
    return JsonResponse(await system_service.remove_organization(organization_id))


@router.post("/dictionary/page", summary="查询字典列表", tags=["管理台兼容层-系统管理"])
async def page_dictionaries(params: DictionaryQuery):
    return JsonResponse(await system_service.page_dictionaries(params))


@router.post("/dictionary/list", summary="查询字典列表", tags=["管理台兼容层-系统管理"])
async def list_dictionaries(params: DictionaryQuery = Body(default_factory=DictionaryQuery)):
    return JsonResponse(await system_service.list_dictionaries(params))


@router.post("/dictionary/add", summary="新增字典", tags=["管理台兼容层-系统管理"])
@log_api
async def add_dictionary(form: DictionaryForm):
    return JsonResponse(await system_service.add_dictionary(form))


@router.post("/dictionary/update", summary="修改字典", tags=["管理台兼容层-系统管理"])
@log_api
async def update_dictionary(form: DictionaryForm):
    return JsonResponse(await system_service.update_dictionary(form))


@router.post("/dictionary/remove/{dictionary_id}", summary="删除字典", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_dictionary(dictionary_id: int):
    return JsonResponse(await system_service.remove_dictionary(dictionary_id))


@router.post("/dictionary-data/page", summary="分页查询字典数据", tags=["管理台兼容层-系统管理"])
async def page_dictionary_data(params: DictionaryDataQuery):
    return JsonResponse(await system_service.page_dictionary_data(params))


@router.post("/dictionary-data/list", summary="查询字典数据列表", tags=["管理台兼容层-系统管理"])
async def list_dictionary_data(
    params: DictionaryDataQuery = Body(default_factory=DictionaryDataQuery),
):
    return JsonResponse(await system_service.list_dictionary_data(params))


@router.post("/dictionary-data/add", summary="新增字典数据", tags=["管理台兼容层-系统管理"])
@log_api
async def add_dictionary_data(form: DictionaryDataForm):
    return JsonResponse(await system_service.add_dictionary_data(form))


@router.post("/dictionary-data/update", summary="修改字典数据", tags=["管理台兼容层-系统管理"])
@log_api
async def update_dictionary_data(form: DictionaryDataForm):
    return JsonResponse(await system_service.update_dictionary_data(form))


@router.post("/dictionary-data/remove/{detail_id}", summary="删除字典数据", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_dictionary_data(detail_id: int):
    return JsonResponse(await system_service.remove_dictionary_data(detail_id))


@router.post("/dictionary-data/remove/batch", summary="批量删除字典数据", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_dictionary_data_batch(detail_ids: list[int]):
    return JsonResponse(await system_service.remove_dictionary_data_batch(detail_ids))


@router.post("/login-record/page", summary="分页查询登录日志", tags=["管理台兼容层-系统管理"])
async def page_login_records(params: LoginRecordQuery):
    return JsonResponse(await system_service.page_login_records(params))


@router.post("/login-record/list", summary="查询登录日志列表", tags=["管理台兼容层-系统管理"])
async def list_login_records(params: LoginRecordQuery = Body(default_factory=LoginRecordQuery)):
    return JsonResponse(await system_service.list_login_records(params))


@router.post("/operation-record/page", summary="分页查询操作日志", tags=["管理台兼容层-系统管理"])
async def page_operation_records(params: OperationRecordQuery):
    return JsonResponse(await system_service.page_operation_records(params))


@router.post("/operation-record/list", summary="查询操作日志列表", tags=["管理台兼容层-系统管理"])
async def list_operation_records(
    params: OperationRecordQuery = Body(default_factory=OperationRecordQuery),
):
    return JsonResponse(await system_service.list_operation_records(params))


@router.post("/user-file/page", summary="分页查询用户文件", tags=["管理台兼容层-系统管理"])
async def page_user_files(params: UserFileQuery, request: Request):
    return JsonResponse(
        await system_service.page_user_files(params, get_admin_user_from_request(request))
    )


@router.post("/user-file/list", summary="查询用户文件列表", tags=["管理台兼容层-系统管理"])
async def list_user_files(
    request: Request,
    params: UserFileQuery = Body(default_factory=UserFileQuery),
):
    return JsonResponse(
        await system_service.list_user_files(params, get_admin_user_from_request(request))
    )


@router.post("/user-file/add", summary="新增用户文件", tags=["管理台兼容层-系统管理"])
@log_api
async def add_user_file(form: UserFileForm, request: Request):
    return JsonResponse(
        await system_service.add_user_file(form, get_admin_user_from_request(request))
    )


@router.post("/user-file/update", summary="修改用户文件", tags=["管理台兼容层-系统管理"])
@log_api
async def update_user_file(form: UserFileForm, request: Request):
    return JsonResponse(
        await system_service.update_user_file(form, get_admin_user_from_request(request))
    )


@router.post("/user-file/remove/{file_id}", summary="删除用户文件", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_user_file(file_id: int, request: Request):
    return JsonResponse(
        await system_service.remove_user_file(file_id, get_admin_user_from_request(request))
    )


@router.post("/user-file/remove/batch", summary="批量删除用户文件", tags=["管理台兼容层-系统管理"])
@log_api
async def remove_user_files(file_ids: list[int], request: Request):
    return JsonResponse(
        await system_service.remove_user_files(file_ids, get_admin_user_from_request(request))
    )
