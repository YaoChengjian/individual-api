from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `pro_demand_apply_record` (
    `id` VARCHAR(32) NOT NULL PRIMARY KEY COMMENT '主键 ID',
    `create_time` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_delete` BOOL NOT NULL COMMENT '逻辑删除标志' DEFAULT 0,
    `demand_id` VARCHAR(32) NOT NULL COMMENT '原始需求ID',
    `review_no` VARCHAR(50) COMMENT '需求审核编号',
    `user_id` VARCHAR(32) NOT NULL COMMENT 'Web用户ID',
    `title` VARCHAR(50) NOT NULL COMMENT '需求标题',
    `desc` LONGTEXT COMMENT '需求说明',
    `qualification_require` LONGTEXT COMMENT '资格要求',
    `limit_date` DATE COMMENT '截止日期',
    `contact_name` VARCHAR(50) COMMENT '联系人',
    `contact_phone` VARCHAR(30) COMMENT '联系电话',
    `status` INT NOT NULL COMMENT '状态。0：草稿；1：待审核；2：审核通过；3：审核驳回；4：撤销申请' DEFAULT 1,
    `reason` LONGTEXT COMMENT '驳回理由',
    `tag_name_list` JSON NOT NULL COMMENT '申请时的标签名称列表',
    `scene_ids` JSON NOT NULL COMMENT '申请时的应用场景ID列表',
    `scene_name_list` JSON NOT NULL COMMENT '申请时的应用场景名称列表',
    `ecology_ids` JSON NOT NULL COMMENT '申请时的产品形态ID列表',
    `ecology_name_list` JSON NOT NULL COMMENT '申请时的产品形态名称列表',
    KEY `idx_pro_demand__review__304048` (`review_no`)
) CHARACTER SET utf8mb4 COMMENT='需求申请记录快照表';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `pro_demand_apply_record`;"""
