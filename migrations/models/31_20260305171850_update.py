from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `gen_label` ADD `color` VARCHAR(32) COMMENT '标签颜色色号';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `gen_label` DROP COLUMN `color`;"""
