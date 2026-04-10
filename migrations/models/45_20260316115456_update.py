from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` ADD `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：禁用' DEFAULT 1;
        ALTER TABLE `pro_demand_apply_record` ADD `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：禁用' DEFAULT 1;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` DROP COLUMN `shelf_status`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `shelf_status`;"""
