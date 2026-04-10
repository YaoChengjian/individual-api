from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` ADD `demand_no` VARCHAR(50) COMMENT '需求编号';
        ALTER TABLE `pro_demand_apply_record` ADD `demand_no` VARCHAR(50) COMMENT '需求编号';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` DROP COLUMN `demand_no`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `demand_no`;"""
