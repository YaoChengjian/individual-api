from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `product_pic` VARCHAR(300) COMMENT '产品图片';
        ALTER TABLE `pro_product_apply_record` ADD `product_pic` VARCHAR(300) COMMENT '产品图片';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `product_pic`;
        ALTER TABLE `pro_product_apply_record` DROP COLUMN `product_pic`;"""
