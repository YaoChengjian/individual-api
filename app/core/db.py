# logging 配一次
import logging
from typing import Iterable

from tortoise import Tortoise, connections

from app.config import ConfigClass

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
for name in ("tortoise", "tortoise.db_client", "tortoise.backends", "tortoise.query"):
    logging.getLogger(name).setLevel(logging.DEBUG)


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    # 本地开发阶段自动补齐缺失表结构，降低首次启动门槛。
    if ConfigClass.env_mode == 'dev':
        await Tortoise.generate_schemas(safe=True)
    if ConfigClass.db.engine != "sqlite":
        await ensure_admin_compat_schema_extensions()
    # 仅在调试时打开
    connections.get("default").log_queries = ConfigClass.env_mode == 'dev'


async def close_db():
    await Tortoise.close_connections()


# ✅ 供 Aerich 使用
TORTOISE_ORM = {
    "connections": {
        "default": ConfigClass.db.url  # 使用你的动态配置
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",  # ✅ Aerich 自带表结构必须添加
                "app.api.admin_compat.models",
            ],
            "default_connection": "default"
        },
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai"
}

# 是否启用逻辑删除
LOGIC_DELETE_ENABLED = True


async def ensure_admin_compat_schema_extensions():
    """
    兼容层当前仍以“启动自动补结构”为主。

    Tortoise 的 `generate_schemas` 只能补表，不能给已有表补新增字段，
    所以这里仅保留当前单系统还需要的补列逻辑。
    """

    connection = connections.get("default")

    column_specs = [
        ("admin_compat_role", "is_system_role", "`is_system_role` TINYINT NOT NULL DEFAULT 0 COMMENT '是否系统内置角色'"),
        ("admin_compat_dictionary_data", "color", "`color` VARCHAR(30) NULL COMMENT '显示颜色'"),
        ("admin_compat_dictionary_data", "ripple", "`ripple` TINYINT NOT NULL DEFAULT 0 COMMENT '是否开启波纹，0 否，1 是'"),
    ]
    for table_name, column_name, column_sql in column_specs:
        await _add_column_if_missing(connection, table_name, column_name, column_sql)

    await _ensure_role_unique_index(connection)
    await _ensure_patrol_task_table(connection)
    await _ensure_patrol_area_table(connection)
    await _ensure_patrol_point_table(connection)
    await _ensure_patrol_task_point_table(connection)
    await _ensure_patrol_user_device_table(connection)
    await _ensure_inspection_event_table(connection)
    await _ensure_evidence_file_table(connection)
    await _ensure_work_order_table(connection)
    await _ensure_work_order_flow_table(connection)
    await _ensure_push_record_table(connection)
    await _ensure_inspection_report_table(connection)
    await _ensure_law_document_table(connection)
    await _ensure_print_record_table(connection)


async def _add_column_if_missing(connection, table_name: str, column_name: str, column_sql: str):
    rows = await connection.execute_query_dict(
        """
        SELECT COUNT(*) AS count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        [table_name, column_name],
    )
    if rows and int(rows[0].get("count", 0)) > 0:
        return
    await connection.execute_query(f"ALTER TABLE `{table_name}` ADD COLUMN {column_sql}")


async def _add_index_if_missing(
    connection,
    table_name: str,
    index_name: str,
    columns: Iterable[str],
):
    rows = await connection.execute_query_dict(
        """
        SELECT COUNT(*) AS count
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
        """,
        [table_name, index_name],
    )
    if rows and int(rows[0].get("count", 0)) > 0:
        return

    column_sql = ", ".join(f"`{column}`" for column in columns)
    await connection.execute_query(
        f"ALTER TABLE `{table_name}` ADD INDEX `{index_name}` ({column_sql})"
    )


async def _ensure_role_unique_index(connection):
    """
    单系统下角色标识保持全局唯一。
    """

    rows = await connection.execute_query_dict(
        """
        SELECT INDEX_NAME, NON_UNIQUE
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'admin_compat_role'
        GROUP BY INDEX_NAME, NON_UNIQUE
        """
    )
    existing_index_names = {row["INDEX_NAME"] for row in rows}
    if "uniq_admin_compa_role__role_code" in existing_index_names:
        return
    for row in rows:
        index_name = row["INDEX_NAME"]
        if index_name == "PRIMARY":
            continue
        if int(row.get("NON_UNIQUE", 1)) == 0:
            await connection.execute_query(
                f"ALTER TABLE `admin_compat_role` DROP INDEX `{index_name}`"
            )
    await connection.execute_query(
        """
        ALTER TABLE `admin_compat_role`
        ADD UNIQUE INDEX `uniq_admin_compa_role__role_code` (`role_code`)
        """
    )


async def _ensure_patrol_task_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_patrol_task` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `task_code` VARCHAR(40) NOT NULL COMMENT '任务编号',
          `task_title` VARCHAR(200) NOT NULL COMMENT '任务标题',
          `task_type` VARCHAR(50) NOT NULL COMMENT '任务类型字典值',
          `patrol_location` VARCHAR(200) NOT NULL COMMENT '巡查地点',
          `plan_time` DATETIME(6) NOT NULL COMMENT '计划时间',
          `executor_id` INT NULL COMMENT '执行人 ID',
          `executor_name` VARCHAR(100) NOT NULL COMMENT '执行人名称',
          `task_status` VARCHAR(50) NOT NULL COMMENT '任务状态字典值',
          `progress` INT NOT NULL DEFAULT 0 COMMENT '完成进度',
          `exception_count` INT NOT NULL DEFAULT 0 COMMENT '异常事件数',
          `creator_id` INT NULL COMMENT '创建人 ID',
          `creator_name` VARCHAR(100) NOT NULL COMMENT '创建人名称',
          UNIQUE KEY `uniq_admin_compa_patrol_task_code` (`task_code`),
          KEY `idx_admin_compa_patrol_task_type` (`task_type`),
          KEY `idx_admin_compa_patrol_task_status` (`task_status`),
          KEY `idx_admin_compa_patrol_plan_time` (`plan_time`),
          KEY `idx_admin_compa_patrol_executor` (`executor_id`),
          KEY `idx_admin_compa_patrol_creator` (`creator_id`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查任务表'
        """
    )
    task_columns = [
        ("priority", "`priority` VARCHAR(30) NOT NULL DEFAULT 'medium' COMMENT '任务优先级字典值'"),
        ("description", "`description` TEXT NULL COMMENT '任务说明'"),
        ("ai_focus", "`ai_focus` TINYINT NOT NULL DEFAULT 0 COMMENT '是否 AI 识别重点任务，0 否，1 是'"),
        ("area_ids", "`area_ids` JSON NULL COMMENT '巡查社区面 ID 集合'"),
        ("point_ids", "`point_ids` JSON NULL COMMENT '巡查点位 ID 集合'"),
        ("start_time", "`start_time` DATETIME(6) NULL COMMENT '任务开始时间'"),
        ("end_time", "`end_time` DATETIME(6) NULL COMMENT '任务结束时间'"),
        ("duration_hours", "`duration_hours` INT NOT NULL DEFAULT 1 COMMENT '预计时长，单位小时'"),
        ("repeat_rule", "`repeat_rule` VARCHAR(50) NOT NULL DEFAULT 'none' COMMENT '重复规则字典值'"),
    ]
    for column_name, column_sql in task_columns:
        await _add_column_if_missing(
            connection,
            "admin_compat_patrol_task",
            column_name,
            column_sql,
        )
    await _add_index_if_missing(
        connection,
        "admin_compat_patrol_task",
        "idx_admin_compa_patrol_start_time",
        ("start_time",),
    )
    await _add_index_if_missing(
        connection,
        "admin_compat_patrol_task",
        "idx_admin_compa_patrol_end_time",
        ("end_time",),
    )


async def _ensure_patrol_area_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_patrol_area` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `area_code` VARCHAR(50) NOT NULL COMMENT '区域编码',
          `area_name` VARCHAR(100) NOT NULL COMMENT '区域名称',
          `center_lat` DOUBLE NOT NULL COMMENT '中心点纬度',
          `center_lng` DOUBLE NOT NULL COMMENT '中心点经度',
          `boundary` JSON NULL COMMENT '区域边界坐标',
          `sort_number` INT NOT NULL DEFAULT 0 COMMENT '排序值',
          `comments` TEXT NULL COMMENT '备注',
          UNIQUE KEY `uniq_admin_compa_patrol_area_code` (`area_code`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查社区面表'
        """
    )


async def _ensure_patrol_point_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_patrol_point` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `area_id` INT NOT NULL COMMENT '所属区域 ID',
          `point_code` VARCHAR(50) NOT NULL COMMENT '点位编码',
          `point_name` VARCHAR(100) NOT NULL COMMENT '点位名称',
          `point_type` VARCHAR(50) NOT NULL DEFAULT 'building' COMMENT '点位类型',
          `lat` DOUBLE NOT NULL COMMENT '纬度',
          `lng` DOUBLE NOT NULL COMMENT '经度',
          `sort_number` INT NOT NULL DEFAULT 0 COMMENT '排序值',
          `comments` TEXT NULL COMMENT '备注',
          UNIQUE KEY `uniq_admin_compa_patrol_point_code` (`point_code`),
          KEY `idx_admin_compa_patrol_point_area` (`area_id`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查点位表'
        """
    )


async def _ensure_patrol_task_point_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_patrol_task_point` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `task_id` INT NOT NULL COMMENT '任务 ID',
          `point_id` INT NOT NULL COMMENT '基础点位 ID',
          `point_code` VARCHAR(50) NOT NULL COMMENT '点位编码',
          `point_name` VARCHAR(100) NOT NULL COMMENT '点位名称',
          `address` VARCHAR(255) NOT NULL COMMENT '点位地址',
          `lat` DOUBLE NOT NULL COMMENT '纬度',
          `lng` DOUBLE NOT NULL COMMENT '经度',
          `status` VARCHAR(50) NOT NULL DEFAULT 'PENDING' COMMENT '点位巡查状态',
          `arrived_time` DATETIME(6) NULL COMMENT '到达时间',
          `started_time` DATETIME(6) NULL COMMENT '开始巡查时间',
          `closed_time` DATETIME(6) NULL COMMENT '闭环时间',
          `pre_check` JSON NULL COMMENT '点位预检信息',
          UNIQUE KEY `uniq_admin_compa_task_point` (`task_id`, `point_id`),
          KEY `idx_admin_compa_task_point_task` (`task_id`),
          KEY `idx_admin_compa_task_point_point` (`point_id`),
          KEY `idx_admin_compa_task_point_status` (`status`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查任务点位表'
        """
    )


async def _ensure_patrol_user_device_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_patrol_user_device` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `user_id` INT NOT NULL COMMENT '用户 ID',
          `user_name` VARCHAR(100) NOT NULL COMMENT '巡查员名称',
          `employee_no` VARCHAR(50) NOT NULL COMMENT '工号',
          `device_type` VARCHAR(50) NOT NULL COMMENT '设备类型',
          `device_name` VARCHAR(100) NOT NULL COMMENT '设备名称',
          `device_sn` VARCHAR(100) NOT NULL COMMENT '设备序列号',
          `online_status` VARCHAR(20) NOT NULL DEFAULT 'online' COMMENT '在线状态',
          `bind_status` VARCHAR(20) NOT NULL DEFAULT 'bound' COMMENT '绑定状态',
          UNIQUE KEY `uniq_admin_compa_patrol_user_device` (`user_id`, `device_type`),
          KEY `idx_admin_compa_patrol_user_device_user` (`user_id`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查员设备绑定表'
        """
    )


async def _ensure_inspection_event_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_inspection_event` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `event_code` VARCHAR(50) NOT NULL COMMENT '事件编号',
          `event_title` VARCHAR(200) NOT NULL COMMENT '事件标题',
          `event_type` VARCHAR(50) NOT NULL COMMENT '事件类型',
          `risk_level` VARCHAR(30) NOT NULL COMMENT '风险等级',
          `source` VARCHAR(50) NOT NULL DEFAULT 'AI识别' COMMENT '事件来源',
          `status` VARCHAR(50) NOT NULL COMMENT '事件状态',
          `task_id` INT NULL COMMENT '关联任务 ID',
          `task_code` VARCHAR(40) NULL COMMENT '关联任务编号',
          `inspector_id` INT NULL COMMENT '巡查员 ID',
          `inspector_name` VARCHAR(100) NOT NULL COMMENT '巡查员名称',
          `area_id` INT NULL COMMENT '所属区域 ID',
          `area_name` VARCHAR(100) NOT NULL COMMENT '所属区域名称',
          `point_id` INT NULL COMMENT '关联点位 ID',
          `point_name` VARCHAR(100) NOT NULL COMMENT '点位名称',
          `lat` DOUBLE NOT NULL COMMENT '纬度',
          `lng` DOUBLE NOT NULL COMMENT '经度',
          `confidence` DOUBLE NOT NULL DEFAULT 0 COMMENT 'AI 识别置信度',
          `description` TEXT NULL COMMENT '事件描述',
          `image_url` VARCHAR(500) NULL COMMENT '现场图片',
          `detected_time` DATETIME(6) NULL COMMENT '识别时间',
          UNIQUE KEY `uniq_admin_compa_event_code` (`event_code`),
          KEY `idx_admin_compa_event_risk` (`risk_level`),
          KEY `idx_admin_compa_event_status` (`status`),
          KEY `idx_admin_compa_event_task` (`task_id`),
          KEY `idx_admin_compa_event_area` (`area_id`),
          KEY `idx_admin_compa_event_point` (`point_id`),
          KEY `idx_admin_compa_event_detected_time` (`detected_time`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查事件表'
        """
    )
    event_columns = [
        ("event_type_name", "`event_type_name` VARCHAR(100) NULL COMMENT '事件类型名称'"),
        ("risk_level_name", "`risk_level_name` VARCHAR(50) NULL COMMENT '风险等级名称'"),
        ("marked_image_url", "`marked_image_url` VARCHAR(500) NULL COMMENT '标注图片'"),
        ("bbox", "`bbox` JSON NULL COMMENT 'AI 标注框'"),
        ("model_name", "`model_name` VARCHAR(100) NULL COMMENT 'AI 模型名称'"),
        ("model_version", "`model_version` VARCHAR(50) NULL COMMENT 'AI 模型版本'"),
    ]
    for column_name, column_sql in event_columns:
        await _add_column_if_missing(
            connection,
            "admin_compat_inspection_event",
            column_name,
            column_sql,
        )


async def _ensure_evidence_file_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_evidence_file` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `evidence_no` VARCHAR(50) NOT NULL COMMENT '证据编号',
          `task_id` INT NOT NULL COMMENT '任务 ID',
          `point_record_id` INT NULL COMMENT '任务点位记录 ID',
          `point_id` INT NULL COMMENT '基础点位 ID',
          `detection_id` INT NULL COMMENT 'AI 识别事件 ID',
          `file_type` VARCHAR(30) NOT NULL DEFAULT 'IMAGE' COMMENT '文件类型',
          `file_name` VARCHAR(200) NOT NULL COMMENT '文件名称',
          `file_url` VARCHAR(500) NOT NULL COMMENT '文件地址',
          `captured_by_id` VARCHAR(50) NULL COMMENT '取证人 ID',
          `captured_by_name` VARCHAR(100) NOT NULL COMMENT '取证人',
          `captured_time` DATETIME(6) NULL COMMENT '取证时间',
          UNIQUE KEY `uniq_admin_compa_evidence_no` (`evidence_no`),
          KEY `idx_admin_compa_evidence_task` (`task_id`),
          KEY `idx_admin_compa_evidence_point_record` (`point_record_id`),
          KEY `idx_admin_compa_evidence_point` (`point_id`),
          KEY `idx_admin_compa_evidence_detection` (`detection_id`),
          KEY `idx_admin_compa_evidence_time` (`captured_time`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查取证表'
        """
    )


async def _ensure_work_order_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_work_order` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `work_order_code` VARCHAR(50) NOT NULL COMMENT '工单编号',
          `title` VARCHAR(200) NOT NULL COMMENT '工单标题',
          `risk_level` VARCHAR(30) NOT NULL COMMENT '风险等级',
          `source` VARCHAR(50) NOT NULL DEFAULT 'AI识别' COMMENT '来源',
          `reporter_id` INT NULL COMMENT '上报人 ID',
          `reporter_name` VARCHAR(100) NOT NULL COMMENT '上报人',
          `area_id` INT NULL COMMENT '所属区域 ID',
          `area_name` VARCHAR(100) NOT NULL COMMENT '所属区域',
          `point_name` VARCHAR(100) NULL COMMENT '点位名称',
          `event_id` INT NULL COMMENT '关联事件 ID',
          `task_id` INT NULL COMMENT '关联任务 ID',
          `status` VARCHAR(50) NOT NULL COMMENT '工单状态',
          `platform_code` VARCHAR(80) NULL COMMENT '治理平台工单号',
          `deadline_time` DATETIME(6) NULL COMMENT '处置截止时间',
          `remaining_minutes` INT NOT NULL DEFAULT 0 COMMENT '剩余分钟',
          `responsible_department` VARCHAR(120) NULL COMMENT '责任部门',
          `handler_name` VARCHAR(100) NULL COMMENT '处理人',
          `description` TEXT NULL COMMENT '隐患描述',
          `suggestion` TEXT NULL COMMENT '处置建议',
          `timeline` JSON NULL COMMENT '流转记录',
          UNIQUE KEY `uniq_admin_compa_work_order_code` (`work_order_code`),
          KEY `idx_admin_compa_work_order_risk` (`risk_level`),
          KEY `idx_admin_compa_work_order_status` (`status`),
          KEY `idx_admin_compa_work_order_reporter` (`reporter_id`),
          KEY `idx_admin_compa_work_order_area` (`area_id`),
          KEY `idx_admin_compa_work_order_event` (`event_id`),
          KEY `idx_admin_compa_work_order_task` (`task_id`),
          KEY `idx_admin_compa_work_order_deadline` (`deadline_time`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层事件工单表'
        """
    )
    work_order_columns = [
        ("event_type", "`event_type` VARCHAR(50) NULL COMMENT '隐患类型'"),
        ("event_type_name", "`event_type_name` VARCHAR(100) NULL COMMENT '隐患类型名称'"),
        ("risk_level_name", "`risk_level_name` VARCHAR(50) NULL COMMENT '风险等级名称'"),
        ("point_record_id", "`point_record_id` INT NULL COMMENT '关联任务点位记录 ID'"),
        ("location_name", "`location_name` VARCHAR(160) NULL COMMENT '地点名称'"),
        ("address_detail", "`address_detail` VARCHAR(255) NULL COMMENT '详细地址'"),
        ("lat", "`lat` DOUBLE NULL COMMENT '纬度'"),
        ("lng", "`lng` DOUBLE NULL COMMENT '经度'"),
        ("push_status", "`push_status` VARCHAR(50) NOT NULL DEFAULT 'NOT_PUSHED' COMMENT '推送状态'"),
        ("third_order_no", "`third_order_no` VARCHAR(100) NULL COMMENT '第三方工单编号'"),
        ("report_time", "`report_time` DATETIME(6) NULL COMMENT '上报时间'"),
        ("evidence_list", "`evidence_list` JSON NULL COMMENT '现场取证列表'"),
    ]
    for column_name, column_sql in work_order_columns:
        await _add_column_if_missing(
            connection,
            "admin_compat_work_order",
            column_name,
            column_sql,
        )
    await _add_index_if_missing(
        connection,
        "admin_compat_work_order",
        "idx_admin_compa_work_order_point_record",
        ("point_record_id",),
    )
    await _add_index_if_missing(
        connection,
        "admin_compat_work_order",
        "idx_admin_compa_work_order_push_status",
        ("push_status",),
    )
    await _add_index_if_missing(
        connection,
        "admin_compat_work_order",
        "idx_admin_compa_work_order_report_time",
        ("report_time",),
    )


async def _ensure_work_order_flow_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_work_order_flow` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `business_type` VARCHAR(50) NOT NULL COMMENT '业务类型',
          `business_id` INT NOT NULL COMMENT '业务 ID',
          `business_code` VARCHAR(80) NULL COMMENT '业务编号',
          `action` VARCHAR(80) NOT NULL COMMENT '动作',
          `from_status` VARCHAR(50) NULL COMMENT '原状态',
          `to_status` VARCHAR(50) NULL COMMENT '新状态',
          `operator_id` VARCHAR(50) NULL COMMENT '操作人 ID',
          `operator_name` VARCHAR(100) NOT NULL COMMENT '操作人',
          `remark` TEXT NULL COMMENT '说明',
          `event_type` VARCHAR(80) NULL COMMENT '预留大屏事件类型',
          `extra` JSON NULL COMMENT '扩展数据',
          KEY `idx_admin_compa_flow_business` (`business_type`, `business_id`),
          KEY `idx_admin_compa_flow_code` (`business_code`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层业务流转记录表'
        """
    )


async def _ensure_push_record_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_push_record` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `request_id` VARCHAR(80) NOT NULL COMMENT '请求编号',
          `work_order_id` INT NOT NULL COMMENT '工单 ID',
          `work_order_code` VARCHAR(50) NOT NULL COMMENT '工单编号',
          `target_platform` VARCHAR(100) NOT NULL COMMENT '目标平台',
          `push_status` VARCHAR(50) NOT NULL COMMENT '推送状态',
          `third_order_no` VARCHAR(100) NULL COMMENT '第三方工单号',
          `request_body` JSON NULL COMMENT '请求内容',
          `response_body` JSON NULL COMMENT '响应内容',
          `error_message` VARCHAR(255) NULL COMMENT '失败原因',
          `pushed_time` DATETIME(6) NULL COMMENT '推送时间',
          `operator_id` VARCHAR(50) NULL COMMENT '操作人 ID',
          `operator_name` VARCHAR(100) NOT NULL COMMENT '操作人',
          UNIQUE KEY `uniq_admin_compa_push_request` (`request_id`),
          KEY `idx_admin_compa_push_work_order` (`work_order_id`),
          KEY `idx_admin_compa_push_code` (`work_order_code`),
          KEY `idx_admin_compa_push_status` (`push_status`),
          KEY `idx_admin_compa_push_time` (`pushed_time`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层第三方推送记录表'
        """
    )


async def _ensure_inspection_report_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_inspection_report` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `report_code` VARCHAR(50) NOT NULL COMMENT '报告编号',
          `report_title` VARCHAR(200) NOT NULL COMMENT '报告标题',
          `task_id` INT NULL COMMENT '关联任务 ID',
          `work_order_id` INT NULL COMMENT '关联工单 ID',
          `report_status` VARCHAR(50) NOT NULL COMMENT '报告状态',
          `closure_rate` DOUBLE NOT NULL DEFAULT 0 COMMENT '闭环率',
          `point_count` INT NOT NULL DEFAULT 0 COMMENT '巡查点位数',
          `ai_detect_count` INT NOT NULL DEFAULT 0 COMMENT 'AI 识别次数',
          `work_order_count` INT NOT NULL DEFAULT 0 COMMENT '工单数',
          `timeout_count` INT NOT NULL DEFAULT 0 COMMENT '超时数',
          `summary` TEXT NULL COMMENT '报告摘要',
          `generated_time` DATETIME(6) NULL COMMENT '生成时间',
          `archive_time` DATETIME(6) NULL COMMENT '归档时间',
          UNIQUE KEY `uniq_admin_compa_report_code` (`report_code`),
          KEY `idx_admin_compa_report_task` (`task_id`),
          KEY `idx_admin_compa_report_work_order` (`work_order_id`),
          KEY `idx_admin_compa_report_status` (`report_status`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层巡查报告表'
        """
    )


async def _ensure_law_document_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_law_document` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `document_code` VARCHAR(50) NOT NULL COMMENT '文书编号',
          `document_title` VARCHAR(200) NOT NULL COMMENT '文书标题',
          `document_type` VARCHAR(80) NOT NULL COMMENT '文书类型',
          `work_order_id` INT NULL COMMENT '关联工单 ID',
          `checked_unit` VARCHAR(160) NOT NULL COMMENT '被检查单位',
          `check_location` VARCHAR(200) NOT NULL COMMENT '检查地点',
          `print_status` VARCHAR(50) NOT NULL COMMENT '打印状态',
          `inspector_name` VARCHAR(100) NOT NULL COMMENT '巡查员',
          `content` TEXT NULL COMMENT '文书内容',
          `qr_code` VARCHAR(120) NULL COMMENT '二维码编号',
          UNIQUE KEY `uniq_admin_compa_document_code` (`document_code`),
          KEY `idx_admin_compa_document_work_order` (`work_order_id`),
          KEY `idx_admin_compa_document_print_status` (`print_status`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层文书表'
        """
    )
    document_columns = [
        ("document_type_name", "`document_type_name` VARCHAR(100) NULL COMMENT '文书类型名称'"),
        ("target_name", "`target_name` VARCHAR(160) NULL COMMENT '被检查单位/个人'"),
        ("illegal_fact", "`illegal_fact` TEXT NULL COMMENT '违法事实'"),
        ("legal_basis", "`legal_basis` TEXT NULL COMMENT '法律依据'"),
        ("rectification_requirement", "`rectification_requirement` TEXT NULL COMMENT '整改要求'"),
        ("deadline", "`deadline` VARCHAR(120) NULL COMMENT '整改期限'"),
        ("review_requirement", "`review_requirement` VARCHAR(120) NULL COMMENT '复查要求'"),
        ("status", "`status` VARCHAR(50) NOT NULL DEFAULT 'GENERATED' COMMENT '文书状态'"),
        ("qr_code_url", "`qr_code_url` VARCHAR(255) NULL COMMENT '二维码地址'"),
        ("generated_time", "`generated_time` DATETIME(6) NULL COMMENT '生成时间'"),
        ("printed_time", "`printed_time` DATETIME(6) NULL COMMENT '打印时间'"),
    ]
    for column_name, column_sql in document_columns:
        await _add_column_if_missing(
            connection,
            "admin_compat_law_document",
            column_name,
            column_sql,
        )
    await _add_index_if_missing(
        connection,
        "admin_compat_law_document",
        "idx_admin_compa_document_status",
        ("status",),
    )


async def _ensure_print_record_table(connection):
    await connection.execute_query(
        """
        CREATE TABLE IF NOT EXISTS `admin_compat_print_record` (
          `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键 ID',
          `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
          `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
          `document_id` INT NOT NULL COMMENT '文书 ID',
          `document_code` VARCHAR(50) NOT NULL COMMENT '文书编号',
          `printer_name` VARCHAR(120) NOT NULL COMMENT '打印机名称',
          `print_status` VARCHAR(50) NOT NULL COMMENT '打印状态',
          `operator_id` VARCHAR(50) NULL COMMENT '操作人 ID',
          `operator_name` VARCHAR(100) NOT NULL COMMENT '操作人',
          `printed_time` DATETIME(6) NULL COMMENT '打印时间',
          `message` VARCHAR(255) NULL COMMENT '打印结果',
          KEY `idx_admin_compa_print_document` (`document_id`),
          KEY `idx_admin_compa_print_code` (`document_code`),
          KEY `idx_admin_compa_print_status` (`print_status`),
          KEY `idx_admin_compa_print_time` (`printed_time`)
        ) CHARACTER SET utf8mb4 COMMENT='管理台兼容层文书打印记录表'
        """
    )
