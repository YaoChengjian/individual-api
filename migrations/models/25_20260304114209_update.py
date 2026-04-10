from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `pro_product_label_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID',
    `label_id` VARCHAR(32) NOT NULL COMMENT '标签ID（gen_label.id）'
) CHARACTER SET utf8mb4 COMMENT='产品与通用标签关系表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `pro_product_label_rel`;"""
