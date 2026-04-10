from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pol_news` ADD `desc` LONGTEXT COMMENT '新闻描述';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pol_news` DROP COLUMN `desc`;"""
