from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` ADD `data_version` VARCHAR(50) COMMENT '数据版本';
        ALTER TABLE `pro_product` ADD `data_origin` VARCHAR(200) COMMENT '数据来源';
        ALTER TABLE `pro_product` ADD `listing_cert_url` VARCHAR(300) COMMENT '广东省数据资产交易标的挂牌证书-URL';
        ALTER TABLE `pro_product` ADD `update_date` DATE COMMENT '数据最后更新日期';
        ALTER TABLE `pro_product` ADD `data_volume` VARCHAR(50) COMMENT '数据量';
        ALTER TABLE `pro_product` ADD `email` VARCHAR(100) COMMENT '邮箱';
        ALTER TABLE `pro_product` ADD `authorization_type` VARCHAR(100) COMMENT '授权类型';
        ALTER TABLE `pro_product` ADD `update_frequency` VARCHAR(50) COMMENT '更新频率';
        ALTER TABLE `pro_product` MODIFY COLUMN `origin_type` VARCHAR(50) NOT NULL COMMENT '创建的数据来源端。web:web用户创建；admin:后台用户创建' DEFAULT 'web';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` DROP COLUMN `data_version`;
        ALTER TABLE `pro_product` DROP COLUMN `data_origin`;
        ALTER TABLE `pro_product` DROP COLUMN `listing_cert_url`;
        ALTER TABLE `pro_product` DROP COLUMN `update_date`;
        ALTER TABLE `pro_product` DROP COLUMN `data_volume`;
        ALTER TABLE `pro_product` DROP COLUMN `email`;
        ALTER TABLE `pro_product` DROP COLUMN `authorization_type`;
        ALTER TABLE `pro_product` DROP COLUMN `update_frequency`;
        ALTER TABLE `pro_product` MODIFY COLUMN `origin_type` VARCHAR(50) NOT NULL COMMENT '数据来源。web:web用户创建；admin:后台用户创建' DEFAULT 'web';"""
