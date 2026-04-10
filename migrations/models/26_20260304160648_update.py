from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_scene` ADD `is_show_portal` BOOL NOT NULL COMMENT '是否展示在门户。0：隐藏；1：展示' DEFAULT 0;
        ALTER TABLE `pro_scene` ADD `status` BOOL NOT NULL COMMENT '是否启用。0：停用；1：启用' DEFAULT 1;
        ALTER TABLE `pro_scene` ADD `sort_num` INT COMMENT '排序值';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_scene` DROP COLUMN `is_show_portal`;
        ALTER TABLE `pro_scene` DROP COLUMN `status`;
        ALTER TABLE `pro_scene` DROP COLUMN `sort_num`;"""
