from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `web_user` ADD `avatar_url` VARCHAR(500) COMMENT '头像链接';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `web_user` DROP COLUMN `avatar_url`;"""
