from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_application` ADD `company_no` VARCHAR(50) COMMENT '数商编号';
        ALTER TABLE `cert_apply_record` ADD `company_no` VARCHAR(50) COMMENT '数商编号';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_application` DROP COLUMN `company_no`;
        ALTER TABLE `cert_apply_record` DROP COLUMN `company_no`;"""
