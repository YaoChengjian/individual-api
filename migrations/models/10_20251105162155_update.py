from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_ecology` ADD `cover_url` VARCHAR(300) COMMENT '形态图片URL';
        ALTER TABLE `pro_scene` ADD `cover_url` VARCHAR(300) COMMENT '场景图片URL';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_scene` DROP COLUMN `cover_url`;
        ALTER TABLE `pro_ecology` DROP COLUMN `cover_url`;"""
