from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand_apply_record` RENAME COLUMN `tag_name_list` TO `label_name_list`;
        ALTER TABLE `pro_demand_apply_record` ADD `label_id_list` JSON NOT NULL COMMENT '申请时的标签ID列表';
        CREATE TABLE IF NOT EXISTS `pro_demand_label_rel` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `demand_id` VARCHAR(32) NOT NULL COMMENT '需求ID',
    `label_id` VARCHAR(32) NOT NULL COMMENT '标签ID（gen_label.id）'
) CHARACTER SET utf8mb4 COMMENT='需求标签关系表';
        DROP TABLE IF EXISTS `pro_demand_tag`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `pro_demand_apply_record` RENAME COLUMN `label_name_list` TO `tag_name_list`;
        ALTER TABLE `pro_demand_apply_record` DROP COLUMN `label_id_list`;
        DROP TABLE IF EXISTS `pro_demand_label_rel`;"""
