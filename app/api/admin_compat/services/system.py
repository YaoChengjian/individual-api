from datetime import datetime

from tortoise.expressions import Q

from app.api.admin_compat.helpers import build_page_payload, paginate_queryset, resolve_order_field
from app.api.admin_compat.models import (
    AdminCompatDictionary,
    AdminCompatDictionaryData,
    AdminCompatLoginRecord,
    AdminCompatMenu,
    AdminCompatOperationRecord,
    AdminCompatOrganization,
    AdminCompatRole,
    AdminCompatRoleMenu,
    AdminCompatUser,
    AdminCompatUserFile,
    AdminCompatUserRole,
)
from app.api.admin_compat.schemas import (
    CurrentAdminUser,
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
from app.api.admin_compat.services.audit import record_audit_log
from app.api.admin_compat.services.common import (
    build_dictionary_data_out,
    build_dictionary_out,
    build_login_record_out,
    build_menu_out,
    build_operation_records_out,
    build_organization_out,
    build_role_out,
    build_user_file_out,
    build_user_out,
    build_users_out,
    load_dictionary_label_map,
)
from app.common.utils.jwt_utlis import get_password
from app.common.utils.response import fail, success


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _build_tree(items: list[dict], id_field: str, parent_field: str) -> list[dict]:
    data_map = {item[id_field]: {**item, "children": []} for item in items}
    roots = []
    for item in data_map.values():
        parent_id = item[parent_field]
        parent = data_map.get(parent_id)
        if parent:
            parent["children"].append(item)
        else:
            roots.append(item)
    return roots


async def _ensure_admin(current_user: CurrentAdminUser):
    role_codes = await _current_role_codes(current_user)
    if "admin" in role_codes:
        return None
    return fail(1, "当前账号没有管理权限")


async def _current_role_codes(current_user: CurrentAdminUser) -> set[str]:
    relations = await AdminCompatUserRole.filter(user_id=current_user.user_id).all()
    role_ids = sorted({item.role_id for item in relations})
    roles = await AdminCompatRole.filter(id__in=role_ids).all() if role_ids else []
    return {role.role_code for role in roles}


async def _sync_user_roles(user_id: int, role_refs):
    role_ids = sorted({item.roleId for item in role_refs if item.roleId})
    if role_ids:
        roles = await AdminCompatRole.filter(id__in=role_ids).all()
        if len(roles) != len(role_ids):
            return fail(1, "包含不存在的角色")
    await AdminCompatUserRole.filter(user_id=user_id).delete()
    if role_ids:
        await AdminCompatUserRole.bulk_create(
            [AdminCompatUserRole(user_id=user_id, role_id=role_id) for role_id in role_ids]
        )
    return None


def _normalize_meta(meta):
    if meta in (None, ""):
        return {}
    return meta


async def _collect_menu_ids(menu_id: int) -> list[int]:
    ids = [menu_id]
    child_ids = await AdminCompatMenu.filter(parent_id=menu_id).values_list("id", flat=True)
    for child_id in child_ids:
        ids.extend(await _collect_menu_ids(child_id))
    return ids


async def page_roles(params: RoleQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatRole.all()
    if params.roleName:
        queryset = queryset.filter(role_name__contains=params.roleName)
    if params.roleCode:
        queryset = queryset.filter(role_code__contains=params.roleCode)
    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"roleId": "id", "roleCode": "role_code", "roleName": "role_name", "createTime": "create_time"},
        "-create_time",
    )
    total, data = await paginate_queryset(queryset.order_by(order_by), params.page, params.limit)
    return success(build_page_payload([build_role_out(item).model_dump(mode="json") for item in data], total))


async def list_roles(params: RoleQuery | None = None, current_user: CurrentAdminUser | None = None):
    params = params or RoleQuery()
    queryset = AdminCompatRole.all()
    if params.roleName:
        queryset = queryset.filter(role_name__contains=params.roleName)
    if params.roleCode:
        queryset = queryset.filter(role_code__contains=params.roleCode)
    data = await queryset.order_by("create_time").all()
    return success([build_role_out(item).model_dump(mode="json") for item in data])


async def add_role(form: RoleForm, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    role_code = form.roleCode.strip()
    if await AdminCompatRole.get_or_none(role_code=role_code):
        return fail(1, "角色标识已存在")
    await AdminCompatRole.create(
        role_code=role_code,
        role_name=form.roleName.strip(),
        is_system_role=0,
        comments=form.comments,
    )
    await record_audit_log(
        current_user=current_user,
        audit_type="role.add",
        summary=f"新增角色 {form.roleName.strip()}",
        target_type="role",
        target_id=role_code,
        risk_level="high",
    )
    return success(msg="添加成功")


async def update_role(form: RoleForm, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    role = await AdminCompatRole.get_or_none(id=form.roleId)
    if not role:
        return fail(1, "角色不存在")
    duplicate = await AdminCompatRole.filter(role_code=form.roleCode.strip()).exclude(id=role.id).first()
    if duplicate:
        return fail(1, "角色标识已存在")
    before = build_role_out(role).model_dump(mode="json")
    role.role_code = form.roleCode.strip()
    role.role_name = form.roleName.strip()
    role.comments = form.comments
    await role.save()
    await record_audit_log(
        current_user=current_user,
        audit_type="role.update",
        summary=f"修改角色 {role.role_name}",
        target_type="role",
        target_id=role.id,
        before=before,
        after=build_role_out(role).model_dump(mode="json"),
        risk_level="high",
    )
    return success(msg="修改成功")


async def remove_role(role_id: int, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    role = await AdminCompatRole.get_or_none(id=role_id)
    if not role:
        return fail(1, "角色不存在")
    if role.is_system_role:
        return fail(1, "系统内置角色不允许删除")
    await AdminCompatUserRole.filter(role_id=role_id).delete()
    await AdminCompatRoleMenu.filter(role_id=role_id).delete()
    await role.delete()
    return success(msg="删除成功")


async def remove_roles(role_ids: list[int], current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    roles = await AdminCompatRole.filter(id__in=role_ids).all()
    if any(role.is_system_role for role in roles):
        return fail(1, "系统内置角色不允许删除")
    await AdminCompatUserRole.filter(role_id__in=role_ids).delete()
    await AdminCompatRoleMenu.filter(role_id__in=role_ids).delete()
    await AdminCompatRole.filter(id__in=role_ids).delete()
    return success(msg="批量删除成功")


async def list_role_menus(role_id: int, current_user: CurrentAdminUser):
    role = await AdminCompatRole.get_or_none(id=role_id)
    if not role:
        return fail(1, "角色不存在")
    checked_ids = set(await AdminCompatRoleMenu.filter(role_id=role_id).values_list("menu_id", flat=True))
    menus = await AdminCompatMenu.all().order_by("sort_number", "id")
    return success([build_menu_out(item, checked=item.id in checked_ids).model_dump(mode="json") for item in menus])


async def update_role_menus(role_id: int, menu_ids: list[int], current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    role = await AdminCompatRole.get_or_none(id=role_id)
    if not role:
        return fail(1, "角色不存在")
    await AdminCompatRoleMenu.filter(role_id=role_id).delete()
    if menu_ids:
        await AdminCompatRoleMenu.bulk_create(
            [AdminCompatRoleMenu(role_id=role_id, menu_id=menu_id) for menu_id in set(menu_ids)]
        )
    return success(msg="保存成功")


async def page_users(params: UserQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatUser.all()
    if params.username:
        queryset = queryset.filter(username__contains=params.username)
    if params.nickname:
        queryset = queryset.filter(nickname__contains=params.nickname)
    if params.sex:
        queryset = queryset.filter(sex=params.sex)
    if params.phone:
        queryset = queryset.filter(phone__contains=params.phone)
    if params.email:
        queryset = queryset.filter(email__contains=params.email)
    if params.status in (0, 1):
        queryset = queryset.filter(status=params.status)
    if params.organizationId:
        queryset = queryset.filter(organization_id=params.organizationId)
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)
    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"userId": "id", "organizationId": "organization_id", "status": "status", "createTime": "create_time"},
        "-create_time",
    )
    total, users = await paginate_queryset(queryset.order_by(order_by), params.page, params.limit)
    items = [item.model_dump(mode="json") for item in await build_users_out(users)]
    return success(build_page_payload(items, total))


async def list_users(params: UserQuery | None = None, current_user: CurrentAdminUser | None = None):
    params = params or UserQuery(limit=500)
    queryset = AdminCompatUser.all()
    if params.username:
        queryset = queryset.filter(username__contains=params.username)
    if params.nickname:
        queryset = queryset.filter(nickname__contains=params.nickname)
    if params.organizationId:
        queryset = queryset.filter(organization_id=params.organizationId)
    users = await queryset.order_by("-create_time").all()
    return success([item.model_dump(mode="json") for item in await build_users_out(users)])


async def get_user_detail(user_id: int, current_user: CurrentAdminUser):
    user = await AdminCompatUser.get_or_none(id=user_id)
    if not user:
        return fail(1, "用户不存在")
    return success((await build_user_out(user)).model_dump(mode="json"))


async def add_user(form: UserForm, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    username = form.username.strip()
    if await AdminCompatUser.get_or_none(username=username):
        return fail(1, "账号已存在")
    password = (form.password or "").strip()
    if not password or form.password != password or not (5 <= len(password) <= 18):
        return fail(1, "密码必须为5-18位非空白字符")
    user = await AdminCompatUser.create(
        username=username,
        password=get_password(password),
        nickname=form.nickname.strip(),
        avatar=form.avatar,
        sex=form.sex,
        phone=form.phone,
        email=form.email,
        birthday=_parse_datetime(form.birthday).date() if form.birthday else None,
        introduction=form.introduction,
        organization_id=form.organizationId,
        status=form.status,
        address=form.address,
        tell_pre=form.tellPre,
        tell=form.tell,
    )
    role_error = await _sync_user_roles(user.id, form.roles)
    if role_error:
        return role_error
    return success(msg="添加成功")


async def update_user(form: UserForm, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    user = await AdminCompatUser.get_or_none(id=form.userId)
    if not user:
        return fail(1, "用户不存在")
    user.nickname = form.nickname.strip()
    user.avatar = form.avatar
    user.sex = form.sex
    user.phone = form.phone
    user.email = form.email
    user.birthday = _parse_datetime(form.birthday).date() if form.birthday else None
    user.introduction = form.introduction
    user.organization_id = form.organizationId
    user.status = form.status
    user.address = form.address
    user.tell_pre = form.tellPre
    user.tell = form.tell
    await user.save()
    role_error = await _sync_user_roles(user.id, form.roles)
    if role_error:
        return role_error
    return success(msg="修改成功")


async def remove_user(user_id: int, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    if user_id == current_user.user_id:
        return fail(1, "不能删除当前登录用户")
    await AdminCompatUserRole.filter(user_id=user_id).delete()
    await AdminCompatUser.filter(id=user_id).delete()
    return success(msg="删除成功")


async def remove_users(user_ids: list[int], current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    if current_user.user_id in user_ids:
        return fail(1, "不能删除当前登录用户")
    await AdminCompatUserRole.filter(user_id__in=user_ids).delete()
    await AdminCompatUser.filter(id__in=user_ids).delete()
    return success(msg="批量删除成功")


async def update_user_status(form: UserStatusUpdateForm, current_user: CurrentAdminUser):
    forbidden = await _ensure_admin(current_user)
    if forbidden:
        return forbidden
    if form.userId == current_user.user_id and form.status != 0:
        return fail(1, "不能冻结当前登录用户")
    await AdminCompatUser.filter(id=form.userId).update(status=form.status)
    return success(msg="状态更新成功")


async def update_user_password(form: UserPasswordResetForm):
    user = await AdminCompatUser.get_or_none(id=form.userId)
    if not user:
        return fail(1, "用户不存在")
    password = form.password.strip()
    if form.password != password or not (5 <= len(password) <= 18):
        return fail(1, "密码必须为5-18位非空白字符")
    user.password = get_password(password)
    await user.save(update_fields=["password", "update_time"])
    return success(msg="密码重置成功")


async def import_users(_file=None):
    return fail(1, "当前环境暂未接入 Excel 导入能力，请先使用手动新增")


async def check_user_existence(form: ExistenceCheckForm, current_user: CurrentAdminUser | None = None):
    field_map = {"username": "username", "phone": "phone", "email": "email"}
    db_field = field_map.get(form.field)
    if not db_field:
        return fail(1, "暂不支持该字段检查")
    value = form.value.strip()
    if not value:
        return fail(1, "不存在")
    queryset = AdminCompatUser.filter(**{db_field: value})
    if form.id:
        queryset = queryset.exclude(id=form.id)
    return success(msg="已存在") if await queryset.exists() else fail(1, "不存在")


async def page_menus(params: MenuQuery):
    queryset = AdminCompatMenu.all()
    if params.title:
        queryset = queryset.filter(title__contains=params.title)
    if params.path:
        queryset = queryset.filter(path__contains=params.path)
    if params.authority:
        queryset = queryset.filter(authority__contains=params.authority)
    if params.parentId is not None:
        queryset = queryset.filter(parent_id=params.parentId)
    order_by = resolve_order_field(params.sort, params.order, {"menuId": "id", "sortNumber": "sort_number", "createTime": "create_time"}, "sort_number")
    total, data = await paginate_queryset(queryset.order_by(order_by, "id"), params.page, params.limit)
    return success(build_page_payload([build_menu_out(item).model_dump(mode="json") for item in data], total))


async def list_menus(params: MenuQuery | None = None):
    params = params or MenuQuery(limit=500)
    queryset = AdminCompatMenu.all()
    if params.title:
        queryset = queryset.filter(title__contains=params.title)
    if params.path:
        queryset = queryset.filter(path__contains=params.path)
    if params.authority:
        queryset = queryset.filter(authority__contains=params.authority)
    if params.parentId is not None:
        queryset = queryset.filter(parent_id=params.parentId)
    data = await queryset.order_by("sort_number", "id").all()
    return success([build_menu_out(item).model_dump(mode="json") for item in data])


async def add_menu(form: MenuForm):
    menu = await AdminCompatMenu.create(
        parent_id=form.parentId,
        title=form.title.strip(),
        path=form.path,
        component=form.component,
        menu_type=form.menuType,
        sort_number=form.sortNumber,
        authority=form.authority,
        icon=form.icon,
        hide=form.hide,
        meta=_normalize_meta(form.meta),
        open_type=form.openType,
        redirect=form.redirect,
    )
    return success({"menuId": menu.id}, msg="添加成功")


async def update_menu(form: MenuForm):
    menu = await AdminCompatMenu.get_or_none(id=form.menuId)
    if not menu:
        return fail(1, "菜单不存在")
    menu.parent_id = form.parentId
    menu.title = form.title.strip()
    menu.path = form.path
    menu.component = form.component
    menu.menu_type = form.menuType
    menu.sort_number = form.sortNumber
    menu.authority = form.authority
    menu.icon = form.icon
    menu.hide = form.hide
    menu.meta = _normalize_meta(form.meta)
    menu.open_type = form.openType
    menu.redirect = form.redirect
    await menu.save()
    return success(msg="修改成功")


async def remove_menu(menu_id: int):
    menu_ids = await _collect_menu_ids(menu_id)
    await AdminCompatRoleMenu.filter(menu_id__in=menu_ids).delete()
    await AdminCompatMenu.filter(id__in=menu_ids).delete()
    return success(msg="删除成功")


async def page_organizations(params: OrganizationQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatOrganization.all()
    if params.organizationName:
        queryset = queryset.filter(organization_name__contains=params.organizationName)
    if params.organizationFullName:
        queryset = queryset.filter(organization_full_name__contains=params.organizationFullName)
    if params.organizationType:
        queryset = queryset.filter(organization_type=params.organizationType)
    order_by = resolve_order_field(params.sort, params.order, {"organizationId": "id", "sortNumber": "sort_number", "createTime": "create_time"}, "sort_number")
    organization_type_map = await load_dictionary_label_map("organization_type")
    total, data = await paginate_queryset(queryset.order_by(order_by, "id"), params.page, params.limit)
    return success(build_page_payload([build_organization_out(item, organization_type_map).model_dump(mode="json") for item in data], total))


async def list_organizations(params: OrganizationQuery | None = None, current_user: CurrentAdminUser | None = None):
    params = params or OrganizationQuery(limit=500)
    queryset = AdminCompatOrganization.all()
    if params.organizationName:
        queryset = queryset.filter(organization_name__contains=params.organizationName)
    if params.organizationFullName:
        queryset = queryset.filter(organization_full_name__contains=params.organizationFullName)
    if params.organizationType:
        queryset = queryset.filter(organization_type=params.organizationType)
    organization_type_map = await load_dictionary_label_map("organization_type")
    data = await queryset.order_by("sort_number", "id").all()
    return success([build_organization_out(item, organization_type_map).model_dump(mode="json") for item in data])


async def list_organizations_tree(params: OrganizationQuery | None = None, current_user: CurrentAdminUser | None = None):
    raw = (await list_organizations(params, current_user)).get("data", [])
    return success(_build_tree(raw, "organizationId", "parentId"))


async def add_organization(form: OrganizationForm, current_user: CurrentAdminUser):
    await AdminCompatOrganization.create(
        parent_id=form.parentId,
        organization_name=form.organizationName.strip(),
        organization_full_name=form.organizationFullName.strip(),
        organization_code=form.organizationCode,
        organization_type=form.organizationType,
        sort_number=form.sortNumber,
        comments=form.comments,
    )
    return success(msg="添加成功")


async def update_organization(form: OrganizationForm, current_user: CurrentAdminUser):
    organization = await AdminCompatOrganization.get_or_none(id=form.organizationId)
    if not organization:
        return fail(1, "机构不存在")
    organization.parent_id = form.parentId
    organization.organization_name = form.organizationName.strip()
    organization.organization_full_name = form.organizationFullName.strip()
    organization.organization_code = form.organizationCode
    organization.organization_type = form.organizationType
    organization.sort_number = form.sortNumber
    organization.comments = form.comments
    await organization.save()
    return success(msg="修改成功")


async def remove_organization(organization_id: int, current_user: CurrentAdminUser):
    if await AdminCompatOrganization.filter(parent_id=organization_id).exists():
        return fail(1, "该机构下还有子机构，不能删除")
    if await AdminCompatUser.filter(organization_id=organization_id).exists():
        return fail(1, "该机构下还有用户，不能删除")
    await AdminCompatOrganization.filter(id=organization_id).delete()
    return success(msg="删除成功")


async def page_dictionaries(_params: DictionaryQuery):
    dictionaries = await AdminCompatDictionary.all().order_by("sort_number", "id")
    return success([build_dictionary_out(item).model_dump(mode="json") for item in dictionaries])


async def list_dictionaries(params: DictionaryQuery | None = None):
    params = params or DictionaryQuery(limit=500)
    queryset = AdminCompatDictionary.all()
    if params.dictCode:
        queryset = queryset.filter(dict_code__contains=params.dictCode)
    if params.dictName:
        queryset = queryset.filter(dict_name__contains=params.dictName)
    dictionaries = await queryset.order_by("sort_number", "id").all()
    return success([build_dictionary_out(item).model_dump(mode="json") for item in dictionaries])


async def add_dictionary(form: DictionaryForm):
    if await AdminCompatDictionary.get_or_none(dict_code=form.dictCode.strip()):
        return fail(1, "字典值已存在")
    await AdminCompatDictionary.create(dict_code=form.dictCode.strip(), dict_name=form.dictName.strip(), sort_number=form.sortNumber, comments=form.comments)
    return success(msg="添加成功")


async def update_dictionary(form: DictionaryForm):
    dictionary = await AdminCompatDictionary.get_or_none(id=form.dictId)
    if not dictionary:
        return fail(1, "字典不存在")
    duplicate = await AdminCompatDictionary.filter(dict_code=form.dictCode.strip()).exclude(id=dictionary.id).first()
    if duplicate:
        return fail(1, "字典值已存在")
    dictionary.dict_code = form.dictCode.strip()
    dictionary.dict_name = form.dictName.strip()
    dictionary.sort_number = form.sortNumber
    dictionary.comments = form.comments
    await dictionary.save()
    return success(msg="修改成功")


async def remove_dictionary(dictionary_id: int):
    await AdminCompatDictionaryData.filter(dict_id=dictionary_id).delete()
    await AdminCompatDictionary.filter(id=dictionary_id).delete()
    return success(msg="删除成功")


async def page_dictionary_data(params: DictionaryDataQuery):
    queryset = AdminCompatDictionaryData.all()
    dict_code_map = {}
    if params.dictId:
        queryset = queryset.filter(dict_id=params.dictId)
    elif params.dictCode:
        dictionary = await AdminCompatDictionary.get_or_none(dict_code=params.dictCode)
        if not dictionary:
            return success(build_page_payload([], 0))
        queryset = queryset.filter(dict_id=dictionary.id)
        dict_code_map[dictionary.id] = dictionary.dict_code
    if params.dictDataName:
        queryset = queryset.filter(dict_data_name__contains=params.dictDataName)
    if params.dictDataCode:
        queryset = queryset.filter(dict_data_code__contains=params.dictDataCode)
    if params.keywords:
        queryset = queryset.filter(Q(dict_data_name__contains=params.keywords) | Q(dict_data_code__contains=params.keywords))
    order_by = resolve_order_field(params.sort, params.order, {"dictDataId": "id", "sortNumber": "sort_number", "createTime": "create_time"}, "sort_number")
    total, data = await paginate_queryset(queryset.order_by(order_by, "id"), params.page, params.limit)
    if not dict_code_map:
        dict_ids = sorted({item.dict_id for item in data})
        dictionaries = await AdminCompatDictionary.filter(id__in=dict_ids).all() if dict_ids else []
        dict_code_map = {item.id: item.dict_code for item in dictionaries}
    return success(build_page_payload([build_dictionary_data_out(item, dict_code_map.get(item.dict_id)).model_dump(mode="json") for item in data], total))


async def list_dictionary_data(params: DictionaryDataQuery | None = None):
    params = params or DictionaryDataQuery()
    queryset = AdminCompatDictionaryData.all()
    dict_code_map = {}
    if params.dictId:
        queryset = queryset.filter(dict_id=params.dictId)
    elif params.dictCode:
        dictionary = await AdminCompatDictionary.get_or_none(dict_code=params.dictCode)
        if not dictionary:
            return success([])
        queryset = queryset.filter(dict_id=dictionary.id)
        dict_code_map[dictionary.id] = dictionary.dict_code
    if params.dictDataName:
        queryset = queryset.filter(dict_data_name__contains=params.dictDataName)
    if params.dictDataCode:
        queryset = queryset.filter(dict_data_code__contains=params.dictDataCode)
    if params.keywords:
        queryset = queryset.filter(Q(dict_data_name__contains=params.keywords) | Q(dict_data_code__contains=params.keywords))
    data = await queryset.order_by("sort_number", "id").all()
    if not dict_code_map:
        dict_ids = sorted({item.dict_id for item in data})
        dictionaries = await AdminCompatDictionary.filter(id__in=dict_ids).all() if dict_ids else []
        dict_code_map = {item.id: item.dict_code for item in dictionaries}
    return success([build_dictionary_data_out(item, dict_code_map.get(item.dict_id)).model_dump(mode="json") for item in data])


async def add_dictionary_data(form: DictionaryDataForm):
    if not await AdminCompatDictionary.get_or_none(id=form.dictId):
        return fail(1, "字典不存在")
    exists = await AdminCompatDictionaryData.get_or_none(dict_id=form.dictId, dict_data_code=form.dictDataCode.strip())
    if exists:
        return fail(1, "字典数据值已存在")
    await AdminCompatDictionaryData.create(
        dict_id=form.dictId,
        dict_data_code=form.dictDataCode.strip(),
        dict_data_name=form.dictDataName.strip(),
        color=(form.color or "").strip() or None,
        ripple=1 if form.ripple else 0,
        sort_number=form.sortNumber,
        comments=form.comments,
    )
    return success(msg="添加成功")


async def update_dictionary_data(form: DictionaryDataForm):
    detail = await AdminCompatDictionaryData.get_or_none(id=form.dictDataId)
    if not detail:
        return fail(1, "字典数据不存在")
    duplicate = await AdminCompatDictionaryData.filter(dict_id=form.dictId, dict_data_code=form.dictDataCode.strip()).exclude(id=detail.id).first()
    if duplicate:
        return fail(1, "字典数据值已存在")
    detail.dict_id = form.dictId
    detail.dict_data_code = form.dictDataCode.strip()
    detail.dict_data_name = form.dictDataName.strip()
    detail.color = (form.color or "").strip() or None
    detail.ripple = 1 if form.ripple else 0
    detail.sort_number = form.sortNumber
    detail.comments = form.comments
    await detail.save()
    return success(msg="修改成功")


async def remove_dictionary_data(detail_id: int):
    await AdminCompatDictionaryData.filter(id=detail_id).delete()
    return success(msg="删除成功")


async def remove_dictionary_data_batch(detail_ids: list[int]):
    await AdminCompatDictionaryData.filter(id__in=detail_ids).delete()
    return success(msg="批量删除成功")


async def page_login_records(params: LoginRecordQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatLoginRecord.all()
    if params.username:
        queryset = queryset.filter(username__contains=params.username)
    if params.nickname:
        queryset = queryset.filter(nickname__contains=params.nickname)
    if params.loginType is not None:
        queryset = queryset.filter(login_type=params.loginType)
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)
    order_by = resolve_order_field(params.sort, params.order, {"id": "id", "createTime": "create_time", "username": "username"}, "-create_time")
    total, records = await paginate_queryset(queryset.order_by(order_by), params.page, params.limit)
    return success(build_page_payload([build_login_record_out(item).model_dump(mode="json") for item in records], total))


async def list_login_records(params: LoginRecordQuery | None, current_user: CurrentAdminUser):
    params = params or LoginRecordQuery(limit=500)
    queryset = AdminCompatLoginRecord.all()
    if params.username:
        queryset = queryset.filter(username__contains=params.username)
    if params.nickname:
        queryset = queryset.filter(nickname__contains=params.nickname)
    records = await queryset.order_by("-create_time").all()
    return success([build_login_record_out(item).model_dump(mode="json") for item in records])


async def page_operation_records(params: OperationRecordQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatOperationRecord.all()
    if params.username:
        user_ids = await AdminCompatUser.filter(username__contains=params.username).values_list("id", flat=True)
        queryset = queryset.filter(user_id__in=user_ids or [-1])
    if params.module:
        queryset = queryset.filter(path__contains=params.module)
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)
    order_by = resolve_order_field(params.sort, params.order, {"id": "id", "createTime": "create_time", "spendTime": "latency_ms"}, "-create_time")
    total, records = await paginate_queryset(queryset.order_by(order_by), params.page, params.limit)
    return success(build_page_payload([item.model_dump(mode="json") for item in await build_operation_records_out(records)], total))


async def list_operation_records(params: OperationRecordQuery | None, current_user: CurrentAdminUser):
    params = params or OperationRecordQuery(limit=500)
    queryset = AdminCompatOperationRecord.all()
    if params.username:
        user_ids = await AdminCompatUser.filter(username__contains=params.username).values_list("id", flat=True)
        queryset = queryset.filter(user_id__in=user_ids or [-1])
    records = await queryset.order_by("-create_time").all()
    return success([item.model_dump(mode="json") for item in await build_operation_records_out(records)])


async def page_user_files(params: UserFileQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatUserFile.filter(user_id=current_user.user_id)
    if params.name:
        queryset = queryset.filter(name__contains=params.name)
    if params.isDirectory is not None:
        queryset = queryset.filter(is_directory=params.isDirectory)
    if params.parentId is not None:
        queryset = queryset.filter(parent_id=params.parentId)
    order_by = resolve_order_field(params.sort, params.order, {"id": "id", "name": "name", "createTime": "create_time"}, "-create_time")
    total, records = await paginate_queryset(queryset.order_by(order_by), params.page, params.limit)
    return success(build_page_payload([build_user_file_out(item).model_dump(mode="json") for item in records], total))


async def list_user_files(params: UserFileQuery | None, current_user: CurrentAdminUser):
    params = params or UserFileQuery(limit=500)
    queryset = AdminCompatUserFile.filter(user_id=current_user.user_id)
    if params.parentId is not None:
        queryset = queryset.filter(parent_id=params.parentId)
    records = await queryset.order_by("is_directory", "name").all()
    return success([build_user_file_out(item).model_dump(mode="json") for item in records])


async def add_user_file(form: UserFileForm, current_user: CurrentAdminUser):
    record = await AdminCompatUserFile.create(
        user_id=current_user.user_id,
        name=form.name or "未命名",
        is_directory=form.isDirectory or 0,
        parent_id=form.parentId or 0,
        path=form.path,
        length=form.length or 0,
        content_type=form.contentType,
    )
    return success(build_user_file_out(record).model_dump(mode="json"), msg="添加成功")


async def update_user_file(form: UserFileForm, current_user: CurrentAdminUser):
    record = await AdminCompatUserFile.get_or_none(id=form.id, user_id=current_user.user_id)
    if not record:
        return fail(1, "文件不存在")
    if form.name is not None:
        record.name = form.name
    if form.parentId is not None:
        record.parent_id = form.parentId
    await record.save()
    return success(build_user_file_out(record).model_dump(mode="json"), msg="修改成功")


async def remove_user_file(file_id: int, current_user: CurrentAdminUser):
    await AdminCompatUserFile.filter(id=file_id, user_id=current_user.user_id).delete()
    return success(msg="删除成功")


async def remove_user_files(file_ids: list[int], current_user: CurrentAdminUser):
    await AdminCompatUserFile.filter(id__in=file_ids, user_id=current_user.user_id).delete()
    return success(msg="批量删除成功")
