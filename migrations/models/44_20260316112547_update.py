from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` ADD `review_time` DATETIME(6) COMMENT '审核时间';
        ALTER TABLE `pro_demand_apply_record` ADD `review_time` DATETIME(6) COMMENT '审核时间';
        ALTER TABLE `pro_demand_apply_record` ADD `apply_type` INT NOT NULL COMMENT '申请类型。1：初次申请；2：变更申请' DEFAULT 1;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` DROP COLUMN `review_time`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `review_time`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `apply_type`;"""
