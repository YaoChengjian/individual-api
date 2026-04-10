from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_application` ADD `disable_reason` LONGTEXT COMMENT '禁用原因';
        ALTER TABLE `cert_application` ADD `enable_time` DATETIME(6) COMMENT '启用时间';
        ALTER TABLE `cert_application` ADD `enable_operator_user_id` VARCHAR(64) COMMENT '启用操作人ID';
        ALTER TABLE `cert_application` ADD `disable_operator_user_id` VARCHAR(64) COMMENT '禁用操作人ID';
        ALTER TABLE `cert_application` ADD `disable_time` DATETIME(6) COMMENT '禁用时间';
        ALTER TABLE `cert_application` ADD `is_disable` BOOL NOT NULL COMMENT '是否禁用。false：未禁用；true：已禁用' DEFAULT 0;
        CREATE TABLE IF NOT EXISTS `cert_disable_record` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `cert_id` VARCHAR(64) NOT NULL COMMENT '认证ID',
    `user_id` VARCHAR(64) NOT NULL COMMENT '关联Web用户ID',
    `disable_time` DATETIME(6) NOT NULL COMMENT '禁用时间' DEFAULT CURRENT_TIMESTAMP(6),
    `disable_operator_user_id` VARCHAR(64) NOT NULL COMMENT '禁用操作人ID',
    `disable_reason` LONGTEXT COMMENT '禁用原因',
    `enable_time` DATETIME(6) COMMENT '启用时间',
    `enable_operator_user_id` VARCHAR(64) COMMENT '启用操作人ID',
    KEY `idx_cert_disabl_cert_id_3d6d5e` (`cert_id`),
    KEY `idx_cert_disabl_user_id_dccc79` (`user_id`)
) CHARACTER SET utf8mb4 COMMENT='数商禁用记录表';
        CREATE TABLE IF NOT EXISTS `cert_disable_resource_record` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `disable_record_id` VARCHAR(64) NOT NULL COMMENT '禁用记录ID',
    `resource_type` VARCHAR(32) NOT NULL COMMENT '资源类型',
    `resource_id` VARCHAR(64) NOT NULL COMMENT '资源ID',
    `before_shelf_status` INT NOT NULL COMMENT '禁用前上架状态',
    KEY `idx_cert_disabl_disable_72eff3` (`disable_record_id`),
    KEY `idx_cert_disabl_resourc_bda35e` (`resource_type`),
    KEY `idx_cert_disabl_resourc_1dbaec` (`resource_id`)
) CHARACTER SET utf8mb4 COMMENT='数商禁用影响资源记录表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `cert_application` DROP COLUMN `disable_reason`;
        ALTER TABLE `cert_application` DROP COLUMN `enable_time`;
        ALTER TABLE `cert_application` DROP COLUMN `enable_operator_user_id`;
        ALTER TABLE `cert_application` DROP COLUMN `disable_operator_user_id`;
        ALTER TABLE `cert_application` DROP COLUMN `disable_time`;
        ALTER TABLE `cert_application` DROP COLUMN `is_disable`;
        DROP TABLE IF EXISTS `cert_disable_record`;
        DROP TABLE IF EXISTS `cert_disable_resource_record`;"""
