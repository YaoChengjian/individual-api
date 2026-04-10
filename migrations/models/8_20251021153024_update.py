from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `amount` DECIMAL(15,2) NOT NULL COMMENT '金额' DEFAULT 0;
        ALTER TABLE `pro_product` ADD `title` VARCHAR(100) COMMENT '产品标题';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `amount`;
        ALTER TABLE `pro_product` DROP COLUMN `title`;"""
