from datetime import datetime

from tortoise import Model, fields


class CompatBaseModel(Model):
    """
    兼容层统一基础模型。

    这里没有复用项目里原有的 BaseOrmModel，原因是前端管理台的主键、树节点和分页场景
    都更适合用自增整型 ID，能减少前后端字段转换的复杂度。
    """

    id = fields.IntField(pk=True, description="主键 ID")
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True


class AdminCompatOrganization(CompatBaseModel):
    class Meta:
        table = "admin_compat_organization"
        table_description = "管理台兼容层机构表"

    parent_id = fields.IntField(default=0, index=True, description="父级机构 ID，0 表示顶级")
    organization_name = fields.CharField(max_length=100, description="机构名称")
    organization_full_name = fields.CharField(max_length=200, description="机构全称")
    organization_code = fields.CharField(max_length=100, null=True, description="机构编码")
    organization_type = fields.CharField(max_length=50, null=True, description="机构类型字典值")
    sort_number = fields.IntField(default=0, description="排序值")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatRole(CompatBaseModel):
    class Meta:
        table = "admin_compat_role"
        table_description = "管理台兼容层角色表"

    role_code = fields.CharField(max_length=100, unique=True, description="角色编码")
    role_name = fields.CharField(max_length=100, description="角色名称")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatUser(CompatBaseModel):
    class Meta:
        table = "admin_compat_user"
        table_description = "管理台兼容层用户表"

    username = fields.CharField(max_length=100, unique=True, description="登录账号")
    password = fields.CharField(max_length=128, description="密码哈希")
    nickname = fields.CharField(max_length=100, description="昵称")
    avatar = fields.TextField(null=True, description="头像地址或 base64")
    sex = fields.CharField(max_length=20, null=True, description="性别字典值")
    phone = fields.CharField(max_length=30, null=True, description="手机号")
    email = fields.CharField(max_length=120, null=True, description="邮箱")
    birthday = fields.DateField(null=True, description="生日")
    introduction = fields.TextField(null=True, description="简介")
    organization_id = fields.IntField(null=True, index=True, description="所属机构 ID")
    status = fields.IntField(default=0, description="用户状态，0 正常，1 冻结")
    address = fields.CharField(max_length=255, null=True, description="街道地址")
    tell_pre = fields.CharField(max_length=10, null=True, description="联系电话前缀")
    tell = fields.CharField(max_length=20, null=True, description="联系电话")


class AdminCompatUserRole(CompatBaseModel):
    class Meta:
        table = "admin_compat_user_role"
        table_description = "管理台兼容层用户角色关联表"
        unique_together = (("user_id", "role_id"),)

    user_id = fields.IntField(index=True, description="用户 ID")
    role_id = fields.IntField(index=True, description="角色 ID")


class AdminCompatMenu(CompatBaseModel):
    class Meta:
        table = "admin_compat_menu"
        table_description = "管理台兼容层菜单表"

    parent_id = fields.IntField(default=0, index=True, description="父级菜单 ID，0 表示顶级")
    title = fields.CharField(max_length=100, description="菜单名称")
    path = fields.CharField(max_length=255, null=True, description="路由路径")
    component = fields.CharField(max_length=255, null=True, description="前端组件路径")
    menu_type = fields.IntField(default=0, description="菜单类型，0 菜单/目录，1 按钮")
    sort_number = fields.IntField(default=0, description="排序值")
    authority = fields.CharField(max_length=150, null=True, description="权限标识")
    icon = fields.CharField(max_length=100, null=True, description="图标名称")
    hide = fields.IntField(default=0, description="是否隐藏，0 否，1 是")
    meta = fields.JSONField(default=dict, description="前端路由 meta")
    open_type = fields.IntField(default=0, description="打开方式，0 组件，1 内嵌，2 外链")
    redirect = fields.CharField(max_length=255, null=True, description="重定向地址")


class AdminCompatRoleMenu(CompatBaseModel):
    class Meta:
        table = "admin_compat_role_menu"
        table_description = "管理台兼容层角色菜单关联表"
        unique_together = (("role_id", "menu_id"),)

    role_id = fields.IntField(index=True, description="角色 ID")
    menu_id = fields.IntField(index=True, description="菜单 ID")


class AdminCompatDictionary(CompatBaseModel):
    class Meta:
        table = "admin_compat_dictionary"
        table_description = "管理台兼容层字典表"

    dict_code = fields.CharField(max_length=100, unique=True, description="字典编码")
    dict_name = fields.CharField(max_length=100, description="字典名称")
    sort_number = fields.IntField(default=0, description="排序值")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatDictionaryData(CompatBaseModel):
    class Meta:
        table = "admin_compat_dictionary_data"
        table_description = "管理台兼容层字典数据表"
        unique_together = (("dict_id", "dict_data_code"),)

    dict_id = fields.IntField(index=True, description="字典 ID")
    dict_data_code = fields.CharField(max_length=100, description="字典数据编码")
    dict_data_name = fields.CharField(max_length=100, description="字典数据名称")
    sort_number = fields.IntField(default=0, description="排序值")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatFileRecord(CompatBaseModel):
    class Meta:
        table = "admin_compat_file_record"
        table_description = "管理台兼容层文件上传记录表"

    name = fields.CharField(max_length=255, description="文件名称")
    path = fields.CharField(max_length=500, description="文件存储路径")
    length = fields.BigIntField(default=0, description="文件大小")
    content_type = fields.CharField(max_length=100, null=True, description="文件类型")
    create_user_id = fields.IntField(null=True, index=True, description="上传人 ID")


class AdminCompatUserFile(CompatBaseModel):
    class Meta:
        table = "admin_compat_user_file"
        table_description = "管理台兼容层用户文件表"

    user_id = fields.IntField(index=True, description="所属用户 ID")
    name = fields.CharField(max_length=255, description="文件或文件夹名称")
    is_directory = fields.IntField(default=0, description="是否文件夹，0 否，1 是")
    parent_id = fields.IntField(default=0, index=True, description="父级目录 ID")
    path = fields.CharField(max_length=500, null=True, description="文件存储路径")
    length = fields.BigIntField(default=0, description="文件大小")
    content_type = fields.CharField(max_length=100, null=True, description="文件类型")


class AdminCompatLoginRecord(CompatBaseModel):
    class Meta:
        table = "admin_compat_login_record"
        table_description = "管理台兼容层登录日志表"

    user_id = fields.IntField(null=True, index=True, description="用户 ID")
    username = fields.CharField(max_length=100, null=True, description="用户账号")
    nickname = fields.CharField(max_length=100, null=True, description="用户昵称")
    os = fields.CharField(max_length=100, null=True, description="操作系统")
    device = fields.CharField(max_length=100, null=True, description="设备名称")
    browser = fields.CharField(max_length=100, null=True, description="浏览器")
    ip = fields.CharField(max_length=64, null=True, description="IP 地址")
    login_type = fields.IntField(default=0, description="操作类型，0 登录成功，1 登录失败，2 退出登录，3 刷新 token")
    comments = fields.CharField(max_length=255, null=True, description="备注")


class AdminCompatOperationRecord(CompatBaseModel):
    class Meta:
        table = "admin_compat_operation_record"
        table_description = "管理台兼容层操作日志表"

    user_id = fields.IntField(null=True, index=True, description="操作用户 ID")
    user_name = fields.CharField(max_length=100, null=True, description="操作用户名称")
    path = fields.CharField(max_length=255, description="请求路径")
    method = fields.CharField(max_length=16, description="HTTP 方法")
    ip = fields.CharField(max_length=64, null=True, description="客户端 IP")
    summary = fields.CharField(max_length=255, null=True, description="接口摘要")
    req_headers = fields.JSONField(null=True, description="请求头")
    req_body = fields.JSONField(null=True, description="请求体")
    resp_code = fields.IntField(null=True, description="响应业务码")
    resp_msg = fields.CharField(max_length=255, null=True, description="响应消息")
    resp_body = fields.JSONField(null=True, description="响应体")
    latency_ms = fields.IntField(default=0, description="接口耗时，单位毫秒")


class AdminCompatUserMessage(CompatBaseModel):
    class Meta:
        table = "admin_compat_user_message"
        table_description = "管理台兼容层用户消息表"

    user_id = fields.IntField(index=True, description="接收人用户 ID")
    message_type = fields.CharField(max_length=20, index=True, description="消息类型")
    title = fields.CharField(max_length=255, description="消息标题")
    content = fields.TextField(null=True, description="消息内容")
    status = fields.IntField(default=0, description="消息状态，0 未处理，1 已处理")
    avatar = fields.TextField(null=True, description="头像地址")
    icon = fields.CharField(max_length=50, null=True, description="通知图标")
    color = fields.CharField(max_length=30, null=True, description="通知图标底色")
    message_time = fields.DatetimeField(default=datetime.now, description="消息时间")
