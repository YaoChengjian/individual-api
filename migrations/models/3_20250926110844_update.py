from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` MODIFY COLUMN `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；4：撤销申请' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_product` MODIFY COLUMN `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；' DEFAULT 0;"""
