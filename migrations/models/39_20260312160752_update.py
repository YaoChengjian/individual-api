from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` ADD `email` VARCHAR(100) COMMENT '邮箱';
        ALTER TABLE `pro_demand` ADD `demand_detail` LONGTEXT COMMENT '需求详情';
        ALTER TABLE `pro_demand` MODIFY COLUMN `desc` LONGTEXT COMMENT '需求说明（概要）';
        ALTER TABLE `pro_demand_apply_record` ADD `email` VARCHAR(100) COMMENT '邮箱';
        ALTER TABLE `pro_demand_apply_record` ADD `demand_detail` LONGTEXT COMMENT '需求详情';
        ALTER TABLE `pro_demand_apply_record` MODIFY COLUMN `desc` LONGTEXT COMMENT '需求说明（概要）';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` DROP COLUMN `email`;
        ALTER TABLE `pro_demand` DROP COLUMN `demand_detail`;
        ALTER TABLE `pro_demand` MODIFY COLUMN `desc` LONGTEXT COMMENT '需求说明';
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `email`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `demand_detail`;
        ALTER TABLE `pro_demand_apply_record` MODIFY COLUMN `desc` LONGTEXT COMMENT '需求说明';"""
