from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `review_time` DATETIME(6) COMMENT '审核时间';
        ALTER TABLE `pro_product_apply_record` ADD `review_time` DATETIME(6) COMMENT '审核时间';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `review_time`;
        ALTER TABLE `pro_product_apply_record` DROP COLUMN `review_time`;"""
