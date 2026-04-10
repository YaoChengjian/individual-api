from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product_apply_record` ADD `review_no` VARCHAR(50) COMMENT '产品审核编号';
        ALTER TABLE `pro_product_apply_record` ADD INDEX `idx_pro_product_review__310bd4` (`review_no`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product_apply_record` DROP INDEX `idx_pro_product_review__310bd4`;
        ALTER TABLE `pro_product_apply_record` DROP COLUMN `review_no`;"""
