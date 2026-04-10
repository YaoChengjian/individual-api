from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `gen_label` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `label_type` VARCHAR(20) NOT NULL COMMENT '标签类型。product：产品；demand：需求；news：新闻资讯',
    `name` VARCHAR(100) NOT NULL COMMENT '标签名称',
    `desc` LONGTEXT COMMENT '标签说明',
    `status` BOOL NOT NULL COMMENT '是否启用。0：停用；1：启用' DEFAULT 1,
    `sort_num` INT NOT NULL COMMENT '排序值（值越大越靠前）' DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='通用标签表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `gen_label`;"""
