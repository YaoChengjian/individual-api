from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `pol_news` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `title` VARCHAR(300) NOT NULL COMMENT '标题',
    `cover_url` VARCHAR(600) NOT NULL COMMENT '封面图链接',
    `news_type` VARCHAR(100) NOT NULL COMMENT '类型',
    `source` VARCHAR(200) NOT NULL COMMENT '来源',
    `publish_time` DATETIME(6) NOT NULL COMMENT '发布时间',
    `is_top` BOOL NOT NULL COMMENT '是否置顶。0：否；1：是' DEFAULT 0,
    `status` BOOL NOT NULL COMMENT '是否启用。0：停用；1：启用' DEFAULT 1,
    `content` LONGTEXT NOT NULL COMMENT '新闻内容（富文本）'
) CHARACTER SET utf8mb4 COMMENT='政策法规-新闻资讯表';
        CREATE TABLE IF NOT EXISTS `pol_news_label_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `news_id` VARCHAR(32) NOT NULL COMMENT '新闻资讯ID',
    `label_id` VARCHAR(32) NOT NULL COMMENT '标签ID'
) CHARACTER SET utf8mb4 COMMENT='政策法规-新闻资讯与标签关系表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `pol_news`;
        DROP TABLE IF EXISTS `pol_news_label_rel`;"""
