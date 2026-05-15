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

    role_code = fields.CharField(max_length=100, description="角色编码")
    role_name = fields.CharField(max_length=100, description="角色名称")
    is_system_role = fields.IntField(default=0, description="是否系统内置角色，0 否，1 是")
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
    color = fields.CharField(max_length=30, null=True, description="显示颜色")
    ripple = fields.IntField(default=0, description="是否开启波纹，0 否，1 是")
    sort_number = fields.IntField(default=0, description="排序值")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatPatrolTask(CompatBaseModel):
    class Meta:
        table = "admin_compat_patrol_task"
        table_description = "管理台兼容层巡查任务表"

    task_code = fields.CharField(max_length=40, unique=True, description="任务编号")
    task_title = fields.CharField(max_length=200, description="任务标题")
    task_type = fields.CharField(max_length=50, index=True, description="任务类型字典值")
    priority = fields.CharField(max_length=30, default="medium", description="任务优先级字典值")
    description = fields.TextField(null=True, description="任务说明")
    ai_focus = fields.IntField(default=0, description="是否 AI 识别重点任务，0 否，1 是")
    patrol_location = fields.CharField(max_length=200, description="巡查地点")
    area_ids = fields.JSONField(default=list, description="巡查社区面 ID 集合")
    point_ids = fields.JSONField(default=list, description="巡查点位 ID 集合")
    plan_time = fields.DatetimeField(index=True, description="计划时间")
    start_time = fields.DatetimeField(null=True, index=True, description="任务开始时间")
    end_time = fields.DatetimeField(null=True, index=True, description="任务结束时间")
    duration_hours = fields.IntField(default=1, description="预计时长，单位小时")
    repeat_rule = fields.CharField(max_length=50, default="none", description="重复规则字典值")
    executor_id = fields.IntField(null=True, index=True, description="执行人 ID")
    executor_name = fields.CharField(max_length=100, description="执行人名称")
    task_status = fields.CharField(max_length=50, index=True, description="任务状态字典值")
    progress = fields.IntField(default=0, description="完成进度")
    exception_count = fields.IntField(default=0, description="异常事件数")
    creator_id = fields.IntField(null=True, index=True, description="创建人 ID")
    creator_name = fields.CharField(max_length=100, description="创建人名称")


class AdminCompatPatrolArea(CompatBaseModel):
    class Meta:
        table = "admin_compat_patrol_area"
        table_description = "管理台兼容层巡查社区面表"

    area_code = fields.CharField(max_length=50, unique=True, description="区域编码")
    area_name = fields.CharField(max_length=100, description="区域名称")
    center_lat = fields.FloatField(description="中心点纬度")
    center_lng = fields.FloatField(description="中心点经度")
    boundary = fields.JSONField(default=list, description="区域边界坐标")
    sort_number = fields.IntField(default=0, description="排序值")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatPatrolPoint(CompatBaseModel):
    class Meta:
        table = "admin_compat_patrol_point"
        table_description = "管理台兼容层巡查点位表"

    area_id = fields.IntField(index=True, description="所属区域 ID")
    point_code = fields.CharField(max_length=50, unique=True, description="点位编码")
    point_name = fields.CharField(max_length=100, description="点位名称")
    point_type = fields.CharField(max_length=50, default="building", description="点位类型")
    lat = fields.FloatField(description="纬度")
    lng = fields.FloatField(description="经度")
    sort_number = fields.IntField(default=0, description="排序值")
    comments = fields.TextField(null=True, description="备注")


class AdminCompatPatrolTaskPoint(CompatBaseModel):
    class Meta:
        table = "admin_compat_patrol_task_point"
        table_description = "管理台兼容层巡查任务点位表"
        unique_together = (("task_id", "point_id"),)

    task_id = fields.IntField(index=True, description="任务 ID")
    point_id = fields.IntField(index=True, description="基础点位 ID")
    point_code = fields.CharField(max_length=50, description="点位编码")
    point_name = fields.CharField(max_length=100, description="点位名称")
    address = fields.CharField(max_length=255, description="点位地址")
    lat = fields.FloatField(description="纬度")
    lng = fields.FloatField(description="经度")
    status = fields.CharField(max_length=50, default="PENDING", index=True, description="点位巡查状态")
    arrived_time = fields.DatetimeField(null=True, description="到达时间")
    started_time = fields.DatetimeField(null=True, description="开始巡查时间")
    closed_time = fields.DatetimeField(null=True, description="闭环时间")
    pre_check = fields.JSONField(default=dict, description="点位预检信息")


class AdminCompatPatrolUserDevice(CompatBaseModel):
    class Meta:
        table = "admin_compat_patrol_user_device"
        table_description = "管理台兼容层巡查员设备绑定表"
        unique_together = (("user_id", "device_type"),)

    user_id = fields.IntField(index=True, description="用户 ID")
    user_name = fields.CharField(max_length=100, description="巡查员名称")
    employee_no = fields.CharField(max_length=50, description="工号")
    device_type = fields.CharField(max_length=50, description="设备类型")
    device_name = fields.CharField(max_length=100, description="设备名称")
    device_sn = fields.CharField(max_length=100, description="设备序列号")
    online_status = fields.CharField(max_length=20, default="online", description="在线状态")
    bind_status = fields.CharField(max_length=20, default="bound", description="绑定状态")


class AdminCompatInspectionEvent(CompatBaseModel):
    class Meta:
        table = "admin_compat_inspection_event"
        table_description = "管理台兼容层巡查事件表"

    event_code = fields.CharField(max_length=50, unique=True, description="事件编号")
    event_title = fields.CharField(max_length=200, description="事件标题")
    event_type = fields.CharField(max_length=50, description="事件类型")
    risk_level = fields.CharField(max_length=30, index=True, description="风险等级")
    source = fields.CharField(max_length=50, default="AI识别", description="事件来源")
    status = fields.CharField(max_length=50, index=True, description="事件状态")
    task_id = fields.IntField(null=True, index=True, description="关联任务 ID")
    task_code = fields.CharField(max_length=40, null=True, description="关联任务编号")
    inspector_id = fields.IntField(null=True, index=True, description="巡查员 ID")
    inspector_name = fields.CharField(max_length=100, description="巡查员名称")
    area_id = fields.IntField(null=True, index=True, description="所属区域 ID")
    area_name = fields.CharField(max_length=100, description="所属区域名称")
    point_id = fields.IntField(null=True, index=True, description="关联点位 ID")
    point_name = fields.CharField(max_length=100, description="点位名称")
    lat = fields.FloatField(description="纬度")
    lng = fields.FloatField(description="经度")
    confidence = fields.FloatField(default=0, description="AI 识别置信度")
    description = fields.TextField(null=True, description="事件描述")
    image_url = fields.CharField(max_length=500, null=True, description="现场图片")
    event_type_name = fields.CharField(max_length=100, null=True, description="事件类型名称")
    risk_level_name = fields.CharField(max_length=50, null=True, description="风险等级名称")
    marked_image_url = fields.CharField(max_length=500, null=True, description="标注图片")
    bbox = fields.JSONField(default=dict, description="AI 标注框")
    model_name = fields.CharField(max_length=100, null=True, description="AI 模型名称")
    model_version = fields.CharField(max_length=50, null=True, description="AI 模型版本")
    detected_time = fields.DatetimeField(null=True, index=True, description="识别时间")


class AdminCompatEvidenceFile(CompatBaseModel):
    class Meta:
        table = "admin_compat_evidence_file"
        table_description = "管理台兼容层巡查取证表"

    evidence_no = fields.CharField(max_length=50, unique=True, description="证据编号")
    task_id = fields.IntField(index=True, description="任务 ID")
    point_record_id = fields.IntField(null=True, index=True, description="任务点位记录 ID")
    point_id = fields.IntField(null=True, index=True, description="基础点位 ID")
    detection_id = fields.IntField(null=True, index=True, description="AI 识别事件 ID")
    file_type = fields.CharField(max_length=30, default="IMAGE", description="文件类型")
    file_name = fields.CharField(max_length=200, description="文件名称")
    file_url = fields.CharField(max_length=500, description="文件地址")
    captured_by_id = fields.CharField(max_length=50, null=True, description="取证人 ID")
    captured_by_name = fields.CharField(max_length=100, description="取证人")
    captured_time = fields.DatetimeField(null=True, index=True, description="取证时间")


class AdminCompatWorkOrder(CompatBaseModel):
    class Meta:
        table = "admin_compat_work_order"
        table_description = "管理台兼容层事件工单表"

    work_order_code = fields.CharField(max_length=50, unique=True, description="工单编号")
    title = fields.CharField(max_length=200, description="工单标题")
    event_type = fields.CharField(max_length=50, null=True, description="隐患类型")
    event_type_name = fields.CharField(max_length=100, null=True, description="隐患类型名称")
    risk_level = fields.CharField(max_length=30, index=True, description="风险等级")
    risk_level_name = fields.CharField(max_length=50, null=True, description="风险等级名称")
    source = fields.CharField(max_length=50, default="AI识别", description="来源")
    reporter_id = fields.IntField(null=True, index=True, description="上报人 ID")
    reporter_name = fields.CharField(max_length=100, description="上报人")
    area_id = fields.IntField(null=True, index=True, description="所属区域 ID")
    area_name = fields.CharField(max_length=100, description="所属区域")
    point_name = fields.CharField(max_length=100, null=True, description="点位名称")
    event_id = fields.IntField(null=True, index=True, description="关联事件 ID")
    task_id = fields.IntField(null=True, index=True, description="关联任务 ID")
    point_record_id = fields.IntField(null=True, index=True, description="关联任务点位记录 ID")
    location_name = fields.CharField(max_length=160, null=True, description="地点名称")
    address_detail = fields.CharField(max_length=255, null=True, description="详细地址")
    lat = fields.FloatField(null=True, description="纬度")
    lng = fields.FloatField(null=True, description="经度")
    status = fields.CharField(max_length=50, index=True, description="工单状态")
    push_status = fields.CharField(max_length=50, default="NOT_PUSHED", index=True, description="推送状态")
    third_order_no = fields.CharField(max_length=100, null=True, description="第三方工单编号")
    platform_code = fields.CharField(max_length=80, null=True, description="治理平台工单号")
    report_time = fields.DatetimeField(null=True, index=True, description="上报时间")
    deadline_time = fields.DatetimeField(null=True, index=True, description="处置截止时间")
    remaining_minutes = fields.IntField(default=0, description="剩余分钟")
    responsible_department = fields.CharField(max_length=120, null=True, description="责任部门")
    handler_name = fields.CharField(max_length=100, null=True, description="处理人")
    description = fields.TextField(null=True, description="隐患描述")
    suggestion = fields.TextField(null=True, description="处置建议")
    evidence_list = fields.JSONField(default=list, description="现场取证列表")
    timeline = fields.JSONField(default=list, description="流转记录")


class AdminCompatWorkOrderFlow(CompatBaseModel):
    class Meta:
        table = "admin_compat_work_order_flow"
        table_description = "管理台兼容层业务流转记录表"

    business_type = fields.CharField(max_length=50, index=True, description="业务类型")
    business_id = fields.IntField(index=True, description="业务 ID")
    business_code = fields.CharField(max_length=80, null=True, index=True, description="业务编号")
    action = fields.CharField(max_length=80, description="动作")
    from_status = fields.CharField(max_length=50, null=True, description="原状态")
    to_status = fields.CharField(max_length=50, null=True, description="新状态")
    operator_id = fields.CharField(max_length=50, null=True, description="操作人 ID")
    operator_name = fields.CharField(max_length=100, description="操作人")
    remark = fields.TextField(null=True, description="说明")
    event_type = fields.CharField(max_length=80, null=True, description="预留大屏事件类型")
    extra = fields.JSONField(default=dict, description="扩展数据")


class AdminCompatPushRecord(CompatBaseModel):
    class Meta:
        table = "admin_compat_push_record"
        table_description = "管理台兼容层第三方推送记录表"

    request_id = fields.CharField(max_length=80, unique=True, description="请求编号")
    work_order_id = fields.IntField(index=True, description="工单 ID")
    work_order_code = fields.CharField(max_length=50, index=True, description="工单编号")
    target_platform = fields.CharField(max_length=100, description="目标平台")
    push_status = fields.CharField(max_length=50, index=True, description="推送状态")
    third_order_no = fields.CharField(max_length=100, null=True, description="第三方工单号")
    request_body = fields.JSONField(default=dict, description="请求内容")
    response_body = fields.JSONField(default=dict, description="响应内容")
    error_message = fields.CharField(max_length=255, null=True, description="失败原因")
    pushed_time = fields.DatetimeField(null=True, index=True, description="推送时间")
    operator_id = fields.CharField(max_length=50, null=True, description="操作人 ID")
    operator_name = fields.CharField(max_length=100, description="操作人")


class AdminCompatInspectionReport(CompatBaseModel):
    class Meta:
        table = "admin_compat_inspection_report"
        table_description = "管理台兼容层巡查报告表"

    report_code = fields.CharField(max_length=50, unique=True, description="报告编号")
    report_title = fields.CharField(max_length=200, description="报告标题")
    task_id = fields.IntField(null=True, index=True, description="关联任务 ID")
    work_order_id = fields.IntField(null=True, index=True, description="关联工单 ID")
    report_status = fields.CharField(max_length=50, index=True, description="报告状态")
    closure_rate = fields.FloatField(default=0, description="闭环率")
    point_count = fields.IntField(default=0, description="巡查点位数")
    ai_detect_count = fields.IntField(default=0, description="AI 识别次数")
    work_order_count = fields.IntField(default=0, description="工单数")
    timeout_count = fields.IntField(default=0, description="超时数")
    summary = fields.TextField(null=True, description="报告摘要")
    generated_time = fields.DatetimeField(null=True, description="生成时间")
    archive_time = fields.DatetimeField(null=True, description="归档时间")


class AdminCompatLawDocument(CompatBaseModel):
    class Meta:
        table = "admin_compat_law_document"
        table_description = "管理台兼容层文书表"

    document_code = fields.CharField(max_length=50, unique=True, description="文书编号")
    document_title = fields.CharField(max_length=200, description="文书标题")
    document_type = fields.CharField(max_length=80, description="文书类型")
    document_type_name = fields.CharField(max_length=100, null=True, description="文书类型名称")
    work_order_id = fields.IntField(null=True, index=True, description="关联工单 ID")
    checked_unit = fields.CharField(max_length=160, description="被检查单位")
    check_location = fields.CharField(max_length=200, description="检查地点")
    target_name = fields.CharField(max_length=160, null=True, description="被检查单位/个人")
    illegal_fact = fields.TextField(null=True, description="违法事实")
    legal_basis = fields.TextField(null=True, description="法律依据")
    rectification_requirement = fields.TextField(null=True, description="整改要求")
    deadline = fields.CharField(max_length=120, null=True, description="整改期限")
    review_requirement = fields.CharField(max_length=120, null=True, description="复查要求")
    status = fields.CharField(max_length=50, default="GENERATED", index=True, description="文书状态")
    print_status = fields.CharField(max_length=50, index=True, description="打印状态")
    inspector_name = fields.CharField(max_length=100, description="巡查员")
    content = fields.TextField(null=True, description="文书内容")
    qr_code = fields.CharField(max_length=120, null=True, description="二维码编号")
    qr_code_url = fields.CharField(max_length=255, null=True, description="二维码地址")
    generated_time = fields.DatetimeField(null=True, description="生成时间")
    printed_time = fields.DatetimeField(null=True, description="打印时间")


class AdminCompatPrintRecord(CompatBaseModel):
    class Meta:
        table = "admin_compat_print_record"
        table_description = "管理台兼容层文书打印记录表"

    document_id = fields.IntField(index=True, description="文书 ID")
    document_code = fields.CharField(max_length=50, index=True, description="文书编号")
    printer_name = fields.CharField(max_length=120, description="打印机名称")
    print_status = fields.CharField(max_length=50, index=True, description="打印状态")
    operator_id = fields.CharField(max_length=50, null=True, description="操作人 ID")
    operator_name = fields.CharField(max_length=100, description="操作人")
    printed_time = fields.DatetimeField(null=True, index=True, description="打印时间")
    message = fields.CharField(max_length=255, null=True, description="打印结果")


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


class AdminCompatAuditLog(CompatBaseModel):
    class Meta:
        table = "admin_compat_audit_log"
        table_description = "管理台兼容层审计日志表"

    actor_user_id = fields.IntField(null=True, index=True, description="操作人用户 ID")
    actor_name = fields.CharField(max_length=100, null=True, description="操作人名称")
    audit_type = fields.CharField(max_length=50, index=True, description="审计类型")
    target_type = fields.CharField(max_length=50, null=True, description="目标类型")
    target_id = fields.CharField(max_length=100, null=True, description="目标 ID")
    summary = fields.CharField(max_length=255, description="摘要")
    before_json = fields.JSONField(null=True, description="变更前数据")
    after_json = fields.JSONField(null=True, description="变更后数据")
    risk_level = fields.CharField(max_length=20, default="low", description="风险级别")
    ip = fields.CharField(max_length=64, null=True, description="客户端 IP")
    trace_id = fields.CharField(max_length=80, null=True, description="链路追踪 ID")
