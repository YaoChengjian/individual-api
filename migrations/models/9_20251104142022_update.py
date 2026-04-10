from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_ecology` ADD `desc` LONGTEXT COMMENT '形态说明';
        ALTER TABLE `pro_product` ADD `origin_type` VARCHAR(50) NOT NULL COMMENT '数据来源。web:web用户创建；admin:后台用户创建' DEFAULT 'web';
        ALTER TABLE `pro_scene` ADD `desc` LONGTEXT COMMENT '场景说明';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_scene` DROP COLUMN `desc`;
        ALTER TABLE `pro_ecology` DROP COLUMN `desc`;
        ALTER TABLE `pro_product` DROP COLUMN `origin_type`;"""
