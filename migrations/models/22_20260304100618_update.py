from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `listing_cert_date` DATE COMMENT '广东省数据资产交易标的挂牌证书-核发日期';
        ALTER TABLE `pro_product` MODIFY COLUMN `reg_cert_date` DATE COMMENT '广东省数据资产登记凭证-核发日期';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `listing_cert_date`;
        ALTER TABLE `pro_product` MODIFY COLUMN `reg_cert_date` VARCHAR(50) COMMENT '广东省数据资产登记凭证-核发日期';"""
