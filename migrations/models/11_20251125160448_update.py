from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_application` DROP COLUMN `reg_address_detail`;
        ALTER TABLE `cert_application` DROP COLUMN `email`;
        ALTER TABLE `cert_legal_person` MODIFY COLUMN `id_number` VARCHAR(64) COMMENT '证件号';
        ALTER TABLE `cert_legal_person` MODIFY COLUMN `id_type` INT COMMENT '证件类型。1：身份证';
        ALTER TABLE `cert_legal_person` MODIFY COLUMN `name` VARCHAR(50) COMMENT '姓名';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_legal_person` MODIFY COLUMN `id_number` VARCHAR(64) NOT NULL COMMENT '证件号';
        ALTER TABLE `cert_legal_person` MODIFY COLUMN `id_type` INT NOT NULL COMMENT '证件类型。1：身份证';
        ALTER TABLE `cert_legal_person` MODIFY COLUMN `name` VARCHAR(50) NOT NULL COMMENT '姓名';
        ALTER TABLE `cert_application` ADD `reg_address_detail` VARCHAR(300) COMMENT '详细地址';
        ALTER TABLE `cert_application` ADD `email` VARCHAR(120) COMMENT '邮箱';"""
