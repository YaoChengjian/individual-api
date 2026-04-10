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


async def page_roles(params: RoleQuery):
    queryset = AdminCompatRole.all()
    if params.roleName:
        queryset = queryset.filter(role_name__contains=params.roleName)
    if params.roleCode:
        queryset = queryset.filter(role_code__contains=params.roleCode)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "roleId": "id",
            "roleCode": "role_code",
            "roleName": "role_name",
            "createTime": "create_time",
        },
        "-create_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [build_role_out(item).model_dump(mode="json") for item in data]
    return success(build_page_payload(items, total))


async def list_roles(params: RoleQuery | None = None):
    params = params or RoleQuery()
    queryset = AdminCompatRole.all()
    if params.roleName:
        queryset = queryset.filter(role_name__contains=params.roleName)
    if params.roleCode:
        queryset = queryset.filter(role_code__contains=params.roleCode)
    data = await queryset.order_by("create_time").all()
    return success([build_role_out(item).model_dump(mode="json") for item in data])


async def add_role(form: RoleForm):
    exists = await AdminCompatRole.get_or_none(role_code=form.roleCode.strip())
    if exists:
        return fail(1, "角色标识已存在")
    await AdminCompatRole.create(
        role_code=form.roleCode.strip(),
        role_name=form.roleName.strip(),
        comments=form.comments,
    )
    return success(msg="添加成功")


async def update_role(form: RoleForm):
    role = await AdminCompatRole.get_or_none(id=form.roleId)
    if not role:
        return fail(1, "角色不存在")

    duplicate = await AdminCompatRole.filter(role_code=form.roleCode.strip()).exclude(id=role.id).first()
    if duplicate:
        return fail(1, "角色标识已存在")

    role.role_code = form.roleCode.strip()
    role.role_name = form.roleName.strip()
    role.comments = form.comments
    await role.save()
    return success(msg="修改成功")


async def remove_role(role_id: int):
    role = await AdminCompatRole.get_or_none(id=role_id)
    if not role:
        return fail(1, "角色不存在")

    await AdminCompatUserRole.filter(role_id=role_id).delete()
    await AdminCompatRoleMenu.filter(role_id=role_id).delete()
    await role.delete()
    return success(msg="删除成功")


async def remove_roles(role_ids: list[int]):
    if not role_ids:
        return fail(1, "请选择要删除的角色")
    await AdminCompatUserRole.filter(role_id__in=role_ids).delete()
    await AdminCompatRoleMenu.filter(role_id__in=role_ids).delete()
    await AdminCompatRole.filter(id__in=role_ids).delete()
    return success(msg="批量删除成功")


async def list_role_menus(role_id: int):
    role = await AdminCompatRole.get_or_none(id=role_id)
    if not role:
        return fail(1, "角色不存在")

    checked_ids = set(
        await AdminCompatRoleMenu.filter(role_id=role_id).values_list("menu_id", flat=True)
    )
    menus = await AdminCompatMenu.all().order_by("sort_number", "id")
    return success(
        [build_menu_out(item, checked=item.id in checked_ids).model_dump(mode="json") for item in menus]
    )


async def update_role_menus(role_id: int, menu_ids: list[int]):
    role = await AdminCompatRole.get_or_none(id=role_id)
    if not role:
        return fail(1, "角色不存在")

    await AdminCompatRoleMenu.filter(role_id=role_id).delete()
    if menu_ids:
        await AdminCompatRoleMenu.bulk_create(
            [AdminCompatRoleMenu(role_id=role_id, menu_id=menu_id) for menu_id in set(menu_ids)]
        )
    return success(msg="保存成功")


async def page_users(params: UserQuery):
    queryset = AdminCompatUser.all()
    if params.username:
        queryset = queryset.filter(username__contains=params.username)
    if params.nickname:
        queryset = queryset.filter(nickname__contains=params.nickname)
    if params.sex:
        queryset = queryset.filter(sex=params.sex)
    if params.phone:
        queryset = queryset.filter(phone__contains=params.phone)
    if params.organizationId:
        queryset = queryset.filter(organization_id=params.organizationId)
    if params.email:
        queryset = queryset.filter(email__contains=params.email)
    if params.status in (0, 1):
        queryset = queryset.filter(status=params.status)

    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "userId": "id",
            "username": "username",
            "nickname": "nickname",
            "phone": "phone",
            "email": "email",
            "status": "status",
            "createTime": "create_time",
        },
        "-create_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [
        item.model_dump(mode="json")
        for item in await build_users_out(data, include_authorities=False)
    ]
    return success(build_page_payload(items, total))


async def list_users(params: UserQuery | None = None):
    params = params or UserQuery(limit=500)
    queryset = AdminCompatUser.all()
    if params.username:
        queryset = queryset.filter(username__contains=params.username)
    if params.nickname:
        queryset = queryset.filter(nickname__contains=params.nickname)
    if params.status in (0, 1):
        queryset = queryset.filter(status=params.status)
    data = await queryset.order_by("-create_time").all()
    return success(
        [item.model_dump(mode="json") for item in await build_users_out(data)]
    )


async def get_user_detail(user_id: int):
    user = await AdminCompatUser.get_or_none(id=user_id)
    if not user:
        return fail(1, "用户不存在")
    return success((await build_user_out(user)).model_dump(mode="json"))


async def add_user(form: UserForm):
    username = form.username.strip()
    if not username:
        return fail(1, "账号不能为空")
    if not form.password:
        return fail(1, "密码不能为空")

    password = form.password.strip()
    if form.password != password or not (5 <= len(password) <= 18):
        return fail(1, "密码必须为5-18位非空白字符")

    if await AdminCompatUser.get_or_none(username=username):
        return fail(1, "账号已存在")

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
    if form.roles:
        await AdminCompatUserRole.bulk_create(
            [AdminCompatUserRole(user_id=user.id, role_id=role.roleId) for role in form.roles]
        )
    return success(msg="添加成功")


async def update_user(form: UserForm):
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

    await AdminCompatUserRole.filter(user_id=user.id).delete()
    if form.roles:
        await AdminCompatUserRole.bulk_create(
            [AdminCompatUserRole(user_id=user.id, role_id=role.roleId) for role in form.roles]
        )
    return success(msg="修改成功")


async def remove_user(user_id: int, current_user: CurrentAdminUser):
    if user_id == current_user.user_id:
        return fail(1, "不能删除当前登录用户")

    user = await AdminCompatUser.get_or_none(id=user_id)
    if not user:
        return fail(1, "用户不存在")

    await AdminCompatUserRole.filter(user_id=user_id).delete()
    await user.delete()
    return success(msg="删除成功")


async def remove_users(user_ids: list[int], current_user: CurrentAdminUser):
    if not user_ids:
        return fail(1, "请选择要删除的用户")
    if current_user.user_id in user_ids:
        return fail(1, "不能删除当前登录用户")

    await AdminCompatUserRole.filter(user_id__in=user_ids).delete()
    await AdminCompatUser.filter(id__in=user_ids).delete()
    return success(msg="批量删除成功")


async def update_user_status(form: UserStatusUpdateForm, current_user: CurrentAdminUser):
    if form.userId == current_user.user_id and form.status != 0:
        return fail(1, "不能冻结当前登录用户")

    user = await AdminCompatUser.get_or_none(id=form.userId)
    if not user:
        return fail(1, "用户不存在")
    user.status = form.status
    await user.save(update_fields=["status", "update_time"])
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


async def check_user_existence(form: ExistenceCheckForm):
    field_map = {"username": "username", "phone": "phone", "email": "email"}
    db_field = field_map.get(form.field)
    if not db_field:
        return fail(1, "暂不支持该字段检查")

    queryset = AdminCompatUser.filter(**{db_field: form.value.strip()})
    if form.id:
        queryset = queryset.exclude(id=form.id)

    exists = await queryset.exists()
    if exists:
        return success(msg="已存在")
    return fail(1, "不存在")


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

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"menuId": "id", "sortNumber": "sort_number", "createTime": "create_time"},
        "sort_number",
    )
    queryset = queryset.order_by(order_by, "id")
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    return success(
        build_page_payload(
            [build_menu_out(item).model_dump(mode="json") for item in data], total
        )
    )


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
    menu = await AdminCompatMenu.get_or_none(id=menu_id)
    if not menu:
        return fail(1, "菜单不存在")

    menu_ids = await _collect_menu_ids(menu_id)
    await AdminCompatRoleMenu.filter(menu_id__in=menu_ids).delete()
    await AdminCompatMenu.filter(id__in=menu_ids).delete()
    return success(msg="删除成功")


async def page_organizations(params: OrganizationQuery):
    queryset = AdminCompatOrganization.all()
    if params.organizationName:
        queryset = queryset.filter(organization_name__contains=params.organizationName)
    if params.organizationFullName:
        queryset = queryset.filter(
            organization_full_name__contains=params.organizationFullName
        )
    if params.organizationType:
        queryset = queryset.filter(organization_type=params.organizationType)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {
            "organizationId": "id",
            "sortNumber": "sort_number",
            "createTime": "create_time",
        },
        "sort_number",
    )
    organization_type_map = await load_dictionary_label_map("organization_type")
    queryset = queryset.order_by(order_by, "id")
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [
        build_organization_out(item, organization_type_map).model_dump(mode="json")
        for item in data
    ]
    return success(build_page_payload(items, total))


async def list_organizations(params: OrganizationQuery | None = None):
    params = params or OrganizationQuery(limit=500)
    queryset = AdminCompatOrganization.all()
    if params.organizationName:
        queryset = queryset.filter(organization_name__contains=params.organizationName)
    if params.organizationFullName:
        queryset = queryset.filter(
            organization_full_name__contains=params.organizationFullName
        )
    if params.organizationType:
        queryset = queryset.filter(organization_type=params.organizationType)
    organization_type_map = await load_dictionary_label_map("organization_type")
    data = await queryset.order_by("sort_number", "id").all()
    return success(
        [
            build_organization_out(item, organization_type_map).model_dump(mode="json")
            for item in data
        ]
    )


async def list_organizations_tree(params: OrganizationQuery | None = None):
    raw = (await list_organizations(params)).get("data", [])
    return success(_build_tree(raw, "organizationId", "parentId"))


async def add_organization(form: OrganizationForm):
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


async def update_organization(form: OrganizationForm):
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


async def remove_organization(organization_id: int):
    organization = await AdminCompatOrganization.get_or_none(id=organization_id)
    if not organization:
        return fail(1, "机构不存在")

    has_child = await AdminCompatOrganization.filter(parent_id=organization_id).exists()
    if has_child:
        return fail(1, "该机构下还有子机构，不能删除")
    has_user = await AdminCompatUser.filter(organization_id=organization_id).exists()
    if has_user:
        return fail(1, "该机构下还有用户，不能删除")

    await organization.delete()
    return success(msg="删除成功")


async def page_dictionaries(_params: DictionaryQuery):
    dictionaries = await AdminCompatDictionary.all().order_by("sort_number", "id")
    return success([build_dictionary_out(item).model_dump(mode="json") for item in dictionaries])


async def list_dictionaries(params: DictionaryQuery | None = None):
    queryset = AdminCompatDictionary.all()
    params = params or DictionaryQuery(limit=500)
    if params.dictCode:
        queryset = queryset.filter(dict_code__contains=params.dictCode)
    if params.dictName:
        queryset = queryset.filter(dict_name__contains=params.dictName)
    dictionaries = await queryset.order_by("sort_number", "id").all()
    return success([build_dictionary_out(item).model_dump(mode="json") for item in dictionaries])


async def add_dictionary(form: DictionaryForm):
    duplicate = await AdminCompatDictionary.get_or_none(dict_code=form.dictCode.strip())
    if duplicate:
        return fail(1, "字典值已存在")
    await AdminCompatDictionary.create(
        dict_code=form.dictCode.strip(),
        dict_name=form.dictName.strip(),
        sort_number=form.sortNumber,
        comments=form.comments,
    )
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
    dictionary = await AdminCompatDictionary.get_or_none(id=dictionary_id)
    if not dictionary:
        return fail(1, "字典不存在")
    await AdminCompatDictionaryData.filter(dict_id=dictionary_id).delete()
    await dictionary.delete()
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
        queryset = queryset.filter(
            Q(dict_data_name__contains=params.keywords)
            | Q(dict_data_code__contains=params.keywords)
        )

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"dictDataId": "id", "sortNumber": "sort_number", "createTime": "create_time"},
        "sort_number",
    )
    queryset = queryset.order_by(order_by, "id")
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    if not dict_code_map:
        dict_ids = sorted({item.dict_id for item in data})
        dictionaries = await AdminCompatDictionary.filter(id__in=dict_ids).all() if dict_ids else []
        dict_code_map = {item.id: item.dict_code for item in dictionaries}

    items = [
        build_dictionary_data_out(item, dict_code_map.get(item.dict_id)).model_dump(mode="json")
        for item in data
    ]
    return success(build_page_payload(items, total))


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
        queryset = queryset.filter(
            Q(dict_data_name__contains=params.keywords)
            | Q(dict_data_code__contains=params.keywords)
        )

    data = await queryset.order_by("sort_number", "id").all()
    if not dict_code_map:
        dict_ids = sorted({item.dict_id for item in data})
        dictionaries = await AdminCompatDictionary.filter(id__in=dict_ids).all() if dict_ids else []
        dict_code_map = {item.id: item.dict_code for item in dictionaries}

    return success(
        [
            build_dictionary_data_out(item, dict_code_map.get(item.dict_id)).model_dump(mode="json")
            for item in data
        ]
    )


async def add_dictionary_data(form: DictionaryDataForm):
    exists = await AdminCompatDictionaryData.get_or_none(
        dict_id=form.dictId,
        dict_data_code=form.dictDataCode.strip(),
    )
    if exists:
        return fail(1, "字典数据值已存在")
    await AdminCompatDictionaryData.create(
        dict_id=form.dictId,
        dict_data_code=form.dictDataCode.strip(),
        dict_data_name=form.dictDataName.strip(),
        sort_number=form.sortNumber,
        comments=form.comments,
    )
    return success(msg="添加成功")


async def update_dictionary_data(form: DictionaryDataForm):
    detail = await AdminCompatDictionaryData.get_or_none(id=form.dictDataId)
    if not detail:
        return fail(1, "字典数据不存在")
    duplicate = await AdminCompatDictionaryData.filter(
        dict_id=form.dictId,
        dict_data_code=form.dictDataCode.strip(),
    ).exclude(id=detail.id).first()
    if duplicate:
        return fail(1, "字典数据值已存在")

    detail.dict_id = form.dictId
    detail.dict_data_code = form.dictDataCode.strip()
    detail.dict_data_name = form.dictDataName.strip()
    detail.sort_number = form.sortNumber
    detail.comments = form.comments
    await detail.save()
    return success(msg="修改成功")


async def remove_dictionary_data(detail_id: int):
    detail = await AdminCompatDictionaryData.get_or_none(id=detail_id)
    if not detail:
        return fail(1, "字典数据不存在")
    await detail.delete()
    return success(msg="删除成功")


async def remove_dictionary_data_batch(detail_ids: list[int]):
    if not detail_ids:
        return fail(1, "请选择要删除的数据")
    await AdminCompatDictionaryData.filter(id__in=detail_ids).delete()
    return success(msg="批量删除成功")


async def page_login_records(params: LoginRecordQuery):
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

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"createTime": "create_time", "loginType": "login_type", "username": "username"},
        "-create_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [build_login_record_out(item).model_dump(mode="json") for item in data]
    return success(build_page_payload(items, total))


async def list_login_records(params: LoginRecordQuery | None = None):
    params = params or LoginRecordQuery(limit=500)
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
    data = await queryset.order_by("-create_time").all()
    return success([build_login_record_out(item).model_dump(mode="json") for item in data])


async def page_operation_records(params: OperationRecordQuery):
    queryset = AdminCompatOperationRecord.all()
    if params.username:
        user_ids = await AdminCompatUser.filter(username__contains=params.username).values_list("id", flat=True)
        queryset = queryset.filter(user_id__in=user_ids)
    if params.module:
        queryset = queryset.filter(path__contains=f"/{params.module}")
    if params.status in (0, 1):
        if params.status == 0:
            queryset = queryset.filter(Q(resp_code=0) | Q(resp_code__isnull=True))
        else:
            queryset = queryset.exclude(Q(resp_code=0) | Q(resp_code__isnull=True))
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"createTime": "create_time", "spendTime": "latency_ms", "username": "user_name"},
        "-create_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [item.model_dump(mode="json") for item in await build_operation_records_out(data)]
    return success(build_page_payload(items, total))


async def list_operation_records(params: OperationRecordQuery | None = None):
    params = params or OperationRecordQuery(limit=500)
    queryset = AdminCompatOperationRecord.all()
    if params.username:
        user_ids = await AdminCompatUser.filter(username__contains=params.username).values_list("id", flat=True)
        queryset = queryset.filter(user_id__in=user_ids)
    if params.module:
        queryset = queryset.filter(path__contains=f"/{params.module}")
    if params.status in (0, 1):
        if params.status == 0:
            queryset = queryset.filter(Q(resp_code=0) | Q(resp_code__isnull=True))
        else:
            queryset = queryset.exclude(Q(resp_code=0) | Q(resp_code__isnull=True))
    if start := _parse_datetime(params.createTimeStart):
        queryset = queryset.filter(create_time__gte=start)
    if end := _parse_datetime(params.createTimeEnd):
        queryset = queryset.filter(create_time__lte=end)
    data = await queryset.order_by("-create_time").all()
    return success([item.model_dump(mode="json") for item in await build_operation_records_out(data)])


async def page_user_files(params: UserFileQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatUserFile.filter(user_id=current_user.user_id)
    if params.name:
        queryset = queryset.filter(name__contains=params.name)
    if params.isDirectory in (0, 1):
        queryset = queryset.filter(is_directory=params.isDirectory)
    if params.parentId is not None:
        queryset = queryset.filter(parent_id=params.parentId)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"createTime": "create_time", "updateTime": "update_time", "name": "name"},
        "-update_time",
    )
    queryset = queryset.order_by(order_by)
    total, data = await paginate_queryset(queryset, params.page, params.limit)
    items = [build_user_file_out(item).model_dump(mode="json") for item in data]
    return success(build_page_payload(items, total))


async def list_user_files(params: UserFileQuery, current_user: CurrentAdminUser):
    queryset = AdminCompatUserFile.filter(user_id=current_user.user_id)
    if params.name:
        queryset = queryset.filter(name__contains=params.name)
    if params.isDirectory in (0, 1):
        queryset = queryset.filter(is_directory=params.isDirectory)
    if params.parentId is not None:
        queryset = queryset.filter(parent_id=params.parentId)

    order_by = resolve_order_field(
        params.sort,
        params.order,
        {"createTime": "create_time", "updateTime": "update_time", "name": "name"},
        "-update_time",
    )
    data = await queryset.order_by(order_by).all()
    return success([build_user_file_out(item).model_dump(mode="json") for item in data])


async def add_user_file(form: UserFileForm, current_user: CurrentAdminUser):
    name = (form.name or "").strip()
    if not name:
        return fail(1, "名称不能为空")

    parent_id = form.parentId or 0
    if parent_id:
        parent = await AdminCompatUserFile.get_or_none(
            id=parent_id, user_id=current_user.user_id, is_directory=1
        )
        if not parent:
            return fail(1, "父级目录不存在")

    exists = await AdminCompatUserFile.get_or_none(
        user_id=current_user.user_id,
        parent_id=parent_id,
        name=name,
    )
    if exists:
        return fail(1, "同级目录下已存在同名文件")

    await AdminCompatUserFile.create(
        user_id=current_user.user_id,
        name=name,
        is_directory=form.isDirectory or 0,
        parent_id=parent_id,
        path=form.path,
        length=form.length or 0,
        content_type=form.contentType,
    )
    return success(msg="保存成功")


async def update_user_file(form: UserFileForm, current_user: CurrentAdminUser):
    file_record = await AdminCompatUserFile.get_or_none(
        id=form.id, user_id=current_user.user_id
    )
    if not file_record:
        return fail(1, "文件不存在")

    if form.parentId is not None:
        if form.parentId != 0:
            parent = await AdminCompatUserFile.get_or_none(
                id=form.parentId,
                user_id=current_user.user_id,
                is_directory=1,
            )
            if not parent:
                return fail(1, "目标目录不存在")
        file_record.parent_id = form.parentId

    if form.name is not None:
        new_name = form.name.strip()
        if not new_name:
            return fail(1, "名称不能为空")
        duplicate = await AdminCompatUserFile.filter(
            user_id=current_user.user_id,
            parent_id=file_record.parent_id,
            name=new_name,
        ).exclude(id=file_record.id).first()
        if duplicate:
            return fail(1, "同级目录下已存在同名文件")
        file_record.name = new_name

    if form.path is not None:
        file_record.path = form.path
    if form.length is not None:
        file_record.length = form.length
    if form.contentType is not None:
        file_record.content_type = form.contentType
    await file_record.save()
    return success(msg="修改成功")


async def remove_user_file(file_id: int, current_user: CurrentAdminUser):
    file_record = await AdminCompatUserFile.get_or_none(
        id=file_id, user_id=current_user.user_id
    )
    if not file_record:
        return fail(1, "文件不存在")
    file_ids = await _collect_user_file_ids(file_id, current_user.user_id)
    await AdminCompatUserFile.filter(id__in=file_ids, user_id=current_user.user_id).delete()
    return success(msg="删除成功")


async def remove_user_files(file_ids: list[int], current_user: CurrentAdminUser):
    if not file_ids:
        return fail(1, "请选择要删除的文件")
    to_delete: set[int] = set()
    for file_id in file_ids:
        to_delete.update(await _collect_user_file_ids(file_id, current_user.user_id))
    await AdminCompatUserFile.filter(id__in=list(to_delete), user_id=current_user.user_id).delete()
    return success(msg="批量删除成功")


def _normalize_meta(value):
    if value in (None, ""):
        return {}
    if isinstance(value, dict):
        return value
    try:
        import json

        return json.loads(value)
    except Exception:
        return {}


async def _collect_menu_ids(root_menu_id: int) -> list[int]:
    menus = await AdminCompatMenu.all()
    children_map: dict[int, list[int]] = {}
    for menu in menus:
        children_map.setdefault(menu.parent_id, []).append(menu.id)

    collected: list[int] = []
    stack = [root_menu_id]
    while stack:
        current = stack.pop()
        collected.append(current)
        stack.extend(children_map.get(current, []))
    return collected


async def _collect_user_file_ids(root_file_id: int, user_id: int) -> list[int]:
    records = await AdminCompatUserFile.filter(user_id=user_id).all()
    children_map: dict[int, list[int]] = {}
    for record in records:
        children_map.setdefault(record.parent_id, []).append(record.id)

    collected: list[int] = []
    stack = [root_file_id]
    while stack:
        current = stack.pop()
        collected.append(current)
        stack.extend(children_map.get(current, []))
    return collected
