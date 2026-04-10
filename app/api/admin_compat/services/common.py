from typing import Iterable

from app.api.admin_compat.helpers import (
    build_file_url,
    is_image_file,
    json_dumps,
    parse_user_agent,
)
from app.api.admin_compat.models import (
    AdminCompatDictionary,
    AdminCompatDictionaryData,
    AdminCompatFileRecord,
    AdminCompatLoginRecord,
    AdminCompatMenu,
    AdminCompatOrganization,
    AdminCompatOperationRecord,
    AdminCompatRole,
    AdminCompatRoleMenu,
    AdminCompatUser,
    AdminCompatUserFile,
    AdminCompatUserMessage,
    AdminCompatUserRole,
)
from app.api.admin_compat.schemas import (
    DictionaryDataOut,
    DictionaryOut,
    FileRecordOut,
    LoginRecordOut,
    MenuOut,
    OperationRecordOut,
    OrganizationOut,
    RoleOut,
    UserFileOut,
    UserMessageOut,
    UserOut,
)


async def load_dictionary_label_map(dict_code: str) -> dict[str, str]:
    dictionary = await AdminCompatDictionary.get_or_none(dict_code=dict_code)
    if not dictionary:
        return {}
    items = await AdminCompatDictionaryData.filter(dict_id=dictionary.id).all()
    return {item.dict_data_code: item.dict_data_name for item in items}


def build_role_out(role: AdminCompatRole) -> RoleOut:
    return RoleOut(
        roleId=role.id,
        roleCode=role.role_code,
        roleName=role.role_name,
        comments=role.comments,
        createTime=role.create_time,
    )


def build_menu_out(menu: AdminCompatMenu, checked: bool | None = None) -> MenuOut:
    payload = MenuOut(
        menuId=menu.id,
        parentId=menu.parent_id,
        title=menu.title,
        path=menu.path or "",
        component=menu.component,
        menuType=menu.menu_type,
        sortNumber=menu.sort_number,
        authority=menu.authority,
        icon=menu.icon,
        hide=menu.hide,
        meta=menu.meta or {},
        createTime=menu.create_time,
        openType=menu.open_type,
        redirect=menu.redirect,
        checked=checked,
    )
    return payload


def build_organization_out(
    organization: AdminCompatOrganization,
    organization_type_map: dict[str, str] | None = None,
) -> OrganizationOut:
    return OrganizationOut(
        organizationId=organization.id,
        parentId=organization.parent_id,
        organizationName=organization.organization_name,
        organizationFullName=organization.organization_full_name,
        organizationCode=organization.organization_code,
        organizationType=organization.organization_type,
        sortNumber=organization.sort_number,
        comments=organization.comments,
        createTime=organization.create_time,
        organizationTypeName=(organization_type_map or {}).get(
            organization.organization_type or ""
        ),
    )


def build_dictionary_out(dictionary: AdminCompatDictionary) -> DictionaryOut:
    return DictionaryOut(
        dictId=dictionary.id,
        dictCode=dictionary.dict_code,
        dictName=dictionary.dict_name,
        sortNumber=dictionary.sort_number,
        comments=dictionary.comments,
        createTime=dictionary.create_time,
    )


def build_dictionary_data_out(
    detail: AdminCompatDictionaryData,
    dict_code: str | None = None,
) -> DictionaryDataOut:
    return DictionaryDataOut(
        dictDataId=detail.id,
        dictId=detail.dict_id,
        dictDataCode=detail.dict_data_code,
        dictDataName=detail.dict_data_name,
        sortNumber=detail.sort_number,
        comments=detail.comments,
        createTime=detail.create_time,
        dictCode=dict_code,
    )


async def build_users_out(
    users: Iterable[AdminCompatUser],
    *,
    include_authorities: bool = False,
) -> list[UserOut]:
    user_list = list(users)
    if not user_list:
        return []

    user_ids = [user.id for user in user_list]
    role_relations = await AdminCompatUserRole.filter(user_id__in=user_ids).all()
    role_ids = sorted({relation.role_id for relation in role_relations})
    roles = await AdminCompatRole.filter(id__in=role_ids).all() if role_ids else []
    role_map = {role.id: role for role in roles}
    roles_by_user: dict[int, list[AdminCompatRole]] = {user.id: [] for user in user_list}
    for relation in role_relations:
        role = role_map.get(relation.role_id)
        if role:
            roles_by_user.setdefault(relation.user_id, []).append(role)

    org_ids = sorted({user.organization_id for user in user_list if user.organization_id})
    organizations = (
        await AdminCompatOrganization.filter(id__in=org_ids).all() if org_ids else []
    )
    organization_map = {
        organization.id: organization.organization_name for organization in organizations
    }
    sex_map = await load_dictionary_label_map("sex")

    authorities_by_user: dict[int, list[AdminCompatMenu]] = {user.id: [] for user in user_list}
    if include_authorities and role_ids:
        role_menu_relations = await AdminCompatRoleMenu.filter(role_id__in=role_ids).all()
        menu_ids = sorted({relation.menu_id for relation in role_menu_relations})
        menus = (
            await AdminCompatMenu.filter(id__in=menu_ids).order_by("sort_number", "id").all()
            if menu_ids
            else []
        )
        menu_map = {menu.id: menu for menu in menus}
        menus_by_role: dict[int, list[AdminCompatMenu]] = {}
        for relation in role_menu_relations:
            menu = menu_map.get(relation.menu_id)
            if menu:
                menus_by_role.setdefault(relation.role_id, []).append(menu)

        for user in user_list:
            seen_menu_ids: set[int] = set()
            collected: list[AdminCompatMenu] = []
            for role in roles_by_user.get(user.id, []):
                for menu in menus_by_role.get(role.id, []):
                    if menu.id in seen_menu_ids:
                        continue
                    seen_menu_ids.add(menu.id)
                    collected.append(menu)
            authorities_by_user[user.id] = sorted(
                collected, key=lambda item: (item.sort_number, item.id)
            )

    result: list[UserOut] = []
    for user in user_list:
        result.append(
            UserOut(
                userId=user.id,
                username=user.username,
                nickname=user.nickname,
                avatar=user.avatar,
                sex=user.sex,
                phone=user.phone,
                email=user.email,
                birthday=user.birthday,
                introduction=user.introduction,
                organizationId=user.organization_id,
                status=user.status,
                sexName=sex_map.get(user.sex or ""),
                organizationName=organization_map.get(user.organization_id),
                roles=[build_role_out(role) for role in roles_by_user.get(user.id, [])],
                authorities=[
                    build_menu_out(menu) for menu in authorities_by_user.get(user.id, [])
                ],
                createTime=user.create_time,
                address=user.address,
                tellPre=user.tell_pre,
                tell=user.tell,
            )
        )
    return result


async def build_user_out(
    user: AdminCompatUser,
    *,
    include_authorities: bool = False,
) -> UserOut:
    return (await build_users_out([user], include_authorities=include_authorities))[0]


async def build_file_records_out(
    records: Iterable[AdminCompatFileRecord],
) -> list[FileRecordOut]:
    file_list = list(records)
    if not file_list:
        return []

    user_ids = sorted({item.create_user_id for item in file_list if item.create_user_id})
    users = await AdminCompatUser.filter(id__in=user_ids).all() if user_ids else []
    user_map = {user.id: user for user in users}

    result: list[FileRecordOut] = []
    for record in file_list:
        user = user_map.get(record.create_user_id)
        url = build_file_url(record.path)
        result.append(
            FileRecordOut(
                id=record.id,
                name=record.name,
                path=record.path,
                length=int(record.length or 0),
                contentType=record.content_type,
                createUserId=record.create_user_id,
                createTime=record.create_time,
                url=url,
                thumbnail=url if is_image_file(record.path, record.content_type) else None,
                downloadUrl=url,
                createUsername=user.username if user else None,
                createNickname=user.nickname if user else None,
            )
        )
    return result


async def build_file_record_out(record: AdminCompatFileRecord) -> FileRecordOut:
    return (await build_file_records_out([record]))[0]


def build_user_file_out(record: AdminCompatUserFile) -> UserFileOut:
    url = build_file_url(record.path) if record.path else None
    return UserFileOut(
        id=record.id,
        userId=record.user_id,
        name=record.name,
        isDirectory=record.is_directory,
        parentId=record.parent_id,
        path=record.path,
        length=int(record.length or 0),
        contentType=record.content_type,
        createTime=record.create_time,
        updateTime=record.update_time,
        url=url,
        thumbnail=url if is_image_file(record.path, record.content_type) else None,
        downloadUrl=url,
    )


def build_login_record_out(record: AdminCompatLoginRecord) -> LoginRecordOut:
    return LoginRecordOut(
        id=record.id,
        username=record.username,
        os=record.os,
        device=record.device,
        browser=record.browser,
        ip=record.ip,
        loginType=record.login_type,
        comments=record.comments,
        createTime=record.create_time,
        nickname=record.nickname,
    )


def build_message_out(message: AdminCompatUserMessage) -> UserMessageOut:
    return UserMessageOut(
        id=message.id,
        messageType=message.message_type,
        title=message.title,
        time=message.message_time,
        status=message.status,
        content=message.content,
        avatar=message.avatar,
        icon=message.icon,
        color=message.color,
    )


async def build_operation_records_out(
    logs: Iterable[AdminCompatOperationRecord],
) -> list[OperationRecordOut]:
    log_list = list(logs)
    if not log_list:
        return []

    user_ids = [log.user_id for log in log_list if log.user_id is not None]
    users = await AdminCompatUser.filter(id__in=sorted(set(user_ids))).all() if user_ids else []
    user_map = {user.id: user for user in users}

    result: list[OperationRecordOut] = []
    for log in log_list:
        user_id = log.user_id
        user = user_map.get(user_id) if user_id is not None else None

        request_headers = log.req_headers if isinstance(log.req_headers, dict) else {}
        ua_info = parse_user_agent(request_headers.get("user-agent"))
        path = log.path or ""
        normalized_path = path.replace("/api/", "", 1).strip("/")
        module = normalized_path.split("/")[0] if normalized_path else ""
        status = 0 if (log.resp_code in (0, None)) else 1
        result.append(
            OperationRecordOut(
                id=str(log.id),
                userId=user_id,
                module=module,
                description=log.summary or normalized_path.split("/")[-1] if normalized_path else "",
                url=path,
                requestMethod=log.method or "",
                method=log.summary or "",
                params=json_dumps(log.req_body),
                result=json_dumps(log.resp_body),
                error="" if status == 0 else (log.resp_msg or json_dumps(log.resp_body)),
                spendTime=int(log.latency_ms or 0),
                os=ua_info["os"],
                device=ua_info["device"],
                browser=ua_info["browser"],
                ip=log.ip or "",
                status=status,
                createTime=log.create_time,
                nickname=user.nickname if user else (log.user_name or ""),
                username=user.username if user else "",
            )
        )
    return result
