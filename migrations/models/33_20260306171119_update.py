from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `listing_cert_code` VARCHAR(50) COMMENT '广东省数据资产交易标的挂牌证书-编码';
        ALTER TABLE `pro_product_apply_record` ADD `listing_cert_code` VARCHAR(50) COMMENT '广东省数据资产交易标的挂牌证书编码';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `listing_cert_code`;
        ALTER TABLE `pro_product_apply_record` DROP COLUMN `listing_cert_code`;"""
