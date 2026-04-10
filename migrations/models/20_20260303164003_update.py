from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `sys_banner_label_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `banner_id` VARCHAR(32) NOT NULL COMMENT '轮播图ID',
    `label_id` VARCHAR(32) NOT NULL COMMENT '标签ID'
) CHARACTER SET utf8mb4 COMMENT='系统轮播图与标签关系表';
        ALTER TABLE `gen_label` MODIFY COLUMN `label_type` VARCHAR(20) NOT NULL COMMENT '标签类型。product：产品；demand：需求；news：新闻资讯；banner：轮播图';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `gen_label` MODIFY COLUMN `label_type` VARCHAR(20) NOT NULL COMMENT '标签类型。product：产品；demand：需求；news：新闻资讯';
        DROP TABLE IF EXISTS `sys_banner_label_rel`;"""
