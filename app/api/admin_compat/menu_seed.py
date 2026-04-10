"""
管理台菜单与按钮权限种子。

本文件以用户提供的历史 `authorities` 数据为参考来源，尽量保持：
1. 菜单标题、路径、图标名称与原管理后台一致；
2. 隐藏路由的 `active`、内嵌页 `routePath` 等元信息可被前端直接消费；
3. 在保留历史菜单结构的同时，补充当前前端已接入的按钮权限节点。
"""

from typing import Any


def _merge_meta(
    lang: tuple[str, str] | None = None,
    *,
    active: str | None = None,
    badge: dict[str, Any] | None = None,
    route_path: str | None = None,
    open_type: str | None = None,
    hide_footer: bool | None = None,
    hide_timeout: int | None = None,
) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if lang:
        meta["lang"] = {"zh_TW": lang[0], "en": lang[1]}
    if active:
        meta["active"] = active
    if badge:
        meta["props"] = {"badge": badge}
    if route_path:
        meta["routePath"] = route_path
    if open_type:
        meta["openType"] = open_type
    if hide_footer is not None:
        meta["hideFooter"] = hide_footer
    if hide_timeout is not None:
        meta.setdefault("props", {})
        meta["props"]["hideTimeout"] = hide_timeout
    return meta


def _menu(
    key: str,
    parent_key: str | None,
    title: str,
    path: str | None,
    component: str | None,
    sort_number: int,
    authority: str | None,
    *,
    icon: str | None = None,
    hide: int = 0,
    meta: dict[str, Any] | None = None,
    open_type: int = 0,
    redirect: str | None = None,
    menu_type: int = 0,
) -> dict[str, Any]:
    return {
        "key": key,
        "parent_key": parent_key,
        "title": title,
        "path": path,
        "component": component,
        "menu_type": menu_type,
        "sort_number": sort_number,
        "authority": authority,
        "icon": icon,
        "hide": hide,
        "meta": meta or {},
        "open_type": open_type,
        "redirect": redirect,
    }


def _directory(
    key: str,
    parent_key: str | None,
    title: str,
    path: str,
    sort_number: int,
    *,
    icon: str,
    authority: str | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _menu(
        key,
        parent_key,
        title,
        path,
        None,
        sort_number,
        authority,
        icon=icon,
        meta=meta,
    )


def _page(
    key: str,
    parent_key: str | None,
    title: str,
    path: str,
    component: str,
    sort_number: int,
    *,
    icon: str | None = None,
    authority: str | None = None,
    hide: int = 0,
    meta: dict[str, Any] | None = None,
    open_type: int = 0,
) -> dict[str, Any]:
    return _menu(
        key,
        parent_key,
        title,
        path,
        component,
        sort_number,
        authority,
        icon=icon,
        hide=hide,
        meta=meta,
        open_type=open_type,
    )


def _hidden_page(
    key: str,
    parent_key: str,
    title: str,
    path: str,
    component: str,
    sort_number: int,
    *,
    icon: str | None = "IconProLinkOutlined",
    authority: str | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _page(
        key,
        parent_key,
        title,
        path,
        component,
        sort_number,
        icon=icon,
        authority=authority,
        hide=1,
        meta=meta,
    )


def _iframe_page(
    key: str,
    parent_key: str,
    title: str,
    path: str,
    url: str,
    sort_number: int,
    *,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _page(
        key,
        parent_key,
        title,
        path,
        url,
        sort_number,
        icon="IconProLinkOutlined",
        meta=meta,
        open_type=1,
    )


def _external_link(
    key: str,
    title: str,
    url: str,
    sort_number: int,
    *,
    icon: str,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _menu(
        key,
        None,
        title,
        url,
        None,
        sort_number,
        None,
        icon=icon,
        meta=meta,
        open_type=2,
    )


def _button(
    key: str,
    parent_key: str,
    title: str,
    authority: str,
    sort_number: int,
) -> dict[str, Any]:
    return _menu(
        key,
        parent_key,
        title,
        None,
        None,
        sort_number,
        authority,
        hide=1,
        menu_type=1,
    )


DASHBOARD_SEED_MENUS = [
    _directory(
        "dashboard-root",
        None,
        "Dashboard",
        "/dashboard",
        0,
        icon="IconProHomeOutlined",
    ),
    _page(
        "dashboard-workplace",
        "dashboard-root",
        "工作台",
        "/dashboard/workplace",
        "/dashboard/workplace",
        1,
        icon="IconProDesktopOutlined",
        meta=_merge_meta(("工作臺", "Workplace")),
    ),
    _page(
        "dashboard-analysis",
        "dashboard-root",
        "分析页",
        "/dashboard/analysis",
        "/dashboard/analysis",
        2,
        icon="IconProAnalysisOutlined",
        meta=_merge_meta(("分析頁", "Analysis"), badge={"value": 1, "type": "warning"}),
    ),
    _page(
        "dashboard-monitor",
        "dashboard-root",
        "监控页",
        "/dashboard/monitor",
        "/dashboard/monitor",
        3,
        icon="IconProDashboardOutlined",
        meta=_merge_meta(("監控頁", "Monitor")),
    ),
]


SYSTEM_SEED_MENUS = [
    _directory(
        "system-root",
        None,
        "系统管理",
        "/system",
        1,
        icon="IconProSettingOutlined",
        meta=_merge_meta(("系統管理", "System")),
    ),
    _page(
        "system-user",
        "system-root",
        "用户管理",
        "/system/user",
        "/system/user",
        1,
        icon="IconProUserOutlined",
        meta=_merge_meta(("用戶管理", "User")),
    ),
    _button("system-user-query", "system-user", "查询用户", "sys:user:list", 1),
    _button("system-user-add", "system-user", "新增用户", "system:user:add", 101),
    _button("system-user-edit", "system-user", "修改用户", "system:user:edit", 102),
    _button("system-user-remove", "system-user", "删除用户", "system:user:remove", 103),
    _button("system-user-import", "system-user", "导入用户", "system:user:import", 104),
    _button(
        "system-user-reset-password",
        "system-user",
        "重置密码",
        "system:user:reset-password",
        105,
    ),
    _button("system-user-status", "system-user", "修改状态", "system:user:status", 106),
    _hidden_page(
        "system-user-detail",
        "system-user",
        "用户详情",
        "/system/user/details/:id",
        "/system/user/details",
        5,
        icon="IconProUserOutlined",
        meta=_merge_meta(("用戶詳情", "UserDetails"), active="/system/user"),
    ),
    _page(
        "system-role",
        "system-root",
        "角色管理",
        "/system/role",
        "/system/role",
        2,
        icon="IconProIdcardOutlined",
        meta=_merge_meta(("角色管理", "Role")),
    ),
    _button("system-role-query", "system-role", "查询角色", "sys:role:list", 1),
    _button("system-role-add", "system-role", "新增角色", "system:role:add", 101),
    _button("system-role-edit", "system-role", "修改角色", "system:role:edit", 102),
    _button("system-role-remove", "system-role", "删除角色", "system:role:remove", 103),
    _button("system-role-auth", "system-role", "分配权限", "system:role:auth", 104),
    _page(
        "system-menu",
        "system-root",
        "菜单管理",
        "/system/menu",
        "/system/menu",
        3,
        icon="IconProAppstoreOutlined",
        meta=_merge_meta(("選單管理", "Menu")),
    ),
    _button("system-menu-query", "system-menu", "查询菜单", "sys:menu:list", 1),
    _button("system-menu-add", "system-menu", "新增菜单", "system:menu:add", 101),
    _button("system-menu-edit", "system-menu", "修改菜单", "system:menu:edit", 102),
    _button("system-menu-remove", "system-menu", "删除菜单", "system:menu:remove", 103),
    _page(
        "system-organization",
        "system-root",
        "机构管理",
        "/system/organization",
        "/system/organization",
        4,
        icon="IconProCityOutlined",
        meta=_merge_meta(("機构管理", "Organization")),
    ),
    _button("system-organization-query", "system-organization", "查询机构", "sys:org:list", 1),
    _button(
        "system-organization-add",
        "system-organization",
        "新增机构",
        "system:organization:add",
        101,
    ),
    _button(
        "system-organization-edit",
        "system-organization",
        "修改机构",
        "system:organization:edit",
        102,
    ),
    _button(
        "system-organization-remove",
        "system-organization",
        "删除机构",
        "system:organization:remove",
        103,
    ),
    _page(
        "system-dictionary",
        "system-root",
        "字典管理",
        "/system/dictionary",
        "/system/dictionary",
        5,
        icon="IconProBookOutlined",
        meta=_merge_meta(("字典管理", "Dictionary"), hide_footer=True),
    ),
    _button("system-dictionary-query", "system-dictionary", "查询字典", "sys:dict:list", 1),
    _button(
        "system-dictionary-add",
        "system-dictionary",
        "新增字典",
        "system:dictionary:add",
        101,
    ),
    _button(
        "system-dictionary-edit",
        "system-dictionary",
        "修改字典",
        "system:dictionary:edit",
        102,
    ),
    _button(
        "system-dictionary-remove",
        "system-dictionary",
        "删除字典",
        "system:dictionary:remove",
        103,
    ),
    _button(
        "system-dictionary-data-add",
        "system-dictionary",
        "新增字典项",
        "system:dictionary-data:add",
        201,
    ),
    _button(
        "system-dictionary-data-edit",
        "system-dictionary",
        "修改字典项",
        "system:dictionary-data:edit",
        202,
    ),
    _button(
        "system-dictionary-data-remove",
        "system-dictionary",
        "删除字典项",
        "system:dictionary-data:remove",
        203,
    ),
    _page(
        "system-file",
        "system-root",
        "文件管理",
        "/system/file",
        "/system/file",
        6,
        icon="IconProFolderOutlined",
        meta=_merge_meta(("檔案管理", "File")),
    ),
    _button("system-file-query", "system-file", "查看记录", "sys:file:list", 1),
    _button("system-file-remove", "system-file", "删除文件", "system:file:remove", 101),
    _page(
        "system-login-record",
        "system-root",
        "登录日志",
        "/system/login-record",
        "/system/login-record",
        7,
        icon="IconProCalendarOutlined",
        authority="sys:login-record:list",
        meta=_merge_meta(("登入日誌", "LoginRecord")),
    ),
    _page(
        "system-operation-record",
        "system-root",
        "操作日志",
        "/system/operation-record",
        "/system/operation-record",
        8,
        icon="IconProLogOutlined",
        authority="sys:operation-record:list",
        meta=_merge_meta(("操作日誌", "OperationRecord")),
    ),
]


FORM_SEED_MENUS = [
    _directory(
        "form-root",
        None,
        "表单页面",
        "/form",
        2,
        icon="IconProFormOutlined",
        meta=_merge_meta(("表單頁面", "Form"), badge={"value": "New"}),
    ),
    _page(
        "form-basic",
        "form-root",
        "基础表单",
        "/form/basic",
        "/form/basic",
        1,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("基礎表單", "Basic Form")),
    ),
    _page(
        "form-advanced",
        "form-root",
        "复杂表单",
        "/form/advanced",
        "/form/advanced",
        2,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("複雜表單", "Advanced Form")),
    ),
    _page(
        "form-step",
        "form-root",
        "分步表单",
        "/form/step",
        "/form/step",
        3,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("分步表單", "Step Form")),
    ),
    _page(
        "form-build",
        "form-root",
        "表单构建",
        "/form/build",
        "/form/build",
        4,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("表單構建", "Form Build"), badge={"isDot": True}),
    ),
]


LIST_SEED_MENUS = [
    _directory(
        "list-root",
        None,
        "列表页面",
        "/list",
        3,
        icon="IconProTableOutlined",
        meta=_merge_meta(("清單頁面", "List"), hide_timeout=450),
    ),
    _page(
        "list-basic",
        "list-root",
        "基础列表",
        "/list/basic",
        "/list/basic",
        1,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("基礎清單", "Basic List")),
    ),
    _page(
        "list-user",
        "list-root",
        "左树右表",
        "/list/user",
        "/list/user",
        2,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("左樹右表", "Tree List")),
    ),
    _page(
        "list-advanced",
        "list-root",
        "复杂列表",
        "/list/advanced",
        "/list/advanced",
        3,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("複雜清單", "Advanced List")),
    ),
    _directory(
        "list-card-root",
        "list-root",
        "卡片列表",
        "/list/card",
        4,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("卡片清單", "Card List"), hide_timeout=100),
    ),
    _page(
        "list-card-project",
        "list-card-root",
        "项目列表",
        "/list/card/project",
        "/list/card/project",
        1,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("項目清單", "Project")),
    ),
    _page(
        "list-card-application",
        "list-card-root",
        "应用列表",
        "/list/card/application",
        "/list/card/application",
        2,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("應用清單", "Application")),
    ),
    _page(
        "list-card-article",
        "list-card-root",
        "文章列表",
        "/list/card/article",
        "/list/card/article",
        3,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("文章清單", "Article")),
    ),
    _hidden_page(
        "list-basic-add",
        "list-basic",
        "添加用户",
        "/list/basic/add",
        "/list/basic/add",
        4,
        meta=_merge_meta(("添加用戶", "Add User"), active="/list/basic"),
    ),
    _hidden_page(
        "list-basic-edit",
        "list-basic",
        "修改用户",
        "/list/basic/edit/:id",
        "/list/basic/edit",
        5,
        meta=_merge_meta(("編輯用戶", "Edit User"), active="/list/basic"),
    ),
    _directory(
        "list-users-root",
        "list-root",
        "复杂路由",
        "/list/users",
        5,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("複雜路由", "Route Demo"), hide_timeout=100),
    ),
    _page(
        "list-users-male",
        "list-users-root",
        "男用户",
        "/list/users/1",
        "/list/users",
        1,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("男用戶", "Male Users")),
    ),
    _hidden_page(
        "list-users-male-detail",
        "list-users-male",
        "男用户详情",
        "/list/users/details/1/:id",
        "/list/users/details",
        1,
        meta=_merge_meta(("男用戶詳情", "MaleUserDetails"), active="/list/users/1"),
    ),
    _page(
        "list-users-female",
        "list-users-root",
        "女用户",
        "/list/users/2",
        "/list/users",
        2,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("女用戶", "Female Users")),
    ),
    _hidden_page(
        "list-users-female-detail",
        "list-users-female",
        "女用户详情",
        "/list/users/details/2/:id",
        "/list/users/details",
        1,
        meta=_merge_meta(("女用戶詳情", "FemaleUserDetails"), active="/list/users/2"),
    ),
    _page(
        "list-build",
        "list-root",
        "列表构建",
        "/list/build",
        "/list/build",
        5,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("列表構建", "List Build"), badge={"isDot": True}),
    ),
]


RESULT_SEED_MENUS = [
    _directory(
        "result-root",
        None,
        "结果页面",
        "/result",
        4,
        icon="IconProCheckCircleOutlined",
        meta=_merge_meta(("結果頁面", "Result")),
    ),
    _page(
        "result-success",
        "result-root",
        "成功页",
        "/result/success",
        "/result/success",
        1,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("成功頁", "Success")),
    ),
    _page(
        "result-fail",
        "result-root",
        "失败页",
        "/result/fail",
        "/result/fail",
        2,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("失敗頁", "Fail")),
    ),
]


EXCEPTION_SEED_MENUS = [
    _directory(
        "exception-root",
        None,
        "异常页面",
        "/exception",
        5,
        icon="IconProWarningOutlined",
        meta=_merge_meta(("异常頁面", "Exception")),
    ),
    _page(
        "exception-403",
        "exception-root",
        "403",
        "/exception/403",
        "/exception/403",
        1,
        icon="IconProLinkOutlined",
    ),
    _page(
        "exception-404",
        "exception-root",
        "404",
        "/exception/404",
        "/exception/404",
        2,
        icon="IconProLinkOutlined",
    ),
    _page(
        "exception-500",
        "exception-root",
        "500",
        "/exception/500",
        "/exception/500",
        3,
        icon="IconProLinkOutlined",
    ),
]


USER_SEED_MENUS = [
    _directory(
        "user-root",
        None,
        "个人中心",
        "/user",
        6,
        icon="IconProControlOutlined",
        meta=_merge_meta(("個人中心", "User")),
    ),
    _page(
        "user-profile",
        "user-root",
        "我的资料",
        "/user/profile",
        "/user/profile",
        1,
        icon="IconProUserOutlined",
        meta=_merge_meta(("個人資料", "Profile")),
    ),
    _button("user-profile-update", "user-profile", "保存资料", "user:profile:update", 101),
    _button("user-profile-password", "user-profile", "修改密码", "user:profile:password", 102),
    _page(
        "user-message",
        "user-root",
        "我的消息",
        "/user/message",
        "/user/message",
        2,
        icon="IconProMessageOutlined",
        meta=_merge_meta(("我的消息", "Message")),
    ),
    _button("user-message-status", "user-message", "处理消息", "user:message:status", 101),
    _button("user-message-remove", "user-message", "删除消息", "user:message:remove", 102),
]


EXTENSION_SEED_MENUS = [
    _directory(
        "extension-root",
        None,
        "扩展组件",
        "/extension",
        7,
        icon="IconProAppstoreAddOutlined",
        meta=_merge_meta(None, badge={"isDot": True}),
    ),
    _page("extension-table", "extension-root", "高级表格", "/extension/table", "/extension/table", 1, icon="IconProLinkOutlined"),
    _page("extension-modal", "extension-root", "高级弹窗", "/extension/modal", "/extension/modal", 2, icon="IconProLinkOutlined", meta=_merge_meta(None, badge={"isDot": True})),
    _page("extension-message", "extension-root", "消息提示", "/extension/message", "/extension/message", 3, icon="IconProLinkOutlined"),
    _page("extension-layout", "extension-root", "布局组件", "/extension/layout", "/extension/layout", 4, icon="IconProLinkOutlined"),
    _page("extension-table-select", "extension-root", "下拉表格", "/extension/table-select", "/extension/table-select", 5, icon="IconProLinkOutlined"),
    _page("extension-tree-select", "extension-root", "下拉树", "/extension/tree-select", "/extension/tree-select", 6, icon="IconProLinkOutlined"),
    _page("extension-upload", "extension-root", "文件上传", "/extension/upload", "/extension/upload", 7, icon="IconProLinkOutlined"),
    _page("extension-icon", "extension-root", "图标选择", "/extension/icon", "/extension/icon", 8, icon="IconProLinkOutlined"),
    _page("extension-file", "extension-root", "文件列表", "/extension/file", "/extension/file", 9, icon="IconProLinkOutlined"),
    _page("extension-split", "extension-root", "分割面板", "/extension/split", "/extension/split", 10, icon="IconProLinkOutlined", meta=_merge_meta(None, badge={"isDot": True})),
    _page("extension-printer", "extension-root", "打印组件", "/extension/printer", "/extension/printer", 11, icon="IconProLinkOutlined"),
    _page("extension-text", "extension-root", "文本组件", "/extension/text", "/extension/text", 12, icon="IconProLinkOutlined"),
    _page("extension-tag", "extension-root", "标签输入", "/extension/tag", "/extension/tag", 13, icon="IconProLinkOutlined"),
    _page("extension-avatar", "extension-root", "头像组合", "/extension/avatar", "/extension/avatar", 14, icon="IconProLinkOutlined"),
    _page("extension-tour", "extension-root", "引导组件", "/extension/tour", "/extension/tour", 15, icon="IconProLinkOutlined"),
    _page("extension-menu", "extension-root", "导航菜单", "/extension/menu", "/extension/menu", 16, icon="IconProLinkOutlined"),
    _page("extension-check-card", "extension-root", "可选卡片", "/extension/check-card", "/extension/check-card", 17, icon="IconProLinkOutlined"),
    _page("extension-watermark", "extension-root", "水印组件", "/extension/watermark", "/extension/watermark", 18, icon="IconProLinkOutlined"),
    _page("extension-viewer", "extension-root", "查看器", "/extension/viewer", "/extension/viewer", 19, icon="IconProLinkOutlined"),
    _page("extension-steps", "extension-root", "步骤条", "/extension/steps", "/extension/steps", 19, icon="IconProLinkOutlined"),
    _page("extension-segmented", "extension-root", "分段器", "/extension/segmented", "/extension/segmented", 20, icon="IconProLinkOutlined"),
    _page("extension-tabs", "extension-root", "标签页", "/extension/tabs", "/extension/tabs", 21, icon="IconProLinkOutlined"),
    _page("extension-qr-code", "extension-root", "二维码", "/extension/qr-code", "/extension/qr-code", 22, icon="IconProLinkOutlined"),
    _page("extension-bar-code", "extension-root", "条形码", "/extension/bar-code", "/extension/bar-code", 23, icon="IconProLinkOutlined"),
    _page("extension-regions", "extension-root", "城市选择", "/extension/regions", "/extension/regions", 24, icon="IconProLinkOutlined"),
    _page("extension-excel", "extension-root", "导入导出", "/extension/excel", "/extension/excel", 25, icon="IconProLinkOutlined"),
    _page("extension-dragsort", "extension-root", "拖拽排序", "/extension/dragsort", "/extension/dragsort", 26, icon="IconProLinkOutlined"),
    _page("extension-map", "extension-root", "地图组件", "/extension/map", "/extension/map", 27, icon="IconProLinkOutlined"),
    _page("extension-player", "extension-root", "视频播放", "/extension/player", "/extension/player", 28, icon="IconProLinkOutlined"),
    _page("extension-editor", "extension-root", "富文本框", "/extension/editor", "/extension/editor", 29, icon="IconProLinkOutlined"),
    _page("extension-markdown", "extension-root", "markdown", "/extension/markdown", "/extension/markdown", 30, icon="IconProLinkOutlined"),
    _page("extension-role-select", "extension-root", "角色选择", "/extension/role-select", "/extension/role-select", 31, icon="IconProLinkOutlined", meta=_merge_meta(None, badge={"isDot": True})),
    _page("extension-department-select", "extension-root", "部门选择", "/extension/department-select", "/extension/department-select", 31, icon="IconProLinkOutlined", meta=_merge_meta(None, badge={"isDot": True})),
    _page("extension-monaco", "extension-root", "代码编辑", "/extension/monaco", "/extension/monaco", 31, icon="IconProLinkOutlined"),
    _page("extension-user-select", "extension-root", "人员选择", "/extension/user-select", "/extension/user-select", 31, icon="IconProLinkOutlined", meta=_merge_meta(None, badge={"isDot": True})),
]


IFRAME_SEED_MENUS = [
    _directory(
        "iframe-root",
        None,
        "内嵌页面",
        "/iframe",
        8,
        icon="IconProLinkOutlined",
        meta=_merge_meta(("內嵌頁面", "IFrame")),
    ),
    _iframe_page(
        "iframe-website",
        "iframe-root",
        "官网",
        "/iframe/eleadmin",
        "https://www.eleadmin.com",
        1,
        meta=_merge_meta(
            ("官網", "Website"),
            active="/iframe/eleadmin",
            route_path="/iframe/eleadmin/:url?",
            open_type="iframe",
        ),
    ),
    _iframe_page(
        "iframe-doc",
        "iframe-root",
        "文档",
        "/iframe/eleadmin-doc",
        "https://www.eleadmin.com/doc/eleadminplus/",
        2,
        meta=_merge_meta(("檔案", "Document")),
    ),
]


EXAMPLE_SEED_MENUS = [
    _page(
        "example-root",
        None,
        "功能演示",
        "/example",
        "/example",
        9,
        icon="IconProCompassOutlined",
        meta=_merge_meta(("功能演示", "Demo")),
    )
]


EXTERNAL_LINK_SEED_MENUS = [
    _external_link(
        "authorization-link",
        "获取授权",
        "https://eleadmin.com/goods/26",
        10,
        icon="IconProProtectOutlined",
        meta=_merge_meta(("獲取授權", "Authorization")),
    )
]


SEED_MENUS = [
    *DASHBOARD_SEED_MENUS,
    *SYSTEM_SEED_MENUS,
    *FORM_SEED_MENUS,
    *LIST_SEED_MENUS,
    *RESULT_SEED_MENUS,
    *EXCEPTION_SEED_MENUS,
    *USER_SEED_MENUS,
    *EXTENSION_SEED_MENUS,
    *IFRAME_SEED_MENUS,
    *EXAMPLE_SEED_MENUS,
    *EXTERNAL_LINK_SEED_MENUS,
]
