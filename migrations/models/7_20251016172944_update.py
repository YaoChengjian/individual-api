from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand` MODIFY COLUMN `user_id` VARCHAR(32) NOT NULL COMMENT 'Web用户ID';
        ALTER TABLE `pro_demand_tag` MODIFY COLUMN `demand_id` VARCHAR(32) NOT NULL COMMENT '需求ID';
        ALTER TABLE `pro_ecology` MODIFY COLUMN `parent_id` VARCHAR(32) COMMENT '父级分类ID';
        ALTER TABLE `pro_product` MODIFY COLUMN `user_id` VARCHAR(32) NOT NULL COMMENT 'Web用户ID';
        ALTER TABLE `pro_product_ecology_rel` MODIFY COLUMN `ecology_id` VARCHAR(32) NOT NULL COMMENT '产品形态ID';
        ALTER TABLE `pro_product_ecology_rel` MODIFY COLUMN `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID';
        ALTER TABLE `pro_product_scene_rel` MODIFY COLUMN `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID';
        ALTER TABLE `pro_product_scene_rel` MODIFY COLUMN `scene_id` VARCHAR(32) NOT NULL COMMENT '应用场景ID';
        ALTER TABLE `pro_product_tag` MODIFY COLUMN `product_id` VARCHAR(32) NOT NULL COMMENT '产品ID';
        ALTER TABLE `pro_scene` MODIFY COLUMN `parent_id` VARCHAR(32) COMMENT '父级分类ID';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_scene` MODIFY COLUMN `parent_id` VARCHAR(64) COMMENT '父级分类ID';
        ALTER TABLE `pro_demand` MODIFY COLUMN `user_id` VARCHAR(64) NOT NULL COMMENT 'Web用户ID';
        ALTER TABLE `pro_ecology` MODIFY COLUMN `parent_id` VARCHAR(64) COMMENT '父级分类ID';
        ALTER TABLE `pro_product` MODIFY COLUMN `user_id` VARCHAR(64) NOT NULL COMMENT 'Web用户ID';
        ALTER TABLE `pro_demand_tag` MODIFY COLUMN `demand_id` VARCHAR(64) NOT NULL COMMENT '需求ID';
        ALTER TABLE `pro_product_tag` MODIFY COLUMN `product_id` VARCHAR(64) NOT NULL COMMENT '产品ID';
        ALTER TABLE `pro_product_scene_rel` MODIFY COLUMN `product_id` VARCHAR(64) NOT NULL COMMENT '产品ID';
        ALTER TABLE `pro_product_scene_rel` MODIFY COLUMN `scene_id` VARCHAR(64) NOT NULL COMMENT '应用场景ID';
        ALTER TABLE `pro_product_ecology_rel` MODIFY COLUMN `ecology_id` VARCHAR(64) NOT NULL COMMENT '产品形态ID';
        ALTER TABLE `pro_product_ecology_rel` MODIFY COLUMN `product_id` VARCHAR(64) NOT NULL COMMENT '产品ID';"""
