from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `sys_banner` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `title` VARCHAR(200) NOT NULL COMMENT '轮播图标题',
    `cover_url` VARCHAR(600) NOT NULL COMMENT '轮播图片',
    `jump_url` VARCHAR(1000) COMMENT '跳转内容（HTTP链接）',
    `sort_num` INT NOT NULL COMMENT '轮播顺序',
    `status` BOOL NOT NULL COMMENT '是否展示。0：隐藏；1：展示' DEFAULT 1
) CHARACTER SET utf8mb4 COMMENT='系统轮播图表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `sys_banner`;"""
