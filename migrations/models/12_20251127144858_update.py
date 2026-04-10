from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `publisher_name`;
        ALTER TABLE `pro_product` DROP COLUMN `product_scene`;
        ALTER TABLE `pro_product` DROP COLUMN `settle_requirement`;
        ALTER TABLE `pro_product` DROP COLUMN `limit_date`;
        ALTER TABLE `pro_product` DROP COLUMN `product_detail`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `publisher_name` VARCHAR(50) COMMENT '发布者名称';
        ALTER TABLE `pro_product` ADD `product_scene` LONGTEXT COMMENT '产品应用场景';
        ALTER TABLE `pro_product` ADD `settle_requirement` LONGTEXT COMMENT '结算要求';
        ALTER TABLE `pro_product` ADD `limit_date` DATE COMMENT '截止日期';
        ALTER TABLE `pro_product` ADD `product_detail` LONGTEXT COMMENT '产品详情';"""
