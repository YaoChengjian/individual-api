from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` ADD `reason` LONGTEXT COMMENT '驳回理由';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` DROP COLUMN `reason`;"""
