from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `pro_product_tag`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
