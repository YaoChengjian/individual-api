from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `biz_business_zone` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `user_id` VARCHAR(32) NOT NULL COMMENT 'Web用户ID',
    `zone_no` VARCHAR(50) COMMENT '数商专区编号',
    `zone_name` VARCHAR(200) NOT NULL COMMENT '专区名称',
    `zone_link` VARCHAR(300) COMMENT '专区链接',
    `cover_url` VARCHAR(300) COMMENT '专区封面',
    `contact_name` VARCHAR(50) COMMENT '联系人',
    `contact_phone` VARCHAR(30) COMMENT '联系电话',
    `email` VARCHAR(100) COMMENT '邮箱',
    `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；4：撤销申请' DEFAULT 0,
    `review_time` DATETIME(6) COMMENT '审核时间',
    `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：禁用' DEFAULT 1,
    `reason` LONGTEXT COMMENT '驳回理由',
    `origin_type` VARCHAR(50) NOT NULL COMMENT '创建来源。web:前台用户；admin:后台用户' DEFAULT 'web'
) CHARACTER SET utf8mb4 COMMENT='数商专区表';
        CREATE TABLE IF NOT EXISTS `biz_business_zone_apply_record` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `zone_id` VARCHAR(32) NOT NULL COMMENT '原始专区ID',
    `review_no` VARCHAR(50) COMMENT '专区审核编号',
    `apply_type` INT NOT NULL COMMENT '申请类型。1：初次申请；2：变更申请' DEFAULT 1,
    `user_id` VARCHAR(32) NOT NULL COMMENT 'Web用户ID',
    `zone_no` VARCHAR(50) COMMENT '数商专区编号',
    `zone_name` VARCHAR(200) NOT NULL COMMENT '专区名称',
    `zone_link` VARCHAR(300) COMMENT '专区链接',
    `cover_url` VARCHAR(300) COMMENT '专区封面',
    `contact_name` VARCHAR(50) COMMENT '联系人',
    `contact_phone` VARCHAR(30) COMMENT '联系电话',
    `email` VARCHAR(100) COMMENT '邮箱',
    `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；4：撤销申请' DEFAULT 1,
    `review_time` DATETIME(6) COMMENT '审核时间',
    `shelf_status` INT NOT NULL COMMENT '上架状态。1：上架；2：下架；3：禁用' DEFAULT 1,
    `reason` LONGTEXT COMMENT '驳回理由',
    `origin_type` VARCHAR(50) NOT NULL COMMENT '创建来源。web:前台用户；admin:后台用户' DEFAULT 'web',
    KEY `idx_biz_busines_review__3adb05` (`review_no`)
) CHARACTER SET utf8mb4 COMMENT='数商专区申请记录快照表';
        CREATE TABLE IF NOT EXISTS `biz_business_zone_apply_record_file` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `apply_record_id` VARCHAR(32) NOT NULL COMMENT '数商专区申请记录ID',
    `file_name` VARCHAR(200) NOT NULL COMMENT '文件名称',
    `file_path` VARCHAR(300) NOT NULL COMMENT '文件路径',
    KEY `idx_biz_busines_apply_r_7f228a` (`apply_record_id`)
) CHARACTER SET utf8mb4 COMMENT='数商专区申请记录文件表';
        CREATE TABLE IF NOT EXISTS `biz_business_zone_file` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `zone_id` VARCHAR(32) NOT NULL COMMENT '数商专区ID',
    `file_name` VARCHAR(200) NOT NULL COMMENT '文件名称',
    `file_path` VARCHAR(300) NOT NULL COMMENT '文件路径',
    KEY `idx_biz_busines_zone_id_0b18d7` (`zone_id`)
) CHARACTER SET utf8mb4 COMMENT='数商专区文件表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `biz_business_zone_file`;
        DROP TABLE IF EXISTS `biz_business_zone_apply_record_file`;
        DROP TABLE IF EXISTS `biz_business_zone_apply_record`;
        DROP TABLE IF EXISTS `biz_business_zone`;"""
