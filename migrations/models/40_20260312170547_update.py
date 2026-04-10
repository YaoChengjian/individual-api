from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` MODIFY COLUMN `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：禁用' DEFAULT 1;
        ALTER TABLE `pro_product_apply_record` MODIFY COLUMN `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：禁用' DEFAULT 1;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` MODIFY COLUMN `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：管理员强制下架' DEFAULT 1;
        ALTER TABLE `pro_product_apply_record` MODIFY COLUMN `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：管理员强制下架' DEFAULT 1;"""
