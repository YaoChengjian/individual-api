from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `sys_portal_config` DROP COLUMN `tail_content`;
        CREATE TABLE IF NOT EXISTS `sys_portal_tail_config` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `tail_content` LONGTEXT NOT NULL COMMENT '尾页配置（富文本）'
) CHARACTER SET utf8mb4 COMMENT='门户尾页配置表';
        ALTER TABLE `pro_product` ADD `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：管理员强制下架' DEFAULT 1;
        ALTER TABLE `pro_product_apply_record` ADD `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：管理员强制下架' DEFAULT 1;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `shelf_status`;
        ALTER TABLE `sys_portal_config` ADD `tail_content` LONGTEXT COMMENT '尾页配置（富文本）';
        ALTER TABLE `pro_product_apply_record` DROP COLUMN `shelf_status`;
        DROP TABLE IF EXISTS `sys_portal_tail_config`;"""
