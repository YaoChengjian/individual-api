from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `sys_portal_config` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `metrics_source_type` VARCHAR(20) NOT NULL COMMENT '统计指标来源。api：调接口；custom：自定义' DEFAULT 'api',
    `ranking_source_type` VARCHAR(20) NOT NULL COMMENT '排行榜来源。api：调接口；custom：自定义' DEFAULT 'api',
    `tail_content` LONGTEXT COMMENT '尾页配置（富文本）'
) CHARACTER SET utf8mb4 COMMENT='门户配置表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `sys_portal_config`;"""
