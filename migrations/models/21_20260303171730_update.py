from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `sys_custom_metrics` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `icon` VARCHAR(600) NOT NULL COMMENT '图标（HTTP链接）',
    `metrics_name` VARCHAR(200) NOT NULL COMMENT '统计指标',
    `metrics_value` VARCHAR(300) NOT NULL COMMENT '统计值',
    `status` BOOL NOT NULL COMMENT '是否展示。0：隐藏；1：展示' DEFAULT 1,
    `sort_num` INT NOT NULL COMMENT '排序值（值越大越靠前）' DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='系统自定义统计指标表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `sys_custom_metrics`;"""
