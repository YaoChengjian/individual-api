from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `sys_portal_ranking` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `ranking_type` VARCHAR(30) NOT NULL COMMENT '排行榜类型。product：产品；business_zone：数商专区',
    `target_id` VARCHAR(64) NOT NULL COMMENT '关联目标ID',
    `status` BOOL NOT NULL COMMENT '是否展示。0：隐藏；1：展示' DEFAULT 1,
    `sort_num` INT NOT NULL COMMENT '排序值（值越大越靠前）' DEFAULT 0,
    UNIQUE KEY `uid_sys_portal__ranking_64e1db` (`ranking_type`, `target_id`),
    KEY `idx_sys_portal__ranking_232dd8` (`ranking_type`),
    KEY `idx_sys_portal__target__818cc0` (`target_id`)
) CHARACTER SET utf8mb4 COMMENT='门户排行榜表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `sys_portal_ranking`;"""
