from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` DROP COLUMN `limit_date`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `limit_date`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` ADD `limit_date` DATE COMMENT '截止日期';
        ALTER TABLE `pro_demand_apply_record` ADD `limit_date` DATE COMMENT '截止日期';"""
